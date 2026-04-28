from __future__ import annotations

from pathlib import Path

import duckdb

from asteria.data.legacy_audit import compare_legacy_raw_base_coverage


def _create_legacy_raw(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table stock_daily_bar (
                code varchar,
                trade_date date,
                adjust_method varchar
            )
            """
        )
        con.executemany(
            "insert into stock_daily_bar values (?, ?, ?)",
            [
                ("600000.SH", "2024-01-02", "backward"),
                ("600001.SH", "2024-01-02", "backward"),
            ],
        )


def _create_legacy_base(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table stock_daily_adjusted (
                code varchar,
                trade_date date,
                adjust_method varchar
            )
            """
        )
        con.executemany(
            "insert into stock_daily_adjusted values (?, ?, ?)",
            [
                ("600000.SH", "2024-01-02", "backward"),
                ("600002.SH", "2024-01-02", "backward"),
            ],
        )


def test_compare_legacy_raw_base_coverage_is_read_only(tmp_path: Path) -> None:
    raw_db = tmp_path / "legacy" / "raw_market.duckdb"
    base_db = tmp_path / "legacy" / "market_base.duckdb"
    _create_legacy_raw(raw_db)
    _create_legacy_base(base_db)

    summary = compare_legacy_raw_base_coverage(
        legacy_raw_path=raw_db,
        legacy_base_path=base_db,
        asset_type="stock",
        adj_mode="backward",
    )

    assert summary.raw_symbol_count == 2
    assert summary.base_symbol_count == 2
    assert summary.raw_only_symbols == ("600001.SH",)
    assert summary.base_only_symbols == ("600002.SH",)
    assert summary.raw_row_count == 2
    assert summary.base_row_count == 2
