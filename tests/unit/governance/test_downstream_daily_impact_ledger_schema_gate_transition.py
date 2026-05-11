from pathlib import Path
from shutil import copy2, copytree

from scripts.governance.check_project_governance import run_checks
from tests.unit.pipeline.support_state import rewrite_registry_module_fields

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION = "downstream_daily_impact_ledger_schema_card"
DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_RUN_ID = "downstream-daily-impact-ledger-schema-card"
DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_ACTION = "downstream_daily_incremental_runner_build_card"
DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_RUN_ID = "downstream-daily-incremental-runner-build-card"
CURRENT_ACTIVE_MAINLINE_MODULE = "system_readout"
PIPELINE_CURRENT_PROOF_RUN_ID = DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_RUN_ID
PIPELINE_CURRENT_DOC_STATUS = (
    "frozen six-doc set / freeze review passed / single-module orchestration build passed / "
    "full-chain dry-run passed / full-chain day bounded proof passed / one-year strategy "
    "behavior replay blocked / coverage gap diagnosis executed / MALF natural-year coverage "
    "repair passed / year replay rerun blocked / alpha-signal coverage repair passed / "
    "downstream coverage gap evidence closeout passed / position 2024 coverage repair "
    "passed / portfolio_plan 2024 coverage repair passed / trade 2024 coverage repair "
    "passed / system_readout 2024 coverage repair handoff passed / pipeline year replay "
    "source-selection repair passed / year replay disposition decision passed / stage 11 "
    "day dirty scope protocol passed / data daily incremental sample hardened / "
    "MALF daily incremental sample hardened / alpha signal daily incremental sample "
    "hardened / downstream daily impact schema frozen / live next card moved to "
    "downstream daily incremental runner"
)
PIPELINE_CURRENT_FORMAL_DB_PERMISSION = (
    "released_full_chain_bounded_proof_ledger_only; "
    "one_year_strategy_behavior_replay_blocked_incomplete_natural_year_coverage; "
    "coverage_gap_diagnosis_executed; malf_2024_natural_year_coverage_repair_passed; "
    "year_replay_rerun_blocked; alpha_signal_2024_coverage_repair_passed; "
    "coverage_gap_evidence_incomplete_closeout_passed; "
    "position_2024_coverage_repair_passed; portfolio_plan_2024_coverage_repair_passed; "
    "trade_2024_coverage_repair_passed; system_readout_2024_coverage_repair_passed; "
    "year_replay_source_selection_repair_passed; "
    "year_replay_disposition_decision_passed_truthful_closeout; "
    "stage11_day_protocol_frozen; data_daily_incremental_sample_hardened; "
    "malf_daily_incremental_sample_hardened_without_formal_db_mutation; "
    "alpha_signal_daily_incremental_sample_hardened_without_formal_db_mutation; "
    "downstream_daily_impact_schema_frozen; "
    "downstream_daily_runtime_requires_runner_card; "
    "no_formal_H:/Asteria-data_mutation_under_this_card; "
    "full_rebuild_requires_new_card"
)
POSITION_IMPACT_DATE_FIELDS = [
    "candidate_dt",
    "entry_reference_dt",
    "entry_valid_from",
    "entry_valid_until",
    "exit_reference_dt",
    "exit_valid_from",
    "exit_valid_until",
]
PORTFOLIO_IMPACT_DATE_FIELDS = [
    "candidate_dt",
    "plan_dt",
    "exposure_valid_from",
    "exposure_valid_until",
]
TRADE_IMPACT_DATE_FIELDS = [
    "plan_dt",
    "intent_dt",
    "execution_valid_from",
    "execution_valid_until",
    "execution_dt",
    "rejection_dt",
]
SYSTEM_IMPACT_DATE_FIELDS = ["readout_dt"]
EXPECTED_SCOPE_FIELDS = ["symbol", "trade_date", "timeframe", "source_run_id"]
EXPECTED_LINEAGE_FIELDS = ["source_run_id", "target_run_id"]
EXPECTED_REPLAY_SCOPE_FIELDS = ["symbol", "trade_date", "source_run_id"]
EXPECTED_CHECKPOINT_POLICY = "stage11_daily_protocol_scope"
EXPECTED_REPLAY_SCOPE = ["symbol", "trade_date", "source_run_id"]
EXPECTED_CHECKPOINT_KEY = ["symbol", "trade_date", "source_run_id"]


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


