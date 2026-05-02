from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb

from asteria.data.contracts import LegacyImportRequest
from asteria.data.legacy_import import run_legacy_data_import


def _create_raw_db(path: Path, timeframe: str) -> None:
    table = {
        "day": "stock_daily_bar",
        "week": "stock_weekly_bar",
        "month": "stock_monthly_bar",
    }[timeframe]
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            f"""
            create table {table} (
                bar_nk varchar,
                source_file_nk varchar,
                asset_type varchar,
                code varchar,
                name varchar,
                trade_date date,
                adjust_method varchar,
                open double,
                high double,
                low double,
                close double,
                volume double,
                amount double,
                source_path varchar,
                source_mtime_utc timestamp,
                first_seen_run_id varchar,
                last_seen_run_id varchar,
                created_at timestamp,
                updated_at timestamp,
                timeframe varchar
            )
            """
        )
        rows = [
            (
                f"{timeframe}-raw-1",
                f"{timeframe}-file-1",
                "stock",
                "600000.SH",
                "浦发银行",
                "2024-01-02",
                "backward",
                10.0,
                11.0,
                9.5,
                10.5,
                1000.0,
                10500.0,
                f"H:/legacy/{timeframe}/600000.csv",
                "2024-01-03 00:00:00",
                "legacy-first",
                "legacy-last",
                "2024-01-03 00:00:00",
                "2024-01-03 00:00:00",
                timeframe,
            )
        ]
        if timeframe == "day":
            rows.append(
                (
                    "day-raw-2",
                    "day-file-1",
                    "stock",
                    "600000.SH",
                    "浦发银行",
                    "2024-01-03",
                    "backward",
                    10.5,
                    11.5,
                    10.1,
                    11.0,
                    1100.0,
                    12100.0,
                    "H:/legacy/day/600000.csv",
                    "2024-01-04 00:00:00",
                    "legacy-first",
                    "legacy-last",
                    "2024-01-04 00:00:00",
                    "2024-01-04 00:00:00",
                    "day",
                )
            )
        con.executemany(
            f"""
            insert into {table}
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )


def _create_base_db(path: Path, timeframe: str) -> None:
    table = {
        "day": "stock_daily_adjusted",
        "week": "stock_weekly_adjusted",
        "month": "stock_monthly_adjusted",
    }[timeframe]
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            f"""
            create table {table} (
                daily_bar_nk varchar,
                code varchar,
                name varchar,
                timeframe varchar,
                trade_date date,
                adjust_method varchar,
                open double,
                high double,
                low double,
                close double,
                volume double,
                amount double,
                source_bar_nk varchar,
                first_seen_run_id varchar,
                last_materialized_run_id varchar,
                created_at timestamp,
                updated_at timestamp
            )
            """
        )
        rows = [
            (
                f"{timeframe}-base-1",
                "600000.SH",
                "浦发银行",
                timeframe,
                "2024-01-02",
                "backward",
                10.0,
                11.0,
                9.5,
                10.5,
                1000.0,
                10500.0,
                f"{timeframe}-raw-1",
                "legacy-first",
                "legacy-materialized",
                "2024-01-03 00:00:00",
                "2024-01-03 00:00:00",
            )
        ]
        if timeframe == "day":
            rows.append(
                (
                    "day-base-2",
                    "600000.SH",
                    "浦发银行",
                    "day",
                    "2024-01-03",
                    "backward",
                    10.5,
                    11.5,
                    10.1,
                    11.0,
                    1100.0,
                    12100.0,
                    "day-raw-2",
                    "legacy-first",
                    "legacy-materialized",
                    "2024-01-04 00:00:00",
                    "2024-01-04 00:00:00",
                )
            )
        con.executemany(
            f"""
            insert into {table}
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )


def test_legacy_import_writes_working_raw_and_base_dbs(tmp_path: Path) -> None:
    raw_root = tmp_path / "legacy" / "raw"
    base_root = tmp_path / "legacy" / "base"
    _create_raw_db(raw_root / "raw_market.duckdb", "day")
    _create_raw_db(raw_root / "raw_market_week.duckdb", "week")
    _create_raw_db(raw_root / "raw_market_month.duckdb", "month")
    _create_base_db(base_root / "market_base.duckdb", "day")
    _create_base_db(base_root / "market_base_week.duckdb", "week")
    _create_base_db(base_root / "market_base_month.duckdb", "month")

    target_root = tmp_path / "asteria-temp" / "data" / "legacy-import-run"
    summary = run_legacy_data_import(
        LegacyImportRequest(
            raw_root=raw_root,
            base_root=base_root,
            target_root=target_root,
            run_id="legacy-import-run",
        )
    )

    assert summary.status == "completed"
    assert summary.raw_rows_written == 4
    assert summary.base_rows_written == 4
    assert summary.base_rows_by_timeframe == {"day": 2, "week": 1, "month": 1}

    with duckdb.connect(str(target_root / "raw_market.duckdb"), read_only=True) as con:
        rows = con.execute(
            """
            select symbol, timeframe, bar_dt, adj_mode, close_px, source_revision
            from raw_market_bar
            order by timeframe, bar_dt
            """
        ).fetchall()
        assert ("600000.SH", "day", date(2024, 1, 2), "backward", 10.5, "day-raw-1") in rows
        assert con.execute("select count(*) from raw_market_source_file").fetchone()[0] == 3

    for timeframe, expected_count in {"day": 2, "week": 1, "month": 1}.items():
        db_path = target_root / f"market_base_{timeframe}.duckdb"
        with duckdb.connect(str(db_path), read_only=True) as con:
            row_count = con.execute("select count(*) from market_base_bar").fetchone()[0]
            assert row_count == expected_count
            duplicate_groups = con.execute(
                """
                select count(*)
                from (
                    select symbol, timeframe, bar_dt, price_line, adj_mode, count(*) as n
                    from market_base_bar
                    group by 1, 2, 3, 4, 5
                    having n > 1
                )
                """
            ).fetchone()[0]
            assert duplicate_groups == 0
            latest = con.execute(
                """
                select symbol, timeframe, price_line, adj_mode
                from market_base_latest
                """
            ).fetchone()
            assert latest == ("600000.SH", timeframe, "analysis_price_line", "backward")
