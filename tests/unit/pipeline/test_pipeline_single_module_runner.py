from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pytest
from tests.unit.pipeline.support import (
    SYSTEM_SOURCE_RUN_ID,
    build_governance_repo,
    build_prepared_pipeline_repo,
    seed_system_source,
)

from asteria.pipeline.bootstrap import (
    run_pipeline_audit,
    run_pipeline_bounded_proof,
    run_pipeline_build,
)
from asteria.pipeline.contracts import PipelineBuildRequest
from asteria.pipeline.schema import PIPELINE_TABLES


def build_request(
    tmp_path: Path,
    *,
    repo_root: Path | None = None,
    mode: str = "bounded",
    module_scope: str = "system_readout",
) -> PipelineBuildRequest:
    return PipelineBuildRequest(
        repo_root=(repo_root or Path(__file__).resolve().parents[3]),
        source_system_db=tmp_path / "data" / "system.duckdb",
        target_pipeline_db=tmp_path / "data" / "pipeline.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="pipeline-single-module-orchestration-unit-001",
        mode=mode,
        module_scope=module_scope,
        source_chain_release_version=SYSTEM_SOURCE_RUN_ID,
    )


def test_request_rejects_out_of_scope_mode_and_module_scope(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsupported Pipeline run mode"):
        build_request(tmp_path, mode="full")
    with pytest.raises(ValueError, match="Unsupported Pipeline module_scope"):
        build_request(tmp_path, module_scope="trade")


def test_build_writes_only_orchestration_metadata_tables(tmp_path: Path) -> None:
    seed_system_source(tmp_path)
    repo_root = build_prepared_pipeline_repo(tmp_path)

    summary = run_pipeline_build(build_request(tmp_path, repo_root=repo_root))

    assert summary.status == "completed"
    assert summary.step_count == 1
    assert summary.gate_snapshot_count >= 6
    assert summary.manifest_count >= 3
    with duckdb.connect(str(tmp_path / "data" / "pipeline.duckdb"), read_only=True) as con:
        tables = {
            row[0]
            for row in con.execute(
                "select table_name from information_schema.tables where table_schema = 'main'"
            ).fetchall()
        }
        step_rows = con.execute(
            """
            select module_name, step_name, step_status
            from pipeline_step_run
            order by step_seq
            """
        ).fetchall()
        gate_names = {
            row[0] for row in con.execute("select gate_name from module_gate_snapshot").fetchall()
        }
        manifest_roles = {
            row[0] for row in con.execute("select artifact_role from build_manifest").fetchall()
        }

    assert tables == set(PIPELINE_TABLES)
    assert step_rows == [("system_readout", "single_module_orchestration", "promoted")]
    assert "current_allowed_next_card" in gate_names
    assert "source_db" in manifest_roles
    assert "target_db" in manifest_roles
    assert "gate_registry" in manifest_roles


def test_audit_hard_fails_when_step_checkpoint_is_missing(tmp_path: Path) -> None:
    seed_system_source(tmp_path)
    request = build_request(tmp_path, repo_root=build_prepared_pipeline_repo(tmp_path))
    run_pipeline_build(request)
    request.step_checkpoint_path(1).unlink()

    summary = run_pipeline_audit(request)

    assert summary.hard_fail_count > 0
    report_payload = json.loads(Path(summary.report_path or "").read_text(encoding="utf-8"))
    failed_checks = {
        row["check_name"]
        for row in report_payload["checks"]
        if row["severity"] == "hard" and row["status"] == "fail"
    }
    assert "pipeline_required_checkpoint_present" in failed_checks


def test_bounded_proof_writes_closeout_and_resume_reuses_checkpoint(tmp_path: Path) -> None:
    seed_system_source(tmp_path)
    repo_root = build_prepared_pipeline_repo(tmp_path)

    summary = run_pipeline_bounded_proof(
        repo_root=repo_root,
        source_system_db=tmp_path / "data" / "system.duckdb",
        target_pipeline_db=tmp_path / "data" / "pipeline.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="pipeline-single-module-orchestration-unit-001",
        source_chain_release_version=SYSTEM_SOURCE_RUN_ID,
        module_scope="system_readout",
    )

    assert summary.hard_fail_count == 0
    assert summary.validated_zip is not None
    assert Path(summary.validated_zip).exists()
    assert Path(summary.manifest_path or "").exists()

    resumed = run_pipeline_build(build_request(tmp_path, repo_root=repo_root, mode="resume"))

    assert resumed.status == "completed"
    assert resumed.resume_reused is True


def test_build_rejects_registry_without_prepared_single_module_gate(tmp_path: Path) -> None:
    seed_system_source(tmp_path)
    repo_root = build_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            'current_allowed_next_card = "pipeline_single_module_orchestration_build_card"',
            'current_allowed_next_card = ""',
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="single-module orchestration build is not currently authorized",
    ):
        run_pipeline_build(build_request(tmp_path, repo_root=repo_root))
