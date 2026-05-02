from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb

from asteria.data.contracts import DataProductionAuditSummary

BASE_DATABASES = (
    "market_base_day.duckdb",
    "market_base_week.duckdb",
    "market_base_month.duckdb",
)


def run_data_production_audit(
    *,
    data_root: Path,
    run_id: str,
) -> DataProductionAuditSummary:
    checks: dict[str, str] = {}
    hard_fail_count = 0

    raw_db = data_root / "raw_market.duckdb"
    raw_status = _check_raw_market(raw_db)
    checks["raw_market.duckdb:natural_key_uniqueness"] = raw_status
    hard_fail_count += raw_status == "failed"

    for db_name in BASE_DATABASES:
        db_path = data_root / db_name
        if not db_path.exists():
            if db_name == "market_base_day.duckdb":
                checks[f"{db_name}:execution_price_line_present"] = "failed"
                hard_fail_count += 1
            continue
        for check_name, status in _check_market_base(
            db_path,
            require_execution_price_line=db_name == "market_base_day.duckdb",
        ).items():
            checks[f"{db_name}:{check_name}"] = status
            hard_fail_count += status == "failed"

    status = "passed" if hard_fail_count == 0 else "failed"
    return DataProductionAuditSummary(
        run_id=run_id,
        status=status,
        hard_fail_count=int(hard_fail_count),
        checks=checks,
    )


def _check_raw_market(path: Path) -> str:
    if not path.exists():
        return "failed"
    with duckdb.connect(str(path), read_only=True) as con:
        duplicate_count = _count_result(
            con.execute(
                """
                select count(*)
                from (
                    select source_vendor, symbol, timeframe, bar_dt, adj_mode, source_revision
                    from raw_market_bar
                    group by 1, 2, 3, 4, 5, 6
                    having count(*) > 1
                )
                """
            ).fetchone()
        )
    return "passed" if duplicate_count == 0 else "failed"


def _check_market_base(path: Path, *, require_execution_price_line: bool) -> dict[str, str]:
    with duckdb.connect(str(path), read_only=True) as con:
        natural_dups = _count_result(
            con.execute(
                """
                select count(*)
                from (
                    select symbol, timeframe, bar_dt, price_line, adj_mode
                    from market_base_bar
                    group by 1, 2, 3, 4, 5
                    having count(*) > 1
                )
                """
            ).fetchone()
        )
        latest_dups = _count_result(
            con.execute(
                """
                select count(*)
                from (
                    select symbol, timeframe, price_line, adj_mode
                    from market_base_latest
                    group by 1, 2, 3, 4
                    having count(*) > 1
                )
                """
            ).fetchone()
        )
        price_line_failures = _count_result(
            con.execute(
                """
                select count(*)
                from market_base_bar
                where (price_line = 'analysis_price_line' and adj_mode = 'none')
                   or (price_line = 'execution_price_line' and adj_mode <> 'none')
                """
            ).fetchone()
        )
        execution_line_count = _count_result(
            con.execute(
                """
                select count(*)
                from market_base_bar
                where timeframe = 'day'
                  and price_line = 'execution_price_line'
                  and adj_mode = 'none'
                """
            ).fetchone()
        )
    checks = {
        "natural_key_uniqueness": "passed" if natural_dups == 0 else "failed",
        "latest_pointer_uniqueness": "passed" if latest_dups == 0 else "failed",
        "price_line_mapping": "passed" if price_line_failures == 0 else "failed",
    }
    if require_execution_price_line:
        checks["execution_price_line_present"] = "passed" if execution_line_count > 0 else "failed"
    return checks


def _count_result(row: tuple[Any, ...] | None) -> int:
    if row is None:
        return 1
    return int(row[0])
