from pathlib import Path
from shutil import copy2, copytree

from scripts.governance.check_project_governance import run_checks
from tests.unit.pipeline.constants import (
    PIPELINE_FULL_DAILY_INCREMENTAL_CHAIN_ACTION,
    PIPELINE_FULL_DAILY_INCREMENTAL_CHAIN_RUN_ID,
)
from tests.unit.pipeline.support_state import rewrite_registry_module_fields

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


NEXT_RELEASE_CLOSEOUT_ACTION = "full_rebuild_and_daily_incremental_release_closeout_card"
NEXT_RELEASE_CLOSEOUT_RUN_ID = "full-rebuild-and-daily-incremental-release-closeout-card"


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


def test_pipeline_full_daily_incremental_chain_closure_moves_live_next_to_release_closeout() -> (
    None
):
    repo_root = Path(__file__).resolve().parents[3]
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    pipeline_contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    system_contract_path = repo_root / "governance" / "module_api_contracts" / "system_readout.toml"
    trade_contract_path = repo_root / "governance" / "module_api_contracts" / "trade.toml"

    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    with pipeline_contract_path.open("rb") as handle:
        pipeline_contract = tomllib.load(handle)
    with system_contract_path.open("rb") as handle:
        system_contract = tomllib.load(handle)
    with trade_contract_path.open("rb") as handle:
        trade_contract = tomllib.load(handle)

    modules = {module["module_id"]: module for module in registry["modules"]}
    conclusion_index = (
        repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    ).read_text(encoding="utf-8")
    full_chain_card = (
        repo_root
        / "docs/04-execution/records/pipeline"
        / f"{PIPELINE_FULL_DAILY_INCREMENTAL_CHAIN_RUN_ID}.card.md"
    ).read_text(encoding="utf-8")
    full_chain_record = (
        repo_root
        / "docs/04-execution/records/pipeline"
        / f"{PIPELINE_FULL_DAILY_INCREMENTAL_CHAIN_RUN_ID}.record.md"
    ).read_text(encoding="utf-8")
    full_chain_conclusion = (
        repo_root
        / "docs/04-execution/records/pipeline"
        / f"{PIPELINE_FULL_DAILY_INCREMENTAL_CHAIN_RUN_ID}.conclusion.md"
    ).read_text(encoding="utf-8")
    full_chain_evidence = (
        repo_root
        / "docs/04-execution/records/pipeline"
        / f"{PIPELINE_FULL_DAILY_INCREMENTAL_CHAIN_RUN_ID}.evidence-index.md"
    ).read_text(encoding="utf-8")
    next_closeout_card = (
        repo_root / "docs/04-execution/records/pipeline" / f"{NEXT_RELEASE_CLOSEOUT_RUN_ID}.card.md"
    ).read_text(encoding="utf-8")

    assert registry["current_allowed_next_card"] == NEXT_RELEASE_CLOSEOUT_ACTION
    assert modules["trade"]["next_allowed_action"] == NEXT_RELEASE_CLOSEOUT_ACTION
    assert modules["system_readout"]["next_card"] == NEXT_RELEASE_CLOSEOUT_ACTION
    assert modules["system_readout"]["next_allowed_action"] == NEXT_RELEASE_CLOSEOUT_ACTION
    assert modules["pipeline"]["next_card"] == NEXT_RELEASE_CLOSEOUT_ACTION
    assert modules["pipeline"]["next_allowed_action"] == NEXT_RELEASE_CLOSEOUT_ACTION
    assert modules["pipeline"]["proof_run_id"] == PIPELINE_FULL_DAILY_INCREMENTAL_CHAIN_RUN_ID
    assert (
        modules["pipeline"]["active_card"] == "docs/04-execution/records/pipeline/"
        f"{PIPELINE_FULL_DAILY_INCREMENTAL_CHAIN_RUN_ID}.card.md"
    )
    assert pipeline_contract["next_allowed_action"] == NEXT_RELEASE_CLOSEOUT_ACTION
    assert system_contract["next_allowed_action"] == NEXT_RELEASE_CLOSEOUT_ACTION
    assert trade_contract["next_allowed_action"] == NEXT_RELEASE_CLOSEOUT_ACTION
    assert "pipeline_full_daily_incremental_chain_passed" in modules["pipeline"]["proof_status"]
    assert (
        "daily_incremental_release_closeout_requires_new_card"
        in (modules["pipeline"]["formal_db_permission"])
    )
    assert (
        f"| Pipeline | `{PIPELINE_FULL_DAILY_INCREMENTAL_CHAIN_RUN_ID}` | "
        "`passed / pipeline full daily incremental chain proof passed` |" in conclusion_index
    )
    assert NEXT_RELEASE_CLOSEOUT_RUN_ID in conclusion_index
    assert "状态：`passed / pipeline full daily incremental chain proof passed`" in full_chain_card
    assert "pipeline full daily incremental chain proof passed" in full_chain_record
    assert "no formal H:/Asteria-data mutation" in full_chain_conclusion
    assert "daily incremental release closeout not executed" in full_chain_conclusion
    assert "formal full rebuild not executed" in full_chain_evidence
    assert "状态：`prepared / not executed`" in next_closeout_card


def test_project_governance_rejects_closed_full_daily_chain_as_live_next_card(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    system_contract_path = repo_root / "governance" / "module_api_contracts" / "system_readout.toml"
    pipeline_contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    trade_contract_path = repo_root / "governance" / "module_api_contracts" / "trade.toml"

    registry_text = rewrite_registry_module_fields(
        registry_path.read_text(encoding="utf-8"),
        module_id="system_readout",
        field_updates={"next_card": f'"{PIPELINE_FULL_DAILY_INCREMENTAL_CHAIN_ACTION}"'},
    )
    registry_text = rewrite_registry_module_fields(
        registry_text,
        module_id="pipeline",
        field_updates={"next_card": f'"{PIPELINE_FULL_DAILY_INCREMENTAL_CHAIN_ACTION}"'},
    )
    registry_path.write_text(
        registry_text.replace(
            f'current_allowed_next_card = "{NEXT_RELEASE_CLOSEOUT_ACTION}"',
            f'current_allowed_next_card = "{PIPELINE_FULL_DAILY_INCREMENTAL_CHAIN_ACTION}"',
            1,
        ).replace(
            f'next_allowed_action = "{NEXT_RELEASE_CLOSEOUT_ACTION}"',
            f'next_allowed_action = "{PIPELINE_FULL_DAILY_INCREMENTAL_CHAIN_ACTION}"',
            3,
        ),
        encoding="utf-8",
    )
    for path in (system_contract_path, pipeline_contract_path, trade_contract_path):
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                f'next_allowed_action = "{NEXT_RELEASE_CLOSEOUT_ACTION}"',
                f'next_allowed_action = "{PIPELINE_FULL_DAILY_INCREMENTAL_CHAIN_ACTION}"',
                1,
            ),
            encoding="utf-8",
        )

    assert any(
        "current allowed next card must not point to a closed execution conclusion" in message
        for message in _messages(repo_root)
    )
