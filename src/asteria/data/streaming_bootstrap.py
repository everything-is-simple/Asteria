from __future__ import annotations

import json
from datetime import datetime, timezone

import duckdb

from asteria.data.contracts import (
    DATA_SCHEMA_VERSION,
    SOURCE_VENDOR,
    DataBootstrapRequest,
    DataBootstrapSummary,
    ParsedTdxFile,
    RawMarketBar,
    TdxSourceFile,
)
from asteria.data.native_csv_bootstrap import run_native_csv_bootstrap
from asteria.data.schema import bootstrap_market_base_day_database, bootstrap_raw_market_database
from asteria.data.tdx_text import discover_tdx_text_files, parse_tdx_text_file


def should_use_streaming_bootstrap(request: DataBootstrapRequest) -> bool:
    return request.mode == "full" and request.symbol_limit is None


def run_streaming_data_bootstrap(request: DataBootstrapRequest) -> DataBootstrapSummary:
    bootstrap_raw_market_database(request.raw_db_path)
    bootstrap_market_base_day_database(request.base_db_path)

    sources = discover_tdx_text_files(
        request.source_root,
        asset_type=request.asset_type,
        adj_mode=request.adj_mode,
        symbol_limit=request.symbol_limit,
    )
    now = _utc_now()
    if len(sources) > 100:
        return run_native_csv_bootstrap(request, sources=sources, now=now)

    raw_rows_written = 0
    base_rows_written = 0
    dirty_scopes: set[tuple[str, str]] = set()

    with (
        duckdb.connect(str(request.raw_db_path)) as raw_con,
        duckdb.connect(str(request.base_db_path)) as base_con,
    ):
        _reset_run_rows(raw_con, base_con, request)
        for source in sources:
            parsed = parse_tdx_text_file(source)
            rows = _filter_bars(parsed.bars, request)
            _write_raw_source(raw_con, request, parsed, rows, now)
            _write_base_source(base_con, request, source, rows, now)
            raw_rows_written += len(rows)
            base_rows_written += len(rows)
            if rows:
                dirty_scopes.add((source.symbol, source.adj_mode))
        _write_run_rows(
            raw_con,
            base_con,
            request,
            source_file_count=len(sources),
            raw_rows_written=raw_rows_written,
            base_rows_written=base_rows_written,
            dirty_scope_count=len(dirty_scopes),
            now=now,
        )

    summary = DataBootstrapSummary(
        run_id=request.run_id,
        status="completed",
        raw_db_path=str(request.raw_db_path),
        base_db_path=str(request.base_db_path),
        source_file_count=len(sources),
        raw_rows_written=raw_rows_written,
        base_rows_written=base_rows_written,
        dirty_scope_count=len(dirty_scopes),
        changed_source_file_count=len(sources),
    )
    _save_checkpoint(request, summary)
    return summary


def _reset_run_rows(
    raw_con: duckdb.DuckDBPyConnection,
    base_con: duckdb.DuckDBPyConnection,
    request: DataBootstrapRequest,
) -> None:
    raw_con.execute("delete from raw_market_sync_run where run_id = ?", [request.run_id])
    raw_con.execute("delete from raw_market_source_file where run_id = ?", [request.run_id])
    raw_con.execute("delete from raw_market_bar where run_id = ?", [request.run_id])
    base_con.execute("delete from market_base_run where run_id = ?", [request.run_id])
    base_con.execute("delete from market_base_bar where run_id = ?", [request.run_id])
    base_con.execute("delete from market_base_latest where run_id = ?", [request.run_id])
    base_con.execute("delete from market_base_dirty_scope where run_id = ?", [request.run_id])


def _write_raw_source(
    con: duckdb.DuckDBPyConnection,
    request: DataBootstrapRequest,
    parsed: ParsedTdxFile,
    rows: tuple[RawMarketBar, ...],
    now: datetime,
) -> None:
    source = parsed.source
    con.execute("begin transaction")
    con.execute(
        """
        delete from raw_market_source_file
        where source_path = ? and asset_type = ? and symbol = ? and adj_mode = ?
        """,
        [str(source.source_path), source.asset_type, source.symbol, source.adj_mode],
    )
    con.execute(
        """
        delete from raw_market_bar
        where symbol = ? and asset_type = ? and timeframe = ? and adj_mode = ?
        """,
        [source.symbol, source.asset_type, "day", source.adj_mode],
    )
    con.execute(
        """
        insert into raw_market_source_file
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            source.source_file_key,
            SOURCE_VENDOR,
            request.run_id,
            source.asset_type,
            source.symbol,
            source.adj_mode,
            str(source.source_path),
            source.source_size_bytes,
            source.source_mtime,
            source.source_content_hash,
            request.run_id,
            DATA_SCHEMA_VERSION,
            now,
        ],
    )
    if rows:
        con.executemany(
            """
            insert into raw_market_bar
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [_raw_tuple(source, row, request.run_id, now) for row in rows],
        )
    con.execute("commit")


