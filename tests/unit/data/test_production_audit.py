from __future__ import annotations

from pathlib import Path

import duckdb

from asteria.data.production_audit import run_data_production_audit
from asteria.data.schema import (
    bootstrap_market_base_day_database,
    bootstrap_market_meta_database,
    bootstrap_raw_market_database,
)


def _seed_clean_data(root: Path) -> None:
    raw_db = root / "raw_market.duckdb"
    base_db = root / "market_base_day.duckdb"
    meta_db = root / "market_meta.duckdb"
    bootstrap_raw_market_database(raw_db)
    bootstrap_market_base_day_database(base_db)
    for timeframe in ("week", "month"):
        bootstrap_market_base_day_database(root / f"market_base_{timeframe}.duckdb")
    bootstrap_market_meta_database(meta_db)
    with duckdb.connect(str(raw_db)) as con:
        con.execute(
            """
            insert into raw_market_sync_run
            values ('run-1', 'data_bootstrap', 'daily_incremental', 'stock', 'backward',
                    'H:\\tdx_offline_Data', 'completed', 2, 2, 'data-bootstrap-v1',
                    current_timestamp)
            """
        )
        con.execute(
            """
            insert into raw_market_source_file
            values
            ('source-1', 'tdx_offline_txt', 'run-1', 'stock', '600000.SH',
             'backward', 'source-path-1', 100, current_timestamp, 'rev-1',
             'run-1', 'data-bootstrap-v1', current_timestamp),
            ('source-2', 'tdx_offline_txt', 'run-1', 'stock', '600000.SH',
             'none', 'source-path-2', 100, current_timestamp, 'rev-2',
             'run-1', 'data-bootstrap-v1', current_timestamp)
            """
        )
        con.execute(
            """
            insert into raw_market_bar
            values
            ('source-1', 'tdx_offline_txt', 'run-1', 'rev-1', '600000.SH', 'stock',
             'day', date '2024-01-02', date '2024-01-02', 'backward',
             10, 11, 9, 10.5, 100, 1050, 'run-1', 'data-bootstrap-v1', current_timestamp),
            ('source-2', 'tdx_offline_txt', 'run-1', 'rev-2', '600000.SH', 'stock',
             'day', date '2024-01-02', date '2024-01-02', 'none',
             9, 10, 8, 9.5, 100, 950, 'run-1', 'data-bootstrap-v1', current_timestamp)
            """
        )
    with duckdb.connect(str(base_db)) as con:
        con.execute(
            """
            insert into market_base_run
            values ('run-1', 'data_bootstrap', 'daily_incremental', 'stock', 'backward',
                    'completed', 2, 2, 1, 'data-bootstrap-v1', current_timestamp)
            """
        )
        con.execute(
            """
            insert into market_base_bar
            values
            ('600000.SH', 'stock', 'day', date '2024-01-02', date '2024-01-02',
             'analysis_price_line', 'backward', 10, 11, 9, 10.5, 100, 1050,
             'tdx_offline_txt', 'run-1', 'rev-1', 'source-path-1', 'run-1',
             'data-bootstrap-v1', current_timestamp),
            ('600000.SH', 'stock', 'day', date '2024-01-02', date '2024-01-02',
             'execution_price_line', 'none', 9, 10, 8, 9.5, 100, 950,
             'tdx_offline_txt', 'run-1', 'rev-2', 'source-path-2', 'run-1',
             'data-bootstrap-v1', current_timestamp)
            """
        )
        con.execute(
            """
            insert into market_base_latest
            values
            ('600000.SH', 'stock', 'day', 'analysis_price_line', 'backward',
             date '2024-01-02', 'run-1', 'data-bootstrap-v1', current_timestamp),
            ('600000.SH', 'stock', 'day', 'execution_price_line', 'none',
             date '2024-01-02', 'run-1', 'data-bootstrap-v1', current_timestamp)
            """
        )
        con.execute(
            """
            insert into market_base_dirty_scope
            values ('600000.SH|day|backward|run-1', '600000.SH', 'stock', 'day',
                    'backward', date '2024-01-02', date '2024-01-02',
                    'source_file_changed', 'open', 'run-1', 'run-1',
                    'data-bootstrap-v1', current_timestamp)
            """
        )
    for timeframe in ("week", "month"):
        with duckdb.connect(str(root / f"market_base_{timeframe}.duckdb")) as con:
            con.execute(
                """
                insert into market_base_run
                values ('run-1', 'legacy_data_import', 'full', 'stock', 'backward',
                        'completed', 1, 1, 1, 'data-bootstrap-v1', current_timestamp)
                """
            )
            con.execute(
                """
                insert into market_base_bar
                values ('600000.SH', 'stock', ?, date '2024-01-05', date '2024-01-05',
                        'analysis_price_line', 'backward', 10, 11, 9, 10.5, 100, 1050,
                        'legacy_lifespan', 'run-1', 'rev-1', 'source-path-1', 'run-1',
                        'data-bootstrap-v1', current_timestamp)
                """,
                [timeframe],
            )
            con.execute(
                """
                insert into market_base_latest
                values ('600000.SH', 'stock', ?, 'analysis_price_line', 'backward',
                        date '2024-01-05', 'run-1', 'data-bootstrap-v1',
                        current_timestamp)
                """,
                [timeframe],
            )
            con.execute(
                """
                insert into market_base_dirty_scope
                values (?, '600000.SH', 'stock', ?, 'backward', date '2024-01-05',
                        date '2024-01-05', 'legacy_import', 'open', 'run-1',
                        'run-1', 'data-bootstrap-v1', current_timestamp)
                """,
                [f"600000.SH|{timeframe}|backward|run-1", timeframe],
            )
    with duckdb.connect(str(meta_db)) as con:
        con.execute(
            """
            insert into trade_calendar
            values
            ('CN_A_SHARE', date '2024-01-02', true, 'day', 'market_base_day.duckdb',
             'run-1', 'data-market-meta-v1', current_timestamp)
            """
        )
        con.execute(
            """
            insert into instrument_master
            values
            ('600000.SH', '600000.SH', 'SH', 'stock', date '2024-01-02',
             date '2024-01-02', 'observed', 'raw_market_and_market_base',
             'run-1', 'data-market-meta-v1', current_timestamp)
            """
        )
        con.execute(
            """
            insert into instrument_alias
            values
            ('tdx_offline_txt', 'SH#600000', '600000.SH', 'source_path_stem',
             'H:\\tdx_offline_Data\\stock-day\\Non-Adjusted\\SH#600000.txt',
             date '1900-01-01', 'run-1', 'data-market-meta-v1', current_timestamp)
            """
        )
        con.execute(
            """
            insert into universe_membership
            values
            ('stock_observed', '600000.SH', date '2024-01-02', 'observed',
             'raw_market_and_market_base', 'run-1', 'data-market-meta-v1',
             current_timestamp)
            """
        )
        con.execute(
            """
            insert into tradability_fact
            values
            ('600000.SH', date '2024-01-02', 'has_execution_bar', true,
             'execution_price_line', 'none', 'market_base_day.duckdb',
             'run-1', 'data-market-meta-v1', current_timestamp)
            """
        )


