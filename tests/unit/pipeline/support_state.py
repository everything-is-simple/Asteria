from __future__ import annotations

from tests.unit.pipeline.constants import (
    CURRENT_ACTIVE_MAINLINE_MODULE,
    CURRENT_ALLOWED_NEXT_CARD_ACTION,
    CURRENT_PIPELINE_ACTIVE_CARD,
    DATA_DAILY_HARDENING_ACTION,
    MALF_BASELINE_DOC_STATUS,
    MALF_BASELINE_PROOF_STATUS,
    MALF_CURRENT_DOC_STATUS,
    MALF_CURRENT_PROOF_STATUS,
    PIPELINE_CURRENT_DOC_STATUS,
    PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
    PIPELINE_CURRENT_GATE_STATE,
    PIPELINE_DISPOSITION_DECISION_ACTION,
    PIPELINE_MALF_REPAIR_ACTION,
    PIPELINE_MALF_REPAIR_ACTIVE_CARD,
    PIPELINE_MALF_REPAIR_PREPARED_DOC_STATUS,
    PIPELINE_MALF_REPAIR_PREPARED_FORMAL_DB_PERMISSION,
    PIPELINE_MALF_REPAIR_PREPARED_GATE_STATE,
    PIPELINE_MALF_REPAIR_RUN_ID,
    PIPELINE_SOURCE_SELECTION_REPAIR_ACTION,
    PIPELINE_STAGE11_PROTOCOL_ACTION,
)

POSITION_CURRENT_DOC_STATUS = (
    'doc_status = "freeze review passed / release decision passed / bounded proof passed / '
    "2024 coverage repair passed / downstream breakpoint moved to portfolio_plan / "
    "daily impact schema frozen / downstream daily incremental sample hardened / "
    'full build not executed"'
)
POSITION_BASELINE_DOC_STATUS = (
    'doc_status = "freeze review passed / release decision passed / bounded proof passed / '
    'full build not executed"'
)
POSITION_CURRENT_ACTIVE_CARD = (
    'active_card = "docs/04-execution/records/position/'
    'position-2024-coverage-repair-card-20260509-01.card.md"'
)
POSITION_BASELINE_ACTIVE_CARD = (
    'active_card = "docs/04-execution/records/position/'
    'position-bounded-proof-build-card-20260506-01.card.md"'
)
POSITION_CURRENT_PAUSE = (
    'position_construction_pause = "bounded_proof_passed; '
    "2024_coverage_repair_passed; downstream_breakpoint_moved_to_portfolio_plan; "
    "daily_impact_schema_frozen; downstream_daily_runtime_requires_runner_card; "
    'full_build_requires_new_card"'
)
POSITION_BASELINE_PAUSE = (
    'position_construction_pause = "bounded_proof_passed; full_build_requires_new_card"'
)
POSITION_CURRENT_QUEUE = (
    'pre_position_repair_queue = "data_reference_target_maintenance_scope -> '
    "data_reference_target_maintenance_closeout -> malf_week_bounded_proof_build -> "
    "malf_month_bounded_proof_build -> alpha_production_builder_hardening -> "
    "signal_production_builder_hardening -> upstream_pre_position_release_decision; "
    "closed=position_bounded_proof_build_card; latest_execution="
    "position_2024_coverage_repair_card_passed; handoff_completed="
    "trade_2024_coverage_repair_card; stage11_schema_frozen="
    "downstream_daily_impact_ledger_schema_card; current="
    'downstream_daily_incremental_runner_build_card"'
)
POSITION_BASELINE_QUEUE = (
    'pre_position_repair_queue = "data_reference_target_maintenance_scope -> '
    "data_reference_target_maintenance_closeout -> malf_week_bounded_proof_build -> "
    "malf_month_bounded_proof_build -> alpha_production_builder_hardening -> "
    "signal_production_builder_hardening -> upstream_pre_position_release_decision; "
    'closed=position_bounded_proof_build_card; current=portfolio_plan_freeze_review"'
)
POSITION_CURRENT_PROOF_STATUS = (
    'proof_status = "bounded_proof_passed; 2024_coverage_repair_passed; '
    "downstream_breakpoint_moved_to_portfolio_plan; daily_impact_schema_frozen; "
    'downstream_daily_incremental_sample_hardened; full_build_not_executed"'
)
POSITION_BASELINE_PROOF_STATUS = 'proof_status = "bounded_proof_passed; full_build_not_executed"'


def rewrite_registry_module_fields(
    registry_text: str,
    *,
    module_id: str,
    field_updates: dict[str, str],
) -> str:
    lines = registry_text.splitlines()
    in_module = False
    for idx, line in enumerate(lines):
        if line == f'module_id = "{module_id}"':
            in_module = True
            continue
        if in_module and line == "[[modules]]":
            break
        if not in_module:
            continue
        for field_name, field_value in field_updates.items():
            if line.startswith(f"{field_name} = "):
                lines[idx] = f"{field_name} = {field_value}"
                break
    return "\n".join(lines) + "\n"