def _load_toml(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _topology_entry(topology: dict, db_name: str) -> dict:
    return next(entry for entry in topology["databases"] if entry["db_name"] == db_name)


def test_downstream_daily_impact_schema_moves_live_next_to_runner() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    registry = _load_toml(repo_root / "governance" / "module_gate_registry.toml")
    pipeline_contract = _load_toml(
        repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    )
    system_contract = _load_toml(
        repo_root / "governance" / "module_api_contracts" / "system_readout.toml"
    )

    modules = {module["module_id"]: module for module in registry["modules"]}
    conclusion_index = (
        repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    ).read_text(encoding="utf-8")
    schema_conclusion = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / f"{DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_RUN_ID}.conclusion.md"
    ).read_text(encoding="utf-8")
    prepared_runner_card = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / f"{DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_RUN_ID}.card.md"
    ).read_text(encoding="utf-8")

    assert registry["active_mainline_module"] == CURRENT_ACTIVE_MAINLINE_MODULE
    assert registry["current_allowed_next_card"] == DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_ACTION
    assert modules["system_readout"]["next_card"] == DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_ACTION
    assert (
        modules["system_readout"]["next_allowed_action"]
        == DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_ACTION
    )
    assert modules["pipeline"]["doc_status"] == PIPELINE_CURRENT_DOC_STATUS
    assert modules["pipeline"]["formal_db_permission"] == PIPELINE_CURRENT_FORMAL_DB_PERMISSION
    assert modules["pipeline"]["next_card"] == DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_ACTION
    assert modules["pipeline"]["proof_run_id"] == PIPELINE_CURRENT_PROOF_RUN_ID
    assert pipeline_contract["next_allowed_action"] == DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_ACTION
    assert pipeline_contract["release_conclusion"] == (
        "docs/04-execution/records/pipeline/"
        "downstream-daily-impact-ledger-schema-card.conclusion.md"
    )
    assert pipeline_contract["evidence_index"] == (
        "docs/04-execution/records/pipeline/"
        "downstream-daily-impact-ledger-schema-card.evidence-index.md"
    )
    assert system_contract["next_allowed_action"] == DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_ACTION
    assert (
        f"| Pipeline | `{DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_RUN_ID}` | "
        "`passed / downstream daily impact schema frozen` |" in conclusion_index
    )
    assert "状态：`passed / downstream daily impact schema frozen`" in schema_conclusion
    assert (
        f"| allowed next action | `{DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_ACTION}` |"
        in schema_conclusion
    )
    assert (
        f"| prepared next card | `{DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_RUN_ID}` |"
        in schema_conclusion
    )
    assert "状态：`prepared / not executed`" in prepared_runner_card


