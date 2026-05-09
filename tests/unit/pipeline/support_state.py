from __future__ import annotations

from tests.unit.pipeline.constants import (
    CURRENT_ACTIVE_MAINLINE_MODULE,
    CURRENT_PIPELINE_ACTIVE_CARD,
    MALF_BASELINE_DOC_STATUS,
    MALF_BASELINE_PROOF_STATUS,
    MALF_CURRENT_DOC_STATUS,
    MALF_CURRENT_PROOF_STATUS,
    PIPELINE_COVERAGE_GAP_EVIDENCE_INCOMPLETE_CLOSEOUT_ACTION,
    PIPELINE_CURRENT_DOC_STATUS,
    PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
    PIPELINE_CURRENT_GATE_STATE,
    PIPELINE_MALF_REPAIR_ACTION,
    PIPELINE_MALF_REPAIR_ACTIVE_CARD,
    PIPELINE_MALF_REPAIR_PREPARED_DOC_STATUS,
    PIPELINE_MALF_REPAIR_PREPARED_FORMAL_DB_PERMISSION,
    PIPELINE_MALF_REPAIR_PREPARED_GATE_STATE,
    PIPELINE_MALF_REPAIR_RUN_ID,
)


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
            (
                "current_allowed_next_card = "
                f'"{PIPELINE_COVERAGE_GAP_EVIDENCE_INCOMPLETE_CLOSEOUT_ACTION}"'
            ),
            f'current_allowed_next_card = "{PIPELINE_MALF_REPAIR_ACTION}"',
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
            f'next_card = "{PIPELINE_COVERAGE_GAP_EVIDENCE_INCOMPLETE_CLOSEOUT_ACTION}"',
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
            f'next_allowed_action = "{PIPELINE_COVERAGE_GAP_EVIDENCE_INCOMPLETE_CLOSEOUT_ACTION}"',
            'next_allowed_action = "malf_2024_natural_year_coverage_repair_card"',
            1,
        )
        .replace(
            CURRENT_PIPELINE_ACTIVE_CARD,
            PIPELINE_MALF_REPAIR_ACTIVE_CARD,
            1,
        )
    )