def rewind_current_malf_repair_state(registry_text: str) -> str:
    return (
        registry_text.replace(
            f'active_mainline_module = "{CURRENT_ACTIVE_MAINLINE_MODULE}"',
            'active_mainline_module = "system_readout"',
            1,
        )
        .replace(
            f'doc_status = "{MALF_CURRENT_DOC_STATUS}"\nallow_build = false',
            f'doc_status = "{MALF_BASELINE_DOC_STATUS}"\nallow_build = false',
            1,
        )
        .replace(
            (f'current_allowed_next_card = "{CURRENT_ALLOWED_NEXT_CARD_ACTION}"'),
            f'current_allowed_next_card = "{PIPELINE_MALF_REPAIR_ACTION}"',
            1,
        )
        .replace(
            'active_foundation_card = "data-ledger-daily-incremental-hardening-card"',
            'active_foundation_card = "none"',
            1,
        )
        .replace(
            (
                f'next_card = "pipeline_one_year_strategy_behavior_replay_rerun_build_card"\n'
                'active_card = "docs/04-execution/records/malf/'
                f'{PIPELINE_MALF_REPAIR_RUN_ID}.card.md"\n'
                "allow_review = false\n"
                f'proof_status = "{MALF_CURRENT_PROOF_STATUS}"'
            ),
            (
                'next_card = "alpha_production_builder_hardening"\n'
                'active_card = "docs/04-execution/records/malf/'
                'malf-month-bounded-proof-build-20260506-01.card.md"\n'
                "allow_review = false\n"
                f'proof_status = "{MALF_BASELINE_PROOF_STATUS}"'
            ),
            1,
        )
        .replace(
            f'doc_status = "{PIPELINE_CURRENT_DOC_STATUS}"',
            f'doc_status = "{PIPELINE_MALF_REPAIR_PREPARED_DOC_STATUS}"',
            1,
        )
        .replace(
            f'next_card = "{PIPELINE_SOURCE_SELECTION_REPAIR_ACTION}"',
            f'next_card = "{PIPELINE_MALF_REPAIR_ACTION}"',
            1,
        )
        .replace(
            f'next_card = "{PIPELINE_DISPOSITION_DECISION_ACTION}"',
            f'next_card = "{PIPELINE_MALF_REPAIR_ACTION}"',
            1,
        )
        .replace(
            f'next_card = "{PIPELINE_STAGE11_PROTOCOL_ACTION}"',
            f'next_card = "{PIPELINE_MALF_REPAIR_ACTION}"',
            1,
        )
        .replace(
            f'next_card = "{DATA_DAILY_HARDENING_ACTION}"',
            f'next_card = "{PIPELINE_MALF_REPAIR_ACTION}"',
            1,
        )
        .replace(
            f'proof_status = "{PIPELINE_CURRENT_GATE_STATE}"',
            f'proof_status = "{PIPELINE_MALF_REPAIR_PREPARED_GATE_STATE}"',
            1,
        )
        .replace(
            PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
            PIPELINE_MALF_REPAIR_PREPARED_FORMAL_DB_PERMISSION,
            1,
        )
        .replace(
            f'next_allowed_action = "{PIPELINE_SOURCE_SELECTION_REPAIR_ACTION}"',
            'next_allowed_action = "malf_2024_natural_year_coverage_repair_card"',
            1,
        )
        .replace(
            f'next_allowed_action = "{PIPELINE_DISPOSITION_DECISION_ACTION}"',
            'next_allowed_action = "malf_2024_natural_year_coverage_repair_card"',
            1,
        )
        .replace(
            f'next_allowed_action = "{PIPELINE_STAGE11_PROTOCOL_ACTION}"',
            'next_allowed_action = "malf_2024_natural_year_coverage_repair_card"',
            1,
        )
        .replace(
            f'next_allowed_action = "{DATA_DAILY_HARDENING_ACTION}"',
            'next_allowed_action = "malf_2024_natural_year_coverage_repair_card"',
            1,
        )
        .replace(
            CURRENT_PIPELINE_ACTIVE_CARD,
            PIPELINE_MALF_REPAIR_ACTIVE_CARD,
            1,
        )
        .replace(
            POSITION_CURRENT_DOC_STATUS,
            POSITION_BASELINE_DOC_STATUS,
            1,
        )
        .replace(
            'next_card = "position_2024_coverage_repair_card"',
            'next_card = "portfolio_plan_freeze_review"',
            1,
        )
        .replace(
            POSITION_CURRENT_ACTIVE_CARD,
            POSITION_BASELINE_ACTIVE_CARD,
            1,
        )
        .replace(
            POSITION_CURRENT_PAUSE,
            POSITION_BASELINE_PAUSE,
            1,
        )
        .replace(
            POSITION_CURRENT_QUEUE,
            POSITION_BASELINE_QUEUE,
            1,
        )
        .replace(
            POSITION_CURRENT_PROOF_STATUS,
            POSITION_BASELINE_PROOF_STATUS,
            1,
        )
        .replace(
            'next_allowed_action = "position_2024_coverage_repair_card"',
            'next_allowed_action = "portfolio_plan_freeze_review"',
            1,
        )
    )
