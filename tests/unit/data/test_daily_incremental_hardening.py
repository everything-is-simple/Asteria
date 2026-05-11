from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import duckdb

from asteria.data.daily_incremental_hardening import (
    DataDailyIncrementalHardeningRequest,
    run_data_daily_incremental_hardening,
)
from asteria.data.schema import bootstrap_market_base_database


def _write_tdx_file(path: Path, symbol: str, rows: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"{symbol} 测试证券 日线 后复权\n"
        "      日期\t开盘\t最高\t最低\t收盘\t成交量\t成交额\n" + "\n".join(rows) + "\n",
        encoding="gbk",
    )


def _request(
    tmp_path: Path,
    run_id: str,
    *,
    mode: str = "daily_incremental",
) -> DataDailyIncrementalHardeningRequest:
    return DataDailyIncrementalHardeningRequest(
        source_root=tmp_path / "tdx",
        target_root=tmp_path / "asteria-data",
        temp_root=tmp_path / "asteria-temp",
        report_root=tmp_path / "asteria-report",
        run_id=run_id,
        mode=mode,
        start_dt="2024-01-01",
        end_dt="2024-12-31",
        symbol_limit=10,
    )


def _seed_week_month_ledgers(root: Path) -> None:
    for timeframe in ("week", "month"):
        db_path = root / f"market_base_{timeframe}.duckdb"
        bootstrap_market_base_database(db_path)
        with duckdb.connect(str(db_path)) as con:
            con.execute(
                """
                insert into market_base_run
                values ('seed-run', 'legacy_data_import', 'full', 'stock', 'backward',
                        'completed', 1, 1, 1, 'data-bootstrap-v1', current_timestamp)
                """
            )
            con.execute(
                """
                insert into market_base_bar
                values ('600000.SH', 'stock', ?, date '2024-01-05', date '2024-01-05',
                        'analysis_price_line', 'backward', 10, 11, 9, 10.5, 100, 1050,
                        'legacy_lifespan', 'seed-run', 'rev-1', 'source-path', 'seed-run',
                        'data-bootstrap-v1', current_timestamp)
                """,
                [timeframe],
            )
            con.execute(
                """
                insert into market_base_latest
                values ('600000.SH', 'stock', ?, 'analysis_price_line', 'backward',
                        date '2024-01-05', 'seed-run', 'data-bootstrap-v1',
                        current_timestamp)
                """,
                [timeframe],
            )
            con.execute(
                """
                insert into market_base_dirty_scope
                values (?, '600000.SH', 'stock', ?, 'backward', date '2024-01-05',
                        date '2024-01-05', 'legacy_import', 'open', 'seed-run',
                        'seed-run', 'data-bootstrap-v1', current_timestamp)
                """,
                [f"600000.SH|{timeframe}|backward|seed-run", timeframe],
            )


def _row_count(path: Path, table: str) -> int:
    with duckdb.connect(str(path), read_only=True) as con:
        return int(con.execute(f"select count(*) from {table}").fetchone()[0])


def test_daily_incremental_hardening_writes_manifest_checkpoint_ledger_and_audit(
    tmp_path: Path,
) -> None:
    _write_tdx_file(
        tmp_path / "tdx" / "stock-day" / "Backward-Adjusted" / "SH#600000.txt",
        "SH#600000",
        ("2024-01-02\t10\t11\t9\t10.5\t100\t1050",),
    )
    _seed_week_month_ledgers(tmp_path / "asteria-data")

    summary = run_data_daily_incremental_hardening(_request(tmp_path, "hardening-001"))

    assert summary.status == "passed"
    assert summary.bootstrap.raw_rows_written == 1
    assert summary.daily_dirty_scope_count == 1
    assert summary.ledger_audit["market_base_week.duckdb"].status == "passed"
    assert summary.ledger_audit["market_base_month.duckdb"].status == "passed"

    source_manifest = json.loads(Path(summary.source_manifest_path).read_text(encoding="utf-8"))
    checkpoint = json.loads(Path(summary.checkpoint_path).read_text(encoding="utf-8"))
    audit = json.loads(Path(summary.audit_summary_path).read_text(encoding="utf-8"))
    ledger_text = Path(summary.batch_ledger_path).read_text(encoding="utf-8")

    assert source_manifest["run_id"] == "hardening-001"
    assert source_manifest["source_count"] == 1
    assert checkpoint["status"] == "completed"
    assert checkpoint["hardening"]["daily_dirty_scope_count"] == 1
    assert audit["status"] == "passed"
    assert '"status": "promoted"' in ledger_text


