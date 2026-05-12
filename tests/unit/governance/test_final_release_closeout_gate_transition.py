from pathlib import Path
from shutil import copy2, copytree

from scripts.governance.check_project_governance import run_checks
from tests.unit.pipeline.constants import FORMAL_RELEASE_PROOF_RUN_ID
from tests.unit.pipeline.support_state import rewrite_registry_module_fields

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


FINAL_RELEASE_CLOSEOUT_RUN_ID = "final-release-closeout-card"


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


def test_final_release_closeout_terminal_state_is_registered() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    pipeline_contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    records_root = repo_root / "docs" / "04-execution" / "records" / "pipeline"

    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    with pipeline_contract_path.open("rb") as handle:
        pipeline_contract = tomllib.load(handle)

    modules = {module["module_id"]: module for module in registry["modules"]}
    card = (records_root / f"{FINAL_RELEASE_CLOSEOUT_RUN_ID}.card.md").read_text(encoding="utf-8")
    conclusion = (records_root / f"{FINAL_RELEASE_CLOSEOUT_RUN_ID}.conclusion.md").read_text(
        encoding="utf-8"
    )
    evidence = (records_root / f"{FINAL_RELEASE_CLOSEOUT_RUN_ID}.evidence-index.md").read_text(
        encoding="utf-8"
    )
    conclusion_index = (
        repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    ).read_text(encoding="utf-8")

    assert registry["current_allowed_next_card"] == ""
    mainline_modules = [module for module in modules.values() if module.get("mainline") is True]
    assert all(not module.get("allow_build", False) for module in mainline_modules)
    assert all(not module.get("allow_review", False) for module in mainline_modules)
    assert modules["pipeline"]["active_card"] == (
        f"docs/04-execution/records/pipeline/{FINAL_RELEASE_CLOSEOUT_RUN_ID}.card.md"
    )
    assert modules["pipeline"]["release_conclusion"] == (
        f"docs/04-execution/records/pipeline/{FINAL_RELEASE_CLOSEOUT_RUN_ID}.conclusion.md"
    )
    assert modules["pipeline"]["evidence_index"] == (
        f"docs/04-execution/records/pipeline/{FINAL_RELEASE_CLOSEOUT_RUN_ID}.evidence-index.md"
    )
    assert "final_release_closeout_passed" in modules["pipeline"]["proof_status"]
    assert "v1_complete" in modules["pipeline"]["formal_db_permission"]
    assert modules["pipeline"]["next_card"] == ""
    assert modules["system_readout"]["next_card"] == ""
    assert modules["trade"]["next_allowed_action"] == ""
    assert pipeline_contract["next_allowed_action"] == ""
    assert pipeline_contract["release_conclusion"] == modules["pipeline"]["release_conclusion"]
    assert pipeline_contract["evidence_index"] == modules["pipeline"]["evidence_index"]
    assert "状态：`passed / v1 complete`" in card
    assert "状态：`passed / v1 complete`" in conclusion
    assert "final closeout manifest" in evidence
    assert (
        f"| Pipeline | `{FINAL_RELEASE_CLOSEOUT_RUN_ID}` | `passed / v1 complete` |"
    ) in conclusion_index
    assert FORMAL_RELEASE_PROOF_RUN_ID in conclusion


def test_blocked_final_closeout_can_remain_current_reentry_card(tmp_path: Path) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    records_root = repo_root / "docs" / "04-execution" / "records" / "pipeline"

    registry_text = registry_path.read_text(encoding="utf-8")
    registry_text = registry_text.replace(
        'current_allowed_next_card = ""',
        'current_allowed_next_card = "final_release_closeout_card"',
    )
    registry_text = rewrite_registry_module_fields(
        registry_text,
        module_id="pipeline",
        field_updates={
            "next_card": '"final_release_closeout_card"',
            "proof_status": (
                '"formal_full_rebuild_and_daily_incremental_release_proof_passed; '
                'final_release_closeout_blocked; final_release_evidence_inconsistent"'
            ),
            "formal_db_permission": (
                '"final_release_evidence_passed; '
                'final_release_closeout_blocked_evidence_inconsistent"'
            ),
        },
    )
    registry_path.write_text(registry_text, encoding="utf-8")
    (records_root / f"{FINAL_RELEASE_CLOSEOUT_RUN_ID}.conclusion.md").write_text(
        "# Final Release Closeout Card Conclusion\n\n"
        "状态：`blocked / final release evidence inconsistent`\n",
        encoding="utf-8",
    )

    messages = [finding.message for finding in run_checks(repo_root)]

    assert (
        "current allowed next card must not point to a closed execution conclusion" not in messages
    )
