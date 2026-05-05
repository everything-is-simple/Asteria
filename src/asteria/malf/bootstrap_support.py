from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

from asteria.malf.contracts import MalfBuildSummary, MalfDayRequest
from asteria.malf.source_contract import market_base_day_clauses

CORE_SNAPSHOT_INSERT_SQL = """
insert into malf_core_state_snapshot (
    snapshot_id, symbol, timeframe, bar_dt, system_state, wave_id, old_wave_id,
    wave_core_state, direction, progress_updated, transition_span,
    guard_boundary_price, current_effective_guard_pivot_id,
    current_effective_guard_price, transition_id, break_id,
    transition_boundary_high, transition_boundary_low, active_candidate_id,
    active_candidate_guard_pivot_id, confirmation_pivot_id, new_wave_id,
    run_id, schema_version, core_rule_version, pivot_detection_rule_version,
    core_event_ordering_version, price_compare_policy, epsilon_policy,
    source_market_base_run_id, created_at
) values (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
)
"""


def delete_run(con: duckdb.DuckDBPyConnection, run_id: str, tables: tuple[str, ...]) -> None:
    for table in tables:
        con.execute(f"delete from {table} where run_id = ?", [run_id])


def insert_core_run(
    con: duckdb.DuckDBPyConnection,
    request: MalfDayRequest,
    input_row_count: int,
    source_market_base_run_id: str | None,
    created_at: datetime,
) -> None:
    con.execute(
        """
        insert into malf_core_run (
            run_id, runner_name, mode, timeframe, status, source_db, input_row_count,
            schema_version, core_rule_version, pivot_detection_rule_version,
            core_event_ordering_version, price_compare_policy, epsilon_policy,
            source_market_base_run_id, created_at
        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            request.pivot_detection_rule_version,
            request.core_event_ordering_version,
            request.price_compare_policy,
            request.epsilon_policy,
            source_market_base_run_id,
            created_at,
        ],
    )


def insert_values_sql(table_name: str, column_count: int) -> str:
    placeholders = ", ".join(["?"] * column_count)
    return f"insert into {table_name} values ({placeholders})"


def insert_lifespan_run(
    con: duckdb.DuckDBPyConnection,
    request: MalfDayRequest,
    source_core_run_id: str | None,
    input_wave_count: int,
    created_at: datetime,
) -> None:
    con.execute(
        """
        insert into malf_lifespan_run (
            run_id, runner_name, mode, timeframe, status, source_core_run_id,
            input_wave_count, schema_version, lifespan_rule_version, sample_version,
            created_at, pivot_detection_rule_version, core_event_ordering_version,
            price_compare_policy, epsilon_policy
        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            created_at,
            request.pivot_detection_rule_version,
            request.core_event_ordering_version,
            request.price_compare_policy,
            request.epsilon_policy,
        ],
    )


def insert_service_run(
    con: duckdb.DuckDBPyConnection,
    request: MalfDayRequest,
    source_core_run_id: str | None,
    source_lifespan_run_id: str | None,
    published_row_count: int,
    created_at: datetime,
) -> None:
    con.execute(
        """
        insert into malf_service_run (
            run_id, runner_name, mode, timeframe, status, source_core_run_id,
            source_lifespan_run_id, published_row_count, schema_version, service_version,
            created_at, pivot_detection_rule_version, core_event_ordering_version,
            price_compare_policy, epsilon_policy
        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
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
            request.pivot_detection_rule_version,
            request.core_event_ordering_version,
            request.price_compare_policy,
            request.epsilon_policy,
        ],
    )


def count_market_base_rows(request: MalfDayRequest) -> int:
    if not request.source_db.exists():
        raise FileNotFoundError(f"Missing market_base source DB: {request.source_db}")
    clauses, params = market_base_day_clauses(request)
    query = f"select count(*) from market_base_bar where {' and '.join(clauses)}"
    with duckdb.connect(str(request.source_db), read_only=True) as con:
        row = con.execute(query, params).fetchone()
        return 0 if row is None else int(row[0])


def count_rows_for_run(path: Path, table_name: str, run_id: str) -> int:
    if not path.exists():
        return 0
    with duckdb.connect(str(path), read_only=True) as con:
        row = con.execute(
            f"select count(*) from {table_name} where run_id = ?",
            [run_id],
        ).fetchone()
        return 0 if row is None else int(row[0])


def latest_run_id(path: Path, table_name: str) -> str | None:
    if not path.exists():
        return None
    with duckdb.connect(str(path), read_only=True) as con:
        row = con.execute(
            f"select run_id from {table_name} order by created_at desc limit 1"
        ).fetchone()
        return None if row is None else str(row[0])


def load_completed_checkpoint(request: MalfDayRequest, stage: str) -> MalfBuildSummary | None:
    if request.mode != "resume":
        return None
    checkpoint = load_checkpoint(request.checkpoint_path(stage))
    if checkpoint and checkpoint.get("status") == "completed":
        summary = MalfBuildSummary(**checkpoint["summary"])
        return MalfBuildSummary(**{**summary.as_dict(), "resume_reused": True})
    return None


def load_checkpoint(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_checkpoint(path: Path, summary: MalfBuildSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": summary.status,
        "summary": summary.as_dict(),
        "created_at": utc_now().isoformat(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def report_path(report_root: Path, run_id: str) -> Path:
    date_part = utc_now().date().isoformat()
    return report_root / "malf" / date_part / f"{run_id}-audit-summary.json"


def require(value: str | None, name: str) -> None:
    if not value:
        raise ValueError(f"{name} is required for this MALF runner stage")


def require_build_mode(request: MalfDayRequest, stage: str) -> None:
    if request.mode == "audit-only":
        raise ValueError(f"{stage} build does not support audit-only mode")


def executemany_if_rows(
    con: duckdb.DuckDBPyConnection, sql: str, rows: list[tuple[object, ...]]
) -> None:
    if rows:
        con.executemany(sql, rows)


def resolve_source_market_base_run_id(request: MalfDayRequest) -> str | None:
    if request.source_market_base_run_id:
        return request.source_market_base_run_id
    if not request.source_db.exists():
        return None
    clauses, params = market_base_day_clauses(request)
    query = f"""
        select run_id, count(*) as row_count
        from market_base_bar
        where {" and ".join(clauses)}
        group by run_id
        order by row_count desc, run_id desc
        limit 1
    """
    with duckdb.connect(str(request.source_db), read_only=True) as con:
        row = con.execute(query, params).fetchone()
    return None if row is None or row[0] is None else str(row[0])


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
