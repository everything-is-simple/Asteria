from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

from asteria.data.contracts import (
    DATA_SW_INDUSTRY_SCHEMA_VERSION,
    SW_INDUSTRY_EFFECTIVE_DATE,
    SW_INDUSTRY_SOURCE_VENDOR,
    SwIndustrySnapshotImportRequest,
    SwIndustrySnapshotImportSummary,
)
from asteria.data.schema import bootstrap_market_meta_database
from asteria.data.xlsx_reader import read_first_sheet

EXPECTED_SW_INDUSTRY_SOURCE_SHA256 = (
    "B242AB04E0F68357CF90772E3F15367644D3E74C08A767EB9C5EDCF21467FCBB"
)
SW_INDUSTRY_SCHEMA = "sw2021_level3_snapshot"
SW_SOURCE_REQUIRED_COLUMNS = (
    "交易所",
    "行业代码",
    "股票代码",
    "公司简称",
    "新版一级行业",
    "新版二级行业",
    "新版三级行业",
)


@dataclass(frozen=True)
class SwIndustrySourceRow:
    exchange: str
    industry_code: str
    stock_code: str
    company_name: str
    level1_name: str
    level2_name: str
    level3_name: str

    @property
    def industry_name(self) -> str:
        return "|".join((self.level1_name, self.level2_name, self.level3_name))


def run_sw_industry_snapshot_import(
    request: SwIndustrySnapshotImportRequest,
) -> SwIndustrySnapshotImportSummary:
    source_sha256 = _sha256(request.source_path) if request.source_path.exists() else ""
    rows, source_checks = _read_source_with_checks(request, source_sha256)
    if _has_failed(source_checks) or request.mode == "audit-only":
        summary = _summarize_existing(request, source_sha256, rows, source_checks)
        _write_report(request, summary)
        return summary

    if not request.formal_db_path.exists():
        checks = {**source_checks, "market_meta.duckdb:exists": "failed"}
        summary = _build_summary(request, source_sha256, rows, checks, promoted=False)
        _write_report(request, summary)
        return summary

    request.staging_db_path.parent.mkdir(parents=True, exist_ok=True)
    if request.staging_db_path.exists():
        request.staging_db_path.unlink()
    shutil.copy2(request.formal_db_path, request.staging_db_path)
    bootstrap_market_meta_database(request.staging_db_path)
    _write_snapshot_rows(request, rows)
    checks = {
        **source_checks,
        **_audit_database(request.staging_db_path, rows, require_matched_count=True),
    }
    staging_summary = _build_summary(request, source_sha256, rows, checks, promoted=False)
    if staging_summary.status != "passed":
        _write_report(request, staging_summary)
        return staging_summary

    shutil.copy2(request.staging_db_path, request.formal_db_path)
    formal_checks = {
        **source_checks,
        **_audit_database(request.formal_db_path, rows, require_matched_count=True),
    }
    summary = _build_summary(request, source_sha256, rows, formal_checks, promoted=True)
    _write_report(request, summary)
    return summary


def parse_sw_industry_xlsx(path: Path) -> tuple[SwIndustrySourceRow, ...]:
    table = read_first_sheet(path)
    if not table:
        return ()
    header = table[0]
    missing = [column for column in SW_SOURCE_REQUIRED_COLUMNS if column not in header]
    if missing:
        raise ValueError(f"Missing SW industry columns: {missing}")
    index = {name: header.index(name) for name in SW_SOURCE_REQUIRED_COLUMNS}
    rows = []
    for raw in table[1:]:
        padded = raw + [""] * (len(header) - len(raw))
        rows.append(
            SwIndustrySourceRow(
                exchange=padded[index["交易所"]].strip(),
                industry_code=padded[index["行业代码"]].strip(),
                stock_code=padded[index["股票代码"]].strip(),
                company_name=padded[index["公司简称"]].strip(),
                level1_name=padded[index["新版一级行业"]].strip(),
                level2_name=padded[index["新版二级行业"]].strip(),
                level3_name=padded[index["新版三级行业"]].strip(),
            )
        )
    return tuple(rows)


def _read_source_with_checks(
    request: SwIndustrySnapshotImportRequest,
    source_sha256: str,
) -> tuple[tuple[SwIndustrySourceRow, ...], dict[str, str]]:
    checks = {
        "sw_industry_source:exists": "passed" if request.source_path.exists() else "failed",
        "sw_industry_source:sha256": "passed",
        "sw_industry_source:required_columns": "failed",
        "sw_industry_source:duplicate_stock_code": "failed",
    }
    if request.expected_source_sha256 and source_sha256.upper() != request.expected_source_sha256:
        checks["sw_industry_source:sha256"] = "failed"
    if not request.source_path.exists():
        return (), checks
    try:
        rows = parse_sw_industry_xlsx(request.source_path)
    except (KeyError, ValueError):
        return (), checks
    checks["sw_industry_source:required_columns"] = "passed"
    duplicate_codes = _duplicate_stock_codes(rows)
    checks["sw_industry_source:duplicate_stock_code"] = (
        "passed" if not duplicate_codes else "failed"
    )
    return rows, checks


