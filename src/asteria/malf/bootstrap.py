from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

from asteria.malf.contracts import MalfBuildSummary, MalfDayRequest
from asteria.malf.schema import (
    bootstrap_malf_core_day_database,
    bootstrap_malf_lifespan_day_database,
    bootstrap_malf_service_day_database,
)


def run_malf_day_core_build(request: MalfDayRequest) -> MalfBuildSummary:
    checkpoint = _load_checkpoint(request.checkpoint_path("core"))
    if request.mode == "resume" and checkpoint and checkpoint.get("status") == "completed":
        summary = MalfBuildSummary(**checkpoint["summary"])
        return MalfBuildSummary(**{**summary.as_dict(), "resume_reused": True})

    input_row_count = _count_market_base_rows(request)
    bootstrap_malf_core_day_database(request.core_db)
    now = _utc_now()
    with duckdb.connect(str(request.core_db)) as con:
        con.execute("begin transaction")
        con.execute("delete from malf_core_run where run_id = ?", [request.run_id])
        con.execute(
            "delete from malf_schema_version where schema_version = ?",
            [request.schema_version],
        )
        con.execute(
            """
            insert into malf_core_run
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
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
                now,
            ],
        )
        con.execute(
            "insert into malf_schema_version values (?, ?)",
            [request.schema_version, now],
        )
        con.execute("commit")

    summary = MalfBuildSummary(
        run_id=request.run_id,
        stage="core",
        status="completed",
        input_row_count=input_row_count,
    )
    _save_checkpoint(request.checkpoint_path("core"), summary)
    return summary


def run_malf_day_lifespan_build(request: MalfDayRequest) -> MalfBuildSummary:
    checkpoint = _load_checkpoint(request.checkpoint_path("lifespan"))
    if request.mode == "resume" and checkpoint and checkpoint.get("status") == "completed":
        summary = MalfBuildSummary(**checkpoint["summary"])
        return MalfBuildSummary(**{**summary.as_dict(), "resume_reused": True})

    bootstrap_malf_lifespan_day_database(request.lifespan_db)
    input_wave_count = _count_rows(request.core_db, "malf_wave_ledger")
    source_core_run_id = _latest_run_id(request.core_db, "malf_core_run")
    now = _utc_now()
    with duckdb.connect(str(request.lifespan_db)) as con:
        con.execute("begin transaction")
        con.execute("delete from malf_lifespan_run where run_id = ?", [request.run_id])
        con.execute(
            "delete from malf_sample_version where sample_version = ?",
            [request.sample_version],
        )
        con.execute(
            "delete from malf_rule_version where lifespan_rule_version = ?",
            [request.lifespan_rule_version],
        )
        con.execute(
            """
            insert into malf_lifespan_run
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
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
                now,
            ],
        )
        con.execute(
            "insert into malf_sample_version values (?, ?)",
            [request.sample_version, now],
        )
        con.execute(
            "insert into malf_rule_version values (?, ?)",
            [request.lifespan_rule_version, now],
        )
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
    checkpoint = _load_checkpoint(request.checkpoint_path("service"))
    if request.mode == "resume" and checkpoint and checkpoint.get("status") == "completed":
        summary = MalfBuildSummary(**checkpoint["summary"])
        return MalfBuildSummary(**{**summary.as_dict(), "resume_reused": True})

    bootstrap_malf_service_day_database(request.service_db)
    source_core_run_id = _latest_run_id(request.core_db, "malf_core_run")
    source_lifespan_run_id = _latest_run_id(request.lifespan_db, "malf_lifespan_run")
    now = _utc_now()
    with duckdb.connect(str(request.service_db)) as con:
        con.execute("begin transaction")
        con.execute("delete from malf_service_run where run_id = ?", [request.run_id])
        con.execute("delete from malf_interface_audit where run_id = ?", [request.run_id])
        con.execute(
            """
            insert into malf_service_run
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                request.run_id,
                "malf_day_service_build",
                request.mode,
                request.timeframe,
                "completed",
                source_core_run_id,
                source_lifespan_run_id,
                0,
                request.schema_version,
                request.service_version,
                now,
            ],
        )
        con.execute(
            """
            insert into malf_interface_audit
            values (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                f"{request.run_id}|service_scaffold",
                request.run_id,
                "service_scaffold_no_wave_position",
                "soft",
                "observe",
                0,
                (
                    "Scaffold build writes service ledger and audit shell; "
                    "semantic WavePosition publication is pending."
                ),
                now,
            ],
        )
        con.execute("commit")

    summary = MalfBuildSummary(
        run_id=request.run_id,
        stage="service",
        status="completed",
        published_row_count=0,
    )
    _save_checkpoint(request.checkpoint_path("service"), summary)
    return summary


def run_malf_day_audit(request: MalfDayRequest) -> MalfBuildSummary:
    checkpoint = _load_checkpoint(request.checkpoint_path("audit"))
    if request.mode == "resume" and checkpoint and checkpoint.get("status") == "completed":
        summary = MalfBuildSummary(**checkpoint["summary"])
        return MalfBuildSummary(**{**summary.as_dict(), "resume_reused": True})

    report_path = _report_path(request.report_root, request.run_id)
    payload = {
        "run_id": request.run_id,
        "timeframe": request.timeframe,
        "schema_version": request.schema_version,
        "core_run_exists": _latest_run_id(request.core_db, "malf_core_run") is not None,
        "lifespan_run_exists": _latest_run_id(request.lifespan_db, "malf_lifespan_run") is not None,
        "service_run_exists": _latest_run_id(request.service_db, "malf_service_run") is not None,
        "service_audit_rows": _count_rows(request.service_db, "malf_interface_audit"),
        "generated_at": _utc_now().isoformat(),
    }
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


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
