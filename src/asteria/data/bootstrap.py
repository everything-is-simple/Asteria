from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

from asteria.data.contracts import (
    DATA_SCHEMA_VERSION,
    SOURCE_VENDOR,
    DataBootstrapRequest,
    DataBootstrapSummary,
    ParsedTdxFile,
    RawMarketBar,
)
from asteria.data.schema import bootstrap_market_base_day_database, bootstrap_raw_market_database
from asteria.data.streaming_bootstrap import (
    run_streaming_data_bootstrap,
    should_use_streaming_bootstrap,
)
from asteria.data.tdx_text import discover_tdx_text_files, parse_tdx_text_file


def run_data_bootstrap(request: DataBootstrapRequest) -> DataBootstrapSummary:
    if should_use_streaming_bootstrap(request):
        return run_streaming_data_bootstrap(request)

    checkpoint = _load_checkpoint(request.checkpoint_path)
    if request.mode == "resume" and checkpoint and checkpoint.get("status") == "completed":
        summary = DataBootstrapSummary(**checkpoint["summary"])
        return DataBootstrapSummary(**{**summary.as_dict(), "resume_reused": True})

    if request.mode == "audit-only":
        return _audit_only_summary(request)

    bootstrap_raw_market_database(request.raw_db_path)
    bootstrap_market_base_day_database(request.base_db_path)
    all_parsed_files = _load_source_files(request)
    checkpoint_symbols = _processed_symbols_from_checkpoint(checkpoint)
    parsed_files = _select_files_for_mode(request, all_parsed_files, checkpoint_symbols)
    raw_rows = [bar for parsed in parsed_files for bar in _filter_bars(parsed.bars, request)]
    dirty_scopes = tuple(sorted({(bar.symbol, bar.adj_mode) for bar in raw_rows}))

    _write_raw_market(request, parsed_files, raw_rows)
    _write_market_base(request, parsed_files, raw_rows, dirty_scopes)

    skipped_count = len(all_parsed_files) - len(parsed_files)
    summary = DataBootstrapSummary(
        run_id=request.run_id,
        status="completed",
        raw_db_path=str(request.raw_db_path),
        base_db_path=str(request.base_db_path),
        source_file_count=len(parsed_files),
        raw_rows_written=len(raw_rows),
        base_rows_written=len(raw_rows),
        dirty_scope_count=len(dirty_scopes),
        checkpoint_reused=bool(checkpoint_symbols),
        changed_source_file_count=len(parsed_files),
        skipped_source_file_count=skipped_count,
    )
    _save_checkpoint(request.checkpoint_path, summary)
    return summary


def _load_source_files(request: DataBootstrapRequest) -> tuple[ParsedTdxFile, ...]:
    sources = discover_tdx_text_files(
        request.source_root,
        asset_type=request.asset_type,
        adj_mode=request.adj_mode,
        symbol_limit=request.symbol_limit,
    )
    return tuple(parse_tdx_text_file(source) for source in sources)


def _select_files_for_mode(
    request: DataBootstrapRequest,
    parsed_files: tuple[ParsedTdxFile, ...],
    checkpoint_symbols: set[str],
) -> tuple[ParsedTdxFile, ...]:
    if request.mode == "resume" and checkpoint_symbols:
        return tuple(
            parsed for parsed in parsed_files if parsed.source.symbol not in checkpoint_symbols
        )
    if request.mode != "daily_incremental":
        return parsed_files
    unchanged = _unchanged_source_keys(request, parsed_files)
    return tuple(
        parsed for parsed in parsed_files if parsed.source.source_file_key not in unchanged
    )


def _unchanged_source_keys(
    request: DataBootstrapRequest,
    parsed_files: tuple[ParsedTdxFile, ...],
) -> set[str]:
    if not request.raw_db_path.exists():
        return set()
    unchanged: set[str] = set()
    with duckdb.connect(str(request.raw_db_path), read_only=True) as con:
        for parsed in parsed_files:
            source = parsed.source
            existing = con.execute(
                """
                select source_size_bytes, source_mtime, source_content_hash
                from raw_market_source_file
                where source_path = ?
                  and asset_type = ?
                  and symbol = ?
                  and adj_mode = ?
                order by created_at desc
                limit 1
                """,
                [
                    str(source.source_path),
                    source.asset_type,
                    source.symbol,
                    source.adj_mode,
                ],
            ).fetchone()
            if existing is None:
                continue
            existing_size, _existing_mtime, existing_hash = existing
            if (
                int(existing_size) == source.source_size_bytes
                and str(existing_hash) == source.source_content_hash
            ):
                unchanged.add(source.source_file_key)
    return unchanged


