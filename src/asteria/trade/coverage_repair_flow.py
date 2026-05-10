from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb

from asteria.trade.audit_engine import build_trade_audit_rows
from asteria.trade.contracts import TradeBuildRequest
from asteria.trade.coverage_repair_contracts import (
    FOCUS_DATES,
    FOCUS_END,
    FOCUS_START,
    Trade2024CoverageRepairRequest,
)
from asteria.trade.coverage_repair_shared import trade_report_dir
from asteria.trade.rules import PortfolioPlanInput, portfolio_plan_input_from_row
from asteria.trade.schema import bootstrap_trade_database


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


def load_focus_portfolio_plan_inputs(
    portfolio_plan_db: Path,
    portfolio_plan_run_id: str,
) -> list[PortfolioPlanInput]:
    if not portfolio_plan_db.exists():
        raise FileNotFoundError(f"Missing Portfolio Plan DB: {portfolio_plan_db}")
    with duckdb.connect(str(portfolio_plan_db), read_only=True) as con:
        rows = con.execute(
            """
            select a.portfolio_admission_id, a.position_candidate_id, a.symbol, a.timeframe,
                   a.plan_dt, a.admission_state, a.admission_reason,
                   te.target_exposure_id, te.exposure_type, te.target_weight,
                   te.target_notional, te.target_quantity_hint,
                   a.source_position_release_version, a.portfolio_plan_rule_version,
                   r.run_id, a.run_id, t.trim_reason
            from portfolio_admission_ledger a
            left join portfolio_target_exposure te
              on a.portfolio_admission_id = te.portfolio_admission_id
             and (te.exposure_type = 'target_weight' or te.exposure_type is null)
            left join portfolio_trim_ledger t
              on a.portfolio_admission_id = t.portfolio_admission_id
            left join portfolio_plan_run r
              on a.run_id = r.run_id
            where a.timeframe = 'day'
              and a.run_id = ?
              and a.plan_dt >= ?
              and a.plan_dt <= ?
            order by a.symbol, a.plan_dt, a.portfolio_admission_id
            """,
            [portfolio_plan_run_id, FOCUS_START, FOCUS_END],
        ).fetchall()
    inputs = [portfolio_plan_input_from_row(row) for row in rows]
    distinct_dates = {item.plan_dt.isoformat() for item in inputs}
    missing = sorted(set(FOCUS_DATES) - distinct_dates)
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"released Portfolio Plan day surface missing focus dates: {joined}")
    return inputs