def _summarize_existing(
    request: SwIndustrySnapshotImportRequest,
    source_sha256: str,
    rows: tuple[SwIndustrySourceRow, ...],
    source_checks: dict[str, str],
) -> SwIndustrySnapshotImportSummary:
    db_checks = (
        _audit_database(request.formal_db_path, rows, require_matched_count=False)
        if request.formal_db_path.exists()
        else {"market_meta.duckdb:exists": "failed"}
    )
    return _build_summary(
        request,
        source_sha256,
        rows,
        {**source_checks, **db_checks},
        promoted=False,
    )


def _write_snapshot_rows(
    request: SwIndustrySnapshotImportRequest,
    rows: tuple[SwIndustrySourceRow, ...],
) -> None:
    now = _utc_now()
    with duckdb.connect(str(request.staging_db_path)) as con:
        con.execute("begin transaction")
        con.execute(
            """
            delete from industry_classification
            where industry_schema = ?
               or source_vendor = ?
            """,
            [SW_INDUSTRY_SCHEMA, SW_INDUSTRY_SOURCE_VENDOR],
        )
        con.execute(
            """
            create temp table sw_source(
                exchange varchar,
                industry_code varchar,
                stock_code varchar,
                industry_name varchar
            )
            """
        )
        con.executemany(
            "insert into sw_source values (?, ?, ?, ?)",
            [(row.exchange, row.industry_code, row.stock_code, row.industry_name) for row in rows],
        )
        con.execute(
            """
            insert into industry_classification
            select
                master.instrument_id,
                ? as industry_schema,
                source.industry_code,
                source.industry_name,
                ? as effective_date,
                ? as source_vendor,
                ? as run_id,
                ? as schema_version,
                ? as created_at
            from sw_source as source
            inner join instrument_master as master
                on master.instrument_id = source.stock_code
            where source.exchange = 'A股'
              and master.asset_type = 'stock'
              and master.exchange_code in ('SH', 'SZ', 'BJ')
            """,
            [
                SW_INDUSTRY_SCHEMA,
                SW_INDUSTRY_EFFECTIVE_DATE,
                SW_INDUSTRY_SOURCE_VENDOR,
                request.run_id,
                DATA_SW_INDUSTRY_SCHEMA_VERSION,
                now,
            ],
        )
        con.execute("commit")


def _audit_database(
    path: Path,
    rows: tuple[SwIndustrySourceRow, ...],
    *,
    require_matched_count: bool,
) -> dict[str, str]:
    if not path.exists():
        return {"market_meta.duckdb:exists": "failed"}
    checks: dict[str, str] = {"market_meta.duckdb:exists": "passed"}
    with duckdb.connect(str(path), read_only=True) as con:
        policy_failures = _count_result(
            con.execute(
                """
                select count(*)
                from industry_classification
                where industry_schema <> ?
                   or effective_date <> ?
                   or source_vendor <> ?
                   or schema_version <> ?
                """,
                [
                    SW_INDUSTRY_SCHEMA,
                    SW_INDUSTRY_EFFECTIVE_DATE,
                    SW_INDUSTRY_SOURCE_VENDOR,
                    DATA_SW_INDUSTRY_SCHEMA_VERSION,
                ],
            ).fetchone()
        )
        checks["market_meta.duckdb:industry_classification_source_policy"] = (
            "passed" if policy_failures == 0 else "failed"
        )
        duplicates = _count_result(
            con.execute(
                """
                select count(*)
                from (
                    select instrument_id, industry_schema, effective_date
                    from industry_classification
                    group by 1, 2, 3
                    having count(*) > 1
                )
                """
            ).fetchone()
        )
        checks["market_meta.duckdb:industry_classification_natural_key_uniqueness"] = (
            "passed" if duplicates == 0 else "failed"
        )
        orphan_rows = _count_result(
            con.execute(
                """
                select count(*)
                from industry_classification as industry
                left join instrument_master as master
                    on master.instrument_id = industry.instrument_id
                where master.instrument_id is null
                   or master.asset_type <> 'stock'
                   or master.exchange_code not in ('SH', 'SZ', 'BJ')
                """
            ).fetchone()
        )
        checks["market_meta.duckdb:industry_classification_instrument_scope"] = (
            "passed" if orphan_rows == 0 else "failed"
        )
        if require_matched_count:
            expected = _matched_rows(con, rows)
            inserted = _industry_row_count(con)
            checks["market_meta.duckdb:industry_classification_matched_count"] = (
                "passed" if inserted == expected else "failed"
            )
    return checks


