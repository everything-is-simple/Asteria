from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import duckdb

from asteria.trade.contracts import TradeBuildRequest
from asteria.trade.schema import TRADE_TABLES


@dataclass(frozen=True)
class TradeAuditCheck:
    check_name: str
    severity: str
    status: str
    failed_count: int
    sample_payload: str


def build_trade_audit_rows(
    request: TradeBuildRequest,
    created_at: datetime,
    audit_db_path: str | None = None,
) -> tuple[list[tuple[object, ...]], dict[str, Any]]:
    target_db = request.target_trade_db if audit_db_path is None else audit_db_path
    checks: list[TradeAuditCheck] = []
    trade_counts = {
        "input_portfolio_plan_count": 0,
        "order_intent_count": 0,
        "execution_plan_count": 0,
        "fill_count": 0,
        "rejection_count": 0,
    }
    with duckdb.connect(str(request.source_portfolio_plan_db), read_only=True) as source_con:
        checks.extend(_source_checks(source_con, request))
    with duckdb.connect(str(target_db), read_only=True) as trade_con:
        checks.extend(_trade_checks(trade_con, request))
        trade_counts = {
            "input_portfolio_plan_count": _scalar(
                trade_con, "select count(*) from trade_portfolio_snapshot"
            ),
            "order_intent_count": _scalar(trade_con, "select count(*) from order_intent_ledger"),
            "execution_plan_count": _scalar(
                trade_con, "select count(*) from execution_plan_ledger"
            ),
            "fill_count": _scalar(trade_con, "select count(*) from fill_ledger"),
            "rejection_count": _scalar(trade_con, "select count(*) from order_rejection_ledger"),
        }
    hard_fail_count = sum(check.failed_count for check in checks if check.severity == "hard")
    rows = [_row(request, created_at, check) for check in checks]
    payload = {
        "run_id": request.run_id,
        "timeframe": request.timeframe,
        "hard_fail_count": hard_fail_count,
        "checks": [
            {
                "check_name": check.check_name,
                "severity": check.severity,
                "status": check.status,
                "failed_count": check.failed_count,
                "sample_payload": check.sample_payload,
            }
            for check in checks
        ],
        **trade_counts,
    }
    return rows, payload


def _source_checks(
    source_con: duckdb.DuckDBPyConnection,
    request: TradeBuildRequest,
) -> list[TradeAuditCheck]:
    checks: list[TradeAuditCheck] = []
    checks.append(
        _table_presence_check(
            source_con,
            "portfolio_plan_source_surface_present",
            {
                "portfolio_plan_run",
                "portfolio_plan_audit",
                "portfolio_admission_ledger",
                "portfolio_target_exposure",
                "portfolio_trim_ledger",
            },
        )
    )
    checks.append(
        _query_check(
            source_con,
            "portfolio_plan_source_release_locked",
            """
            select case when count(*) = 1 then 0 else 1 end
            from portfolio_plan_run
            where run_id = ? and status = 'completed' and hard_fail_count = 0
            """,
            [request.source_portfolio_plan_run_id or request.source_portfolio_plan_release_version],
        )
    )
    checks.append(
        _query_check(
            source_con,
            "portfolio_plan_source_audit_clean",
            """
            select case when count(*) = 0 then 0 else 1 end
            from portfolio_plan_audit
            where run_id = ? and severity = 'hard' and status = 'fail'
            """,
            [request.source_portfolio_plan_run_id or request.source_portfolio_plan_release_version],
        )
    )
    return checks


