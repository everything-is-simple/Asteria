from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

from asteria.data.contracts import (
    DATA_MARKET_META_SCHEMA_VERSION,
    MarketMetaBuildRequest,
    MarketMetaBuildSummary,
)
from asteria.data.schema import bootstrap_market_meta_database

MARKET_META_TABLES = (
    "trade_calendar",
    "instrument_master",
    "instrument_alias",
    "universe_membership",
    "tradability_fact",
    "industry_classification",
    "meta_run",
    "meta_schema_version",
    "meta_source_manifest",
)

NATURAL_KEY_CHECKS = {
    "trade_calendar": ("calendar_code", "trade_date"),
    "instrument_master": ("instrument_id",),
    "instrument_alias": ("source_vendor", "source_symbol", "effective_date"),
    "universe_membership": ("universe_name", "instrument_id", "effective_date"),
    "tradability_fact": ("instrument_id", "trade_date", "fact_name"),
}


def run_market_meta_build(request: MarketMetaBuildRequest) -> MarketMetaBuildSummary:
    if request.mode == "audit-only":
        return _summary_from_audit(request, request.formal_db_path, promoted=False)

    request.staging_db_path.parent.mkdir(parents=True, exist_ok=True)
    if request.staging_db_path.exists():
        request.staging_db_path.unlink()

    bootstrap_market_meta_database(request.staging_db_path)
    _write_market_meta(request)
    audit_summary = _summary_from_audit(request, request.staging_db_path, promoted=False)
    if audit_summary.status != "passed":
        return audit_summary

    request.data_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(request.staging_db_path, request.formal_db_path)
    return _summary_from_audit(request, request.formal_db_path, promoted=True)


def audit_market_meta_database(path: Path) -> tuple[dict[str, str], int, dict[str, int]]:
    checks: dict[str, str] = {}
    row_counts: dict[str, int] = {}
    if not path.exists():
        return {"market_meta.duckdb:exists": "failed"}, 1, row_counts

    hard_fail_count = 0
    with duckdb.connect(str(path), read_only=True) as con:
        existing_tables = {
            str(row[0])
            for row in con.execute(
                """
                select table_name
                from information_schema.tables
                where table_schema = 'main'
                """
            ).fetchall()
        }
        checks["market_meta.duckdb:exists"] = "passed"
        for table in MARKET_META_TABLES:
            table_status = "passed" if table in existing_tables else "failed"
            checks[f"market_meta.duckdb:{table}_exists"] = table_status
            hard_fail_count += table_status == "failed"
            if table_status == "passed":
                row_counts[table] = _count_result(
                    con.execute(f"select count(*) from {table}").fetchone()
                )
        if hard_fail_count:
            return checks, int(hard_fail_count), row_counts

        for table, key_columns in NATURAL_KEY_CHECKS.items():
            duplicate_count = _count_duplicates(con, table, key_columns)
            status = "passed" if duplicate_count == 0 else "failed"
            checks[f"market_meta.duckdb:{table}_natural_key_uniqueness"] = status
            hard_fail_count += status == "failed"

        source_policy_failures = _count_result(
            con.execute(
                """
                select count(*)
                from tradability_fact
                where fact_name <> 'has_execution_bar'
                   or fact_value is distinct from true
                   or source_price_line <> 'execution_price_line'
                   or source_adj_mode <> 'none'
                   or source_db_name <> 'market_base_day.duckdb'
                """
            ).fetchone()
        )
        source_policy_status = "passed" if source_policy_failures == 0 else "failed"
        checks["market_meta.duckdb:tradability_fact_source_policy"] = source_policy_status
        hard_fail_count += source_policy_status == "failed"

        industry_rows = row_counts.get("industry_classification", 0)
        checks["market_meta.duckdb:industry_classification_source_gap"] = (
            "passed" if industry_rows == 0 else "failed"
        )
        hard_fail_count += industry_rows != 0

    return checks, int(hard_fail_count), row_counts


def _write_market_meta(request: MarketMetaBuildRequest) -> None:
    now = _utc_now()
    paths = _source_paths(request.data_root)
    with duckdb.connect(str(request.staging_db_path)) as con:
        _attach_existing_sources(con, paths)
        con.execute("begin transaction")
        _clear_tables(con)
        _write_trade_calendar(con, request, now)
        _write_instrument_master(con, now)
        _write_instrument_alias(con, paths.raw_db, request.run_id, now)
        _write_universe_membership(con, now)
        _write_tradability_fact(con, request, now)
        _write_meta_source_manifest(con, request, paths, now)
        _write_meta_versions_and_run(con, request, now)
        con.execute("commit")


