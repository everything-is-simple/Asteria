from pathlib import Path
from shutil import copy2, copytree

from scripts.governance.check_project_governance import run_checks
from tests.unit.pipeline.support import (
    PIPELINE_CURRENT_DOC_STATUS,
    PIPELINE_DRY_RUN_CARD_ACTION,
)

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


def _copy_governance_repo(tmp_path: Path) -> Path:
    source_root = Path(__file__).resolve().parents[3]
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    for file_name in ["README.md", "AGENTS.md", "pyproject.toml"]:
        copy2(source_root / file_name, repo_root / file_name)
    for directory_name in ["docs", "governance"]:
        copytree(source_root / directory_name, repo_root / directory_name)
    scripts_governance = repo_root / "scripts" / "governance"
    scripts_governance.mkdir(parents=True)
    copy2(
        source_root / "scripts" / "governance" / "check_project_governance.py",
        scripts_governance / "check_project_governance.py",
    )
    return repo_root


def _messages(repo_root: Path) -> list[str]:
    return [finding.message for finding in run_checks(repo_root)]


def test_pipeline_scope_freeze_preserves_historical_scope_after_runtime_pass() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    modules = {module["module_id"]: module for module in registry["modules"]}
    conclusion_index = (
        repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    ).read_text(encoding="utf-8")
    pipeline_scope_conclusion = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / "pipeline-build-runtime-authorization-scope-freeze-20260508-01.conclusion.md"
    ).read_text(encoding="utf-8")
    pipeline_scope_evidence = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / "pipeline-build-runtime-authorization-scope-freeze-20260508-01.evidence-index.md"
    ).read_text(encoding="utf-8")
    pipeline_runtime_card = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / "pipeline-single-module-orchestration-build-card-20260508-01.card.md"
    ).read_text(encoding="utf-8")
    pipeline_runtime_conclusion = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / "pipeline-single-module-orchestration-build-card-20260508-01.conclusion.md"
    ).read_text(encoding="utf-8")

    assert registry["active_mainline_module"] == "system_readout"
    assert registry["active_foundation_card"] == "none"
    assert registry["current_allowed_next_card"] == PIPELINE_DRY_RUN_CARD_ACTION
    assert registry["latest_mainline_release_run_id"] == (
        "system-readout-bounded-proof-build-card-20260508-01"
    )
    assert modules["system_readout"]["allow_build"] is False
    assert modules["system_readout"]["allow_review"] is False
    assert modules["system_readout"]["status"] == "released"
    assert modules["system_readout"]["proof_status"] == (
        "bounded_proof_passed; full_build_not_executed"
    )
    assert modules["system_readout"]["next_card"] == "pipeline_freeze_review"
    assert modules["pipeline"]["status"] == "released"
    assert modules["pipeline"]["doc_status"] == PIPELINE_CURRENT_DOC_STATUS
    assert modules["pipeline"]["formal_db_permission"] == (
        "released_single_module_orchestration_ledger_only; "
        "full_chain_dry_run_prepared_not_executed; bounded_proof_requires_new_card"
    )
    assert modules["pipeline"]["next_card"] == PIPELINE_DRY_RUN_CARD_ACTION
    assert "pipeline-build-runtime-authorization-scope-freeze-20260508-01" in conclusion_index
    assert (
        "| Pipeline | `pipeline-build-runtime-authorization-scope-freeze-20260508-01` | "
        "`passed / scope frozen` |" in conclusion_index
    )
    assert "pipeline-single-module-orchestration-build-card-20260508-01" in conclusion_index
    assert "状态：`passed`" in pipeline_scope_conclusion
    assert "single-module orchestration build prepared" in pipeline_scope_conclusion
    assert (
        "| allowed next action | `pipeline_single_module_orchestration_build_card` |"
        in pipeline_scope_conclusion
    )
    assert (
        "[next prepared card](pipeline-single-module-orchestration-build-card-20260508-01.card.md)"
        in pipeline_scope_conclusion
    )
    assert "pipeline-single-module-orchestration-build-card-20260508-01" in pipeline_scope_evidence
    assert "状态：`passed`" in pipeline_runtime_card
    assert "状态：`passed`" in pipeline_runtime_conclusion


def test_project_governance_rejects_pipeline_current_next_without_pipeline_match(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            f'current_allowed_next_card = "{PIPELINE_DRY_RUN_CARD_ACTION}"',
            'current_allowed_next_card = "pipeline_build_runtime_authorization_scope_freeze"',
        ).replace(
            f'next_card = "{PIPELINE_DRY_RUN_CARD_ACTION}"',
            'next_card = "pipeline_build_runtime_authorization_scope_freeze"',
        ),
        encoding="utf-8",
    )

    assert any(
        "current allowed next card must not point to a closed execution conclusion" in message
        for message in _messages(repo_root)
    )
