from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb

from asteria.build_orchestration import (
    BatchLedgerEntry,
    append_batch_ledger,
    write_checkpoint,
    write_manifest,
)
from asteria.build_orchestration.ledger import utc_now_iso
from asteria.pipeline.artifacts import (
    load_completed_checkpoint,
    report_path,
    save_checkpoint,
    utc_now,
    write_pipeline_evidence,
)
from asteria.pipeline.audit_engine import build_pipeline_audit_rows
from asteria.pipeline.contracts import PipelineBuildRequest, PipelineBuildSummary
from asteria.pipeline.runtime_io import load_runtime_inputs
from asteria.pipeline.schema import PIPELINE_TABLES, bootstrap_pipeline_database


def run_pipeline_build(request: PipelineBuildRequest) -> PipelineBuildSummary:
    checkpoint = load_completed_checkpoint(request, "build")
    if checkpoint:
        return checkpoint
    if request.mode == "audit-only":
        return run_pipeline_audit(request)
    if _target_contains_run(request):
        raise ValueError(f"target pipeline.duckdb already contains run_id: {request.run_id}")

    created_at = utc_now()
    runtime_inputs = load_runtime_inputs(request, created_at=created_at)
    staging_db = request.staging_db_path
    if staging_db.exists():
        staging_db.unlink()
    write_manifest(request.runtime_manifest_path, runtime_inputs.manifest)
    _append_step_batch_entries(request, runtime_inputs, status="started")
    bootstrap_pipeline_database(staging_db)
    with duckdb.connect(str(staging_db)) as con:
        con.execute("begin transaction")
        _delete_run(con, request)
        con.executemany(
            """
            insert into pipeline_run
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                [
                    request.run_id,
                    "run_pipeline_record",
                    request.module_scope,
                    request.mode,
                    "staged",
                    runtime_inputs.steps[-1].module_name,
                    request.source_chain_release_version,
                    runtime_inputs.steps[-1].source_db,
                    len(runtime_inputs.step_rows),
                    len(runtime_inputs.gate_rows),
                    len(runtime_inputs.manifest_rows),
                    0,
                    request.schema_version,
                    request.pipeline_version,
                    runtime_inputs.gate_registry_version,
                    created_at,
                ]
            ],
        )
        con.executemany(
            """
            insert into pipeline_step_run
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            runtime_inputs.step_rows,
        )
        con.executemany(
            """
            insert into module_gate_snapshot
            values (?, ?, ?, ?, ?, ?, ?)
            """,
            runtime_inputs.gate_rows,
        )
        con.executemany(
            """
            insert into build_manifest
            values (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            runtime_inputs.manifest_rows,
        )
        con.execute("commit")
    for step in runtime_inputs.steps:
        write_checkpoint(
            request.step_checkpoint_path(step.step_seq),
            {
                "run_id": request.run_id,
                "module_scope": request.module_scope,
                "step_seq": step.step_seq,
                "step_name": step.step_name,
                "step_status": "staged",
                "module_name": step.module_name,
            },
        )

    audit = _run_pipeline_audit_on_db(request, staging_db)
    status = "completed" if audit.hard_fail_count == 0 else "failed"
    if audit.hard_fail_count == 0:
        _promote_staging_db(request, staging_db)
        _mark_steps_promoted(request, runtime_inputs)
    else:
        _append_step_batch_entries(
            request,
            runtime_inputs,
            status="failed",
            audit_summary_path=audit.report_path,
            error="pipeline audit failed",
        )
    summary = PipelineBuildSummary(
        run_id=request.run_id,
        stage="build",
        status=status,
        module_scope=request.module_scope,
        step_count=len(runtime_inputs.step_rows),
        gate_snapshot_count=len(runtime_inputs.gate_rows),
        manifest_count=len(runtime_inputs.manifest_rows),
        audit_count=audit.audit_count,
        hard_fail_count=audit.hard_fail_count,
        report_path=audit.report_path,
    )
    save_checkpoint(request.checkpoint_path("build"), summary)
    return summary


def run_pipeline_audit(request: PipelineBuildRequest) -> PipelineBuildSummary:
    return _run_pipeline_audit_on_db(request, request.target_pipeline_db)


def run_pipeline_bounded_proof(
    *,
    repo_root: Path,
    source_system_db: Path,
    target_pipeline_db: Path,
    report_root: Path,
    validated_root: Path,
    temp_root: Path,
    run_id: str,
    source_chain_release_version: str,
    module_scope: str = "system_readout",
    mode: str = "bounded",
) -> PipelineBuildSummary:
    request = PipelineBuildRequest(
        repo_root=repo_root,
        source_system_db=source_system_db,
        target_pipeline_db=target_pipeline_db,
        report_root=report_root,
        validated_root=validated_root,
        temp_root=temp_root,
        run_id=run_id,
        mode=mode,
        source_chain_release_version=source_chain_release_version,
        module_scope=module_scope,
    )
    summary = run_pipeline_build(request)
    evidence = write_pipeline_evidence(request, summary)
    return PipelineBuildSummary(**{**summary.as_dict(), **evidence})


def run_pipeline_full_chain_dry_run(
    *,
    repo_root: Path,
    source_system_db: Path,
    target_pipeline_db: Path,
    report_root: Path,
    validated_root: Path,
    temp_root: Path,
    run_id: str,
    source_chain_release_version: str,
    mode: str = "dry-run",
) -> PipelineBuildSummary:
    request = PipelineBuildRequest(
        repo_root=repo_root,
        source_system_db=source_system_db,
        target_pipeline_db=target_pipeline_db,
        report_root=report_root,
        validated_root=validated_root,
        temp_root=temp_root,
        run_id=run_id,
        mode=mode,
        source_chain_release_version=source_chain_release_version,
        module_scope="full_chain_day",
    )
    summary = run_pipeline_build(request)
    evidence = write_pipeline_evidence(request, summary)
    return PipelineBuildSummary(**{**summary.as_dict(), **evidence})


def _run_pipeline_audit_on_db(
    request: PipelineBuildRequest,
    audit_db_path: Path,
) -> PipelineBuildSummary:
    bootstrap_pipeline_database(audit_db_path)
    created_at = utc_now()
    audit_rows, payload = build_pipeline_audit_rows(request, created_at, audit_db_path)
    with duckdb.connect(str(audit_db_path)) as con:
        con.execute("begin transaction")
        con.execute("delete from pipeline_audit where run_id = ?", [request.run_id])
        con.executemany(
            "insert into pipeline_audit values (?, ?, ?, ?, ?, ?, ?, ?)",
            audit_rows,
        )
        con.execute(
            """
            update pipeline_run
            set audit_count = ?, run_status = ?
            where pipeline_run_id = ?
            """,
            [
                len(audit_rows),
                "completed" if _payload_int(payload, "hard_fail_count") == 0 else "failed",
                request.run_id,
            ],
        )
        con.execute("commit")
    audit_report_path = write_audit_report(request, payload)
    summary = PipelineBuildSummary(
        run_id=request.run_id,
        stage="audit",
        status="completed" if _payload_int(payload, "hard_fail_count") == 0 else "failed",
        module_scope=request.module_scope,
        step_count=_payload_int(payload, "step_count"),
        gate_snapshot_count=_payload_int(payload, "gate_snapshot_count"),
        manifest_count=_payload_int(payload, "manifest_count"),
        audit_count=_payload_int(payload, "audit_count"),
        hard_fail_count=_payload_int(payload, "hard_fail_count"),
        report_path=str(audit_report_path),
    )
    save_checkpoint(request.checkpoint_path("audit"), summary)
    return summary


def write_audit_report(request: PipelineBuildRequest, payload: dict[str, object]) -> Path:
    path = report_path(request.report_root, request.run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _delete_run(con: duckdb.DuckDBPyConnection, request: PipelineBuildRequest) -> None:
    con.execute("delete from pipeline_audit where run_id = ?", [request.run_id])
    con.execute("delete from build_manifest where pipeline_run_id = ?", [request.run_id])
    con.execute("delete from module_gate_snapshot where pipeline_run_id = ?", [request.run_id])
    con.execute("delete from pipeline_step_run where pipeline_run_id = ?", [request.run_id])
    con.execute("delete from pipeline_run where pipeline_run_id = ?", [request.run_id])


def _mark_steps_promoted(
    request: PipelineBuildRequest,
    runtime_inputs: Any,
) -> None:
    _append_step_batch_entries(
        request,
        runtime_inputs,
        status="promoted",
        row_counts={
            "pipeline_step_run": len(runtime_inputs.steps),
            "module_gate_snapshot": len(runtime_inputs.gate_rows),
        },
    )
    for step in runtime_inputs.steps:
        write_checkpoint(
            request.step_checkpoint_path(step.step_seq),
            {
                "run_id": request.run_id,
                "module_scope": request.module_scope,
                "step_seq": step.step_seq,
                "step_name": step.step_name,
                "step_status": "promoted",
                "module_name": step.module_name,
            },
        )
    with duckdb.connect(str(request.target_pipeline_db)) as con:
        con.execute(
            """
            update pipeline_step_run
            set step_status = ?, completed_at = ?
            where pipeline_run_id = ?
            """,
            ["promoted", utc_now(), request.run_id],
        )


def _promote_staging_db(request: PipelineBuildRequest, staging_db: Path) -> None:
    if _target_contains_run(request):
        raise ValueError(f"target pipeline.duckdb already contains run_id: {request.run_id}")
    request.target_pipeline_db.parent.mkdir(parents=True, exist_ok=True)
    if request.target_pipeline_db.exists():
        bootstrap_pipeline_database(request.target_pipeline_db)
        with duckdb.connect(str(request.target_pipeline_db)) as con:
            con.execute(f"attach '{staging_db.as_posix()}' as staging_db")
            for table_name in PIPELINE_TABLES:
                con.execute(f"insert into {table_name} select * from staging_db.{table_name}")
            con.execute("detach staging_db")
        staging_db.unlink()
        return
    staging_db.rename(request.target_pipeline_db)


def _append_step_batch_entries(
    request: PipelineBuildRequest,
    runtime_inputs: Any,
    *,
    status: str,
    audit_summary_path: str | None = None,
    error: str | None = None,
    row_counts: dict[str, int] | None = None,
) -> None:
    for step in runtime_inputs.steps:
        append_batch_ledger(
            request.batch_ledger_path,
            BatchLedgerEntry(
                run_id=request.run_id,
                batch_id=step.batch_id,
                status=status,
                started_at=utc_now_iso() if status == "started" else None,
                completed_at=utc_now_iso() if status != "started" else None,
                promoted_at=utc_now_iso() if status == "promoted" else None,
                audit_summary_path=audit_summary_path,
                error=error,
                row_counts=row_counts if status == "promoted" else None,
            ),
        )


def _payload_int(payload: dict[str, object], key: str) -> int:
    value = payload[key]
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"expected integer payload for {key}, got {type(value).__name__}")
    return value


def _target_contains_run(request: PipelineBuildRequest) -> bool:
    if not request.target_pipeline_db.exists():
        return False
    with duckdb.connect(str(request.target_pipeline_db), read_only=True) as con:
        tables = {
            str(row[0])
            for row in con.execute(
                "select table_name from information_schema.tables where table_schema = 'main'"
            ).fetchall()
        }
        if "pipeline_run" not in tables:
            return False
        row = con.execute(
            "select count(*) from pipeline_run where pipeline_run_id = ?",
            [request.run_id],
        ).fetchone()
    return False if row is None else int(row[0]) > 0