def _build_summary(
    request: SwIndustrySnapshotImportRequest,
    source_sha256: str,
    rows: tuple[SwIndustrySourceRow, ...],
    checks: dict[str, str],
    *,
    promoted: bool,
) -> SwIndustrySnapshotImportSummary:
    counts = _coverage_counts(request.formal_db_path, rows)
    count_path = (
        request.formal_db_path
        if promoted or request.mode == "audit-only"
        else request.staging_db_path
    )
    inserted = _current_inserted_count(count_path)
    hard_fail_count = sum(status == "failed" for status in checks.values())
    return SwIndustrySnapshotImportSummary(
        run_id=request.run_id,
        mode=request.mode,
        status="passed" if hard_fail_count == 0 else "failed",
        hard_fail_count=int(hard_fail_count),
        formal_db_path=str(request.formal_db_path),
        staging_db_path=str(request.staging_db_path),
        source_path=str(request.source_path),
        source_sha256=source_sha256,
        source_row_count=len(rows),
        source_a_share_row_count=counts["source_a_share"],
        matched_instrument_count=counts["matched"],
        inserted_industry_rows=inserted,
        unmatched_a_share_count=counts["unmatched_a_share"],
        non_a_share_excluded_count=counts["non_a_share"],
        master_unmatched_count=counts["master_unmatched"],
        checks=checks,
        source_gaps={
            "st_status": "source_gap_retained",
            "suspension_status": "source_gap_retained",
            "listing_delisting_status": "source_gap_retained",
            "industry_history": "source_gap_retained",
        },
        promoted=promoted,
    )


def _coverage_counts(path: Path, rows: tuple[SwIndustrySourceRow, ...]) -> dict[str, int]:
    a_share_codes = {row.stock_code for row in rows if row.exchange == "A股"}
    non_a_share = len(rows) - len(a_share_codes)
    if not path.exists():
        return {
            "source_a_share": len(a_share_codes),
            "matched": 0,
            "unmatched_a_share": len(a_share_codes),
            "non_a_share": non_a_share,
            "master_unmatched": 0,
        }
    with duckdb.connect(str(path), read_only=True) as con:
        master_codes = {
            str(row[0])
            for row in con.execute(
                """
                select instrument_id
                from instrument_master
                where asset_type = 'stock'
                  and exchange_code in ('SH', 'SZ', 'BJ')
                """
            ).fetchall()
        }
    matched = len(a_share_codes.intersection(master_codes))
    return {
        "source_a_share": len(a_share_codes),
        "matched": matched,
        "unmatched_a_share": len(a_share_codes) - matched,
        "non_a_share": non_a_share,
        "master_unmatched": len(master_codes.difference(a_share_codes)),
    }


def _matched_rows(con: duckdb.DuckDBPyConnection, rows: tuple[SwIndustrySourceRow, ...]) -> int:
    a_share_codes = tuple(row.stock_code for row in rows if row.exchange == "A股")
    if not a_share_codes:
        return 0
    placeholders = ", ".join("?" for _ in a_share_codes)
    return _count_result(
        con.execute(
            f"""
            select count(*)
            from instrument_master
            where asset_type = 'stock'
              and exchange_code in ('SH', 'SZ', 'BJ')
              and instrument_id in ({placeholders})
            """,
            list(a_share_codes),
        ).fetchone()
    )


def _industry_row_count(con: duckdb.DuckDBPyConnection) -> int:
    return _count_result(con.execute("select count(*) from industry_classification").fetchone())


def _current_inserted_count(path: Path) -> int:
    if not path.exists():
        return 0
    with duckdb.connect(str(path), read_only=True) as con:
        return _industry_row_count(con)


def _duplicate_stock_codes(rows: tuple[SwIndustrySourceRow, ...]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for row in rows:
        if row.stock_code in seen:
            duplicates.add(row.stock_code)
        seen.add(row.stock_code)
    return duplicates


def _has_failed(checks: dict[str, str]) -> bool:
    return any(status == "failed" for status in checks.values())


def _write_report(
    request: SwIndustrySnapshotImportRequest,
    summary: SwIndustrySnapshotImportSummary,
) -> None:
    request.report_dir.mkdir(parents=True, exist_ok=True)
    (request.report_dir / "audit-summary.json").write_text(
        json.dumps(summary.as_dict(), ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    (request.report_dir / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": request.run_id,
                "source_path": str(request.source_path),
                "source_sha256": summary.source_sha256,
                "effective_date_policy": "inferred_from_file_title_ended_july",
                "schema_version": DATA_SW_INDUSTRY_SCHEMA_VERSION,
            },
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    (request.report_dir / "closeout.md").write_text(
        "\n".join(
            (
                "# Data Market Meta SW Industry Snapshot Closeout",
                "",
                f"run_id: `{request.run_id}`",
                f"status: `{summary.status}`",
                "",
                f"- source rows: {summary.source_row_count}",
                f"- A-share rows: {summary.source_a_share_row_count}",
                f"- matched instruments: {summary.matched_instrument_count}",
                f"- inserted industry rows: {summary.inserted_industry_rows}",
                f"- unmatched A-share rows: {summary.unmatched_a_share_count}",
                f"- non-A-share excluded rows: {summary.non_a_share_excluded_count}",
                "",
                "`effective_date=2021-07-31` is inferred from the source file title.",
                "ST, suspension, listing/delisting, and industry history remain source gaps.",
                "",
            )
        ),
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _count_result(row: tuple[Any, ...] | None) -> int:
    if row is None:
        return 1
    return int(row[0])


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
