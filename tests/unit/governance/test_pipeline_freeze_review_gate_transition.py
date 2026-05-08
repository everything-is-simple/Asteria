from pathlib import Path
from shutil import copy2, copytree

from scripts.governance.check_project_governance import run_checks

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


def test_pipeline_scope_freeze_reopens_single_module_prepared_card() -> None:
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
    pipeline_prepared_card = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / "pipeline-single-module-orchestration-build-card-20260508-01.card.md"
    ).read_text(encoding="utf-8")

    assert registry["active_mainline_module"] == "system_readout"
    assert registry["active_foundation_card"] == "none"
    assert registry["current_allowed_next_card"] == (
        "pipeline_single_module_orchestration_build_card"
    )
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
    assert modules["pipeline"]["status"] == "freeze_review_passed"
    assert modules["pipeline"]["doc_status"] == (
        "frozen six-doc set / freeze review passed / "
        "single-module orchestration build prepared / build not executed"
    )
    assert modules["pipeline"]["formal_db_permission"] == (
        "freeze_review_passed_but_pipeline_db_not_released; "
        "single_module_orchestration_build_card_only"
    )
    assert modules["pipeline"]["next_card"] == ("pipeline_single_module_orchestration_build_card")
    assert "pipeline-build-runtime-authorization-scope-freeze-20260508-01" in conclusion_index
    assert (
        "| Pipeline | `pipeline-build-runtime-authorization-scope-freeze-20260508-01` | "
        "`passed / scope frozen` |" in conclusion_index
    )
    assert "当前已准备但未执行的下一卡" in conclusion_index
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
    assert "状态：`prepared / not executed`" in pipeline_prepared_card


def test_project_governance_rejects_pipeline_current_next_without_pipeline_match(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            'next_card = "pipeline_single_module_orchestration_build_card"',
            'next_card = "none"',
            1,
        ),
        encoding="utf-8",
    )

    assert any(
        "current_allowed_next_card must match active module next_card" in message
        for message in _messages(repo_root)
    )
