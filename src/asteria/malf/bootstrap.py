from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

from asteria.malf.audit_engine import build_audit_rows
from asteria.malf.contracts import MalfBuildSummary, MalfDayRequest
from asteria.malf.core_engine import build_core_rows
from asteria.malf.lifespan_engine import build_lifespan_rows
from asteria.malf.schema import (
    bootstrap_malf_core_day_database,
    bootstrap_malf_lifespan_day_database,
    bootstrap_malf_service_day_database,
)
from asteria.malf.service_engine import build_wave_position_rows


def run_malf_day_core_build(request: MalfDayRequest) -> MalfBuildSummary:
    _require_build_mode(request, "core")
    _require(request.core_rule_version, "core_rule_version")
    checkpoint = _load_completed_checkpoint(request, "core")
    if checkpoint:
        return checkpoint

    input_row_count = _count_market_base_rows(request)
    bootstrap_malf_core_day_database(request.core_db)
    now = _utc_now()
    rows = build_core_rows(request, now)
    with duckdb.connect(str(request.core_db)) as con:
        con.execute("begin transaction")
        _delete_run(con, request.run_id, _CORE_RUN_TABLES)
        con.execute(
            "delete from malf_schema_version where schema_version = ?",
            [request.schema_version],
        )
        con.executemany(
            "insert into malf_pivot_ledger values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    item.pivot_id,
                    item.symbol,
                    request.timeframe,
                    item.pivot_dt,
                    item.confirmed_dt,
                    item.pivot_type,
                    item.pivot_price,
                    item.pivot_seq_in_bar,
                    item.pivot_dt,
                    request.run_id,
                    request.schema_version,
                    request.core_rule_version,
                    now,
                )
                for item in rows.pivots
            ],
        )
        con.executemany(
            "insert into malf_structure_ledger values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows.structures,
        )
        con.executemany(
            """
            insert into malf_wave_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    item.wave_id,
                    item.symbol,
                    request.timeframe,
                    item.wave_seq,
                    item.direction,
                    item.birth_type,
                    item.start_pivot_id,
                    item.candidate_guard_pivot_id,
                    item.confirm_pivot_id,
                    item.confirm_dt,
                    item.wave_core_state,
                    item.terminated_dt,
                    item.terminated_by_break_id,
                    item.final_progress.pivot_id,
                    item.final_progress.pivot_price,
                    item.final_guard.pivot_id,
                    item.final_guard.pivot_price,
                    request.run_id,
                    request.schema_version,
                    request.core_rule_version,
                    now,
                )
                for item in rows.waves
            ],
        )
        con.executemany(
            "insert into malf_break_ledger values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows.breaks,
        )
        con.executemany(
            "insert into malf_transition_ledger values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    item.transition_id,
                    item.old_wave_id,
                    item.break_id,
                    item.old_direction,
                    item.old_progress.pivot_id,
                    item.old_progress.pivot_price,
                    item.break_dt,
                    item.state,
                    item.confirmed_dt,
                    item.new_wave_id,
                    request.run_id,
                    request.schema_version,
                    request.core_rule_version,
                    now,
                )
                for item in rows.transitions
            ],
        )
        con.executemany(
            "insert into malf_candidate_ledger values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    item.candidate_id,
                    item.transition_id,
                    item.guard.pivot_id,
                    item.direction,
                    item.guard.pivot_dt,
                    item.is_active_at_close,
                    item.invalidated_by_candidate_id,
                    item.reference_price,
                    item.confirmed_by_pivot_id,
                    item.confirmed_wave_id,
                    request.run_id,
                    request.schema_version,
                    request.core_rule_version,
                    now,
                )
                for item in rows.candidates
            ],
        )
        _insert_core_run(con, request, input_row_count, now)
        con.execute("insert into malf_schema_version values (?, ?)", [request.schema_version, now])
        con.execute("commit")

    summary = MalfBuildSummary(
        run_id=request.run_id,
        stage="core",
        status="completed",
        input_row_count=input_row_count,
        input_wave_count=len(rows.waves),
    )
    _save_checkpoint(request.checkpoint_path("core"), summary)
    return summary


def run_malf_day_lifespan_build(request: MalfDayRequest) -> MalfBuildSummary:
    _require_build_mode(request, "lifespan")
    _require(request.lifespan_rule_version, "lifespan_rule_version")
    _require(request.sample_version, "sample_version")
    checkpoint = _load_completed_checkpoint(request, "lifespan")
    if checkpoint:
        return checkpoint

    bootstrap_malf_lifespan_day_database(request.lifespan_db)
    input_wave_count = _count_rows(request.core_db, "malf_wave_ledger")
    source_core_run_id = _latest_run_id(request.core_db, "malf_core_run")
    now = _utc_now()
    snapshots, profiles = build_lifespan_rows(request.core_db, request, now)
    with duckdb.connect(str(request.lifespan_db)) as con:
        con.execute("begin transaction")
        _delete_run(con, request.run_id, _LIFESPAN_RUN_TABLES)
        con.executemany(
            """
            insert into malf_lifespan_snapshot
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            snapshots,
        )
        con.executemany(
            """
            insert into malf_lifespan_profile
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            profiles,
        )
        con.execute(
            "delete from malf_sample_version where sample_version = ?",
            [request.sample_version],
        )
        con.execute(
            "delete from malf_rule_version where lifespan_rule_version = ?",
            [request.lifespan_rule_version],
        )
        con.execute(
            "insert into malf_sample_version values (?, ?, ?, ?, ?, ?, ?)",
            [
                request.sample_version,
                "all_eligible_symbols",
                request.timeframe,
                "both",
                "all",
                "<= current bar_dt",
                now,
            ],
        )
        con.execute(
            "insert into malf_rule_version values (?, ?, ?, ?, ?)",
            [request.lifespan_rule_version, 0.25, 0.75, 0.75, now],
        )
        _insert_lifespan_run(con, request, source_core_run_id, input_wave_count, now)
        con.execute("commit")

    summary = MalfBuildSummary(
        run_id=request.run_id,
        stage="lifespan",
        status="completed",
        input_wave_count=input_wave_count,
    )
    _save_checkpoint(request.checkpoint_path("lifespan"), summary)
    return summary


def run_malf_day_service_build(request: MalfDayRequest) -> MalfBuildSummary:
    _require_build_mode(request, "service")
    _require(request.service_version, "service_version")
    checkpoint = _load_completed_checkpoint(request, "service")
    if checkpoint:
        return checkpoint

    bootstrap_malf_service_day_database(request.service_db)
    source_core_run_id = _latest_run_id(request.core_db, "malf_core_run")
    source_lifespan_run_id = _latest_run_id(request.lifespan_db, "malf_lifespan_run")
    now = _utc_now()
    rows, latest_rows = build_wave_position_rows(
        request.lifespan_db, source_core_run_id, source_lifespan_run_id, request, now
    )
    with duckdb.connect(str(request.service_db)) as con:
        con.execute("begin transaction")
        _delete_run(con, request.run_id, _SERVICE_RUN_TABLES)
        con.executemany(
            """
            insert into malf_wave_position
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        con.executemany(
            """
            insert into malf_wave_position_latest
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            latest_rows,
        )
        _insert_service_run(
            con,
            request,
            source_core_run_id,
            source_lifespan_run_id,
            len(rows),
            now,
        )
        con.execute("commit")

    summary = MalfBuildSummary(
        run_id=request.run_id,
        stage="service",
        status="completed",
        published_row_count=len(rows),
    )
    _save_checkpoint(request.checkpoint_path("service"), summary)
    return summary


def run_malf_day_audit(request: MalfDayRequest) -> MalfBuildSummary:
    checkpoint = _load_completed_checkpoint(request, "audit")
    if checkpoint:
        return checkpoint

    bootstrap_malf_service_day_database(request.service_db)
    now = _utc_now()
    audit_rows, payload = build_audit_rows(
        request.core_db, request.lifespan_db, request.service_db, request, now
    )
    with duckdb.connect(str(request.service_db)) as con:
        con.execute("begin transaction")
        con.execute("delete from malf_interface_audit where run_id = ?", [request.run_id])
        con.executemany(
            "insert into malf_interface_audit values (?, ?, ?, ?, ?, ?, ?, ?)",
            audit_rows,
        )
        con.execute("commit")

    report_path = _report_path(request.report_root, request.run_id)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = MalfBuildSummary(
        run_id=request.run_id,
        stage="audit",
        status="completed",
        report_path=str(report_path),
    )
    _save_checkpoint(request.checkpoint_path("audit"), summary)
    return summary


_CORE_RUN_TABLES = (
    "malf_core_run",
    "malf_pivot_ledger",
    "malf_structure_ledger",
    "malf_wave_ledger",
    "malf_break_ledger",
    "malf_transition_ledger",
    "malf_candidate_ledger",
)
_LIFESPAN_RUN_TABLES = (
    "malf_lifespan_run",
    "malf_lifespan_snapshot",
    "malf_lifespan_profile",
)
_SERVICE_RUN_TABLES = (
    "malf_service_run",
    "malf_wave_position",
    "malf_wave_position_latest",
    "malf_interface_audit",
)


def _delete_run(con: duckdb.DuckDBPyConnection, run_id: str, tables: tuple[str, ...]) -> None:
    for table in tables:
        con.execute(f"delete from {table} where run_id = ?", [run_id])


def _insert_core_run(
    con: duckdb.DuckDBPyConnection,
    request: MalfDayRequest,
    input_row_count: int,
    created_at: datetime,
) -> None:
    con.execute(
        "insert into malf_core_run values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            request.run_id,
            "malf_day_core_build",
            request.mode,
            request.timeframe,
            "completed",
            str(request.source_db),
            input_row_count,
            request.schema_version,
            request.core_rule_version,
            created_at,
        ],
    )


def _insert_lifespan_run(
    con: duckdb.DuckDBPyConnection,
    request: MalfDayRequest,
    source_core_run_id: str | None,
    input_wave_count: int,
    created_at: datetime,
) -> None:
    con.execute(
        "insert into malf_lifespan_run values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            request.run_id,
            "malf_day_lifespan_build",
            request.mode,
            request.timeframe,
            "completed",
            source_core_run_id,
            input_wave_count,
            request.schema_version,
            request.lifespan_rule_version,
            request.sample_version,
            created_at,
        ],
    )


def _insert_service_run(
    con: duckdb.DuckDBPyConnection,
    request: MalfDayRequest,
    source_core_run_id: str | None,
    source_lifespan_run_id: str | None,
    published_row_count: int,
    created_at: datetime,
) -> None:
    con.execute(
        "insert into malf_service_run values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            request.run_id,
            "malf_day_service_build",
            request.mode,
            request.timeframe,
            "completed",
            source_core_run_id,
            source_lifespan_run_id,
            published_row_count,
            request.schema_version,
            request.service_version,
            created_at,
        ],
    )


def _count_market_base_rows(request: MalfDayRequest) -> int:
    if not request.source_db.exists():
        raise FileNotFoundError(f"Missing market_base source DB: {request.source_db}")
    clauses = ["timeframe = ?"]
    params: list[object] = [request.timeframe]
    if request.start_date:
        clauses.append("bar_dt >= ?")
        params.append(request.start_date)
    if request.end_date:
        clauses.append("bar_dt <= ?")
        params.append(request.end_date)
    query = f"select count(*) from market_base_bar where {' and '.join(clauses)}"
    with duckdb.connect(str(request.source_db), read_only=True) as con:
        row = con.execute(query, params).fetchone()
        return 0 if row is None else int(row[0])


def _count_rows(path: Path, table_name: str) -> int:
    if not path.exists():
        return 0
    with duckdb.connect(str(path), read_only=True) as con:
        row = con.execute(f"select count(*) from {table_name}").fetchone()
        return 0 if row is None else int(row[0])


def _latest_run_id(path: Path, table_name: str) -> str | None:
    if not path.exists():
        return None
    with duckdb.connect(str(path), read_only=True) as con:
        row = con.execute(
            f"select run_id from {table_name} order by created_at desc limit 1"
        ).fetchone()
        return None if row is None else str(row[0])


def _load_completed_checkpoint(request: MalfDayRequest, stage: str) -> MalfBuildSummary | None:
    if request.mode != "resume":
        return None
    checkpoint = _load_checkpoint(request.checkpoint_path(stage))
    if checkpoint and checkpoint.get("status") == "completed":
        summary = MalfBuildSummary(**checkpoint["summary"])
        return MalfBuildSummary(**{**summary.as_dict(), "resume_reused": True})
    return None


def _load_checkpoint(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _save_checkpoint(path: Path, summary: MalfBuildSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": summary.status,
        "summary": summary.as_dict(),
        "created_at": _utc_now().isoformat(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _report_path(report_root: Path, run_id: str) -> Path:
    date_part = _utc_now().date().isoformat()
    return report_root / "malf" / date_part / f"{run_id}-audit-summary.json"


def _require(value: str | None, name: str) -> None:
    if not value:
        raise ValueError(f"{name} is required for this MALF runner stage")


def _require_build_mode(request: MalfDayRequest, stage: str) -> None:
    if request.mode == "audit-only":
        raise ValueError(f"{stage} build does not support audit-only mode")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
