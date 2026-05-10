from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb

from asteria.portfolio_plan.audit_engine import build_portfolio_plan_audit_rows
from asteria.portfolio_plan.contracts import PortfolioPlanBuildRequest
from asteria.portfolio_plan.coverage_repair_contracts import (
    FOCUS_DATES,
    FOCUS_END,
    FOCUS_START,
    PortfolioPlan2024CoverageRepairRequest,
)
from asteria.portfolio_plan.coverage_repair_shared import portfolio_plan_report_dir
from asteria.portfolio_plan.rules import PositionPlanInput, position_input_from_row
from asteria.portfolio_plan.schema import bootstrap_portfolio_plan_database


def resolve_released_chain(system_db: Path) -> dict[str, Any]:
    with duckdb.connect(str(system_db), read_only=True) as con:
        row = con.execute(
            """
            select run_id
            from system_readout_run
            where status = 'completed'
            order by created_at desc
            limit 1
            """
        ).fetchone()
        if row is None or row[0] is None:
            raise ValueError("missing completed system_readout_run row")
        released_system_run_id = str(row[0])
        manifest_rows = [
            {
                "module_name": str(item[0]),
                "source_db": str(item[1]),
                "source_run_id": str(item[2]),
                "source_release_version": str(item[3]),
            }
            for item in con.execute(
                """
                select module_name, source_db, source_run_id, source_release_version
                from system_source_manifest
                where system_readout_run_id = ?
                """,
                [released_system_run_id],
            ).fetchall()
        ]
    return {
        "released_system_run_id": released_system_run_id,
        "manifest_rows": manifest_rows,
    }


def single_manifest_row(
    manifest_rows: list[dict[str, str]],
    module_name: str,
) -> dict[str, str]:
    matches = [row for row in manifest_rows if row["module_name"] == module_name]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {module_name} manifest row")
    return matches[0]


def load_focus_position_inputs(
    position_db: Path,
    position_run_id: str,
) -> list[PositionPlanInput]:
    if not position_db.exists():
        raise FileNotFoundError(f"Missing Position DB: {position_db}")
    with duckdb.connect(str(position_db), read_only=True) as con:
        rows = con.execute(
            """
            select c.position_candidate_id, c.signal_id, c.symbol, c.timeframe,
                   c.candidate_dt, c.candidate_type, c.candidate_state,
                   c.position_bias, c.reason_code, c.run_id, c.position_rule_version,
                   e.entry_plan_id, x.exit_plan_id
            from position_candidate_ledger c
            left join position_entry_plan e
              on c.position_candidate_id = e.position_candidate_id
            left join position_exit_plan x
              on c.position_candidate_id = x.position_candidate_id
            where c.timeframe = 'day'
              and c.run_id = ?
              and c.candidate_dt >= ?
              and c.candidate_dt <= ?
            order by c.symbol, c.candidate_dt, c.position_candidate_id
            """,
            [position_run_id, FOCUS_START, FOCUS_END],
        ).fetchall()
    positions = [position_input_from_row(row) for row in rows]
    distinct_dates = {item.candidate_dt.isoformat() for item in positions}
    missing = sorted(set(FOCUS_DATES) - distinct_dates)
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"released Position day surface missing focus dates: {joined}")
    return positions