def test_production_audit_passes_clean_analysis_and_execution_lines(tmp_path: Path) -> None:
    data_root = tmp_path / "asteria-data"
    _seed_clean_data(data_root)

    summary = run_data_production_audit(data_root=data_root, run_id="audit-clean-001")

    assert summary.status == "passed"
    assert summary.hard_fail_count == 0
    assert summary.checks["market_base_day.duckdb:price_line_mapping"] == "passed"
    assert summary.checks["raw_market.duckdb:source_manifest_diff_ready"] == "passed"
    assert summary.checks["market_base_week.duckdb:dirty_scope_present"] == "passed"
    assert summary.checks["market_base_month.duckdb:dirty_scope_present"] == "passed"
    assert summary.checks["market_meta.duckdb:industry_classification_source_policy"] == "passed"


def test_production_audit_fails_when_week_month_ledgers_are_missing(tmp_path: Path) -> None:
    data_root = tmp_path / "asteria-data"
    _seed_clean_data(data_root)
    (data_root / "market_base_week.duckdb").unlink()
    (data_root / "market_base_month.duckdb").unlink()

    summary = run_data_production_audit(data_root=data_root, run_id="audit-missing-wm-001")

    assert summary.status == "failed"
    assert summary.checks["market_base_week.duckdb:exists"] == "failed"
    assert summary.checks["market_base_month.duckdb:exists"] == "failed"


def test_production_audit_accepts_sw_industry_snapshot_rows(tmp_path: Path) -> None:
    data_root = tmp_path / "asteria-data"
    _seed_clean_data(data_root)
    with duckdb.connect(str(data_root / "market_meta.duckdb")) as con:
        con.execute(
            """
            insert into industry_classification
            values
            ('600000.SH', 'sw2021_level3_snapshot', '010101',
             '银行|股份制银行|股份制银行III', date '2021-07-31',
             'sw_industry_reference_xlsx', 'run-1',
             'data-market-meta-sw-industry-v1', current_timestamp)
            """
        )

    summary = run_data_production_audit(data_root=data_root, run_id="audit-sw-clean-001")

    assert summary.status == "passed"
    assert summary.checks["market_meta.duckdb:industry_classification_source_policy"] == "passed"


