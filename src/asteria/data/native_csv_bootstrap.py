from __future__ import annotations

from datetime import datetime

import duckdb

from asteria.data.contracts import (
    DATA_SCHEMA_VERSION,
    SOURCE_VENDOR,
    DataBootstrapRequest,
    DataBootstrapSummary,
    TdxSourceFile,
)
from asteria.data.native_csv_support import (
    chunked,
    create_temp_source_manifest,
    normalized_path,
    price_line_for_adj_mode,
    save_checkpoint,
    scalar,
    source_has_data_rows,
    sql_file_list,
)
from asteria.data.schema import bootstrap_market_base_day_database, bootstrap_raw_market_database


def run_native_csv_bootstrap(
    request: DataBootstrapRequest,
    *,
    sources: tuple[TdxSourceFile, ...],
    now: datetime,
) -> DataBootstrapSummary:
    data_sources = tuple(source for source in sources if source_has_data_rows(source))
    bootstrap_raw_market_database(request.raw_db_path)
    bootstrap_market_base_day_database(request.base_db_path)
    with duckdb.connect(str(request.raw_db_path)) as con:
        con.execute(f"attach '{request.base_db_path}' as base_db")
        create_temp_source_manifest(con)
        _load_source_manifest(con, request, sources, now)
        _cleanup_existing_scope(con, request)
        _create_temp_parsed_stage(con, request, data_sources)
        source_file_count = len(sources)
        raw_rows_written = scalar(con, "select count(*) from temp_parsed_stage")
        dirty_scope_count = scalar(
            con,
            """
            select count(*)
            from (
                select distinct symbol, adj_mode
                from temp_parsed_stage
            )
            """,
        )
        _insert_raw_tables(
            con,
            request,
            source_file_count=source_file_count,
            raw_rows_written=raw_rows_written,
            now=now,
        )
        _insert_base_tables(
            con,
            request,
            base_rows_written=raw_rows_written,
            dirty_scope_count=dirty_scope_count,
            now=now,
        )
        con.execute("detach base_db")

    summary = DataBootstrapSummary(
        run_id=request.run_id,
        status="completed",
        raw_db_path=str(request.raw_db_path),
        base_db_path=str(request.base_db_path),
        source_file_count=source_file_count,
        raw_rows_written=raw_rows_written,
        base_rows_written=raw_rows_written,
        dirty_scope_count=dirty_scope_count,
        changed_source_file_count=source_file_count,
    )
    save_checkpoint(request, summary, now=now)
    return summary


