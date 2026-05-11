from __future__ import annotations

from pathlib import Path

from tests.unit.pipeline.constants import (
    CURRENT_ALLOWED_NEXT_CARD_ACTION,
    CURRENT_PIPELINE_ACTIVE_CARD,
    PIPELINE_CURRENT_DOC_STATUS,
    PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
    PIPELINE_CURRENT_GATE_STATE,
    PIPELINE_DISPOSITION_DECISION_ACTION,
    PIPELINE_DISPOSITION_DECISION_RUN_ID,
    PIPELINE_SOURCE_SELECTION_REPAIR_RUN_ID,
)
from tests.unit.pipeline.support_repo_builders import (
    _active_card_line,
    _evidence_index_line,
    _release_conclusion_line,
    build_governance_repo,
)
from tests.unit.pipeline.support_state import rewrite_registry_module_fields

PRE_DISPOSITION_DOC_STATUS = (
    "frozen six-doc set / freeze review passed / single-module orchestration build passed / "
    "full-chain dry-run passed / full-chain day bounded proof passed / one-year strategy "
    "behavior replay blocked / coverage gap diagnosis executed / MALF natural-year coverage "
    "repair passed / year replay rerun blocked / alpha-signal coverage repair passed / "
    "downstream coverage gap evidence closeout passed / position 2024 coverage repair "
    "passed / portfolio_plan 2024 coverage repair passed / trade 2024 coverage repair "
    "passed / system_readout 2024 coverage repair handoff passed / pipeline year replay "
    "source-selection repair passed / live next card moved to pipeline disposition decision"
)
PRE_DISPOSITION_GATE_STATE = (
    "single_module_orchestration_build_passed; full_chain_dry_run_passed; "
    "full_chain_day_bounded_proof_passed; one_year_strategy_behavior_replay_blocked; "
    "coverage_gap_diagnosis_executed; malf_2024_natural_year_coverage_repair_passed; "
    "year_replay_rerun_blocked; alpha_signal_2024_coverage_repair_passed; "
    "coverage_gap_evidence_incomplete_closeout_passed; position_2024_coverage_repair_passed; "
    "portfolio_plan_2024_coverage_repair_passed; trade_2024_coverage_repair_passed; "
    "system_readout_2024_coverage_repair_handoff_passed; year_replay_source_selection_repair_passed"
)
PRE_DISPOSITION_FORMAL_DB_PERMISSION = (
    "released_full_chain_bounded_proof_ledger_only; "
    "one_year_strategy_behavior_replay_blocked_incomplete_natural_year_coverage; "
    "coverage_gap_diagnosis_executed; malf_2024_natural_year_coverage_repair_passed; "
    "year_replay_rerun_blocked; alpha_signal_2024_coverage_repair_passed; "
    "coverage_gap_evidence_incomplete_closeout_passed; "
    "position_2024_coverage_repair_passed; portfolio_plan_2024_coverage_repair_passed; "
    "trade_2024_coverage_repair_passed; system_readout_2024_coverage_repair_passed; "
    "year_replay_source_selection_repair_passed; "
    "year_replay_disposition_decision_requires_new_card; full_rebuild_requires_new_card"
)


def build_year_replay_disposition_authorized_repo(tmp_path: Path) -> Path:
    repo_root = build_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_text = registry_text.replace(
        f'current_allowed_next_card = "{CURRENT_ALLOWED_NEXT_CARD_ACTION}"',
        f'current_allowed_next_card = "{PIPELINE_DISPOSITION_DECISION_ACTION}"',
        1,
    ).replace(
        'active_foundation_card = "data-ledger-daily-incremental-hardening-card"',
        'active_foundation_card = "none"',
        1,
    )
    registry_text = rewrite_registry_module_fields(
        registry_text,
        module_id="system_readout",
        field_updates={
            "next_card": f'"{PIPELINE_DISPOSITION_DECISION_ACTION}"',
            "next_allowed_action": f'"{PIPELINE_DISPOSITION_DECISION_ACTION}"',
        },
    )
    registry_text = rewrite_registry_module_fields(
        registry_text,
        module_id="pipeline",
        field_updates={
            "next_card": f'"{PIPELINE_DISPOSITION_DECISION_ACTION}"',
        },
    )
    registry_path.write_text(
        registry_text.replace(
            CURRENT_PIPELINE_ACTIVE_CARD,
            _active_card_line(PIPELINE_SOURCE_SELECTION_REPAIR_RUN_ID),
            1,
        )
        .replace(
            _release_conclusion_line(PIPELINE_DISPOSITION_DECISION_RUN_ID),
            _release_conclusion_line(PIPELINE_SOURCE_SELECTION_REPAIR_RUN_ID),
            1,
        )
        .replace(
            _evidence_index_line(PIPELINE_DISPOSITION_DECISION_RUN_ID),
            _evidence_index_line(PIPELINE_SOURCE_SELECTION_REPAIR_RUN_ID),
            1,
        )
        .replace(
            f'proof_run_id = "{PIPELINE_DISPOSITION_DECISION_RUN_ID}"',
            f'proof_run_id = "{PIPELINE_SOURCE_SELECTION_REPAIR_RUN_ID}"',
            1,
        )
        .replace(
            f'doc_status = "{PIPELINE_CURRENT_DOC_STATUS}"',
            f'doc_status = "{PRE_DISPOSITION_DOC_STATUS}"',
            1,
        )
        .replace(
            f'proof_status = "{PIPELINE_CURRENT_GATE_STATE}"',
            f'proof_status = "{PRE_DISPOSITION_GATE_STATE}"',
            1,
        )
        .replace(
            PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
            PRE_DISPOSITION_FORMAL_DB_PERMISSION,
            1,
        ),
        encoding="utf-8",
    )
    contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    contract_text = contract_path.read_text(encoding="utf-8")
    contract_path.write_text(
        contract_text.replace(
            f'next_allowed_action = "{CURRENT_ALLOWED_NEXT_CARD_ACTION}"',
            f'next_allowed_action = "{PIPELINE_DISPOSITION_DECISION_ACTION}"',
            1,
        )
        .replace(
            _release_conclusion_line(PIPELINE_DISPOSITION_DECISION_RUN_ID),
            _release_conclusion_line(PIPELINE_SOURCE_SELECTION_REPAIR_RUN_ID),
            1,
        )
        .replace(
            _evidence_index_line(PIPELINE_DISPOSITION_DECISION_RUN_ID),
            _evidence_index_line(PIPELINE_SOURCE_SELECTION_REPAIR_RUN_ID),
            1,
        )
        .replace(
            f'gate_state = "{PIPELINE_CURRENT_GATE_STATE}"',
            f'gate_state = "{PRE_DISPOSITION_GATE_STATE}"',
            1,
        )
        .replace(
            PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
            PRE_DISPOSITION_FORMAL_DB_PERMISSION,
            1,
        ),
        encoding="utf-8",
    )
    return repo_root