def test_daily_incremental_hardening_skips_unchanged_source_without_duplicate_rows(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "tdx" / "stock-day" / "Backward-Adjusted" / "SH#600000.txt"
    _write_tdx_file(
        source_file,
        "SH#600000",
        ("2024-01-02\t10\t11\t9\t10.5\t100\t1050",),
    )
    _seed_week_month_ledgers(tmp_path / "asteria-data")
    first = run_data_daily_incremental_hardening(_request(tmp_path, "hardening-skip-001"))
    second = run_data_daily_incremental_hardening(_request(tmp_path, "hardening-skip-002"))

    assert first.bootstrap.raw_rows_written == 1
    assert second.bootstrap.raw_rows_written == 0
    assert second.bootstrap.skipped_source_file_count == 1
    assert _row_count(tmp_path / "asteria-data" / "raw_market.duckdb", "raw_market_bar") == 1
    assert _row_count(tmp_path / "asteria-data" / "market_base_day.duckdb", "market_base_bar") == 1


def test_daily_incremental_hardening_reprocesses_changed_source_with_day_dirty_scope(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "tdx" / "stock-day" / "Backward-Adjusted" / "SH#600000.txt"
    _write_tdx_file(
        source_file,
        "SH#600000",
        ("2024-01-02\t10\t11\t9\t10.5\t100\t1050",),
    )
    _seed_week_month_ledgers(tmp_path / "asteria-data")
    run_data_daily_incremental_hardening(_request(tmp_path, "hardening-change-001"))

    _write_tdx_file(
        source_file,
        "SH#600000",
        (
            "2024-01-02\t10\t11\t9\t10.6\t100\t1060",
            "2024-01-03\t10.6\t11\t10\t10.8\t120\t1296",
        ),
    )
    changed = run_data_daily_incremental_hardening(_request(tmp_path, "hardening-change-002"))

    assert changed.bootstrap.changed_source_file_count == 1
    assert changed.daily_dirty_scope_count == 1
    with duckdb.connect(str(tmp_path / "asteria-data" / "market_base_day.duckdb")) as con:
        rows = con.execute(
            """
            select bar_dt, close_px, run_id
            from market_base_bar
            order by bar_dt
            """
        ).fetchall()
        dirty = con.execute(
            """
            select symbol, timeframe, source_run_id, run_id
            from market_base_dirty_scope
            where run_id = 'hardening-change-002'
            """
        ).fetchone()
    assert rows == [
        (date(2024, 1, 2), 10.6, "hardening-change-002"),
        (date(2024, 1, 3), 10.8, "hardening-change-002"),
    ]
    assert dirty == ("600000.SH", "day", "hardening-change-002", "hardening-change-002")


def test_daily_incremental_hardening_resume_reuses_completed_checkpoint(
    tmp_path: Path,
) -> None:
    _write_tdx_file(
        tmp_path / "tdx" / "stock-day" / "Backward-Adjusted" / "SH#600000.txt",
        "SH#600000",
        ("2024-01-02\t10\t11\t9\t10.5\t100\t1050",),
    )
    _seed_week_month_ledgers(tmp_path / "asteria-data")
    run_data_daily_incremental_hardening(_request(tmp_path, "hardening-resume-001"))

    resumed = run_data_daily_incremental_hardening(
        _request(tmp_path, "hardening-resume-001", mode="resume")
    )

    assert resumed.bootstrap.resume_reused is True
    assert _row_count(tmp_path / "asteria-data" / "market_base_day.duckdb", "market_base_bar") == 1


def test_daily_incremental_hardening_audits_week_month_read_only(tmp_path: Path) -> None:
    _write_tdx_file(
        tmp_path / "tdx" / "stock-day" / "Backward-Adjusted" / "SH#600000.txt",
        "SH#600000",
        ("2024-01-02\t10\t11\t9\t10.5\t100\t1050",),
    )
    _seed_week_month_ledgers(tmp_path / "asteria-data")
    before = {
        timeframe: _row_count(
            tmp_path / "asteria-data" / f"market_base_{timeframe}.duckdb",
            "market_base_bar",
        )
        for timeframe in ("week", "month")
    }

    summary = run_data_daily_incremental_hardening(_request(tmp_path, "hardening-audit-001"))

    after = {
        timeframe: _row_count(
            tmp_path / "asteria-data" / f"market_base_{timeframe}.duckdb",
            "market_base_bar",
        )
        for timeframe in ("week", "month")
    }
    assert before == after
    assert summary.ledger_audit["market_base_week.duckdb"].read_only is True
    assert summary.ledger_audit["market_base_month.duckdb"].read_only is True