def _write_base_source(
    con: duckdb.DuckDBPyConnection,
    request: DataBootstrapRequest,
    source: TdxSourceFile,
    rows: tuple[RawMarketBar, ...],
    now: datetime,
) -> None:
    price_line = _price_line_for_adj_mode(source.adj_mode)
    con.execute("begin transaction")
    con.execute(
        """
        delete from market_base_bar
        where symbol = ? and timeframe = ? and price_line = ? and adj_mode = ?
        """,
        [source.symbol, "day", price_line, source.adj_mode],
    )
    con.execute(
        """
        delete from market_base_latest
        where symbol = ? and timeframe = ? and price_line = ? and adj_mode = ?
        """,
        [source.symbol, "day", price_line, source.adj_mode],
    )
    con.execute(
        """
        delete from market_base_dirty_scope
        where symbol = ? and timeframe = ? and adj_mode = ? and run_id = ?
        """,
        [source.symbol, "day", source.adj_mode, request.run_id],
    )
    if rows:
        con.executemany(
            """
            insert into market_base_bar
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [_base_tuple(source, row, price_line, request.run_id, now) for row in rows],
        )
        con.execute(
            """
            insert into market_base_latest
            values (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                source.symbol,
                request.asset_type,
                "day",
                price_line,
                source.adj_mode,
                max(row.bar_dt for row in rows),
                request.run_id,
                DATA_SCHEMA_VERSION,
                now,
            ],
        )
        con.execute(
            """
            insert into market_base_dirty_scope
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                f"{source.symbol}|day|{source.adj_mode}|{request.run_id}",
                source.symbol,
                request.asset_type,
                "day",
                source.adj_mode,
                min(row.bar_dt for row in rows),
                max(row.bar_dt for row in rows),
                "source_file_changed",
                "open",
                request.run_id,
                request.run_id,
                DATA_SCHEMA_VERSION,
                now,
            ],
        )
    con.execute("commit")


def _write_run_rows(
    raw_con: duckdb.DuckDBPyConnection,
    base_con: duckdb.DuckDBPyConnection,
    request: DataBootstrapRequest,
    *,
    source_file_count: int,
    raw_rows_written: int,
    base_rows_written: int,
    dirty_scope_count: int,
    now: datetime,
) -> None:
    raw_con.execute(
        """
        insert into raw_market_sync_run
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            request.run_id,
            "data_bootstrap",
            request.mode,
            request.asset_type,
            request.adj_mode,
            str(request.source_root),
            "completed",
            source_file_count,
            raw_rows_written,
            DATA_SCHEMA_VERSION,
            now,
        ],
    )
    base_con.execute(
        """
        insert into market_base_run
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            request.run_id,
            "data_bootstrap",
            request.mode,
            request.asset_type,
            request.adj_mode,
            "completed",
            raw_rows_written,
            base_rows_written,
            dirty_scope_count,
            DATA_SCHEMA_VERSION,
            now,
        ],
    )


def _raw_tuple(
    source: TdxSourceFile,
    row: RawMarketBar,
    run_id: str,
    now: datetime,
) -> tuple[object, ...]:
    return (
        source.source_file_key,
        SOURCE_VENDOR,
        run_id,
        source.source_content_hash[:16],
        row.symbol,
        row.asset_type,
        row.timeframe,
        row.bar_dt,
        row.trade_date,
        row.adj_mode,
        row.open_px,
        row.high_px,
        row.low_px,
        row.close_px,
        row.volume,
        row.amount,
        run_id,
        DATA_SCHEMA_VERSION,
        now,
    )


def _base_tuple(
    source: TdxSourceFile,
    row: RawMarketBar,
    price_line: str,
    run_id: str,
    now: datetime,
) -> tuple[object, ...]:
    return (
        row.symbol,
        row.asset_type,
        row.timeframe,
        row.bar_dt,
        row.trade_date,
        price_line,
        row.adj_mode,
        row.open_px,
        row.high_px,
        row.low_px,
        row.close_px,
        row.volume,
        row.amount,
        SOURCE_VENDOR,
        run_id,
        source.source_content_hash[:16],
        str(source.source_path),
        run_id,
        DATA_SCHEMA_VERSION,
        now,
    )


def _filter_bars(
    bars: tuple[RawMarketBar, ...],
    request: DataBootstrapRequest,
) -> tuple[RawMarketBar, ...]:
    return tuple(
        row
        for row in bars
        if (request.start_date is None or row.trade_date >= request.start_date)
        and (request.end_date is None or row.trade_date <= request.end_date)
    )


def _price_line_for_adj_mode(adj_mode: str) -> str:
    return "execution_price_line" if adj_mode == "none" else "analysis_price_line"


def _save_checkpoint(request: DataBootstrapRequest, summary: DataBootstrapSummary) -> None:
    request.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": summary.status,
        "summary": summary.as_dict(),
        "created_at": _utc_now().isoformat(),
    }
    request.checkpoint_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
