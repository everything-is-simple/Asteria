from __future__ import annotations

import json
from pathlib import Path

import duckdb

from asteria.pipeline.contracts import PipelineBuildRequest
from asteria.pipeline.schema import PIPELINE_TABLES


def build_pipeline_audit_rows(
    request: PipelineBuildRequest,
    created_at: object,
    audit_db_path: Path,
) -> tuple[list[list[object]], dict[str, object]]:
    with duckdb.connect(str(audit_db_path), read_only=True) as con:
        run_row = con.execute(
            """
            select module_scope, run_mode, source_release_version, step_count,
                   gate_snapshot_count, manifest_count
            from pipeline_run
            where pipeline_run_id = ?
            """,
            [request.run_id],
        ).fetchone()
        step_modules = con.execute(
            """
            select distinct module_name
            from pipeline_step_run
            where pipeline_run_id = ?
            """,
            [request.run_id],
        ).fetchall()
        step_rows = con.execute(
            """
            select count(*)
            from pipeline_step_run
            where pipeline_run_id = ?
            """,
            [request.run_id],
        ).fetchone()
        gate_names = {
            str(row[0])
            for row in con.execute(
                """
                select gate_name
                from module_gate_snapshot
                where pipeline_run_id = ?
                """,
                [request.run_id],
            ).fetchall()
        }
        manifest_roles = {
            str(row[0])
            for row in con.execute(
                """
                select artifact_role
                from build_manifest
                where pipeline_run_id = ?
                """,
                [request.run_id],
            ).fetchall()
        }
        tables = {
            str(row[0])
            for row in con.execute(
                "select table_name from information_schema.tables where table_schema = 'main'"
            ).fetchall()
        }
    if run_row is None or step_rows is None:
        raise ValueError(f"missing pipeline_run row for audit: {request.run_id}")

    checks = [
        _hard_check(
            request,
            created_at,
            "pipeline_run_mode_authorized",
            run_row[1] in {"bounded", "resume", "audit-only"},
            {"run_mode": run_row[1]},
        ),
        _hard_check(
            request,
            created_at,
            "pipeline_single_module_scope_only",
            run_row[0] == "system_readout"
            and [str(row[0]) for row in step_modules] == ["system_readout"]
            and int(step_rows[0]) == 1,
            {
                "module_scope": run_row[0],
                "step_modules": [str(row[0]) for row in step_modules],
                "step_count": int(step_rows[0]),
            },
        ),
        _hard_check(
            request,
            created_at,
            "pipeline_gate_snapshot_traceability",
            {
                "active_mainline_module",
                "current_allowed_next_card",
                "status",
                "next_card",
                "proof_status",
            }.issubset(gate_names),
            {"gate_names": sorted(gate_names)},
        ),
        _hard_check(
            request,
            created_at,
            "pipeline_manifest_traceability",
            {
                "source_db",
                "target_db",
                "gate_registry",
                "runtime_manifest",
                "step_checkpoint",
            }.issubset(manifest_roles),
            {"artifact_roles": sorted(manifest_roles)},
        ),
        _hard_check(
            request,
            created_at,
            "pipeline_required_checkpoint_present",
            request.step_checkpoint_path(1).exists() and request.runtime_manifest_path.exists(),
            {
                "step_checkpoint": str(request.step_checkpoint_path(1)),
                "runtime_manifest": str(request.runtime_manifest_path),
            },
        ),
        _hard_check(
            request,
            created_at,
            "pipeline_only_allowed_tables_present",
            tables == set(PIPELINE_TABLES),
            {"tables": sorted(tables)},
        ),
        _hard_check(
            request,
            created_at,
            "pipeline_source_release_locked",
            str(run_row[2]) == request.source_chain_release_version,
            {
                "source_release_version": str(run_row[2]),
                "expected_release_version": request.source_chain_release_version,
            },
        ),
    ]
    hard_fail_count = sum(
        _coerce_int(row[5]) for row in checks if row[3] == "hard" and row[4] == "fail"
    )
    payload = {
        "run_id": request.run_id,
        "module_scope": request.module_scope,
        "step_count": int(run_row[3]),
        "gate_snapshot_count": int(run_row[4]),
        "manifest_count": int(run_row[5]),
        "audit_count": len(checks),
        "hard_fail_count": hard_fail_count,
        "checks": [_row_to_payload(row) for row in checks],
    }
    return checks, payload


def _hard_check(
    request: PipelineBuildRequest,
    created_at: object,
    check_name: str,
    passed: bool,
    sample_payload: dict[str, object],
) -> list[object]:
    return [
        f"{request.run_id}|{check_name}",
        request.run_id,
        check_name,
        "hard",
        "pass" if passed else "fail",
        0 if passed else 1,
        json.dumps(sample_payload, ensure_ascii=False, sort_keys=True),
        created_at,
    ]


def _row_to_payload(row: list[object]) -> dict[str, object]:
    return {
        "audit_id": row[0],
        "run_id": row[1],
        "check_name": row[2],
        "severity": row[3],
        "status": row[4],
        "failed_count": row[5],
        "sample_payload": json.loads(str(row[6])),
    }


def _coerce_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"expected int-compatible audit value, got {type(value).__name__}")
    return value