def _trade_checks(
    trade_con: duckdb.DuckDBPyConnection,
    request: TradeBuildRequest,
) -> list[TradeAuditCheck]:
    checks: list[TradeAuditCheck] = []
    checks.append(
        _table_presence_check(trade_con, "trade_table_surface_present", set(TRADE_TABLES))
    )
    checks.append(
        _query_check(
            trade_con,
            "trade_run_row_present",
            "select case when count(*) = 1 then 0 else 1 end from trade_run where run_id = ?",
            [request.run_id],
        )
    )
    checks.append(
        _query_check(
            trade_con,
            "order_intent_natural_key_unique",
            """
            select count(*) from (
                select portfolio_admission_id, order_side, trade_rule_version, count(*) row_count
                from order_intent_ledger
                group by 1, 2, 3
                having row_count > 1
            )
            """,
        )
    )
    checks.append(
        _query_check(
            trade_con,
            "execution_plan_natural_key_unique",
            """
            select count(*) from (
                select order_intent_id, execution_plan_type, trade_rule_version, count(*) row_count
                from execution_plan_ledger
                group by 1, 2, 3
                having row_count > 1
            )
            """,
        )
    )
    checks.append(
        _query_check(
            trade_con,
            "fill_natural_key_unique",
            """
            select count(*) from (
                select
                    order_intent_id,
                    execution_dt,
                    fill_seq,
                    trade_rule_version,
                    count(*) row_count
                from fill_ledger
                group by 1, 2, 3, 4
                having row_count > 1
            )
            """,
        )
    )
    checks.append(
        _query_check(
            trade_con,
            "order_rejection_natural_key_unique",
            """
            select count(*) from (
                select order_intent_id, rejection_reason, trade_rule_version, count(*) row_count
                from order_rejection_ledger
                group by 1, 2, 3
                having row_count > 1
            )
            """,
        )
    )
    checks.append(
        _query_check(
            trade_con,
            "execution_plan_for_each_order_intent",
            """
            select case when count(*) = 0 then 0 else count(*) end
            from order_intent_ledger i
            left join execution_plan_ledger e
              on i.order_intent_id = e.order_intent_id
            where i.order_intent_state = 'intended'
              and e.order_intent_id is null
            """,
        )
    )
    checks.append(
        _query_check(
            trade_con,
            "no_simulated_fill_rows_without_evidence_source",
            "select case when count(*) = 0 then 0 else count(*) end from fill_ledger",
        )
    )
    checks.append(
        TradeAuditCheck(
            check_name="fill_ledger_retained_gap_recorded",
            severity="soft",
            status="observe",
            failed_count=0,
            sample_payload='{"fill_source_state":"retained_gap_without_evidence_source"}',
        )
    )
    checks.append(
        _forbidden_columns_check(
            trade_con,
            "forbidden_trade_columns_absent",
            {
                "strategy_score",
                "system_readout_id",
                "actual_fill",
                "broker_order_id",
                "portfolio_allocation",
            },
        )
    )
    checks.append(
        _query_check(
            trade_con,
            "unexpected_trade_tables_absent",
            """
            select case when count(*) = 0 then 0 else count(*) end
            from information_schema.tables
            where table_schema = 'main' and table_name not in (
                'trade_run',
                'trade_schema_version',
                'trade_rule_version',
                'trade_portfolio_snapshot',
                'order_intent_ledger',
                'execution_plan_ledger',
                'fill_ledger',
                'order_rejection_ledger',
                'trade_audit'
            )
            """,
        )
    )
    return checks


def _table_presence_check(
    con: duckdb.DuckDBPyConnection,
    check_name: str,
    expected: set[str],
) -> TradeAuditCheck:
    tables = {
        str(row[0])
        for row in con.execute(
            "select table_name from information_schema.tables where table_schema = 'main'"
        ).fetchall()
    }
    missing = sorted(expected - tables)
    failed_count = len(missing)
    payload = {"missing": missing, "present": sorted(tables & expected)}
    return TradeAuditCheck(
        check_name=check_name,
        severity="hard",
        status="pass" if failed_count == 0 else "fail",
        failed_count=failed_count,
        sample_payload=str(payload),
    )


def _forbidden_columns_check(
    con: duckdb.DuckDBPyConnection,
    check_name: str,
    forbidden: set[str],
) -> TradeAuditCheck:
    rows = []
    for table in (
        "trade_portfolio_snapshot",
        "order_intent_ledger",
        "execution_plan_ledger",
        "fill_ledger",
        "order_rejection_ledger",
        "trade_audit",
    ):
        for row in con.execute(f"describe {table}").fetchall():
            if row[0] in forbidden:
                rows.append(f"{table}.{row[0]}")
    return TradeAuditCheck(
        check_name=check_name,
        severity="hard",
        status="pass" if not rows else "fail",
        failed_count=len(rows),
        sample_payload=str({"forbidden_columns": rows}),
    )


def _query_check(
    con: duckdb.DuckDBPyConnection,
    check_name: str,
    sql: str,
    params: list[object] | None = None,
) -> TradeAuditCheck:
    row = con.execute(sql, params or []).fetchone()
    failed_count = 0 if row is None else int(row[0])
    return TradeAuditCheck(
        check_name=check_name,
        severity="hard",
        status="pass" if failed_count == 0 else "fail",
        failed_count=failed_count,
        sample_payload="{}" if failed_count == 0 else str({"failed_count": failed_count}),
    )


def _row(
    request: TradeBuildRequest,
    created_at: datetime,
    check: TradeAuditCheck,
) -> tuple[object, ...]:
    return (
        f"{request.run_id}|{request.timeframe}|{check.check_name}",
        request.run_id,
        check.check_name,
        check.severity,
        check.status,
        check.failed_count,
        check.sample_payload,
        created_at,
    )


def _scalar(con: duckdb.DuckDBPyConnection, sql: str) -> int:
    row = con.execute(sql).fetchone()
    return 0 if row is None else int(row[0])
