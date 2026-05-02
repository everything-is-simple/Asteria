from __future__ import annotations

from pathlib import Path

import duckdb

from asteria.data.contracts import MarketMetaBuildRequest
from asteria.data.market_meta import run_market_meta_build
from asteria.data.schema import (
    bootstrap_market_base_day_database,
    bootstrap_market_meta_database,
    bootstrap_raw_market_database,
)


def _seed_meta_inputs(root: Path) -> None:
    raw_db = root / "raw_market.duckdb"
    base_db = root / "market_base_day.duckdb"
    bootstrap_raw_market_database(raw_db)
    bootstrap_market_base_day_database(base_db)
    with duckdb.connect(str(raw_db)) as con:
        con.execute(
            """
            insert into raw_market_source_file
            values
            ('source-1', 'tdx_offline_txt', 'run-1', 'stock', '600000.SH', 'none',
             'H:\\tdx_offline_Data\\stock-day\\Non-Adjusted\\SH#600000.txt',
             100, current_timestamp, 'hash-1', 'run-1', 'data-bootstrap-v1',
             current_timestamp)
            """
        )
        con.execute(
            """
            insert into raw_market_bar
            values
            ('source-1', 'tdx_offline_txt', 'run-1', 'rev-1', '600000.SH', 'stock',
             'day', date '2024-01-02', date '2024-01-02', 'none',
             9, 10, 8, 9.5, 100, 950, 'run-1', 'data-bootstrap-v1',
             current_timestamp)
            """
        )
    with duckdb.connect(str(base_db)) as con:
        con.execute(
            """
            insert into market_base_bar
            values
            ('600000.SH', 'stock', 'day', date '2024-01-02', date '2024-01-02',
             'analysis_price_line', 'backward', 10, 11, 9, 10.5, 100, 1050,
             'legacy_lifespan', 'run-1', 'rev-1', 'source-path-1', 'run-1',
             'data-bootstrap-v1', current_timestamp),
            ('600000.SH', 'stock', 'day', date '2024-01-02', date '2024-01-02',
             'execution_price_line', 'none', 9, 10, 8, 9.5, 100, 950,
             'legacy_lifespan', 'run-1', 'rev-2', 'source-path-2', 'run-1',
             'data-bootstrap-v1', current_timestamp)
            """
        )


def test_market_meta_schema_bootstrap_creates_all_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "market_meta.duckdb"

    bootstrap_market_meta_database(db_path)

    with duckdb.connect(str(db_path), read_only=True) as con:
        tables = {
            row[0]
            for row in con.execute(
                """
                select table_name
                from information_schema.tables
                where table_schema = 'main'
                """
            ).fetchall()
        }
    assert tables == {
        "trade_calendar",
        "instrument_master",
        "instrument_alias",
        "universe_membership",
        "tradability_fact",
        "industry_classification",
        "meta_run",
        "meta_schema_version",
        "meta_source_manifest",
    }


def test_bounded_market_meta_build_derives_minimal_observable_facts(tmp_path: Path) -> None:
    data_root = tmp_path / "asteria-data"
    temp_root = tmp_path / "asteria-temp"
    _seed_meta_inputs(data_root)

    summary = run_market_meta_build(
        MarketMetaBuildRequest(
            data_root=data_root,
            temp_root=temp_root,
            mode="bounded",
            run_id="meta-bounded-001",
        )
    )

    assert summary.status == "passed"
    assert summary.hard_fail_count == 0
    assert summary.row_counts["trade_calendar"] == 1
    assert summary.row_counts["instrument_master"] == 1
    assert summary.row_counts["instrument_alias"] == 1
    assert summary.row_counts["universe_membership"] == 1
    assert summary.row_counts["tradability_fact"] == 1
    assert summary.source_gaps["industry_classification"] == "source_gap_empty_allowed"
    with duckdb.connect(str(data_root / "market_meta.duckdb"), read_only=True) as con:
        assert con.execute("select source_symbol from instrument_alias").fetchone() == (
            "SH#600000",
        )
        assert con.execute(
            """
            select fact_name, fact_value, source_price_line, source_adj_mode
            from tradability_fact
            """
        ).fetchone() == ("has_execution_bar", True, "execution_price_line", "none")
        assert con.execute("select count(*) from industry_classification").fetchone() == (0,)


def test_market_meta_rebuild_is_idempotent_for_natural_keys(tmp_path: Path) -> None:
    data_root = tmp_path / "asteria-data"
    temp_root = tmp_path / "asteria-temp"
    _seed_meta_inputs(data_root)
    request = MarketMetaBuildRequest(
        data_root=data_root,
        temp_root=temp_root,
        mode="bounded",
        run_id="meta-idempotent-001",
    )

    first = run_market_meta_build(request)
    second = run_market_meta_build(request)

    assert first.status == "passed"
    assert second.status == "passed"
    with duckdb.connect(str(data_root / "market_meta.duckdb"), read_only=True) as con:
        duplicate_count = con.execute(
            """
            select count(*)
            from (
                select instrument_id, trade_date, fact_name
                from tradability_fact
                group by 1, 2, 3
                having count(*) > 1
            )
            """
        ).fetchone()
    assert duplicate_count == (0,)


def test_market_meta_audit_only_does_not_create_database(tmp_path: Path) -> None:
    data_root = tmp_path / "asteria-data"
    temp_root = tmp_path / "asteria-temp"
    data_root.mkdir()

    summary = run_market_meta_build(
        MarketMetaBuildRequest(
            data_root=data_root,
            temp_root=temp_root,
            mode="audit-only",
            run_id="meta-audit-only-001",
        )
    )

    assert summary.status == "failed"
    assert summary.checks["market_meta.duckdb:exists"] == "failed"
    assert not (data_root / "market_meta.duckdb").exists()
