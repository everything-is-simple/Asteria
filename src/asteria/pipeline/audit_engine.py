from __future__ import annotations

import json
from pathlib import Path

import duckdb

from asteria.pipeline.contracts import FULL_CHAIN_DAY_MODULES, PipelineBuildRequest
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
        step_modules = [
            str(row[0])
            for row in con.execute(
                """
                select module_name
                from pipeline_step_run
                where pipeline_run_id = ?
                order by step_seq
                """,
                [request.run_id],
            ).fetchall()
        ]
        step_rows = con.execute(
            """
            select count(*)
            from pipeline_step_run
            where pipeline_run_id = ?
            """,
            [request.run_id],
        ).fetchone()
        gate_pairs = {
            (str(row[0]), str(row[1]))
            for row in con.execute(
                """
                select module_name, gate_name
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
            _run_mode_authorized(str(run_row[0]), str(run_row[1])),
            {"module_scope": run_row[0], "run_mode": run_row[1]},
        ),
        _hard_check(
            request,
            created_at,
            "pipeline_scope_shape_authorized",
            _scope_shape_authorized(str(run_row[0]), step_modules, int(step_rows[0])),
            {
                "module_scope": run_row[0],
                "step_modules": step_modules,
                "step_count": int(step_rows[0]),
            },
        ),
        _hard_check(
            request,
            created_at,
            "pipeline_gate_snapshot_traceability",
            _gate_snapshot_traceability_ok(str(run_row[0]), gate_pairs),
            {"gate_pairs": sorted(f"{name}:{gate}" for name, gate in gate_pairs)},
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
            _required_checkpoints_present(request, str(run_row[0])),
            {
                "runtime_manifest": str(request.runtime_manifest_path),
                "module_scope": str(run_row[0]),
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
    if request.module_scope == "year_replay":
        checks.append(
            _hard_check(
                request,
                created_at,
                "pipeline_year_replay_full_year_coverage",
                _year_replay_full_year_coverage_ok(request),
                {
                    "target_year": request.target_year,
                    "required_start": f"{request.target_year}-01-01",
                    "required_end": f"{request.target_year}-12-31",
                },
            )
        )
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


def _run_mode_authorized(module_scope: str, run_mode: str) -> bool:
    if module_scope == "system_readout":
        return run_mode in {"bounded", "resume", "audit-only"}
    if module_scope == "full_chain_day":
        return run_mode in {"bounded", "dry-run", "resume", "audit-only"}
    if module_scope == "year_replay":
        return run_mode in {"bounded", "resume", "audit-only"}
    return False


def _scope_shape_authorized(
    module_scope: str,
    step_modules: list[str],
    step_count: int,
) -> bool:
    if module_scope == "system_readout":
        return step_modules == ["system_readout"] and step_count == 1
    if module_scope in {"full_chain_day", "year_replay"}:
        return step_modules == list(FULL_CHAIN_DAY_MODULES) and step_count == len(
            FULL_CHAIN_DAY_MODULES
        )
    return False


def _gate_snapshot_traceability_ok(
    module_scope: str,
    gate_pairs: set[tuple[str, str]],
) -> bool:
    required = {
        ("registry", "active_mainline_module"),
        ("registry", "current_allowed_next_card"),
        ("pipeline", "status"),
        ("pipeline", "next_card"),
    }
    if module_scope == "system_readout":
        required |= {
            ("system_readout", "proof_status"),
            ("system_readout", "next_card"),
        }
    elif module_scope in {"full_chain_day", "year_replay"}:
        required |= {(module_name, "proof_status") for module_name in FULL_CHAIN_DAY_MODULES}
    return required.issubset(gate_pairs)


def _required_checkpoints_present(request: PipelineBuildRequest, module_scope: str) -> bool:
    step_count = 1 if module_scope == "system_readout" else len(FULL_CHAIN_DAY_MODULES)
    return request.runtime_manifest_path.exists() and all(
        request.step_checkpoint_path(step_seq).exists() for step_seq in range(1, step_count + 1)
    )


def _year_replay_full_year_coverage_ok(request: PipelineBuildRequest) -> bool:
    if request.target_year is None:
        return False
    with duckdb.connect(str(request.source_system_db), read_only=True) as con:
        row = con.execute(
            """
            select min(readout_dt), max(readout_dt)
            from system_chain_readout
            where system_readout_run_id = ?
              and readout_dt >= ?
              and readout_dt <= ?
            """,
            [
                request.source_chain_release_version,
                f"{request.target_year}-01-01",
                f"{request.target_year}-12-31",
            ],
        ).fetchone()
    if row is None or row[0] is None or row[1] is None:
        return False
    return (
        str(row[0]) == f"{request.target_year}-01-01"
        and str(row[1]) == f"{request.target_year}-12-31"
    )


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
