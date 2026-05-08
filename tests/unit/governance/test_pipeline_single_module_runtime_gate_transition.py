from pathlib import Path
from shutil import copy2, copytree

from scripts.governance.check_project_governance import run_checks
from tests.unit.pipeline.support import (
    PIPELINE_CURRENT_DOC_STATUS,
    PIPELINE_DRY_RUN_CARD_ACTION,
    PIPELINE_DRY_RUN_CARD_RUN_ID,
    PIPELINE_DRY_RUN_SCOPE_FREEZE_RUN_ID,
    PIPELINE_PREPARED_DOC_STATUS,
    PIPELINE_RUN_ID,
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
    for directory_name in ["docs", "governance", "scripts"]:
        copytree(source_root / directory_name, repo_root / directory_name)
    return repo_root


def _messages(repo_root: Path) -> list[str]:
    return [finding.message for finding in run_checks(repo_root)]


def test_pipeline_dry_run_scope_freeze_prepares_next_card_after_single_module_pass() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    modules = {module["module_id"]: module for module in registry["modules"]}
    conclusion_index = (
        repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    ).read_text(encoding="utf-8")
    pipeline_runtime_conclusion = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / "pipeline-single-module-orchestration-build-card-20260508-01.conclusion.md"
    ).read_text(encoding="utf-8")
    pipeline_scope_conclusion = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / "pipeline-full-chain-dry-run-authorization-scope-freeze-20260508-01.conclusion.md"
    ).read_text(encoding="utf-8")
    pipeline_dry_run_card = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / "pipeline-full-chain-dry-run-card-20260508-01.card.md"
    ).read_text(encoding="utf-8")

    assert registry["active_mainline_module"] == "system_readout"
    assert registry["current_allowed_next_card"] == PIPELINE_DRY_RUN_CARD_ACTION
    assert modules["pipeline"]["status"] == "released"
    assert modules["pipeline"]["doc_status"] == PIPELINE_CURRENT_DOC_STATUS
    assert modules["pipeline"]["next_card"] == PIPELINE_DRY_RUN_CARD_ACTION
    assert modules["pipeline"]["proof_run_id"] == PIPELINE_RUN_ID
    assert PIPELINE_RUN_ID in conclusion_index
    assert PIPELINE_DRY_RUN_SCOPE_FREEZE_RUN_ID in conclusion_index
    assert f"| Pipeline | `{PIPELINE_RUN_ID}` | `passed` |" in conclusion_index
    assert f"| Pipeline | `{PIPELINE_DRY_RUN_SCOPE_FREEZE_RUN_ID}` | `passed / scope frozen` |" in (
        conclusion_index
    )
    assert f"| Pipeline | `{PIPELINE_DRY_RUN_CARD_RUN_ID}` |" not in conclusion_index
    assert PIPELINE_DRY_RUN_CARD_RUN_ID in conclusion_index
    assert "状态：`passed`" in pipeline_runtime_conclusion
    assert "| allowed next action | `none` |" in pipeline_runtime_conclusion
    assert "状态：`passed`" in pipeline_scope_conclusion
    assert (
        f"| allowed next action | `{PIPELINE_DRY_RUN_CARD_ACTION}` |" in pipeline_scope_conclusion
    )
    assert (
        f"[next prepared card]({PIPELINE_DRY_RUN_CARD_RUN_ID}.card.md)" in pipeline_scope_conclusion
    )
    assert "状态：`prepared / not executed`" in pipeline_dry_run_card


def test_project_governance_rejects_pipeline_scripts_when_single_module_runtime_not_authorized(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            'current_allowed_next_card = "pipeline_single_module_orchestration_build_card"',
            'current_allowed_next_card = ""',
        )
        .replace(
            f'status = "released"\ndoc_status = "{PIPELINE_CURRENT_DOC_STATUS}"',
            f'status = "freeze_review_passed"\ndoc_status = "{PIPELINE_PREPARED_DOC_STATUS}"',
            1,
        )
        .replace(
            f'next_card = "{PIPELINE_DRY_RUN_CARD_ACTION}"',
            'next_card = "pipeline_single_module_orchestration_build_card"',
            1,
        ),
        encoding="utf-8",
    )

    assert any(
        "pre-gate module has forbidden formal runner" in message for message in _messages(repo_root)
    )