def test_production_audit_fails_when_sw_industry_source_policy_is_wrong(
    tmp_path: Path,
) -> None:
    data_root = tmp_path / "asteria-data"
    _seed_clean_data(data_root)
    with duckdb.connect(str(data_root / "market_meta.duckdb")) as con:
        con.execute(
            """
            insert into industry_classification
            values
            ('600000.SH', 'sw2021_level3_snapshot', '010101',
             '银行|股份制银行|股份制银行III', date '2021-07-31',
             'unapproved_source', 'run-1',
             'data-market-meta-sw-industry-v1', current_timestamp)
            """
        )

    summary = run_data_production_audit(data_root=data_root, run_id="audit-sw-source-001")

    assert summary.status == "failed"
    assert summary.checks["market_meta.duckdb:industry_classification_source_policy"] == "failed"


def test_production_audit_fails_when_sw_industry_natural_key_duplicates(
    tmp_path: Path,
) -> None:
    data_root = tmp_path / "asteria-data"
    _seed_clean_data(data_root)
    with duckdb.connect(str(data_root / "market_meta.duckdb")) as con:
        con.execute(
            """
            insert into industry_classification
            values
            ('600000.SH', 'sw2021_level3_snapshot', '010101',
             '银行|股份制银行|股份制银行III', date '2021-07-31',
             'sw_industry_reference_xlsx', 'run-1',
             'data-market-meta-sw-industry-v1', current_timestamp),
            ('600000.SH', 'sw2021_level3_snapshot', '010101',
             '银行|股份制银行|股份制银行III', date '2021-07-31',
             'sw_industry_reference_xlsx', 'run-2',
             'data-market-meta-sw-industry-v1', current_timestamp)
            """
        )

    summary = run_data_production_audit(data_root=data_root, run_id="audit-sw-dups-001")

    assert summary.status == "failed"
    assert (
        summary.checks["market_meta.duckdb:industry_classification_natural_key_uniqueness"]
        == "failed"
    )


def test_production_audit_fails_when_market_meta_is_absent(tmp_path: Path) -> None:
    data_root = tmp_path / "asteria-data"
    _seed_clean_data(data_root)
    (data_root / "market_meta.duckdb").unlink()

    summary = run_data_production_audit(data_root=data_root, run_id="audit-missing-meta-001")

    assert summary.status == "failed"
    assert summary.checks["market_meta.duckdb:exists"] == "failed"


def test_production_audit_fails_when_market_meta_natural_key_duplicates(
    tmp_path: Path,
) -> None:
    data_root = tmp_path / "asteria-data"
    _seed_clean_data(data_root)
    with duckdb.connect(str(data_root / "market_meta.duckdb")) as con:
        con.execute(
            """
            insert into tradability_fact
            values
            ('600000.SH', date '2024-01-02', 'has_execution_bar', true,
             'execution_price_line', 'none', 'market_base_day.duckdb',
             'run-2', 'data-market-meta-v1', current_timestamp)
            """
        )

    summary = run_data_production_audit(data_root=data_root, run_id="audit-meta-dups-001")

    assert summary.status == "failed"
    assert summary.checks["market_meta.duckdb:tradability_fact_natural_key_uniqueness"] == "failed"


def test_production_audit_fails_when_tradability_source_is_not_execution_none(
    tmp_path: Path,
) -> None:
    data_root = tmp_path / "asteria-data"
    _seed_clean_data(data_root)
    with duckdb.connect(str(data_root / "market_meta.duckdb")) as con:
        con.execute("update tradability_fact set source_adj_mode = 'backward'")

    summary = run_data_production_audit(data_root=data_root, run_id="audit-meta-source-001")

    assert summary.status == "failed"
    assert summary.checks["market_meta.duckdb:tradability_fact_source_policy"] == "failed"


def test_production_audit_fails_when_execution_line_uses_adjusted_price(
    tmp_path: Path,
) -> None:
    data_root = tmp_path / "asteria-data"
    _seed_clean_data(data_root)
    with duckdb.connect(str(data_root / "market_base_day.duckdb")) as con:
        con.execute(
            """
            update market_base_bar
            set adj_mode = 'backward'
            where price_line = 'execution_price_line'
            """
        )

    summary = run_data_production_audit(data_root=data_root, run_id="audit-fail-001")

    assert summary.status == "failed"
    assert summary.hard_fail_count == 2
    assert summary.checks["market_base_day.duckdb:price_line_mapping"] == "failed"
    assert summary.checks["market_base_day.duckdb:execution_price_line_present"] == "failed"


def test_production_audit_fails_when_day_execution_line_is_absent(
    tmp_path: Path,
) -> None:
    data_root = tmp_path / "asteria-data"
    _seed_clean_data(data_root)
    with duckdb.connect(str(data_root / "market_base_day.duckdb")) as con:
        con.execute("delete from market_base_bar where price_line = 'execution_price_line'")
        con.execute("delete from market_base_latest where price_line = 'execution_price_line'")

    summary = run_data_production_audit(
        data_root=data_root,
        run_id="audit-missing-execution-001",
    )

    assert summary.status == "failed"
    assert summary.hard_fail_count == 1
    assert summary.checks["market_base_day.duckdb:execution_price_line_present"] == "failed"
