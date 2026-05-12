from pathlib import Path
from shutil import copy2, copytree

from scripts.governance.check_project_governance import run_checks
from tests.unit.pipeline.support import (
    ALPHA_SIGNAL_DAILY_INCREMENTAL_LEDGER_RUN_ID,
    CURRENT_ACTIVE_MAINLINE_MODULE,
    CURRENT_ALLOWED_NEXT_CARD_ACTION,
    CURRENT_PIPELINE_ACTIVE_CARD,
    DATA_DAILY_HARDENING_ACTION,
    DATA_DAILY_HARDENING_RUN_ID,
    MALF_DAILY_INCREMENTAL_LEDGER_ACTION,
    MALF_DAILY_INCREMENTAL_LEDGER_RUN_ID,
    PIPELINE_CURRENT_DOC_STATUS,
    PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
    PIPELINE_CURRENT_PROOF_RUN_ID,
    PIPELINE_STAGE11_PROTOCOL_ACTION,
    PIPELINE_STAGE11_PROTOCOL_RUN_ID,
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


def test_stage11_protocol_passes_and_moves_live_next_card_to_data_daily_hardening() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    pipeline_contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    system_contract_path = repo_root / "governance" / "module_api_contracts" / "system_readout.toml"
    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    with pipeline_contract_path.open("rb") as handle:
        pipeline_contract = tomllib.load(handle)
    with system_contract_path.open("rb") as handle:
        system_contract = tomllib.load(handle)

    modules = {module["module_id"]: module for module in registry["modules"]}
    conclusion_index = (
        repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    ).read_text(encoding="utf-8")
    protocol_conclusion = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / f"{PIPELINE_STAGE11_PROTOCOL_RUN_ID}.conclusion.md"
    ).read_text(encoding="utf-8")
    prepared_data_card = (
        repo_root / "docs/04-execution/records/data/" / f"{DATA_DAILY_HARDENING_RUN_ID}.card.md"
    ).read_text(encoding="utf-8")

    assert registry["active_mainline_module"] == CURRENT_ACTIVE_MAINLINE_MODULE
    assert registry["active_foundation_card"] == "none"
    assert registry["current_allowed_next_card"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert modules["data"]["latest_completed_card"] == DATA_DAILY_HARDENING_ACTION
    assert modules["data"]["next_card"] == MALF_DAILY_INCREMENTAL_LEDGER_ACTION
    assert modules["system_readout"]["next_card"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert modules["system_readout"]["next_allowed_action"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert modules["pipeline"]["doc_status"] == PIPELINE_CURRENT_DOC_STATUS
    assert modules["pipeline"]["formal_db_permission"] == PIPELINE_CURRENT_FORMAL_DB_PERMISSION
    assert modules["pipeline"]["next_card"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert modules["pipeline"]["proof_run_id"] == PIPELINE_CURRENT_PROOF_RUN_ID
    assert modules["pipeline"]["active_card"] == CURRENT_PIPELINE_ACTIVE_CARD.replace(
        'active_card = "', ""
    ).replace('"', "")
    assert pipeline_contract["next_allowed_action"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert pipeline_contract["release_conclusion"] == (
        f"docs/04-execution/records/pipeline/{PIPELINE_CURRENT_PROOF_RUN_ID}.conclusion.md"
    )
    assert pipeline_contract["evidence_index"] == (
        f"docs/04-execution/records/pipeline/{PIPELINE_CURRENT_PROOF_RUN_ID}.evidence-index.md"
    )
    assert pipeline_contract["daily_protocol_timeframe"] == "day"
    assert pipeline_contract["daily_protocol_lineage_fields"] == [
        "source_run_id",
        "target_run_id",
    ]
    assert pipeline_contract["daily_protocol_read_only_modules"] == [
        "system_readout",
        "pipeline",
    ]
    assert system_contract["next_allowed_action"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert system_contract["daily_protocol_role"] == "read_only_consumer"
    assert system_contract["daily_protocol_lineage_fields"] == [
        "source_run_id",
        "target_run_id",
    ]
    assert (
        repo_root
        / "docs/04-execution/records/malf/"
        / f"{MALF_DAILY_INCREMENTAL_LEDGER_RUN_ID}.card.md"
    ).exists()
    assert (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / f"{ALPHA_SIGNAL_DAILY_INCREMENTAL_LEDGER_RUN_ID}.card.md"
    ).exists()
    assert (
        f"| Pipeline | `{PIPELINE_STAGE11_PROTOCOL_RUN_ID}` | `passed / protocol frozen` |"
        in conclusion_index
    )
    assert (
        f"| Data | `{DATA_DAILY_HARDENING_RUN_ID}` | "
        "`passed / data daily incremental sample hardened` |" in conclusion_index
    )
    assert "状态：`passed / protocol frozen`" in protocol_conclusion
    assert f"| allowed next action | `{DATA_DAILY_HARDENING_ACTION}` |" in protocol_conclusion
    assert f"| prepared next card | `{DATA_DAILY_HARDENING_RUN_ID}` |" in protocol_conclusion
    assert "状态：`passed / data daily incremental sample hardened`" in prepared_data_card


def test_project_governance_rejects_closed_stage11_protocol_as_live_next_card(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    pipeline_contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    registry_text = rewrite_registry_module_fields(
        registry_path.read_text(encoding="utf-8"),
        module_id="pipeline",
        field_updates={
            "next_card": f'"{PIPELINE_STAGE11_PROTOCOL_ACTION}"',
            "active_card": (
                '"docs/04-execution/records/pipeline/'
                'system-wide-daily-dirty-scope-protocol-card.card.md"'
            ),
        },
    )
    registry_path.write_text(
        registry_text.replace(
            f'current_allowed_next_card = "{CURRENT_ALLOWED_NEXT_CARD_ACTION}"',
            f'current_allowed_next_card = "{PIPELINE_STAGE11_PROTOCOL_ACTION}"',
            1,
        ),
        encoding="utf-8",
    )
    pipeline_contract_path.write_text(
        pipeline_contract_path.read_text(encoding="utf-8").replace(
            f'next_allowed_action = "{CURRENT_ALLOWED_NEXT_CARD_ACTION}"',
            f'next_allowed_action = "{PIPELINE_STAGE11_PROTOCOL_ACTION}"',
            1,
        ),
        encoding="utf-8",
    )

    assert any(
        "current allowed next card must not point to a closed execution conclusion" in message
        for message in _messages(repo_root)
    )
