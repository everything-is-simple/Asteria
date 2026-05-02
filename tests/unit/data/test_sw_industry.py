from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import duckdb

from asteria.data.contracts import (
    DATA_SW_INDUSTRY_SCHEMA_VERSION,
    SW_INDUSTRY_EFFECTIVE_DATE,
    SW_INDUSTRY_SOURCE_VENDOR,
    SwIndustrySnapshotImportRequest,
)
from asteria.data.schema import bootstrap_market_meta_database
from asteria.data.sw_industry import (
    EXPECTED_SW_INDUSTRY_SOURCE_SHA256,
    run_sw_industry_snapshot_import,
)


def _write_xlsx(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row_xml = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for col_index, value in enumerate(row, start=1):
            ref = f"{chr(64 + col_index)}{row_index}"
            cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{value}</t></is></c>')
        row_xml.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<sheetData>{''.join(row_xml)}</sheetData></worksheet>"
    )
    with ZipFile(path, "w", ZIP_DEFLATED) as zf:
        zf.writestr(
            "[Content_Types].xml",
            (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Override PartName="/xl/workbook.xml" '
                'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                '<Override PartName="/xl/worksheets/sheet1.xml" '
                'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                "</Types>"
            ),
        )
        zf.writestr(
            "_rels/.rels",
            (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/'
                'relationships">'
                '<Relationship Id="rId1" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                'relationships/officeDocument" '
                'Target="xl/workbook.xml"/></Relationships>'
            ),
        )
        zf.writestr(
            "xl/workbook.xml",
            (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                '<sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets></workbook>'
            ),
        )
        zf.writestr(
            "xl/_rels/workbook.xml.rels",
            (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/'
                'relationships">'
                '<Relationship Id="rId1" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                'relationships/worksheet" '
                'Target="worksheets/sheet1.xml"/></Relationships>'
            ),
        )
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def _seed_market_meta(path: Path) -> None:
    bootstrap_market_meta_database(path)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            insert into instrument_master
            values
            ('600000.SH', '600000.SH', 'SH', 'stock', date '2024-01-02',
             date '2024-01-02', 'observed', 'fixture', 'run-1',
             'data-market-meta-v1', current_timestamp),
            ('000001.SZ', '000001.SZ', 'SZ', 'stock', date '2024-01-02',
             date '2024-01-02', 'observed', 'fixture', 'run-1',
             'data-market-meta-v1', current_timestamp),
            ('830001.BJ', '830001.BJ', 'BJ', 'stock', date '2024-01-02',
             date '2024-01-02', 'observed', 'fixture', 'run-1',
             'data-market-meta-v1', current_timestamp)
            """
        )


def _source_rows() -> list[list[str]]:
    return [
        [
            "交易所",
            "行业代码",
            "股票代码",
            "公司简称",
            "新版一级行业",
            "新版二级行业",
            "新版三级行业",
        ],
        ["A股", "010101", "600000.SH", "浦发银行", "银行", "股份制银行", "股份制银行III"],
        ["A股", "020202", "000001.SZ", "平安银行", "银行", "股份制银行", "股份制银行III"],
        ["A股", "030303", "999999.SH", "未匹配A", "电子", "半导体", "数字芯片设计"],
        ["港股", "040404", "00005.HK", "汇丰控股", "银行", "银行", "银行III"],
    ]


def test_sw_industry_snapshot_import_writes_only_matched_a_share_rows(
    tmp_path: Path,
) -> None:
    data_root = tmp_path / "asteria-data"
    temp_root = tmp_path / "asteria-temp"
    source_path = tmp_path / "sw.xlsx"
    _seed_market_meta(data_root / "market_meta.duckdb")
    _write_xlsx(source_path, _source_rows())

    summary = run_sw_industry_snapshot_import(
        SwIndustrySnapshotImportRequest(
            data_root=data_root,
            temp_root=temp_root,
            source_path=source_path,
            mode="full",
            run_id="sw-industry-test-001",
            expected_source_sha256=None,
        )
    )

    assert summary.status == "passed"
    assert summary.hard_fail_count == 0
    assert summary.source_row_count == 4
    assert summary.source_a_share_row_count == 3
    assert summary.matched_instrument_count == 2
    assert summary.inserted_industry_rows == 2
    assert summary.unmatched_a_share_count == 1
    assert summary.non_a_share_excluded_count == 1
    assert summary.master_unmatched_count == 1
    with duckdb.connect(str(data_root / "market_meta.duckdb"), read_only=True) as con:
        rows = con.execute(
            """
            select instrument_id, industry_schema, industry_code, industry_name,
                   effective_date, source_vendor, run_id, schema_version
            from industry_classification
            order by instrument_id
            """
        ).fetchall()
    assert rows == [
        (
            "000001.SZ",
            "sw2021_level3_snapshot",
            "020202",
            "银行|股份制银行|股份制银行III",
            SW_INDUSTRY_EFFECTIVE_DATE,
            SW_INDUSTRY_SOURCE_VENDOR,
            "sw-industry-test-001",
            DATA_SW_INDUSTRY_SCHEMA_VERSION,
        ),
        (
            "600000.SH",
            "sw2021_level3_snapshot",
            "010101",
            "银行|股份制银行|股份制银行III",
            SW_INDUSTRY_EFFECTIVE_DATE,
            SW_INDUSTRY_SOURCE_VENDOR,
            "sw-industry-test-001",
            DATA_SW_INDUSTRY_SCHEMA_VERSION,
        ),
    ]


def test_sw_industry_snapshot_audit_only_does_not_write_database(tmp_path: Path) -> None:
    data_root = tmp_path / "asteria-data"
    temp_root = tmp_path / "asteria-temp"
    source_path = tmp_path / "sw.xlsx"
    _seed_market_meta(data_root / "market_meta.duckdb")
    _write_xlsx(source_path, _source_rows())

    summary = run_sw_industry_snapshot_import(
        SwIndustrySnapshotImportRequest(
            data_root=data_root,
            temp_root=temp_root,
            source_path=source_path,
            mode="audit-only",
            run_id="sw-industry-audit-only-001",
            expected_source_sha256=None,
        )
    )

    assert summary.status == "passed"
    assert summary.promoted is False
    assert not (temp_root / "data" / "sw-industry-audit-only-001" / "market_meta.duckdb").exists()
    with duckdb.connect(str(data_root / "market_meta.duckdb"), read_only=True) as con:
        assert con.execute("select count(*) from industry_classification").fetchone() == (0,)


def test_sw_industry_snapshot_rejects_duplicate_source_codes(tmp_path: Path) -> None:
    data_root = tmp_path / "asteria-data"
    temp_root = tmp_path / "asteria-temp"
    source_path = tmp_path / "sw.xlsx"
    _seed_market_meta(data_root / "market_meta.duckdb")
    rows = _source_rows()
    rows.append(["A股", "090909", "600000.SH", "重复", "银行", "银行", "银行III"])
    _write_xlsx(source_path, rows)

    summary = run_sw_industry_snapshot_import(
        SwIndustrySnapshotImportRequest(
            data_root=data_root,
            temp_root=temp_root,
            source_path=source_path,
            mode="full",
            run_id="sw-industry-duplicate-001",
            expected_source_sha256=None,
        )
    )

    assert summary.status == "failed"
    assert summary.checks["sw_industry_source:duplicate_stock_code"] == "failed"
    with duckdb.connect(str(data_root / "market_meta.duckdb"), read_only=True) as con:
        assert con.execute("select count(*) from industry_classification").fetchone() == (0,)


def test_sw_industry_snapshot_rejects_unexpected_source_hash(tmp_path: Path) -> None:
    data_root = tmp_path / "asteria-data"
    temp_root = tmp_path / "asteria-temp"
    source_path = tmp_path / "sw.xlsx"
    _seed_market_meta(data_root / "market_meta.duckdb")
    _write_xlsx(source_path, _source_rows())

    summary = run_sw_industry_snapshot_import(
        SwIndustrySnapshotImportRequest(
            data_root=data_root,
            temp_root=temp_root,
            source_path=source_path,
            mode="full",
            run_id="sw-industry-hash-001",
            expected_source_sha256=EXPECTED_SW_INDUSTRY_SOURCE_SHA256,
        )
    )

    assert summary.status == "failed"
    assert summary.checks["sw_industry_source:sha256"] == "failed"
