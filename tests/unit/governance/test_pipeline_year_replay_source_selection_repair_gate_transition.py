from pathlib import Path
from shutil import copy2, copytree

from scripts.governance.check_project_governance import run_checks
from tests.unit.pipeline.support import (
    CURRENT_ACTIVE_MAINLINE_MODULE,
    CURRENT_ALLOWED_NEXT_CARD_ACTION,
    PIPELINE_CURRENT_DOC_STATUS,
    PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
    PIPELINE_CURRENT_PROOF_RUN_ID,
    PIPELINE_DISPOSITION_DECISION_RUN_ID,
    PIPELINE_SOURCE_SELECTION_REPAIR_ACTION,
    PIPELINE_SOURCE_SELECTION_REPAIR_RUN_ID,
    PIPELINE_STAGE11_PROTOCOL_RUN_ID,
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


def test_pipeline_source_selection_repair_advances_live_next_card() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    modules = {module["module_id"]: module for module in registry["modules"]}
    conclusion_index = (
        repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    ).read_text(encoding="utf-8")
    repair_conclusion = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / f"{PIPELINE_SOURCE_SELECTION_REPAIR_RUN_ID}.conclusion.md"
    ).read_text(encoding="utf-8")
    repair_evidence = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / f"{PIPELINE_SOURCE_SELECTION_REPAIR_RUN_ID}.evidence-index.md"
    ).read_text(encoding="utf-8")
    disposition_conclusion = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / f"{PIPELINE_DISPOSITION_DECISION_RUN_ID}.conclusion.md"
    ).read_text(encoding="utf-8")
    protocol_conclusion = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / f"{PIPELINE_STAGE11_PROTOCOL_RUN_ID}.conclusion.md"
    ).read_text(encoding="utf-8")

    assert registry["active_mainline_module"] == CURRENT_ACTIVE_MAINLINE_MODULE
    assert registry["current_allowed_next_card"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert modules["pipeline"]["status"] == "released"
    assert modules["pipeline"]["doc_status"] == PIPELINE_CURRENT_DOC_STATUS
    assert modules["pipeline"]["formal_db_permission"] == PIPELINE_CURRENT_FORMAL_DB_PERMISSION
    assert modules["pipeline"]["next_card"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert modules["pipeline"]["proof_run_id"] == PIPELINE_CURRENT_PROOF_RUN_ID
    assert modules["system_readout"]["next_card"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert modules["system_readout"]["next_allowed_action"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert (
        f"| Pipeline | `{PIPELINE_SOURCE_SELECTION_REPAIR_RUN_ID}` | `passed` |" in conclusion_index
    )
    assert "状态：`passed`" in repair_conclusion
    assert "| allowed next action | `pipeline_year_replay_disposition_decision_card` |" in (
        repair_conclusion
    )
    assert "pipeline-year-replay-disposition-decision-card-20260510-01" in repair_evidence
    assert "状态：`passed`" in disposition_conclusion
    assert "状态：`passed / protocol frozen`" in protocol_conclusion


def test_project_governance_rejects_reopening_closed_source_selection_repair_card(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            (f'current_allowed_next_card = "{CURRENT_ALLOWED_NEXT_CARD_ACTION}"'),
            f'current_allowed_next_card = "{PIPELINE_SOURCE_SELECTION_REPAIR_ACTION}"',
            1,
        ).replace(
            f'next_card = "{CURRENT_ALLOWED_NEXT_CARD_ACTION}"',
            f'next_card = "{PIPELINE_SOURCE_SELECTION_REPAIR_ACTION}"',
            1,
        ),
        encoding="utf-8",
    )

    assert any(
        "current allowed next card must not point to a closed execution conclusion" in message
        for message in _messages(repo_root)
    )
