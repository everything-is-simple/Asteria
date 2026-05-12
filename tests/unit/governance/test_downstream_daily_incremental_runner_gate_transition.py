from pathlib import Path
from shutil import copy2, copytree

from scripts.governance.check_project_governance import run_checks
from tests.unit.pipeline.support import (
    CURRENT_ACTIVE_MAINLINE_MODULE,
    CURRENT_ALLOWED_NEXT_CARD_ACTION,
    CURRENT_PIPELINE_ACTIVE_CARD,
    DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_ACTION,
    DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_RUN_ID,
    PIPELINE_CURRENT_DOC_STATUS,
    PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
    PIPELINE_CURRENT_PROOF_RUN_ID,
    PIPELINE_FULL_DAILY_INCREMENTAL_CHAIN_RUN_ID,
)
from tests.unit.pipeline.support_state import rewrite_registry_module_fields

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


def test_downstream_daily_incremental_runner_closure_moves_live_next_to_pipeline_full_chain() -> (
    None
):
    repo_root = Path(__file__).resolve().parents[3]
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    pipeline_contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    system_contract_path = repo_root / "governance" / "module_api_contracts" / "system_readout.toml"
    trade_contract_path = repo_root / "governance" / "module_api_contracts" / "trade.toml"
    position_contract_path = repo_root / "governance" / "module_api_contracts" / "position.toml"
    portfolio_contract_path = (
        repo_root / "governance" / "module_api_contracts" / "portfolio_plan.toml"
    )
    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    with pipeline_contract_path.open("rb") as handle:
        pipeline_contract = tomllib.load(handle)
    with system_contract_path.open("rb") as handle:
        system_contract = tomllib.load(handle)
    with trade_contract_path.open("rb") as handle:
        trade_contract = tomllib.load(handle)
    with position_contract_path.open("rb") as handle:
        position_contract = tomllib.load(handle)
    with portfolio_contract_path.open("rb") as handle:
        portfolio_contract = tomllib.load(handle)

    modules = {module["module_id"]: module for module in registry["modules"]}
    conclusion_index = (
        repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    ).read_text(encoding="utf-8")
    runner_conclusion = (
        repo_root
        / "docs/04-execution/records/pipeline"
        / f"{DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_RUN_ID}.conclusion.md"
    ).read_text(encoding="utf-8")
    prepared_full_chain_card = (
        repo_root
        / "docs/04-execution/records/pipeline"
        / f"{PIPELINE_FULL_DAILY_INCREMENTAL_CHAIN_RUN_ID}.card.md"
    ).read_text(encoding="utf-8")

    assert registry["active_mainline_module"] == CURRENT_ACTIVE_MAINLINE_MODULE
    assert registry["current_allowed_next_card"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert modules["trade"]["next_allowed_action"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert modules["system_readout"]["next_card"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert modules["system_readout"]["next_allowed_action"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert modules["pipeline"]["doc_status"] == PIPELINE_CURRENT_DOC_STATUS
    assert modules["pipeline"]["formal_db_permission"] == PIPELINE_CURRENT_FORMAL_DB_PERMISSION
    assert modules["pipeline"]["next_card"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert modules["pipeline"]["proof_run_id"] == PIPELINE_CURRENT_PROOF_RUN_ID
    assert modules["pipeline"]["active_card"] == CURRENT_PIPELINE_ACTIVE_CARD.replace(
        'active_card = "', ""
    ).rstrip('"')
    assert "daily_incremental" in position_contract["run_modes"]
    assert "daily_incremental" in portfolio_contract["run_modes"]
    assert "daily_incremental" in trade_contract["run_modes"]
    assert "daily_incremental" in system_contract["run_modes"]
    assert "daily_incremental" in pipeline_contract["run_modes"]
    assert pipeline_contract["next_allowed_action"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert system_contract["next_allowed_action"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert trade_contract["next_allowed_action"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert (
        f"| Pipeline | `{DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_RUN_ID}` | "
        "`passed / downstream daily incremental sample hardened` |" in conclusion_index
    )
    assert "状态：`passed / downstream daily incremental sample hardened`" in runner_conclusion
    assert f"| allowed next action | `{CURRENT_ALLOWED_NEXT_CARD_ACTION}` |" in runner_conclusion
    assert (
        f"| prepared next card | `{PIPELINE_FULL_DAILY_INCREMENTAL_CHAIN_RUN_ID}` |"
        in runner_conclusion
    )
    assert "状态：`prepared / not executed`" in prepared_full_chain_card


def test_project_governance_rejects_closed_downstream_runner_as_live_next_card(
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
        field_updates={"next_card": f'"{DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_ACTION}"'},
    )
    registry_text = rewrite_registry_module_fields(
        registry_text,
        module_id="pipeline",
        field_updates={"next_card": f'"{DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_ACTION}"'},
    )
    registry_path.write_text(
        registry_text.replace(
            f'current_allowed_next_card = "{CURRENT_ALLOWED_NEXT_CARD_ACTION}"',
            f'current_allowed_next_card = "{DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_ACTION}"',
            1,
        ).replace(
            f'next_allowed_action = "{CURRENT_ALLOWED_NEXT_CARD_ACTION}"',
            f'next_allowed_action = "{DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_ACTION}"',
            3,
        ),
        encoding="utf-8",
    )
    for path in (system_contract_path, pipeline_contract_path, trade_contract_path):
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                f'next_allowed_action = "{CURRENT_ALLOWED_NEXT_CARD_ACTION}"',
                f'next_allowed_action = "{DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_ACTION}"',
                1,
            ),
            encoding="utf-8",
        )

    assert any(
        "current allowed next card must not point to a closed execution conclusion" in message
        for message in _messages(repo_root)
    )