def test_downstream_daily_impact_schema_freezes_contracts_and_topology() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    position_contract = _load_toml(
        repo_root / "governance" / "module_api_contracts" / "position.toml"
    )
    portfolio_contract = _load_toml(
        repo_root / "governance" / "module_api_contracts" / "portfolio_plan.toml"
    )
    trade_contract = _load_toml(repo_root / "governance" / "module_api_contracts" / "trade.toml")
    system_contract = _load_toml(
        repo_root / "governance" / "module_api_contracts" / "system_readout.toml"
    )
    pipeline_contract = _load_toml(
        repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    )
    topology = _load_toml(repo_root / "governance" / "database_topology_registry.toml")

    assert position_contract["daily_protocol_role"] == "writer"
    assert position_contract["daily_protocol_scope_fields"] == EXPECTED_SCOPE_FIELDS
    assert position_contract["daily_protocol_lineage_fields"] == EXPECTED_LINEAGE_FIELDS
    assert position_contract["daily_protocol_replay_scope_fields"] == EXPECTED_REPLAY_SCOPE_FIELDS
    assert position_contract["daily_protocol_impact_date_fields"] == POSITION_IMPACT_DATE_FIELDS
    assert "daily_impact_schema_frozen" in position_contract["gate_state"]

    assert portfolio_contract["daily_protocol_role"] == "writer"
    assert portfolio_contract["daily_protocol_scope_fields"] == EXPECTED_SCOPE_FIELDS
    assert portfolio_contract["daily_protocol_lineage_fields"] == EXPECTED_LINEAGE_FIELDS
    assert portfolio_contract["daily_protocol_replay_scope_fields"] == EXPECTED_REPLAY_SCOPE_FIELDS
    assert portfolio_contract["daily_protocol_impact_date_fields"] == PORTFOLIO_IMPACT_DATE_FIELDS
    assert "daily_impact_schema_frozen" in portfolio_contract["gate_state"]

    assert trade_contract["daily_protocol_role"] == "writer"
    assert trade_contract["daily_protocol_scope_fields"] == EXPECTED_SCOPE_FIELDS
    assert trade_contract["daily_protocol_lineage_fields"] == EXPECTED_LINEAGE_FIELDS
    assert trade_contract["daily_protocol_replay_scope_fields"] == EXPECTED_REPLAY_SCOPE_FIELDS
    assert trade_contract["daily_protocol_impact_date_fields"] == TRADE_IMPACT_DATE_FIELDS
    assert "daily_impact_schema_frozen" in trade_contract["gate_state"]

    assert system_contract["daily_protocol_role"] == "read_only_consumer"
    assert system_contract["daily_protocol_scope_fields"] == EXPECTED_SCOPE_FIELDS
    assert system_contract["daily_protocol_lineage_fields"] == EXPECTED_LINEAGE_FIELDS
    assert system_contract["daily_protocol_replay_scope_fields"] == EXPECTED_REPLAY_SCOPE_FIELDS
    assert system_contract["daily_protocol_impact_date_fields"] == SYSTEM_IMPACT_DATE_FIELDS

    assert pipeline_contract["next_allowed_action"] == DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_ACTION
    assert "daily_impact_schema_frozen" in pipeline_contract["gate_state"]
    assert (
        "downstream_daily_runtime_requires_runner_card" in pipeline_contract["formal_db_permission"]
    )
    assert (
        "no_formal_H:/Asteria-data_mutation_under_this_card"
        in (pipeline_contract["formal_db_permission"])
    )

    for db_name in (
        "position.duckdb",
        "portfolio_plan.duckdb",
        "trade.duckdb",
        "system.duckdb",
    ):
        entry = _topology_entry(topology, db_name)
        assert entry["checkpoint_policy"] == EXPECTED_CHECKPOINT_POLICY
        assert entry["checkpoint_key"] == EXPECTED_CHECKPOINT_KEY
        assert entry["replay_scope"] == EXPECTED_REPLAY_SCOPE


def test_project_governance_rejects_closed_downstream_schema_card_as_live_next_card(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    pipeline_contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    system_contract_path = repo_root / "governance" / "module_api_contracts" / "system_readout.toml"

    registry_text = rewrite_registry_module_fields(
        registry_path.read_text(encoding="utf-8"),
        module_id="system_readout",
        field_updates={"next_card": f'"{DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION}"'},
    )
    registry_text = rewrite_registry_module_fields(
        registry_text,
        module_id="pipeline",
        field_updates={"next_card": f'"{DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION}"'},
    )
    registry_path.write_text(
        registry_text.replace(
            f'current_allowed_next_card = "{DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_ACTION}"',
            f'current_allowed_next_card = "{DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION}"',
            1,
        ),
        encoding="utf-8",
    )
    for path in (pipeline_contract_path, system_contract_path):
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                f'next_allowed_action = "{DOWNSTREAM_DAILY_INCREMENTAL_RUNNER_ACTION}"',
                f'next_allowed_action = "{DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION}"',
                1,
            ),
            encoding="utf-8",
        )

    assert any(
        "current allowed next card must not point to a closed execution conclusion" in message
        for message in _messages(repo_root)
    )
