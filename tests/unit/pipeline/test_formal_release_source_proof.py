from __future__ import annotations

import json
from pathlib import Path

import pytest

from asteria.pipeline.formal_release_source_proof import (
    FORMAL_RELEASE_SOURCE_PROOF_CARD,
    FormalReleaseSourceProofRequest,
    run_formal_release_source_proof,
)

RUN_ID = "formal-release-source-proof-unit-001"
NEXT_CARD = "formal_full_rebuild_and_daily_incremental_release_proof_card"


def _write_gate_registry(tmp_path: Path, *, next_card: str = NEXT_CARD) -> Path:
    registry_path = tmp_path / "repo" / "governance" / "module_gate_registry.toml"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(
        "\n".join(
            [
                'registry_version = "test-v1"',
                'active_mainline_module = "system_readout"',
                f'current_allowed_next_card = "{next_card}"',
                "",
                "[[modules]]",
                'module_id = "pipeline"',
                'status = "released"',
                f'next_allowed_action = "{next_card}"',
            ]
        ),
        encoding="utf-8",
    )
    return tmp_path / "repo"


def _request(tmp_path: Path, *, mode: str = "audit-only") -> FormalReleaseSourceProofRequest:
    return FormalReleaseSourceProofRequest(
        repo_root=_write_gate_registry(tmp_path),
        source_root=tmp_path / "source",
        temp_root=tmp_path / "asteria-temp",
        report_root=tmp_path / "asteria-report",
        run_id=RUN_ID,
        mode=mode,
    )


def _write_source_surface(
    source_root: Path,
    name: str,
    *,
    status: str = "passed",
    source_db_root: Path | None = None,
) -> None:
    source_root.mkdir(parents=True, exist_ok=True)
    payload = {
        "proof_scope": name,
        "status": status,
        "source_db_root": str(source_db_root or source_root / "formal-dbs"),
    }
    (source_root / f"{name}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _write_all_source_surfaces(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    db_root = source_root / "formal-dbs"
    db_root.mkdir(parents=True, exist_ok=True)
    for name in (
        "formal-full-rebuild-proof",
        "daily-incremental-release-proof",
        "resume-idempotence-proof",
    ):
        _write_source_surface(source_root, name, source_db_root=db_root)


def test_audit_only_writes_blocker_matrix_without_formal_data_mutation(tmp_path: Path) -> None:
    summary = run_formal_release_source_proof(_request(tmp_path))

    assert summary.card_id == FORMAL_RELEASE_SOURCE_PROOF_CARD
    assert summary.status == "blocked / source surface gaps found"
    assert summary.boundaries["formal_data_mutation"] is False
    assert summary.decisions["formal_full_rebuild_proof"] == "blocked / source proof missing"
    assert Path(summary.source_surface_audit_path).exists()
    assert Path(summary.source_proof_summary_path).exists()
    manifest = json.loads(Path(summary.formal_release_manifest_path).read_text(encoding="utf-8"))
    assert manifest["proof_scope"] == "formal_release"
    assert manifest["full_rebuild_proof"] == "blocked / source proof missing"
    assert (tmp_path / "asteria-data").exists() is False


def test_live_gate_mismatch_rejects_source_proof(tmp_path: Path) -> None:
    repo_root = _write_gate_registry(tmp_path, next_card="pipeline_year_replay_rerun_build_card")
    request = FormalReleaseSourceProofRequest(
        repo_root=repo_root,
        source_root=tmp_path / "source",
        temp_root=tmp_path / "asteria-temp",
        report_root=tmp_path / "asteria-report",
        run_id=RUN_ID,
        mode="source-proof",
    )

    with pytest.raises(ValueError, match="formal release source proof is not currently authorized"):
        run_formal_release_source_proof(request)


@pytest.mark.parametrize(
    ("missing_name", "decision_key"),
    [
        ("formal-full-rebuild-proof", "formal_full_rebuild_proof"),
        ("daily-incremental-release-proof", "daily_incremental_release_proof"),
        ("resume-idempotence-proof", "resume_idempotence_proof"),
    ],
)
def test_missing_required_surface_keeps_manifest_blocked(
    tmp_path: Path,
    missing_name: str,
    decision_key: str,
) -> None:
    _write_all_source_surfaces(tmp_path)
    (tmp_path / "source" / f"{missing_name}.json").unlink()

    summary = run_formal_release_source_proof(_request(tmp_path, mode="source-proof"))

    assert summary.status == "blocked / source surface gaps found"
    assert summary.decisions[decision_key] == "blocked / source proof missing"
    manifest = json.loads(Path(summary.formal_release_manifest_path).read_text(encoding="utf-8"))
    assert manifest[decision_key] == "blocked / source proof missing"
    assert manifest["sample_proof"] is False


def test_source_proof_writes_passed_manifest_when_all_surfaces_pass(tmp_path: Path) -> None:
    _write_all_source_surfaces(tmp_path)

    summary = run_formal_release_source_proof(_request(tmp_path, mode="source-proof"))

    assert summary.status == "passed / source surfaces ready"
    manifest = json.loads(Path(summary.formal_release_manifest_path).read_text(encoding="utf-8"))
    assert manifest["full_rebuild_proof"] == "passed"
    assert manifest["daily_incremental_release_proof"] == "passed"
    assert manifest["resume_idempotence_proof"] == "passed"
    assert manifest["source_db_root"] == str(tmp_path / "source" / "formal-dbs")
    assert summary.boundaries["formal_data_mutation"] is False


def test_resume_reuses_completed_source_proof_checkpoint(tmp_path: Path) -> None:
    _write_all_source_surfaces(tmp_path)
    first = run_formal_release_source_proof(_request(tmp_path, mode="source-proof"))

    resumed = run_formal_release_source_proof(_request(tmp_path, mode="resume"))

    assert first.status == "passed / source surfaces ready"
    assert resumed.status == "passed / source surfaces ready"
    assert resumed.resume_reused is True
    assert resumed.formal_release_manifest_path == first.formal_release_manifest_path