def apply_focus_window_repair(
    *,
    target_portfolio_plan_db: Path,
    build_request: PortfolioPlanBuildRequest,
    portfolio_rows,
    created_at: datetime,
) -> None:
    bootstrap_portfolio_plan_database(target_portfolio_plan_db)
    with duckdb.connect(str(target_portfolio_plan_db)) as con:
        existing = con.execute(
            """
            select run_id
            from portfolio_plan_run
            where run_id = ?
            """,
            [build_request.run_id],
        ).fetchone()
        if existing is None:
            raise ValueError(f"missing released portfolio_plan run row: {build_request.run_id}")
        con.execute("begin transaction")
        _ensure_reference_rows(con, build_request, created_at)
        _delete_focus_window_rows(con, build_request.run_id)
        con.execute(
            """
            delete from portfolio_constraint_ledger
            where run_id = ?
            """,
            [build_request.run_id],
        )
        _insert_rows(
            con,
            """
            insert into portfolio_position_snapshot
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            portfolio_rows.snapshots,
        )
        _insert_rows(
            con,
            """
            insert into portfolio_constraint_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            portfolio_rows.constraints,
        )
        _insert_rows(
            con,
            """
            insert into portfolio_admission_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            portfolio_rows.admissions,
        )
        _insert_rows(
            con,
            """
            insert into portfolio_target_exposure
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            portfolio_rows.exposures,
        )
        _insert_rows(
            con,
            """
            insert into portfolio_trim_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            portfolio_rows.trims,
        )
        snapshot_count = _count_rows(
            con,
            table_name="portfolio_position_snapshot",
            key_name="portfolio_run_id",
            run_id=build_request.run_id,
        )
        admission_count = _count_rows(
            con,
            table_name="portfolio_admission_ledger",
            key_name="run_id",
            run_id=build_request.run_id,
        )
        exposure_count = _count_rows(
            con,
            table_name="portfolio_target_exposure",
            key_name="run_id",
            run_id=build_request.run_id,
        )
        trim_count = _count_rows(
            con,
            table_name="portfolio_trim_ledger",
            key_name="run_id",
            run_id=build_request.run_id,
        )
        con.execute(
            """
            update portfolio_plan_run
            set status = 'completed',
                source_position_db = ?,
                input_position_count = ?,
                admission_count = ?,
                target_exposure_count = ?,
                trim_count = ?,
                hard_fail_count = 0,
                schema_version = ?,
                portfolio_plan_rule_version = ?,
                source_position_release_version = ?,
                source_position_run_id = ?,
                created_at = ?
            where run_id = ?
            """,
            [
                str(build_request.source_position_db),
                snapshot_count,
                admission_count,
                exposure_count,
                trim_count,
                build_request.schema_version,
                build_request.portfolio_plan_rule_version,
                build_request.source_position_release_version,
                build_request.source_position_run_id,
                created_at,
                build_request.run_id,
            ],
        )
        con.execute("commit")


def _ensure_reference_rows(
    con: duckdb.DuckDBPyConnection,
    build_request: PortfolioPlanBuildRequest,
    created_at: datetime,
) -> None:
    schema_row = con.execute(
        """
        select 1
        from portfolio_plan_schema_version
        where schema_version = ?
        limit 1
        """,
        [build_request.schema_version],
    ).fetchone()
    if schema_row is None:
        con.execute(
            "insert into portfolio_plan_schema_version values (?, ?)",
            [build_request.schema_version, created_at],
        )
    rule_row = con.execute(
        """
        select 1
        from portfolio_plan_rule_version
        where portfolio_plan_rule_version = ?
        limit 1
        """,
        [build_request.portfolio_plan_rule_version],
    ).fetchone()
    if rule_row is None:
        con.execute(
            "insert into portfolio_plan_rule_version values (?, ?, ?, ?)",
            [
                build_request.portfolio_plan_rule_version,
                "position_capacity_admission",
                build_request.max_active_symbols,
                created_at,
            ],
        )


def _delete_focus_window_rows(con: duckdb.DuckDBPyConnection, run_id: str) -> None:
    admission_ids = [
        row[0]
        for row in con.execute(
            """
            select portfolio_admission_id
            from portfolio_admission_ledger
            where run_id = ?
              and timeframe = 'day'
              and plan_dt >= ?
              and plan_dt <= ?
            """,
            [run_id, FOCUS_START, FOCUS_END],
        ).fetchall()
    ]
    if admission_ids:
        placeholders = ", ".join(["?"] * len(admission_ids))
        con.execute(
            (
                "delete from portfolio_target_exposure "
                f"where run_id = ? and portfolio_admission_id in ({placeholders})"
            ),
            [run_id, *admission_ids],
        )
        con.execute(
            (
                "delete from portfolio_trim_ledger "
                f"where run_id = ? and portfolio_admission_id in ({placeholders})"
            ),
            [run_id, *admission_ids],
        )
    con.execute(
        """
        delete from portfolio_admission_ledger
        where run_id = ?
          and timeframe = 'day'
          and plan_dt >= ?
          and plan_dt <= ?
        """,
        [run_id, FOCUS_START, FOCUS_END],
    )
    con.execute(
        """
        delete from portfolio_position_snapshot
        where portfolio_run_id = ?
          and timeframe = 'day'
          and candidate_dt >= ?
          and candidate_dt <= ?
        """,
        [run_id, FOCUS_START, FOCUS_END],
    )


def _count_rows(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    key_name: str,
    run_id: str,
) -> int:
    row = con.execute(
        f"select count(*) from {table_name} where {key_name} = ?",
        [run_id],
    ).fetchone()
    return 0 if row is None or row[0] is None else int(row[0])


def _insert_rows(
    con: duckdb.DuckDBPyConnection,
    query: str,
    rows: list[tuple[object, ...]],
) -> None:
    if rows:
        con.executemany(query, rows)


def run_repair_audit(
    *,
    build_request: PortfolioPlanBuildRequest,
    repair_request: PortfolioPlan2024CoverageRepairRequest,
    created_at: datetime,
) -> tuple[Path, dict[str, Any]]:
    audit_rows, payload = build_portfolio_plan_audit_rows(build_request, created_at)
    with duckdb.connect(str(build_request.target_portfolio_plan_db)) as con:
        con.execute("begin transaction")
        con.execute("delete from portfolio_plan_audit where run_id = ?", [build_request.run_id])
        con.executemany(
            "insert into portfolio_plan_audit values (?, ?, ?, ?, ?, ?, ?, ?)",
            audit_rows,
        )
        con.execute(
            """
            update portfolio_plan_run
            set hard_fail_count = ?,
                status = ?,
                input_position_count = ?,
                admission_count = ?,
                target_exposure_count = ?,
                trim_count = ?
            where run_id = ?
            """,
            [
                payload["hard_fail_count"],
                "completed" if int(payload["hard_fail_count"]) == 0 else "failed",
                payload["input_position_count"],
                payload["admission_count"],
                payload["target_exposure_count"],
                payload["trim_count"],
                build_request.run_id,
            ],
        )
        con.execute("commit")
    report_dir = portfolio_plan_report_dir(repair_request.report_root, repair_request.run_id)
    report_dir.mkdir(parents=True, exist_ok=True)
    audit_report_path = report_dir / "portfolio-plan-day-audit-summary.json"
    audit_report_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return audit_report_path, payload
