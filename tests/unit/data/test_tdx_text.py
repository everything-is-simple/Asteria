from __future__ import annotations

from pathlib import Path

from asteria.data.tdx_text import discover_tdx_text_files, parse_tdx_text_file


def _write_tdx_file(path: Path, code_name: str = "浦发银行") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"SH#600000 {code_name} 日线 前复权\n"
        "      日期\t开盘\t最高\t最低\t收盘\t成交量\t成交额\n"
        "2024-01-02\t10.00\t10.50\t9.90\t10.20\t1000\t10200\n"
        "2024-01-03\t10.20\t10.80\t10.10\t10.70\t1100\t11770\n"
        "数据来源: tdx\n",
        encoding="gbk",
    )


def test_discover_tdx_text_files_maps_asset_and_adjustment_folders(tmp_path: Path) -> None:
    source_root = tmp_path / "tdx"
    _write_tdx_file(source_root / "stock-day" / "Backward-Adjusted" / "SH#600000.txt")
    _write_tdx_file(source_root / "stock-day" / "Forward-Adjusted" / "SH#600001.txt")
    _write_tdx_file(source_root / "stock-day" / "Non-Adjusted" / "SH#600002.txt")

    files = discover_tdx_text_files(source_root, asset_type="stock", adj_mode="all")

    assert [item.symbol for item in files] == ["600000.SH", "600001.SH", "600002.SH"]
    assert [item.adj_mode for item in files] == ["backward", "forward", "none"]
    assert all(item.asset_type == "stock" for item in files)


def test_discover_all_adjustment_modes_applies_symbol_limit_per_folder(tmp_path: Path) -> None:
    source_root = tmp_path / "tdx"
    for folder in ("Backward-Adjusted", "Forward-Adjusted", "Non-Adjusted"):
        _write_tdx_file(source_root / "stock-day" / folder / "SH#600000.txt")
        _write_tdx_file(source_root / "stock-day" / folder / "SH#600001.txt")

    files = discover_tdx_text_files(source_root, asset_type="stock", adj_mode="all", symbol_limit=1)

    assert [item.adj_mode for item in files] == ["backward", "forward", "none"]
    assert [item.symbol for item in files] == ["600000.SH", "600000.SH", "600000.SH"]


def test_parse_tdx_text_file_keeps_source_metadata(tmp_path: Path) -> None:
    source_file = tmp_path / "tdx" / "stock-day" / "Backward-Adjusted" / "SH#600000.txt"
    _write_tdx_file(source_file)
    discovered = discover_tdx_text_files(
        tmp_path / "tdx",
        asset_type="stock",
        adj_mode="backward",
    )[0]

    parsed = parse_tdx_text_file(discovered)

    assert parsed.source.symbol == "600000.SH"
    assert parsed.source.source_path == source_file
    assert parsed.source.source_size_bytes > 0
    assert parsed.source.source_content_hash
    assert [bar.trade_date.isoformat() for bar in parsed.bars] == ["2024-01-02", "2024-01-03"]
    assert parsed.bars[0].close_px == 10.20


def test_parse_tdx_text_file_accepts_legacy_day_month_year_dates(tmp_path: Path) -> None:
    source_file = tmp_path / "tdx" / "stock-day" / "Backward-Adjusted" / "SH#600000.txt"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text(
        "600000 浦发银行 日线 后复权\n"
        "      日期\t开盘\t最高\t最低\t收盘\t成交量\t成交额\n"
        "10-11-1999\t29.50\t29.80\t27.00\t27.75\t174085000\t4859102208.00\n",
        encoding="gbk",
    )
    discovered = discover_tdx_text_files(
        tmp_path / "tdx",
        asset_type="stock",
        adj_mode="backward",
    )[0]

    parsed = parse_tdx_text_file(discovered)

    assert parsed.bars[0].trade_date.isoformat() == "1999-11-10"
