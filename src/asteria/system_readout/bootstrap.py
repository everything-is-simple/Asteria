from __future__ import annotations

import json
from pathlib import Path

import duckdb

from asteria.system_readout.artifacts import (
    load_completed_checkpoint,
    report_path,
    save_checkpoint,
    utc_now,
    write_bounded_proof_evidence,
)
from asteria.system_readout.audit_engine import build_system_readout_audit_rows
from asteria.system_readout.contracts import (
    SYSTEM_READOUT_SCHEMA_VERSION,
    SYSTEM_READOUT_VERSION,
    SystemReadoutBuildRequest,
    SystemReadoutBuildSummary,
)
from asteria.system_readout.rules import build_system_readout_rows
from asteria.system_readout.runtime_io import load_chain_inputs
from asteria.system_readout.schema import bootstrap_system_readout_database


def run_system_readout_build(
    request: SystemReadoutBuildRequest,
) -> SystemReadoutBuildSummary:
    checkpoint = load_completed_checkpoint(request, "build")
    if checkpoint:
        return checkpoint
    if request.mode == "audit-only":
        return run_system_readout_audit(request)
    if _target_contains_run(request):
        raise ValueError(f"target system.duckdb already contains run_id: {request.run_id}")

    source_manifests, module_statuses, readouts = load_chain_inputs(request)
    created_at = utc_now()
    built = build_system_readout_rows(
        source_manifests=source_manifests,
        module_statuses=module_statuses,
        readouts=readouts,
        request=request,
        created_at=created_at,
    )
    staging_db = request.staging_db_path
    if staging_db.exists():
        staging_db.unlink()
    bootstrap_system_readout_database(staging_db)
    with duckdb.connect(str(staging_db)) as con:
        con.execute("begin transaction")
        _delete_run(con, request)
        con.execute(
            "delete from system_schema_version where schema_version = ?",
            [request.schema_version],
        )
        con.execute(
            "delete from system_readout_version where system_readout_version = ?",
            [request.system_readout_version],
        )
        con.execute(
            "insert into system_schema_version values (?, ?)",
            [request.schema_version, created_at],
        )
        con.execute(
            "insert into system_readout_version values (?, ?, ?)",
            [request.system_readout_version, request.timeframe, created_at],
        )
        con.executemany(
            "insert into system_source_manifest values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            built.source_manifests,
        )
        con.executemany(
            "insert into system_module_status_snapshot values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            built.module_statuses,
        )
        con.executemany(
            (
                "insert into system_chain_readout "
                "values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            ),
            built.chain_readouts,
        )
        con.executemany(
            "insert into system_summary_snapshot values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            built.summary_snapshots,
        )
        con.executemany(
            "insert into system_audit_snapshot values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            built.audit_snapshots,
        )
        con.execute(
            """
            insert into system_readout_run
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                request.run_id,
                "system_readout_build",
                request.mode,
                request.timeframe,
                "staged",
                request.source_chain_release_version,
                len(built.source_manifests),
                len(built.module_statuses),
                len(built.chain_readouts),
                len(built.summary_snapshots),
                len(built.audit_snapshots),
                0,
                request.schema_version,
                request.system_readout_version,
                created_at,
            ],
        )
        con.execute("commit")

    audit = _run_system_readout_audit_on_db(request, staging_db)
    status = "completed" if audit.hard_fail_count == 0 else "failed"
    if audit.hard_fail_count == 0:
        _promote_staging_db(request, staging_db)
    summary = SystemReadoutBuildSummary(
        run_id=request.run_id,
        stage="build",
        status=status,
        timeframe=request.timeframe,
        source_manifest_count=len(built.source_manifests),
        module_status_count=len(built.module_statuses),
        readout_count=len(built.chain_readouts),
        summary_count=len(built.summary_snapshots),
        audit_snapshot_count=len(built.audit_snapshots),
        hard_fail_count=audit.hard_fail_count,
        report_path=audit.report_path,
    )
    save_checkpoint(request.checkpoint_path("build"), summary)
    return summary


def run_system_readout_audit(
    request: SystemReadoutBuildRequest,
) -> SystemReadoutBuildSummary:
    return _run_system_readout_audit_on_db(request, request.target_system_db)


def run_system_readout_bounded_proof(
    source_malf_service_db: Path,
    source_alpha_root: Path,
    source_signal_db: Path,
    source_position_db: Path,
    source_portfolio_plan_db: Path,
    source_trade_db: Path,
    target_system_db: Path,
    report_root: Path,
    validated_root: Path,
    temp_root: Path,
    run_id: str,
    source_chain_release_version: str,
    start_dt: str | None,
    end_dt: str | None,
    symbol_limit: int | None,
    schema_version: str = SYSTEM_READOUT_SCHEMA_VERSION,
    system_readout_version: str = SYSTEM_READOUT_VERSION,
    mode: str = "bounded",
) -> SystemReadoutBuildSummary:
    request = SystemReadoutBuildRequest(
        source_malf_service_db=source_malf_service_db,
        source_alpha_root=source_alpha_root,
        source_signal_db=source_signal_db,
        source_position_db=source_position_db,
        source_portfolio_plan_db=source_portfolio_plan_db,
        source_trade_db=source_trade_db,
        target_system_db=target_system_db,
        report_root=report_root,
        validated_root=validated_root,
        temp_root=temp_root,
        run_id=run_id,
        mode=mode,
        source_chain_release_version=source_chain_release_version,
        schema_version=schema_version,
        system_readout_version=system_readout_version,
        start_dt=start_dt,
        end_dt=end_dt,
        symbol_limit=symbol_limit,
    )
    summary = run_system_readout_build(request)
    evidence = write_bounded_proof_evidence(request, summary)
    return SystemReadoutBuildSummary(**{**summary.as_dict(), **evidence})


def _run_system_readout_audit_on_db(
    request: SystemReadoutBuildRequest,
    audit_db_path: Path,
) -> SystemReadoutBuildSummary:
    bootstrap_system_readout_database(audit_db_path)
    created_at = utc_now()
    audit_rows, payload = build_system_readout_audit_rows(request, created_at, audit_db_path)
    with duckdb.connect(str(audit_db_path)) as con:
        con.execute("begin transaction")
        con.execute(
            "delete from system_readout_audit where audit_id like ?",
            [f"{request.run_id}|{request.timeframe}|%"],
        )
        con.executemany(
            "insert into system_readout_audit values (?, ?, ?, ?, ?, ?, ?, ?)",
            audit_rows,
        )
        con.execute(
            """
            update system_readout_run
            set hard_fail_count = ?, status = ?
            where run_id = ?
            """,
            [
                payload["hard_fail_count"],
                "completed" if payload["hard_fail_count"] == 0 else "failed",
                request.run_id,
            ],
        )
        con.execute("commit")

    report_path = write_audit_report(request, payload)
    summary = SystemReadoutBuildSummary(
        run_id=request.run_id,
        stage="audit",
        status="completed" if payload["hard_fail_count"] == 0 else "failed",
        timeframe=request.timeframe,
        source_manifest_count=int(payload["source_manifest_count"]),
        module_status_count=int(payload["module_status_count"]),
        readout_count=int(payload["readout_count"]),
        summary_count=int(payload["summary_count"]),
        audit_snapshot_count=int(payload["audit_snapshot_count"]),
        hard_fail_count=int(payload["hard_fail_count"]),
        report_path=str(report_path),
    )
    save_checkpoint(request.checkpoint_path("audit"), summary)
    return summary


def write_audit_report(
    request: SystemReadoutBuildRequest,
    payload: dict[str, object],
) -> Path:
    path = report_path(request.report_root, request.run_id, request.timeframe)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _delete_run(con: duckdb.DuckDBPyConnection, request: SystemReadoutBuildRequest) -> None:
    con.execute("delete from system_readout_audit where run_id = ?", [request.run_id])
    con.execute(
        "delete from system_audit_snapshot where system_readout_run_id = ?",
        [request.run_id],
    )
    con.execute(
        "delete from system_summary_snapshot where system_readout_run_id = ?",
        [request.run_id],
    )
    con.execute(
        "delete from system_chain_readout where system_readout_run_id = ?",
        [request.run_id],
    )
    con.execute(
        "delete from system_module_status_snapshot where system_readout_run_id = ?",
        [request.run_id],
    )
    con.execute(
        "delete from system_source_manifest where system_readout_run_id = ?",
        [request.run_id],
    )
    con.execute("delete from system_readout_run where run_id = ?", [request.run_id])


def _promote_staging_db(request: SystemReadoutBuildRequest, staging_db: Path) -> None:
    if _target_contains_run(request):
        raise ValueError(f"target system.duckdb already contains run_id: {request.run_id}")
    request.target_system_db.parent.mkdir(parents=True, exist_ok=True)
    if request.target_system_db.exists():
        staging_db.replace(request.target_system_db)
        return
    staging_db.rename(request.target_system_db)


def _target_contains_run(request: SystemReadoutBuildRequest) -> bool:
    if not request.target_system_db.exists():
        return False
    with duckdb.connect(str(request.target_system_db), read_only=True) as con:
        tables = {
            str(row[0])
            for row in con.execute(
                "select table_name from information_schema.tables where table_schema = 'main'"
            ).fetchall()
        }
        if "system_readout_run" not in tables:
            return False
        row = con.execute(
            "select count(*) from system_readout_run where run_id = ?",
            [request.run_id],
        ).fetchone()
    return False if row is None else int(row[0]) > 0