def _write_trade_calendar(
    con: duckdb.DuckDBPyConnection,
    request: MarketMetaBuildRequest,
    now: datetime,
) -> None:
    con.execute(
        """
        insert into trade_calendar
        select distinct
            'CN_A_SHARE' as calendar_code,
            trade_date,
            true as is_open,
            'day' as source_timeframe,
            'market_base_day.duckdb' as source_db_name,
            ? as run_id,
            ? as schema_version,
            ? as created_at
        from day_db.market_base_bar
        where trade_date is not null
        """,
        [request.run_id, DATA_MARKET_META_SCHEMA_VERSION, now],
    )


def _write_instrument_master(con: duckdb.DuckDBPyConnection, now: datetime) -> None:
    con.execute(
        """
        create temp table observed_symbol(
            symbol varchar,
            asset_type varchar,
            trade_date date
        )
        """
    )
    if _attached(con, "raw_db"):
        con.execute(
            """
            insert into observed_symbol
            select symbol, asset_type, trade_date
            from raw_db.raw_market_bar
            where symbol is not null and trade_date is not null
            """
        )
    for alias in ("day_db", "week_db", "month_db"):
        if not _attached(con, alias):
            continue
        con.execute(
            f"""
            insert into observed_symbol
            select symbol, asset_type, trade_date
            from {alias}.market_base_bar
            where symbol is not null and trade_date is not null
            """
        )
    con.execute(
        """
        insert into instrument_master
        select
            symbol as instrument_id,
            symbol,
            case
                when ends_with(symbol, '.SH') then 'SH'
                when ends_with(symbol, '.SZ') then 'SZ'
                when ends_with(symbol, '.BJ') then 'BJ'
                else 'UNKNOWN'
            end as exchange_code,
            min(asset_type) as asset_type,
            min(trade_date) as first_seen_date,
            max(trade_date) as latest_seen_date,
            'observed' as list_status,
            'raw_market_and_market_base' as source_scope,
            (select run_id from trade_calendar limit 1) as run_id,
            ? as schema_version,
            ? as created_at
        from observed_symbol
        group by symbol
        """,
        [DATA_MARKET_META_SCHEMA_VERSION, now],
    )


def _write_instrument_alias(
    con: duckdb.DuckDBPyConnection,
    raw_db_path: Path,
    run_id: str,
    now: datetime,
) -> None:
    if not raw_db_path.exists():
        return
    rows = con.execute(
        """
        select distinct source_vendor, symbol, source_path
        from raw_db.raw_market_source_file
        where symbol is not null and source_path is not null
        """
    ).fetchall()
    aliases = []
    seen: set[tuple[str, str]] = set()
    for source_vendor, instrument_id, source_path in rows:
        source_symbol = _source_symbol_from_path(str(source_path))
        key = (str(source_vendor), source_symbol)
        if key in seen:
            continue
        seen.add(key)
        aliases.append(
            (
                str(source_vendor),
                source_symbol,
                str(instrument_id),
                "source_path_stem",
                str(source_path),
                "1900-01-01",
                run_id,
                DATA_MARKET_META_SCHEMA_VERSION,
                now,
            )
        )
    con.executemany(
        """
        insert into instrument_alias
        values (?, ?, ?, ?, ?, cast(? as date), ?, ?, ?)
        """,
        aliases,
    )


def _write_universe_membership(con: duckdb.DuckDBPyConnection, now: datetime) -> None:
    con.execute(
        """
        insert into universe_membership
        select
            'stock_observed' as universe_name,
            instrument_id,
            first_seen_date as effective_date,
            'observed' as membership_status,
            'raw_market_and_market_base' as source_scope,
            run_id,
            schema_version,
            ? as created_at
        from instrument_master
        where asset_type = 'stock'
        """,
        [now],
    )


def _write_tradability_fact(
    con: duckdb.DuckDBPyConnection,
    request: MarketMetaBuildRequest,
    now: datetime,
) -> None:
    con.execute(
        """
        insert into tradability_fact
        select distinct
            symbol as instrument_id,
            trade_date,
            'has_execution_bar' as fact_name,
            true as fact_value,
            'execution_price_line' as source_price_line,
            'none' as source_adj_mode,
            'market_base_day.duckdb' as source_db_name,
            ? as run_id,
            ? as schema_version,
            ? as created_at
        from day_db.market_base_bar
        where trade_date is not null
          and price_line = 'execution_price_line'
          and adj_mode = 'none'
        """,
        [request.run_id, DATA_MARKET_META_SCHEMA_VERSION, now],
    )


