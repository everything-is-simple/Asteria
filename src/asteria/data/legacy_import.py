from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import duckdb

from asteria.data.contracts import (
    DATA_SCHEMA_VERSION,
    LEGACY_SOURCE_VENDOR,
    LegacyImportRequest,
    LegacyImportSummary,
)
from asteria.data.schema import bootstrap_market_base_database, bootstrap_raw_market_database

_RAW_DB_BY_TIMEFRAME = {
    "day": "raw_market.duckdb",
    "week": "raw_market_week.duckdb",
    "month": "raw_market_month.duckdb",
}
_BASE_DB_BY_TIMEFRAME = {
    "day": "market_base.duckdb",
    "week": "market_base_week.duckdb",
    "month": "market_base_month.duckdb",
}
_RAW_TABLE_BY_TIMEFRAME = {
    "day": "stock_daily_bar",
    "week": "stock_weekly_bar",
    "month": "stock_monthly_bar",
}
_BASE_TABLE_BY_TIMEFRAME = {
    "day": "stock_daily_adjusted",
    "week": "stock_weekly_adjusted",
    "month": "stock_monthly_adjusted",
}
_PRICE_LINE = "analysis_price_line"


def run_legacy_data_import(request: LegacyImportRequest) -> LegacyImportSummary:
    request.target_root.mkdir(parents=True, exist_ok=True)
    bootstrap_raw_market_database(request.raw_db_path)
    for timeframe in request.timeframes:
        bootstrap_market_base_database(request.base_db_path(timeframe))

    raw_rows_written = 0
    source_file_count = 0
    base_rows_by_timeframe: dict[str, int] = {}
    now = _utc_now()

    with duckdb.connect(str(request.raw_db_path)) as con:
        con.execute("begin transaction")
        con.execute("delete from raw_market_sync_run where run_id = ?", [request.run_id])
        con.execute("delete from raw_market_source_file where run_id = ?", [request.run_id])
        con.execute("delete from raw_market_bar where run_id = ?", [request.run_id])
        for timeframe in request.timeframes:
            raw_path = request.raw_root / _RAW_DB_BY_TIMEFRAME[timeframe]
            table = _RAW_TABLE_BY_TIMEFRAME[timeframe]
            alias = f"src_{timeframe}"
            _attach_readonly(con, raw_path, alias)
            raw_rows_written += _write_raw_timeframe(con, request, alias, table, timeframe, now)
            source_file_count += _count_source_files(con, alias, table, request.adj_mode)
            con.execute(f"detach {alias}")
        con.execute(
            """
            insert into raw_market_sync_run
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                request.run_id,
                "legacy_data_import",
                "full",
                request.asset_type,
                request.adj_mode,
                str(request.raw_root),
                "completed",
                source_file_count,
                raw_rows_written,
                DATA_SCHEMA_VERSION,
                now,
            ],
        )
        con.execute("commit")

    for timeframe in request.timeframes:
        base_rows_by_timeframe[timeframe] = _write_base_timeframe(request, timeframe, now)

    base_rows_written = sum(base_rows_by_timeframe.values())
    return LegacyImportSummary(
        run_id=request.run_id,
        status="completed",
        target_root=str(request.target_root),
        raw_db_path=str(request.raw_db_path),
        base_db_paths={
            timeframe: str(request.base_db_path(timeframe)) for timeframe in request.timeframes
        },
        source_file_count=source_file_count,
        raw_rows_written=raw_rows_written,
        base_rows_written=base_rows_written,
        base_rows_by_timeframe=base_rows_by_timeframe,
    )


def _write_raw_timeframe(
    con: duckdb.DuckDBPyConnection,
    request: LegacyImportRequest,
    alias: str,
    table: str,
    timeframe: str,
    now: datetime,
) -> int:
    source_rows = con.execute(
        f"""
        select
            coalesce(cast(source_file_nk as varchar), 'legacy|' || code || '|{timeframe}')
                as source_file_key,
            code,
            adjust_method,
            source_path,
            max(source_mtime_utc) as source_mtime_utc
        from {alias}.{table}
        where asset_type = ? and adjust_method = ?
        group by 1, 2, 3, 4
        """,
        [request.asset_type, request.adj_mode],
    ).fetchall()
    con.executemany(
        """
        insert into raw_market_source_file
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row[0],
                LEGACY_SOURCE_VENDOR,
                request.run_id,
                request.asset_type,
                row[1],
                row[2],
                row[3],
                None,
                row[4],
                row[0],
                request.run_id,
                DATA_SCHEMA_VERSION,
                now,
            )
            for row in source_rows
        ],
    )
    con.execute(
        f"""
        insert into raw_market_bar
        select
            coalesce(cast(source_file_nk as varchar), 'legacy|' || code || '|{timeframe}'),
            ?,
            ?,
            cast(bar_nk as varchar),
            code,
            asset_type,
            ?,
            cast(trade_date as date),
            cast(trade_date as date),
            adjust_method,
            open,
            high,
            low,
            close,
            volume,
            amount,
            ?,
            ?,
            ?
        from {alias}.{table}
        where asset_type = ? and adjust_method = ?
        """,
        [
            LEGACY_SOURCE_VENDOR,
            request.run_id,
            timeframe,
            request.run_id,
            DATA_SCHEMA_VERSION,
            now,
            request.asset_type,
            request.adj_mode,
        ],
    )
    return _fetch_count(
        con,
        f"select count(*) from {alias}.{table} where asset_type = ? and adjust_method = ?",
        [request.asset_type, request.adj_mode],
    )


