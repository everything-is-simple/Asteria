from __future__ import annotations

from pathlib import Path

import duckdb

from asteria.data.contracts import (
    LegacyCoverageSummary,
    LegacySourceAuditReport,
    LegacyTimeframeAudit,
)

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
_DB_BY_TIMEFRAME = {
    "day": ("raw_market.duckdb", "market_base.duckdb"),
    "week": ("raw_market_week.duckdb", "market_base_week.duckdb"),
    "month": ("raw_market_month.duckdb", "market_base_month.duckdb"),
}
_RAW_TABLE_BY_TIMEFRAME_ASSET = {
    ("day", "stock"): "stock_daily_bar",
    ("day", "index"): "index_daily_bar",
    ("day", "block"): "block_daily_bar",
    ("week", "stock"): "stock_weekly_bar",
    ("week", "index"): "index_weekly_bar",
    ("week", "block"): "block_weekly_bar",
    ("month", "stock"): "stock_monthly_bar",
    ("month", "index"): "index_monthly_bar",
    ("month", "block"): "block_monthly_bar",
}
_BASE_TABLE_BY_TIMEFRAME_ASSET = {
    ("day", "stock"): "stock_daily_adjusted",
    ("day", "index"): "index_daily_adjusted",
    ("day", "block"): "block_daily_adjusted",
    ("week", "stock"): "stock_weekly_adjusted",
    ("week", "index"): "index_weekly_adjusted",
    ("week", "block"): "block_weekly_adjusted",
    ("month", "stock"): "stock_monthly_adjusted",
    ("month", "index"): "index_monthly_adjusted",
    ("month", "block"): "block_monthly_adjusted",
}


def audit_legacy_raw_base_sources(
    *,
    raw_root: Path,
    base_root: Path,
    adj_mode: str,
    run_id: str = "data-legacy-source-audit",
) -> LegacySourceAuditReport:
    timeframes: dict[str, LegacyTimeframeAudit] = {}
    for timeframe, (raw_name, base_name) in _DB_BY_TIMEFRAME.items():
        raw_path = raw_root / raw_name
        base_path = base_root / base_name
        if not raw_path.exists() or not base_path.exists():
            continue

        stock = compare_legacy_raw_base_coverage(
            legacy_raw_path=raw_path,
            legacy_base_path=base_path,
            asset_type="stock",
            adj_mode=adj_mode,
            timeframe=timeframe,
        )
        sidecar_assets = {
            asset_type: compare_legacy_raw_base_coverage(
                legacy_raw_path=raw_path,
                legacy_base_path=base_path,
                asset_type=asset_type,
                adj_mode=adj_mode,
                timeframe=timeframe,
            )
            for asset_type in ("index", "block")
            if _table_exists(raw_path, _RAW_TABLE_BY_TIMEFRAME_ASSET[(timeframe, asset_type)])
            and _table_exists(base_path, _BASE_TABLE_BY_TIMEFRAME_ASSET[(timeframe, asset_type)])
        }
        timeframes[timeframe] = LegacyTimeframeAudit(
            timeframe=timeframe,
            raw_path=str(raw_path),
            base_path=str(base_path),
            stock=stock,
            sidecar_assets=sidecar_assets,
        )
    return LegacySourceAuditReport(
        run_id=run_id,
        mainline_asset_type="stock",
        adj_mode=adj_mode,
        timeframes=timeframes,
    )


def compare_legacy_raw_base_coverage(
    *,
    legacy_raw_path: Path,
    legacy_base_path: Path,
    asset_type: str,
    adj_mode: str,
    timeframe: str = "day",
) -> LegacyCoverageSummary:
    raw_table = _RAW_TABLE_BY_TIMEFRAME_ASSET.get(
        (timeframe, asset_type), _RAW_TABLE_BY_ASSET[asset_type]
    )
    base_table = _BASE_TABLE_BY_TIMEFRAME_ASSET.get(
        (timeframe, asset_type), _BASE_TABLE_BY_ASSET[asset_type]
    )
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


def _table_exists(path: Path, table: str) -> bool:
    with duckdb.connect(str(path), read_only=True) as con:
        row = con.execute(
            """
            select count(*)
            from information_schema.tables
            where table_schema = 'main' and table_name = ?
            """,
            [table],
        ).fetchone()
    return bool(row and row[0])