def _write_meta_source_manifest(
    con: duckdb.DuckDBPyConnection,
    request: MarketMetaBuildRequest,
    paths: _SourcePaths,
    now: datetime,
) -> None:
    sources = (
        ("raw_market.duckdb", "raw_market_bar", "raw_db", paths.raw_db),
        ("market_base_day.duckdb", "market_base_bar", "day_db", paths.day_db),
        ("market_base_week.duckdb", "market_base_bar", "week_db", paths.week_db),
        ("market_base_month.duckdb", "market_base_bar", "month_db", paths.month_db),
    )
    for db_name, table, alias, path in sources:
        if not _attached(con, alias):
            continue
        source_summary = con.execute(
            f"select count(*), min(trade_date), max(trade_date) from {alias}.{table}"
        ).fetchone()
        if source_summary is None:
            continue
        row_count, min_date, max_date = source_summary
        con.execute(
            """
            insert into meta_source_manifest
            values (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                db_name,
                table,
                int(row_count),
                min_date,
                max_date,
                str(path),
                request.run_id,
                DATA_MARKET_META_SCHEMA_VERSION,
                now,
            ],
        )


def _write_meta_versions_and_run(
    con: duckdb.DuckDBPyConnection,
    request: MarketMetaBuildRequest,
    now: datetime,
) -> None:
    con.execute(
        "insert into meta_schema_version values (?, ?)",
        [DATA_MARKET_META_SCHEMA_VERSION, now],
    )
    counts = _row_counts(con)
    con.execute(
        """
        insert into meta_run
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            request.run_id,
            "run_market_meta_build",
            request.mode,
            "passed",
            str(request.data_root),
            str(request.temp_root),
            counts["trade_calendar"],
            counts["instrument_master"],
            counts["instrument_alias"],
            counts["universe_membership"],
            counts["tradability_fact"],
            1,
            DATA_MARKET_META_SCHEMA_VERSION,
            now,
        ],
    )


def _summary_from_audit(
    request: MarketMetaBuildRequest,
    db_path: Path,
    *,
    promoted: bool,
) -> MarketMetaBuildSummary:
    checks, hard_fail_count, row_counts = audit_market_meta_database(db_path)
    return MarketMetaBuildSummary(
        run_id=request.run_id,
        mode=request.mode,
        status="passed" if hard_fail_count == 0 else "failed",
        hard_fail_count=hard_fail_count,
        formal_db_path=str(request.formal_db_path),
        staging_db_path=str(request.staging_db_path),
        row_counts=row_counts,
        checks=checks,
        source_gaps={"industry_classification": "source_gap_empty_allowed"},
        promoted=promoted,
    )


def _attach_existing_sources(con: duckdb.DuckDBPyConnection, paths: _SourcePaths) -> None:
    for alias, path in (
        ("raw_db", paths.raw_db),
        ("day_db", paths.day_db),
        ("week_db", paths.week_db),
        ("month_db", paths.month_db),
    ):
        if path.exists():
            con.execute(f"attach {_sql_literal(path)} as {alias} (read_only)")


def _attached(con: duckdb.DuckDBPyConnection, alias: str) -> bool:
    row = con.execute(
        "select count(*) from duckdb_databases() where database_name = ?",
        [alias],
    ).fetchone()
    return bool(row and row[0])


def _clear_tables(con: duckdb.DuckDBPyConnection) -> None:
    for table in MARKET_META_TABLES:
        con.execute(f"delete from {table}")


def _row_counts(con: duckdb.DuckDBPyConnection) -> dict[str, int]:
    return {
        table: _count_result(con.execute(f"select count(*) from {table}").fetchone())
        for table in MARKET_META_TABLES
    }


def _count_duplicates(
    con: duckdb.DuckDBPyConnection,
    table: str,
    key_columns: tuple[str, ...],
) -> int:
    columns = ", ".join(key_columns)
    groups = ", ".join(str(index) for index in range(1, len(key_columns) + 1))
    return _count_result(
        con.execute(
            f"""
            select count(*)
            from (
                select {columns}
                from {table}
                group by {groups}
                having count(*) > 1
            )
            """
        ).fetchone()
    )


def _source_symbol_from_path(source_path: str) -> str:
    stem = Path(source_path).stem
    if "\\" in source_path:
        stem = source_path.replace("/", "\\").rsplit("\\", 1)[-1].rsplit(".", 1)[0]
    return stem


def _sql_literal(path: Path) -> str:
    return "'" + str(path).replace("'", "''") + "'"


def _count_result(row: tuple[Any, ...] | None) -> int:
    if row is None:
        return 1
    return int(row[0])


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class _SourcePaths:
    def __init__(self, root: Path) -> None:
        self.raw_db = root / "raw_market.duckdb"
        self.day_db = root / "market_base_day.duckdb"
        self.week_db = root / "market_base_week.duckdb"
        self.month_db = root / "market_base_month.duckdb"


def _source_paths(root: Path) -> _SourcePaths:
    return _SourcePaths(root)
