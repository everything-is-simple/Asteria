from __future__ import annotations

from pathlib import Path

import duckdb

from asteria.data.production_audit import run_data_production_audit
from asteria.data.schema import bootstrap_market_base_day_database, bootstrap_raw_market_database


def _seed_clean_data(root: Path) -> None:
    raw_db = root / "raw_market.duckdb"
    base_db = root / "market_base_day.duckdb"
    bootstrap_raw_market_database(raw_db)
    bootstrap_market_base_day_database(base_db)
    with duckdb.connect(str(raw_db)) as con:
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


def test_production_audit_passes_clean_analysis_and_execution_lines(tmp_path: Path) -> None:
    data_root = tmp_path / "asteria-data"
    _seed_clean_data(data_root)

    summary = run_data_production_audit(data_root=data_root, run_id="audit-clean-001")

    assert summary.status == "passed"
    assert summary.hard_fail_count == 0
    assert summary.checks["market_base_day.duckdb:price_line_mapping"] == "passed"


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
