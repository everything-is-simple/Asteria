from __future__ import annotations

from pathlib import Path

import duckdb

from asteria.data.contracts import LegacyCoverageSummary

_RAW_TABLE_BY_ASSET = {
    "stock": "stock_daily_bar",
    "index": "index_daily_bar",
    "block": "block_daily_bar",
}
_BASE_TABLE_BY_ASSET = {
    "stock": "stock_daily_adjusted",
    "index": "index_daily_adjusted",
    "block": "block_daily_adjusted",
}


def compare_legacy_raw_base_coverage(
    *,
    legacy_raw_path: Path,
    legacy_base_path: Path,
    asset_type: str,
    adj_mode: str,
) -> LegacyCoverageSummary:
    raw_table = _RAW_TABLE_BY_ASSET[asset_type]
    base_table = _BASE_TABLE_BY_ASSET[asset_type]
    raw_symbols, raw_row_count = _symbol_coverage(legacy_raw_path, raw_table, adj_mode)
    base_symbols, base_row_count = _symbol_coverage(legacy_base_path, base_table, adj_mode)

    raw_set = set(raw_symbols)
    base_set = set(base_symbols)
    return LegacyCoverageSummary(
        legacy_raw_path=str(legacy_raw_path),
        legacy_base_path=str(legacy_base_path),
        asset_type=asset_type,
        adj_mode=adj_mode,
        raw_symbol_count=len(raw_symbols),
        base_symbol_count=len(base_symbols),
        raw_row_count=raw_row_count,
        base_row_count=base_row_count,
        raw_only_symbols=tuple(sorted(raw_set - base_set)),
        base_only_symbols=tuple(sorted(base_set - raw_set)),
    )


def _symbol_coverage(path: Path, table: str, adj_mode: str) -> tuple[tuple[str, ...], int]:
    with duckdb.connect(str(path), read_only=True) as con:
        symbols = con.execute(
            f"select distinct code from {table} where adjust_method = ? order by code",
            [adj_mode],
        ).fetchall()
        row = con.execute(
            f"select count(*) from {table} where adjust_method = ?",
            [adj_mode],
        ).fetchone()
    return tuple(row[0] for row in symbols), int(row[0] if row else 0)
