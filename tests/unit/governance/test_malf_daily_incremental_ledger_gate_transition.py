from pathlib import Path
from shutil import copy2, copytree

from scripts.governance.check_project_governance import run_checks
from tests.unit.pipeline.support import (
    ALPHA_SIGNAL_DAILY_INCREMENTAL_LEDGER_ACTION,
    ALPHA_SIGNAL_DAILY_INCREMENTAL_LEDGER_RUN_ID,
    CURRENT_ACTIVE_MAINLINE_MODULE,
    CURRENT_ALLOWED_NEXT_CARD_ACTION,
    MALF_CURRENT_DOC_STATUS,
    MALF_CURRENT_PROOF_STATUS,
    MALF_DAILY_INCREMENTAL_LEDGER_ACTION,
    MALF_DAILY_INCREMENTAL_LEDGER_RUN_ID,
    PIPELINE_CURRENT_DOC_STATUS,
    PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
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


def test_malf_daily_incremental_ledger_closure_moves_live_next_card_to_alpha_signal() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    pipeline_contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    system_contract_path = repo_root / "governance" / "module_api_contracts" / "system_readout.toml"
    malf_contract_path = repo_root / "governance" / "module_api_contracts" / "malf.toml"
    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    with pipeline_contract_path.open("rb") as handle:
        pipeline_contract = tomllib.load(handle)
    with system_contract_path.open("rb") as handle:
        system_contract = tomllib.load(handle)
    with malf_contract_path.open("rb") as handle:
        malf_contract = tomllib.load(handle)

    modules = {module["module_id"]: module for module in registry["modules"]}
    conclusion_index = (
        repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    ).read_text(encoding="utf-8")
    malf_conclusion = (
        repo_root
        / "docs/04-execution/records/malf/"
        / f"{MALF_DAILY_INCREMENTAL_LEDGER_RUN_ID}.conclusion.md"
    ).read_text(encoding="utf-8")
    prepared_alpha_signal_card = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / f"{ALPHA_SIGNAL_DAILY_INCREMENTAL_LEDGER_RUN_ID}.card.md"
    ).read_text(encoding="utf-8")

    assert registry["active_mainline_module"] == CURRENT_ACTIVE_MAINLINE_MODULE
    assert registry["current_allowed_next_card"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert modules["malf"]["doc_status"] == MALF_CURRENT_DOC_STATUS
    assert modules["malf"]["proof_status"] == MALF_CURRENT_PROOF_STATUS
    assert modules["malf"]["next_card"] == ALPHA_SIGNAL_DAILY_INCREMENTAL_LEDGER_ACTION
    assert modules["system_readout"]["next_card"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert modules["system_readout"]["next_allowed_action"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert modules["pipeline"]["doc_status"] == PIPELINE_CURRENT_DOC_STATUS
    assert modules["pipeline"]["formal_db_permission"] == PIPELINE_CURRENT_FORMAL_DB_PERMISSION
    assert modules["pipeline"]["next_card"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert pipeline_contract["next_allowed_action"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert system_contract["next_allowed_action"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert "daily_incremental" in malf_contract["run_modes"]
    assert (
        f"| MALF | `{MALF_DAILY_INCREMENTAL_LEDGER_RUN_ID}` | "
        "`passed / malf daily incremental sample hardened` |" in conclusion_index
    )
    assert "状态：`passed / malf daily incremental sample hardened`" in malf_conclusion
    assert (
        f"| allowed next action | `{ALPHA_SIGNAL_DAILY_INCREMENTAL_LEDGER_ACTION}` |"
        in malf_conclusion
    )
    assert (
        f"| prepared next card | `{ALPHA_SIGNAL_DAILY_INCREMENTAL_LEDGER_RUN_ID}` |"
        in malf_conclusion
    )
    assert "状态：`passed / alpha signal daily incremental sample hardened`" in (
        prepared_alpha_signal_card
    )


def test_project_governance_rejects_closed_malf_daily_incremental_card_as_live_next_card(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    system_contract_path = repo_root / "governance" / "module_api_contracts" / "system_readout.toml"
    pipeline_contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            f'current_allowed_next_card = "{CURRENT_ALLOWED_NEXT_CARD_ACTION}"',
            f'current_allowed_next_card = "{MALF_DAILY_INCREMENTAL_LEDGER_ACTION}"',
            1,
        ).replace(
            f'next_card = "{CURRENT_ALLOWED_NEXT_CARD_ACTION}"',
            f'next_card = "{MALF_DAILY_INCREMENTAL_LEDGER_ACTION}"',
            3,
        ),
        encoding="utf-8",
    )
    for path in (system_contract_path, pipeline_contract_path):
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                f'next_allowed_action = "{CURRENT_ALLOWED_NEXT_CARD_ACTION}"',
                f'next_allowed_action = "{MALF_DAILY_INCREMENTAL_LEDGER_ACTION}"',
                1,
            ),
            encoding="utf-8",
        )

    assert any(
        "current allowed next card must not point to a closed execution conclusion" in message
        for message in _messages(repo_root)
    )
