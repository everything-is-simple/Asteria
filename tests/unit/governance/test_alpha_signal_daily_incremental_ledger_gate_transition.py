from pathlib import Path
from shutil import copy2, copytree

from scripts.governance.check_project_governance import run_checks
from tests.unit.pipeline.support import (
    ALPHA_SIGNAL_DAILY_INCREMENTAL_LEDGER_ACTION,
    ALPHA_SIGNAL_DAILY_INCREMENTAL_LEDGER_RUN_ID,
    CURRENT_ACTIVE_MAINLINE_MODULE,
)

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION = "downstream_daily_impact_ledger_schema_card"
DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_RUN_ID = "downstream-daily-impact-ledger-schema-card"
ALPHA_CURRENT_DOC_STATUS = (
    "frozen six-doc set / bounded proof passed / production hardening passed / "
    "daily incremental sample hardened"
)
SIGNAL_CURRENT_DOC_STATUS = (
    "frozen six-doc set / bounded proof passed / production hardening passed / "
    "daily incremental sample hardened"
)


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


def test_alpha_signal_daily_incremental_closure_moves_live_next_card_to_downstream_schema() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    pipeline_contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    system_contract_path = repo_root / "governance" / "module_api_contracts" / "system_readout.toml"
    alpha_contract_path = repo_root / "governance" / "module_api_contracts" / "alpha.toml"
    signal_contract_path = repo_root / "governance" / "module_api_contracts" / "signal.toml"
    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    with pipeline_contract_path.open("rb") as handle:
        pipeline_contract = tomllib.load(handle)
    with system_contract_path.open("rb") as handle:
        system_contract = tomllib.load(handle)
    with alpha_contract_path.open("rb") as handle:
        alpha_contract = tomllib.load(handle)
    with signal_contract_path.open("rb") as handle:
        signal_contract = tomllib.load(handle)

    modules = {module["module_id"]: module for module in registry["modules"]}
    conclusion_index = (
        repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    ).read_text(encoding="utf-8")
    pipeline_conclusion = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / f"{ALPHA_SIGNAL_DAILY_INCREMENTAL_LEDGER_RUN_ID}.conclusion.md"
    ).read_text(encoding="utf-8")
    prepared_downstream_card = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / f"{DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_RUN_ID}.card.md"
    ).read_text(encoding="utf-8")

    assert registry["active_mainline_module"] == CURRENT_ACTIVE_MAINLINE_MODULE
    assert registry["current_allowed_next_card"] == DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION
    assert modules["alpha"]["doc_status"] == ALPHA_CURRENT_DOC_STATUS
    assert modules["signal"]["doc_status"] == SIGNAL_CURRENT_DOC_STATUS
    assert modules["system_readout"]["next_card"] == DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION
    assert (
        modules["system_readout"]["next_allowed_action"]
        == DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION
    )
    assert modules["pipeline"]["next_card"] == DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION
    assert (
        modules["pipeline"]["next_allowed_action"] == DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION
    )
    assert "daily_incremental" in alpha_contract["run_modes"]
    assert "daily_incremental" in signal_contract["run_modes"]
    assert pipeline_contract["next_allowed_action"] == DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION
    assert system_contract["next_allowed_action"] == DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION
    assert (
        f"| Pipeline | `{ALPHA_SIGNAL_DAILY_INCREMENTAL_LEDGER_RUN_ID}` | "
        "`passed / alpha signal daily incremental sample hardened` |" in conclusion_index
    )
    assert (
        f"| allowed next action | `{DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION}` |"
        in pipeline_conclusion
    )
    assert "状态：`prepared / not executed`" in prepared_downstream_card


def test_project_governance_rejects_closed_alpha_signal_daily_card_as_live_next_card(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    system_contract_path = repo_root / "governance" / "module_api_contracts" / "system_readout.toml"
    pipeline_contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            f'current_allowed_next_card = "{DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION}"',
            f'current_allowed_next_card = "{ALPHA_SIGNAL_DAILY_INCREMENTAL_LEDGER_ACTION}"',
            1,
        ).replace(
            f'next_card = "{DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION}"',
            f'next_card = "{ALPHA_SIGNAL_DAILY_INCREMENTAL_LEDGER_ACTION}"',
            4,
        ),
        encoding="utf-8",
    )
    for path in (system_contract_path, pipeline_contract_path):
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                f'next_allowed_action = "{DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION}"',
                f'next_allowed_action = "{ALPHA_SIGNAL_DAILY_INCREMENTAL_LEDGER_ACTION}"',
                1,
            ),
            encoding="utf-8",
        )

    assert any(
        "current allowed next card must not point to a closed execution conclusion" in message
        for message in _messages(repo_root)
    )
