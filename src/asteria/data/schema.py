from __future__ import annotations

from pathlib import Path

import duckdb


def bootstrap_raw_market_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table if not exists raw_market_sync_run (
                run_id varchar,
                runner_name varchar,
                mode varchar,
                asset_type varchar,
                adj_mode varchar,
                source_root varchar,
                status varchar,
                source_file_count bigint,
                raw_rows_written bigint,
                schema_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists raw_market_source_file (
                source_file_key varchar,
                source_vendor varchar,
                source_batch_id varchar,
                asset_type varchar,
                symbol varchar,
                adj_mode varchar,
                source_path varchar,
                source_size_bytes bigint,
                source_mtime timestamp,
                source_content_hash varchar,
                run_id varchar,
                schema_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists raw_market_bar (
                source_file_key varchar,
                source_vendor varchar,
                source_batch_id varchar,
                source_revision varchar,
                symbol varchar,
                asset_type varchar,
                timeframe varchar,
                bar_dt date,
                trade_date date,
                adj_mode varchar,
                open_px double,
                high_px double,
                low_px double,
                close_px double,
                volume double,
                amount double,
                run_id varchar,
                schema_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists raw_schema_version (
                schema_version varchar,
                created_at timestamp
            )
            """
        )


def bootstrap_market_base_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table if not exists market_base_run (
                run_id varchar,
                runner_name varchar,
                mode varchar,
                asset_type varchar,
                adj_mode varchar,
                status varchar,
                source_row_count bigint,
                base_rows_written bigint,
                dirty_scope_count bigint,
                schema_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists market_base_bar (
                symbol varchar,
                asset_type varchar,
                timeframe varchar,
                bar_dt date,
                trade_date date,
                price_line varchar,
                adj_mode varchar,
                open_px double,
                high_px double,
                low_px double,
                close_px double,
                volume double,
                amount double,
                source_vendor varchar,
                source_batch_id varchar,
                source_revision varchar,
                source_path varchar,
                run_id varchar,
                schema_version varchar,
                created_at timestamp
            )
            """
        )

        con.execute(
            """
            create table if not exists market_base_latest (
                symbol varchar,
                asset_type varchar,
                timeframe varchar,
                price_line varchar,
                adj_mode varchar,
                latest_bar_dt date,
                run_id varchar,
                schema_version varchar,
                created_at timestamp
            )
            """
        )

        con.execute(
            """
            create table if not exists market_base_dirty_scope (
                dirty_key varchar,
                symbol varchar,
                asset_type varchar,
                timeframe varchar,
                adj_mode varchar,
                dirty_start_dt date,
                dirty_end_dt date,
                dirty_reason varchar,
                dirty_status varchar,
                source_run_id varchar,
                run_id varchar,
                schema_version varchar,
                created_at timestamp
            )
            """
        )

        con.execute(
            """
            create table if not exists market_base_schema_version (
                schema_version varchar,
                created_at timestamp
            )
            """
        )


def bootstrap_market_base_day_database(path: Path) -> None:
    bootstrap_market_base_database(path)
