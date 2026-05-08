from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb

from asteria.system_readout.contracts import SystemReadoutBuildRequest
from asteria.system_readout.schema import SYSTEM_READOUT_TABLES

FORBIDDEN_COLUMNS = {
    "fill_id",
    "fill_price",
    "fill_quantity",
    "execution_price",
    "order_intent_state",
    "target_weight",
    "business_mutation",
}


@dataclass(frozen=True)
class SystemReadoutAuditCheck:
    check_name: str
    severity: str
    status: str
    failed_count: int
    sample_payload: str


def build_system_readout_audit_rows(
    request: SystemReadoutBuildRequest,
    created_at: datetime,
    audit_db_path: Path,
) -> tuple[list[tuple[object, ...]], dict[str, Any]]:
    checks: list[SystemReadoutAuditCheck] = []
    query_specs: list[tuple[str, str, list[object] | None]] = [
        (
            "system_readout_run_row_present",
            "select case when count(*) = 1 then 0 else 1 end "
            "from system_readout_run where run_id = ?",
            [request.run_id],
        ),
        (
            "system_source_manifest_trace_count",
            "select case when count(*) >= 6 then 0 else 1 end "
            "from system_source_manifest where system_readout_run_id = ?",
            [request.run_id],
        ),
        (
            "system_chain_readout_natural_key_unique",
            "select count(*) from ("
            "select symbol, timeframe, readout_dt, system_readout_version, count(*) row_count "
            "from system_chain_readout group by 1,2,3,4 having row_count > 1"
            ")",
            None,
        ),
        (
            "system_summary_snapshot_natural_key_unique",
            "select count(*) from ("
            "select summary_scope, summary_dt, system_readout_version, count(*) row_count "
            "from system_summary_snapshot group by 1,2,3 having row_count > 1"
            ")",
            None,
        ),
        (
            "system_audit_snapshot_natural_key_unique",
            "select count(*) from ("
            "select audit_scope, audit_dt, module_name, system_readout_version, count(*) row_count "
            "from system_audit_snapshot group by 1,2,3,4 having row_count > 1"
            ")",
            None,
        ),
        (
            "source_audit_status_all_pass",
            "select count(*) from system_source_manifest where source_audit_status <> 'pass'",
            None,
        ),
        (
            "merged_wave_core_state_and_system_state_absent",
            "select count(*) from system_chain_readout "
            "where wave_core_state is not null and system_state is not null "
            "and wave_core_state = system_state",
            None,
        ),
        (
            "source_gap_rows_marked_explicitly",
            "select count(*) from system_chain_readout "
            "where alpha_ref is null and signal_ref is not null "
            "and readout_status <> 'source_gap'",
            None,
        ),
    ]
    with duckdb.connect(str(audit_db_path), read_only=True) as con:
        checks.append(_table_presence_check(con))
        for check_name, sql, params in query_specs:
            checks.append(_query_check(con, check_name, sql, params))
        checks.append(_forbidden_columns_check(con))
        counts = {
            "source_manifest_count": _scalar(con, "select count(*) from system_source_manifest"),
            "module_status_count": _scalar(
                con,
                "select count(*) from system_module_status_snapshot",
            ),
            "readout_count": _scalar(con, "select count(*) from system_chain_readout"),
            "summary_count": _scalar(con, "select count(*) from system_summary_snapshot"),
            "audit_snapshot_count": _scalar(con, "select count(*) from system_audit_snapshot"),
        }
    hard_fail_count = sum(check.failed_count for check in checks if check.severity == "hard")
    rows = [_row(request.run_id, created_at, check) for check in checks]
    payload = {
        "run_id": request.run_id,
        "timeframe": request.timeframe,
        "hard_fail_count": hard_fail_count,
        "checks": [
            {
                "check_name": check.check_name,
                "severity": check.severity,
                "status": check.status,
                "failed_count": check.failed_count,
                "sample_payload": check.sample_payload,
            }
            for check in checks
        ],
        **counts,
    }
    return rows, payload


def _table_presence_check(con: duckdb.DuckDBPyConnection) -> SystemReadoutAuditCheck:
    tables = {
        str(row[0])
        for row in con.execute(
            "select table_name from information_schema.tables where table_schema = 'main'"
        ).fetchall()
    }
    missing = sorted(set(SYSTEM_READOUT_TABLES) - tables)
    payload = {"missing": missing, "present": sorted(tables & set(SYSTEM_READOUT_TABLES))}
    return SystemReadoutAuditCheck(
        check_name="system_readout_table_surface_present",
        severity="hard",
        status="pass" if not missing else "fail",
        failed_count=len(missing),
        sample_payload=json.dumps(payload, ensure_ascii=False),
    )


def _forbidden_columns_check(con: duckdb.DuckDBPyConnection) -> SystemReadoutAuditCheck:
    rows: list[str] = []
    for table in (
        "system_chain_readout",
        "system_summary_snapshot",
        "system_audit_snapshot",
    ):
        for row in con.execute(f"describe {table}").fetchall():
            if row[0] in FORBIDDEN_COLUMNS:
                rows.append(f"{table}.{row[0]}")
    return SystemReadoutAuditCheck(
        check_name="system_readout_forbidden_columns_absent",
        severity="hard",
        status="pass" if not rows else "fail",
        failed_count=len(rows),
        sample_payload=json.dumps({"forbidden_columns": rows}, ensure_ascii=False),
    )


def _query_check(
    con: duckdb.DuckDBPyConnection,
    check_name: str,
    sql: str,
    params: list[object] | None = None,
) -> SystemReadoutAuditCheck:
    row = con.execute(sql, params or []).fetchone()
    failed_count = 0 if row is None else int(row[0])
    return SystemReadoutAuditCheck(
        check_name=check_name,
        severity="hard",
        status="pass" if failed_count == 0 else "fail",
        failed_count=failed_count,
        sample_payload="{}",
    )


def _scalar(con: duckdb.DuckDBPyConnection, sql: str) -> int:
    row = con.execute(sql).fetchone()
    return 0 if row is None else int(row[0])


def _row(
    run_id: str,
    created_at: datetime,
    check: SystemReadoutAuditCheck,
) -> tuple[object, ...]:
    return (
        f"{run_id}|day|{check.check_name}",
        run_id,
        check.check_name,
        check.severity,
        check.status,
        check.failed_count,
        check.sample_payload,
        created_at,
    )