def _write_base_timeframe(
    request: LegacyImportRequest,
    timeframe: str,
    now: datetime,
) -> int:
    db_path = request.base_db_path(timeframe)
    source_path = request.base_root / _BASE_DB_BY_TIMEFRAME[timeframe]
    table = _BASE_TABLE_BY_TIMEFRAME[timeframe]
    with duckdb.connect(str(db_path)) as con:
        con.execute("begin transaction")
        alias = "src_base"
        _attach_readonly(con, source_path, alias)
        con.execute("delete from market_base_run where run_id = ?", [request.run_id])
        con.execute("delete from market_base_bar where run_id = ?", [request.run_id])
        con.execute("delete from market_base_latest where run_id = ?", [request.run_id])
        con.execute("delete from market_base_dirty_scope where run_id = ?", [request.run_id])
        row_count = _fetch_count(
            con,
            f"select count(*) from {alias}.{table} where adjust_method = ?",
            [request.adj_mode],
        )
        con.execute(
            """
            insert into market_base_run
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                request.run_id,
                "legacy_data_import",
                "full",
                request.asset_type,
                request.adj_mode,
                "completed",
                row_count,
                row_count,
                _dirty_scope_count(con, alias, table, request.adj_mode),
                DATA_SCHEMA_VERSION,
                now,
            ],
        )
        con.execute(
            f"""
            insert into market_base_bar
            select
                code,
                ?,
                ?,
                cast(trade_date as date),
                cast(trade_date as date),
                ?,
                adjust_method,
                open,
                high,
                low,
                close,
                volume,
                amount,
                ?,
                ?,
                coalesce(cast(source_bar_nk as varchar), cast(daily_bar_nk as varchar)),
                null,
                ?,
                ?,
                ?
            from {alias}.{table}
            where adjust_method = ?
            """,
            [
                request.asset_type,
                timeframe,
                _PRICE_LINE,
                LEGACY_SOURCE_VENDOR,
                request.run_id,
                request.run_id,
                DATA_SCHEMA_VERSION,
                now,
                request.adj_mode,
            ],
        )
        con.execute(
            f"""
            insert into market_base_latest
            select code, ?, ?, ?, adjust_method, max(cast(trade_date as date)), ?, ?, ?
            from {alias}.{table}
            where adjust_method = ?
            group by code, adjust_method
            """,
            [
                request.asset_type,
                timeframe,
                _PRICE_LINE,
                request.run_id,
                DATA_SCHEMA_VERSION,
                now,
                request.adj_mode,
            ],
        )
        con.execute(
            f"""
            insert into market_base_dirty_scope
            select
                code || '|{timeframe}|' || adjust_method || '|{request.run_id}',
                code,
                ?,
                ?,
                adjust_method,
                min(cast(trade_date as date)),
                max(cast(trade_date as date)),
                'legacy_import',
                'open',
                ?,
                ?,
                ?,
                ?
            from {alias}.{table}
            where adjust_method = ?
            group by code, adjust_method
            """,
            [
                request.asset_type,
                timeframe,
                request.run_id,
                request.run_id,
                DATA_SCHEMA_VERSION,
                now,
                request.adj_mode,
            ],
        )
        con.execute(f"detach {alias}")
        con.execute("commit")
        return row_count


def _count_source_files(
    con: duckdb.DuckDBPyConnection,
    alias: str,
    table: str,
    adj_mode: str,
) -> int:
    return _fetch_count(
        con,
        f"select count(distinct source_file_nk) from {alias}.{table} where adjust_method = ?",
        [adj_mode],
    )


def _dirty_scope_count(
    con: duckdb.DuckDBPyConnection,
    alias: str,
    table: str,
    adj_mode: str,
) -> int:
    return _fetch_count(
        con,
        f"""
            select count(distinct code || '|' || adjust_method)
            from {alias}.{table}
            where adjust_method = ?
            """,
        [adj_mode],
    )


def _fetch_count(
    con: duckdb.DuckDBPyConnection,
    query: str,
    params: list[object],
) -> int:
    row = con.execute(query, params).fetchone()
    return 0 if row is None else int(row[0])


def _attach_readonly(con: duckdb.DuckDBPyConnection, path: Path, alias: str) -> None:
    escaped = str(path).replace("'", "''")
    con.execute(f"attach database '{escaped}' as {alias} (read_only)")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