def _processed_symbols_from_checkpoint(checkpoint: dict[str, Any] | None) -> set[str]:
    if not checkpoint or checkpoint.get("status") == "completed":
        return set()
    raw_symbols = checkpoint.get("processed_source_symbols", [])
    return {str(symbol) for symbol in raw_symbols}


def _filter_bars(
    bars: tuple[RawMarketBar, ...],
    request: DataBootstrapRequest,
) -> tuple[RawMarketBar, ...]:
    filtered = []
    for bar in bars:
        if request.start_date and bar.trade_date < request.start_date:
            continue
        if request.end_date and bar.trade_date > request.end_date:
            continue
        filtered.append(bar)
    return tuple(filtered)


def _write_raw_market(
    request: DataBootstrapRequest,
    parsed_files: tuple[ParsedTdxFile, ...],
    raw_rows: list[RawMarketBar],
) -> None:
    now = _utc_now()
    rows_by_source = {parsed.source.source_file_key: parsed for parsed in parsed_files}
    with duckdb.connect(str(request.raw_db_path)) as con:
        con.execute("begin transaction")
        con.execute("delete from raw_market_sync_run where run_id = ?", [request.run_id])
        con.execute("delete from raw_market_source_file where run_id = ?", [request.run_id])
        con.execute("delete from raw_market_bar where run_id = ?", [request.run_id])
        con.execute(
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
                len(parsed_files),
                len(raw_rows),
                DATA_SCHEMA_VERSION,
                now,
            ],
        )
        for parsed in parsed_files:
            source = parsed.source
            con.execute(
                """
                delete from raw_market_source_file
                where source_path = ? and asset_type = ? and symbol = ? and adj_mode = ?
                """,
                [
                    str(source.source_path),
                    source.asset_type,
                    source.symbol,
                    source.adj_mode,
                ],
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
        for bar in raw_rows:
            parsed = rows_by_source[_source_key_for_bar(parsed_files, bar)]
            source = parsed.source
            con.execute(
                """
                insert into raw_market_bar
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    source.source_file_key,
                    SOURCE_VENDOR,
                    request.run_id,
                    source.source_content_hash[:16],
                    bar.symbol,
                    bar.asset_type,
                    bar.timeframe,
                    bar.bar_dt,
                    bar.trade_date,
                    bar.adj_mode,
                    bar.open_px,
                    bar.high_px,
                    bar.low_px,
                    bar.close_px,
                    bar.volume,
                    bar.amount,
                    request.run_id,
                    DATA_SCHEMA_VERSION,
                    now,
                ],
            )
        con.execute("commit")


def _write_market_base(
    request: DataBootstrapRequest,
    parsed_files: tuple[ParsedTdxFile, ...],
    raw_rows: list[RawMarketBar],
    dirty_scopes: tuple[tuple[str, str], ...],
) -> None:
    now = _utc_now()
    source_by_key = {
        (parsed.source.symbol, parsed.source.adj_mode): parsed.source for parsed in parsed_files
    }
    with duckdb.connect(str(request.base_db_path)) as con:
        con.execute("begin transaction")
        con.execute("delete from market_base_run where run_id = ?", [request.run_id])
        con.execute("delete from market_base_bar where run_id = ?", [request.run_id])
        con.execute("delete from market_base_latest where run_id = ?", [request.run_id])
        con.execute("delete from market_base_dirty_scope where run_id = ?", [request.run_id])
        con.execute(
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
                len(raw_rows),
                len(raw_rows),
                len(dirty_scopes),
                DATA_SCHEMA_VERSION,
                now,
            ],
        )
        for bar in raw_rows:
            source = source_by_key[(bar.symbol, bar.adj_mode)]
            price_line = _price_line_for_adj_mode(bar.adj_mode)
            con.execute(
                """
                delete from market_base_bar
                where symbol = ? and timeframe = ? and price_line = ? and adj_mode = ?
                """,
                [bar.symbol, bar.timeframe, price_line, bar.adj_mode],
            )
        for bar in raw_rows:
            source = source_by_key[(bar.symbol, bar.adj_mode)]
            price_line = _price_line_for_adj_mode(bar.adj_mode)
            con.execute(
                """
                delete from market_base_bar
                where symbol = ?
                  and timeframe = ?
                  and bar_dt = ?
                  and price_line = ?
                  and adj_mode = ?
                """,
                [bar.symbol, bar.timeframe, bar.bar_dt, price_line, bar.adj_mode],
            )
            con.execute(
                """
                insert into market_base_bar
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    bar.symbol,
                    bar.asset_type,
                    bar.timeframe,
                    bar.bar_dt,
                    bar.trade_date,
                    price_line,
                    bar.adj_mode,
                    bar.open_px,
                    bar.high_px,
                    bar.low_px,
                    bar.close_px,
                    bar.volume,
                    bar.amount,
                    SOURCE_VENDOR,
                    request.run_id,
                    source.source_content_hash[:16],
                    str(source.source_path),
                    request.run_id,
                    DATA_SCHEMA_VERSION,
                    now,
                ],
            )
        for symbol, adj_mode in dirty_scopes:
            symbol_rows = [
                bar for bar in raw_rows if bar.symbol == symbol and bar.adj_mode == adj_mode
            ]
            source = source_by_key[(symbol, adj_mode)]
            price_line = _price_line_for_adj_mode(source.adj_mode)
            con.execute(
                """
                delete from market_base_latest
                where symbol = ? and timeframe = ? and price_line = ? and adj_mode = ?
                """,
                [symbol, "day", price_line, source.adj_mode],
            )
            con.execute(
                """
                insert into market_base_latest
                values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    symbol,
                    request.asset_type,
                    "day",
                    price_line,
                    source.adj_mode,
                    max(bar.bar_dt for bar in symbol_rows),
                    request.run_id,
                    DATA_SCHEMA_VERSION,
                    now,
                ],
            )
            con.execute(
                """
                delete from market_base_dirty_scope
                where symbol = ? and timeframe = ? and adj_mode = ? and run_id = ?
                """,
                [symbol, "day", source.adj_mode, request.run_id],
            )
            con.execute(
                """
                insert into market_base_dirty_scope
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    f"{symbol}|day|{source.adj_mode}|{request.run_id}",
                    symbol,
                    request.asset_type,
                    "day",
                    source.adj_mode,
                    min(bar.bar_dt for bar in symbol_rows),
                    max(bar.bar_dt for bar in symbol_rows),
                    "source_file_changed",
                    "open",
                    request.run_id,
                    request.run_id,
                    DATA_SCHEMA_VERSION,
                    now,
                ],
            )
        con.execute("commit")


def _source_key_for_bar(parsed_files: tuple[ParsedTdxFile, ...], bar: RawMarketBar) -> str:
    for parsed in parsed_files:
        if parsed.source.symbol == bar.symbol and parsed.source.adj_mode == bar.adj_mode:
            return parsed.source.source_file_key
    raise KeyError(bar.symbol)


def _price_line_for_adj_mode(adj_mode: str) -> str:
    return "execution_price_line" if adj_mode == "none" else "analysis_price_line"


def _audit_only_summary(request: DataBootstrapRequest) -> DataBootstrapSummary:
    return DataBootstrapSummary(
        run_id=request.run_id,
        status="completed",
        raw_db_path=str(request.raw_db_path),
        base_db_path=str(request.base_db_path),
        source_file_count=0,
        raw_rows_written=0,
        base_rows_written=0,
        dirty_scope_count=0,
    )


def _load_checkpoint(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _save_checkpoint(path: Path, summary: DataBootstrapSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": summary.status,
        "summary": summary.as_dict(),
        "created_at": _utc_now().isoformat(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