def apply_focus_window_repair(
    *,
    target_trade_db: Path,
    build_request: TradeBuildRequest,
    trade_rows,
    created_at: datetime,
) -> None:
    bootstrap_trade_database(target_trade_db)
    with duckdb.connect(str(target_trade_db)) as con:
        existing = con.execute(
            "select run_id from trade_run where run_id = ?",
            [build_request.run_id],
        ).fetchone()
        if existing is None:
            raise ValueError(f"missing released trade run row: {build_request.run_id}")
        con.execute("begin transaction")
        _ensure_reference_rows(con, build_request, created_at)
        _delete_focus_window_rows(con, build_request.run_id)
        _insert_rows(
            con,
            """
            insert into trade_portfolio_snapshot
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            trade_rows.snapshots,
        )
        _insert_rows(
            con,
            """
            insert into order_intent_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            trade_rows.intents,
        )
        _insert_rows(
            con,
            """
            insert into execution_plan_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            trade_rows.execution_plans,
        )
        _insert_rows(
            con,
            """
            insert into fill_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            trade_rows.fills,
        )
        _insert_rows(
            con,
            """
            insert into order_rejection_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            trade_rows.rejections,
        )
        counts = _trade_counts(con, build_request.run_id)
        con.execute(
            """
            update trade_run
            set status = 'completed',
                source_portfolio_plan_db = ?,
                input_portfolio_plan_count = ?,
                order_intent_count = ?,
                execution_plan_count = ?,
                fill_count = ?,
                rejection_count = ?,
                hard_fail_count = 0,
                schema_version = ?,
                trade_rule_version = ?,
                source_portfolio_plan_release_version = ?,
                source_portfolio_plan_run_id = ?,
                created_at = ?
            where run_id = ?
            """,
            [
                str(build_request.source_portfolio_plan_db),
                counts["snapshots"],
                counts["intents"],
                counts["execution_plans"],
                counts["fills"],
                counts["rejections"],
                build_request.schema_version,
                build_request.trade_rule_version,
                build_request.source_portfolio_plan_release_version,
                build_request.source_portfolio_plan_run_id,
                created_at,
                build_request.run_id,
            ],
        )
        con.execute("commit")


def run_repair_audit(
    *,
    build_request: TradeBuildRequest,
    repair_request: Trade2024CoverageRepairRequest,
    created_at: datetime,
) -> tuple[Path, dict[str, Any]]:
    audit_rows, payload = build_trade_audit_rows(build_request, created_at)
    with duckdb.connect(str(build_request.target_trade_db)) as con:
        con.execute("begin transaction")
        con.execute("delete from trade_audit where run_id = ?", [build_request.run_id])
        con.executemany("insert into trade_audit values (?, ?, ?, ?, ?, ?, ?, ?)", audit_rows)
        con.execute(
            """
            update trade_run
            set hard_fail_count = ?,
                status = ?
            where run_id = ?
            """,
            [
                payload["hard_fail_count"],
                "completed" if int(payload["hard_fail_count"]) == 0 else "failed",
                build_request.run_id,
            ],
        )
        con.execute("commit")
    report_dir = trade_report_dir(repair_request.report_root, repair_request.run_id)
    report_dir.mkdir(parents=True, exist_ok=True)
    audit_report_path = report_dir / "trade-day-audit-summary.json"
    audit_report_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return audit_report_path, payload


def _ensure_reference_rows(
    con: duckdb.DuckDBPyConnection,
    build_request: TradeBuildRequest,
    created_at: datetime,
) -> None:
    schema_row = con.execute(
        "select 1 from trade_schema_version where schema_version = ? limit 1",
        [build_request.schema_version],
    ).fetchone()
    if schema_row is None:
        con.execute(
            "insert into trade_schema_version values (?, ?)",
            [build_request.schema_version, created_at],
        )
    rule_row = con.execute(
        "select 1 from trade_rule_version where trade_rule_version = ? limit 1",
        [build_request.trade_rule_version],
    ).fetchone()
    if rule_row is None:
        con.execute(
            "insert into trade_rule_version values (?, ?, ?, ?)",
            [
                build_request.trade_rule_version,
                "portfolio_plan_to_trade_day",
                "retained_gap_without_fill_source",
                created_at,
            ],
        )


def _delete_focus_window_rows(con: duckdb.DuckDBPyConnection, run_id: str) -> None:
    con.execute(
        """
        delete from fill_ledger
        where run_id = ? and execution_dt >= ? and execution_dt <= ?
        """,
        [run_id, FOCUS_START, FOCUS_END],
    )
    con.execute(
        """
        delete from execution_plan_ledger
        where run_id = ? and execution_valid_from >= ? and execution_valid_from <= ?
        """,
        [run_id, FOCUS_START, FOCUS_END],
    )
    con.execute(
        """
        delete from order_intent_ledger
        where run_id = ? and intent_dt >= ? and intent_dt <= ?
        """,
        [run_id, FOCUS_START, FOCUS_END],
    )
    con.execute(
        """
        delete from order_rejection_ledger
        where run_id = ? and rejection_dt >= ? and rejection_dt <= ?
        """,
        [run_id, FOCUS_START, FOCUS_END],
    )
    con.execute(
        """
        delete from trade_portfolio_snapshot
        where trade_run_id = ? and plan_dt >= ? and plan_dt <= ?
        """,
        [run_id, FOCUS_START, FOCUS_END],
    )


def _trade_counts(con: duckdb.DuckDBPyConnection, run_id: str) -> dict[str, int]:
    return {
        "snapshots": _count_rows(con, "trade_portfolio_snapshot", "trade_run_id", run_id),
        "intents": _count_rows(con, "order_intent_ledger", "run_id", run_id),
        "execution_plans": _count_rows(con, "execution_plan_ledger", "run_id", run_id),
        "fills": _count_rows(con, "fill_ledger", "run_id", run_id),
        "rejections": _count_rows(con, "order_rejection_ledger", "run_id", run_id),
    }


def _count_rows(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    key_name: str,
    run_id: str,
) -> int:
    row = con.execute(
        f"select count(*) from {table_name} where {key_name} = ?", [run_id]
    ).fetchone()
    return 0 if row is None or row[0] is None else int(row[0])


def _insert_rows(
    con: duckdb.DuckDBPyConnection,
    query: str,
    rows: list[tuple[object, ...]],
) -> None:
    if rows:
        con.executemany(query, rows)
