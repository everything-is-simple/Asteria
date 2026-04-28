from __future__ import annotations

from pathlib import Path

import duckdb

from asteria.data.bootstrap import run_data_bootstrap
from asteria.data.contracts import DataBootstrapRequest


def _write_tdx_file(path: Path, symbol: str, rows: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"{symbol} 测试证券 日线 后复权\n"
        "      日期\t开盘\t最高\t最低\t收盘\t成交量\t成交额\n" + "\n".join(rows) + "\n",
        encoding="gbk",
    )


def _request(tmp_path: Path, run_id: str, mode: str = "bounded") -> DataBootstrapRequest:
    return DataBootstrapRequest(
        source_root=tmp_path / "tdx",
        target_root=tmp_path / "asteria-data",
        temp_root=tmp_path / "asteria-temp",
        asset_type="stock",
        adj_mode="backward",
        mode=mode,
        run_id=run_id,
        start_dt="2024-01-01",
        end_dt="2024-12-31",
        symbol_limit=10,
    )


def test_bounded_bootstrap_writes_raw_base_and_dirty_scope(tmp_path: Path) -> None:
    _write_tdx_file(
        tmp_path / "tdx" / "stock-day" / "Backward-Adjusted" / "SH#600000.txt",
        "SH#600000",
        (
            "2024-01-02\t10.00\t10.50\t9.90\t10.20\t1000\t10200",
            "2024-01-03\t10.20\t10.80\t10.10\t10.70\t1100\t11770",
        ),
    )

    summary = run_data_bootstrap(_request(tmp_path, "test-run-001"))

    assert summary.status == "completed"
    assert summary.raw_rows_written == 2
    assert summary.base_rows_written == 2
    assert summary.dirty_scope_count == 1

    raw_db = tmp_path / "asteria-data" / "raw_market.duckdb"
    base_db = tmp_path / "asteria-data" / "market_base_day.duckdb"
    with duckdb.connect(str(raw_db), read_only=True) as con:
        registry = con.execute(
            """
            select source_path, source_size_bytes, source_content_hash, run_id, schema_version
            from raw_market_source_file
            """
        ).fetchone()
        assert registry[0].endswith("SH#600000.txt")
        assert registry[1] > 0
        assert registry[2]
        assert registry[3] == "test-run-001"
        assert registry[4] == "data-bootstrap-v1"

    with duckdb.connect(str(base_db), read_only=True) as con:
        rows = con.execute(
            """
            select symbol, timeframe, price_line, adj_mode, close_px
            from market_base_bar
            order by bar_dt
            """
        ).fetchall()
        dirty = con.execute("select symbol, dirty_status from market_base_dirty_scope").fetchall()
        assert rows == [
            ("600000.SH", "day", "analysis_price_line", "backward", 10.20),
            ("600000.SH", "day", "analysis_price_line", "backward", 10.70),
        ]
        assert dirty == [("600000.SH", "open")]


def test_resume_completed_run_does_not_promote_duplicate_rows(tmp_path: Path) -> None:
    _write_tdx_file(
        tmp_path / "tdx" / "stock-day" / "Backward-Adjusted" / "SH#600000.txt",
        "SH#600000",
        ("2024-01-02\t10\t11\t9\t10.5\t100\t1050",),
    )
    request = _request(tmp_path, "resume-run-001")

    first = run_data_bootstrap(request)
    second = run_data_bootstrap(_request(tmp_path, "resume-run-001", mode="resume"))

    assert first.status == "completed"
    assert second.status == "completed"
    assert second.resume_reused is True

    raw_db = tmp_path / "asteria-data" / "raw_market.duckdb"
    with duckdb.connect(str(raw_db), read_only=True) as con:
        assert con.execute("select count(*) from raw_market_bar").fetchone()[0] == 1


def test_new_run_replaces_existing_base_natural_keys(tmp_path: Path) -> None:
    _write_tdx_file(
        tmp_path / "tdx" / "stock-day" / "Backward-Adjusted" / "SH#600000.txt",
        "SH#600000",
        ("2024-01-02\t10\t11\t9\t10.5\t100\t1050",),
    )

    run_data_bootstrap(_request(tmp_path, "replace-run-001"))
    run_data_bootstrap(_request(tmp_path, "replace-run-002"))

    base_db = tmp_path / "asteria-data" / "market_base_day.duckdb"
    with duckdb.connect(str(base_db), read_only=True) as con:
        assert con.execute("select count(*) from market_base_bar").fetchone()[0] == 1
        assert con.execute("select run_id from market_base_bar").fetchone()[0] == "replace-run-002"


def test_all_adjustment_modes_keep_separate_latest_rows(tmp_path: Path) -> None:
    for folder in ("Backward-Adjusted", "Forward-Adjusted", "Non-Adjusted"):
        _write_tdx_file(
            tmp_path / "tdx" / "stock-day" / folder / "SH#600000.txt",
            "SH#600000",
            ("2024-01-02\t10\t11\t9\t10.5\t100\t1050",),
        )
    request = DataBootstrapRequest(
        source_root=tmp_path / "tdx",
        target_root=tmp_path / "asteria-data",
        temp_root=tmp_path / "asteria-temp",
        asset_type="stock",
        adj_mode="all",
        mode="bounded",
        run_id="all-adj-run-001",
        symbol_limit=10,
    )

    run_data_bootstrap(request)

    base_db = tmp_path / "asteria-data" / "market_base_day.duckdb"
    with duckdb.connect(str(base_db), read_only=True) as con:
        rows = con.execute(
            """
            select price_line, adj_mode
            from market_base_latest
            order by adj_mode, price_line
            """
        ).fetchall()
        assert rows == [
            ("analysis_price_line", "backward"),
            ("analysis_price_line", "forward"),
            ("execution_price_line", "none"),
        ]