def _load_source_manifest(
    con: duckdb.DuckDBPyConnection,
    request: DataBootstrapRequest,
    sources: tuple[TdxSourceFile, ...],
    now: datetime,
) -> None:
    con.executemany(
        """
        insert into temp_source_manifest
        values (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                source.source_file_key,
                source.asset_type,
                source.symbol,
                source.adj_mode,
                str(source.source_path),
                normalized_path(source),
                source.source_size_bytes,
                source.source_mtime,
                source.source_content_hash,
            )
            for source in sources
        ],
    )
    con.execute("delete from raw_market_sync_run where run_id = ?", [request.run_id])
    con.execute("delete from raw_market_source_file where run_id = ?", [request.run_id])
    con.execute("delete from raw_market_bar where run_id = ?", [request.run_id])
    con.execute("delete from base_db.market_base_run where run_id = ?", [request.run_id])
    con.execute("delete from base_db.market_base_bar where run_id = ?", [request.run_id])
    con.execute("delete from base_db.market_base_latest where run_id = ?", [request.run_id])
    con.execute(
        "delete from base_db.market_base_dirty_scope where run_id = ?",
        [request.run_id],
    )


def _cleanup_existing_scope(
    con: duckdb.DuckDBPyConnection,
    request: DataBootstrapRequest,
) -> None:
    con.execute(
        """
        delete from raw_market_source_file
        where adj_mode = ?
          and symbol in (select symbol from temp_source_manifest)
        """,
        [request.adj_mode],
    )
    con.execute(
        """
        delete from raw_market_bar
        where adj_mode = ?
          and symbol in (select symbol from temp_source_manifest)
        """,
        [request.adj_mode],
    )
    con.execute(
        """
        delete from base_db.market_base_bar
        where adj_mode = ?
          and symbol in (select symbol from temp_source_manifest)
        """,
        [request.adj_mode],
    )
    con.execute(
        """
        delete from base_db.market_base_latest
        where adj_mode = ?
          and symbol in (select symbol from temp_source_manifest)
        """,
        [request.adj_mode],
    )
    con.execute(
        """
        delete from base_db.market_base_dirty_scope
        where adj_mode = ?
          and symbol in (select symbol from temp_source_manifest)
        """,
        [request.adj_mode],
    )


def _create_temp_parsed_stage(
    con: duckdb.DuckDBPyConnection,
    request: DataBootstrapRequest,
    data_sources: tuple[TdxSourceFile, ...],
) -> None:
    con.execute("drop table if exists temp_parsed_stage")
    con.execute(
        """
        create temp table temp_parsed_stage (
            source_file_key varchar,
            symbol varchar,
            asset_type varchar,
            adj_mode varchar,
            source_path varchar,
            source_content_hash varchar,
            bar_dt date,
            trade_date date,
            open_px double,
            high_px double,
            low_px double,
            close_px double,
            volume double,
            amount double
        )
        """
    )
    if not data_sources:
        return
    start_clause = (
        f"and parsed_trade_date >= date '{request.start_date.isoformat()}'"
        if request.start_date
        else ""
    )
    end_clause = (
        f"and parsed_trade_date <= date '{request.end_date.isoformat()}'"
        if request.end_date
        else ""
    )
    for chunk in chunked(data_sources, 200):
        file_list = sql_file_list(chunk)
        con.execute(
            f"""
        insert into temp_parsed_stage
        with raw_csv as (
            select
                filename,
                trade_date,
                open_px,
                high_px,
                low_px,
                close_px,
                volume,
                amount
            from read_csv(
                [{file_list}],
                delim='\\t',
                skip=2,
                header=false,
                ignore_errors=true,
                filename=true,
                union_by_name=true,
                columns={{
                    'trade_date':'VARCHAR',
                    'open_px':'DOUBLE',
                    'high_px':'DOUBLE',
                    'low_px':'DOUBLE',
                    'close_px':'DOUBLE',
                    'volume':'DOUBLE',
                    'amount':'DOUBLE'
                }}
            )
        ),
        normalized as (
            select
                filename,
                case
                    when trade_date like '____-__-__' then cast(trade_date as date)
                    when trade_date like '____/__/__'
                        then cast(replace(trade_date, '/', '-') as date)
                    when trade_date like '__-__-____'
                        then cast(
                            substr(trade_date, 7, 4)
                            || '-'
                            || substr(trade_date, 4, 2)
                            || '-'
                            || substr(trade_date, 1, 2) as date
                        )
                    when trade_date like '__/__/____'
                        then cast(
                            substr(trade_date, 7, 4)
                            || '-'
                            || substr(trade_date, 4, 2)
                            || '-'
                            || substr(trade_date, 1, 2) as date
                        )
                    else null
                end as parsed_trade_date,
                open_px,
                high_px,
                low_px,
                close_px,
                volume,
                amount
            from raw_csv
        )
        select
            manifest.source_file_key,
            manifest.symbol,
            manifest.asset_type,
            manifest.adj_mode,
            manifest.source_path,
            manifest.source_content_hash,
            parsed_trade_date as bar_dt,
            parsed_trade_date as trade_date,
            open_px,
            high_px,
            low_px,
            close_px,
            volume,
            amount
        from normalized
        join temp_source_manifest as manifest
          on normalized.filename = manifest.source_path_normalized
        where parsed_trade_date is not null
        {start_clause}
        {end_clause}
        """
        )


def _insert_raw_tables(
    con: duckdb.DuckDBPyConnection,
    request: DataBootstrapRequest,
    *,
    source_file_count: int,
    raw_rows_written: int,
    now: datetime,
) -> None:
    con.execute(
        """
        insert into raw_market_source_file
        select
            source_file_key,
            ?,
            ?,
            asset_type,
            symbol,
            adj_mode,
            source_path,
            source_size_bytes,
            source_mtime,
            source_content_hash,
            ?,
            ?,
            ?
        from temp_source_manifest
        """,
        [SOURCE_VENDOR, request.run_id, request.run_id, DATA_SCHEMA_VERSION, now],
    )
    con.execute(
        """
        insert into raw_market_bar
        select
            source_file_key,
            ?,
            ?,
            substr(source_content_hash, 1, 16),
            symbol,
            asset_type,
            'day',
            bar_dt,
            trade_date,
            adj_mode,
            open_px,
            high_px,
            low_px,
            close_px,
            volume,
            amount,
            ?,
            ?,
            ?
        from temp_parsed_stage
        """,
        [SOURCE_VENDOR, request.run_id, request.run_id, DATA_SCHEMA_VERSION, now],
    )
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
            source_file_count,
            raw_rows_written,
            DATA_SCHEMA_VERSION,
            now,
        ],
    )


def _insert_base_tables(
    con: duckdb.DuckDBPyConnection,
    request: DataBootstrapRequest,
    *,
    base_rows_written: int,
    dirty_scope_count: int,
    now: datetime,
) -> None:
    price_line = price_line_for_adj_mode(request.adj_mode)
    con.execute(
        """
        insert into base_db.market_base_bar
        select
            symbol,
            asset_type,
            'day',
            bar_dt,
            trade_date,
            ?,
            adj_mode,
            open_px,
            high_px,
            low_px,
            close_px,
            volume,
            amount,
            ?,
            ?,
            substr(source_content_hash, 1, 16),
            source_path,
            ?,
            ?,
            ?
        from temp_parsed_stage
        """,
        [
            price_line,
            SOURCE_VENDOR,
            request.run_id,
            request.run_id,
            DATA_SCHEMA_VERSION,
            now,
        ],
    )
    con.execute(
        """
        insert into base_db.market_base_latest
        select
            symbol,
            ?,
            'day',
            ?,
            adj_mode,
            max(bar_dt),
            ?,
            ?,
            ?
        from temp_parsed_stage
        group by symbol, adj_mode
        """,
        [request.asset_type, price_line, request.run_id, DATA_SCHEMA_VERSION, now],
    )
    con.execute(
        """
        insert into base_db.market_base_dirty_scope
        select
            symbol || '|day|' || adj_mode || '|' || ?,
            symbol,
            ?,
            'day',
            adj_mode,
            min(bar_dt),
            max(bar_dt),
            'source_file_changed',
            'open',
            ?,
            ?,
            ?,
            ?
        from temp_parsed_stage
        group by symbol, adj_mode
        """,
        [
            request.run_id,
            request.asset_type,
            request.run_id,
            request.run_id,
            DATA_SCHEMA_VERSION,
            now,
        ],
    )
    con.execute(
        """
        insert into base_db.market_base_run
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            request.run_id,
            "data_bootstrap",
            request.mode,
            request.asset_type,
            request.adj_mode,
            "completed",
            base_rows_written,
            base_rows_written,
            dirty_scope_count,
            DATA_SCHEMA_VERSION,
            now,
        ],
    )
