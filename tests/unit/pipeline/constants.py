SYSTEM_SOURCE_RUN_ID = "system-readout-bounded-proof-unit-001"
PIPELINE_RUN_ID = "pipeline-single-module-orchestration-build-card-20260508-01"
PIPELINE_SCOPE_FREEZE_RUN_ID = "pipeline-build-runtime-authorization-scope-freeze-20260508-01"
PIPELINE_DRY_RUN_SCOPE_FREEZE_RUN_ID = (
    "pipeline-full-chain-dry-run-authorization-scope-freeze-20260508-01"
)
PIPELINE_DRY_RUN_CARD_RUN_ID = "pipeline-full-chain-dry-run-card-20260508-01"
PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID = (
    "pipeline-full-chain-bounded-proof-authorization-scope-freeze-20260508-01"
)
PIPELINE_BOUNDED_PROOF_CARD_RUN_ID = "pipeline-full-chain-bounded-proof-build-card-20260508-01"
PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID = "pipeline-full-chain-bounded-proof-closeout-20260508-01"
PIPELINE_YEAR_REPLAY_SCOPE_FREEZE_RUN_ID = (
    "pipeline-one-year-strategy-behavior-replay-authorization-scope-freeze-20260508-01"
)
PIPELINE_YEAR_REPLAY_CARD_RUN_ID = (
    "pipeline-one-year-strategy-behavior-replay-build-card-20260508-01"
)
PIPELINE_SOURCE_SELECTION_REPAIR_RUN_ID = (
    "pipeline-year-replay-source-selection-repair-card-20260509-01"
)
PIPELINE_DISPOSITION_DECISION_RUN_ID = "pipeline-year-replay-disposition-decision-card-20260510-01"
PIPELINE_YEAR_REPLAY_RERUN_CARD_RUN_ID = (
    "pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01"
)
PIPELINE_YEAR_REPLAY_RERUN_CARD_ACTION = (
    "pipeline_one_year_strategy_behavior_replay_rerun_build_card"
)
PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID = (
    "malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001"
)
PIPELINE_COVERAGE_GAP_DIAGNOSIS_RUN_ID = (
    "pipeline-year-replay-coverage-gap-diagnosis-and-repair-scope-freeze-20260509-01"
)
PIPELINE_MALF_REPAIR_RUN_ID = "malf-2024-natural-year-coverage-repair-card-20260509-01"
PIPELINE_ALPHA_SIGNAL_REPAIR_RUN_ID = "alpha-signal-2024-coverage-repair-card-20260509-01"
PIPELINE_COVERAGE_GAP_EVIDENCE_INCOMPLETE_CLOSEOUT_RUN_ID = (
    "coverage-gap-evidence-incomplete-closeout-card-20260509-01"
)
PIPELINE_DRY_RUN_CARD_ACTION = "pipeline_full_chain_dry_run_card"
PIPELINE_BOUNDED_PROOF_CARD_ACTION = "pipeline_full_chain_bounded_proof_build_card"
PIPELINE_YEAR_REPLAY_CARD_ACTION = "pipeline_one_year_strategy_behavior_replay_build_card"
PIPELINE_COVERAGE_GAP_DIAGNOSIS_ACTION = (
    "pipeline_year_replay_coverage_gap_diagnosis_and_repair_scope_freeze"
)
PIPELINE_MALF_REPAIR_ACTION = "malf_2024_natural_year_coverage_repair_card"
PIPELINE_ALPHA_SIGNAL_REPAIR_ACTION = "alpha_signal_2024_coverage_repair_card"
PIPELINE_COVERAGE_GAP_EVIDENCE_INCOMPLETE_CLOSEOUT_ACTION = (
    "coverage_gap_evidence_incomplete_closeout_card"
)
PIPELINE_POSITION_REPAIR_ACTION = "position_2024_coverage_repair_card"
PIPELINE_SOURCE_SELECTION_REPAIR_ACTION = "pipeline_year_replay_source_selection_repair_card"
PIPELINE_DISPOSITION_DECISION_ACTION = "pipeline_year_replay_disposition_decision_card"
CURRENT_ALLOWED_NEXT_CARD_ACTION = PIPELINE_DISPOSITION_DECISION_ACTION
CURRENT_ACTIVE_MAINLINE_MODULE = "system_readout"
CURRENT_PIPELINE_ACTIVE_CARD = (
    'active_card = "docs/04-execution/records/pipeline/'
    'pipeline-year-replay-source-selection-repair-card-20260509-01.card.md"'
)
PIPELINE_MALF_REPAIR_ACTIVE_CARD = (
    'active_card = "docs/04-execution/records/malf/'
    'malf-2024-natural-year-coverage-repair-card-20260509-01.card.md"'
)
MALF_CURRENT_DOC_STATUS = (
    "delivered six-doc set / v1.4 day runtime sync passed / week/month bounded proof passed"
)
MALF_BASELINE_DOC_STATUS = (
    "delivered six-doc set / v1.4 day runtime sync passed / week/month bounded proof passed"
)
MALF_CURRENT_PROOF_STATUS = (
    "day_bounded_proof_passed; dense_bar_snapshot_resolution_passed; "
    "complete_alignment_closeout_passed; v1_4_day_runtime_sync_implementation_passed; "
    "week_bounded_proof_passed; month_bounded_proof_passed; "
    "2024_natural_year_coverage_repair_passed"
)
MALF_BASELINE_PROOF_STATUS = (
    "day_bounded_proof_passed; dense_bar_snapshot_resolution_passed; "
    "complete_alignment_closeout_passed; v1_4_day_runtime_sync_implementation_passed; "
    "week_bounded_proof_passed; month_bounded_proof_passed"
)
PIPELINE_DRY_RUN_PASSED_DOC_STATUS = (
    "frozen six-doc set / freeze review passed / single-module orchestration build passed / "
    "full-chain dry-run passed"
)
PIPELINE_YEAR_REPLAY_PREPARED_DOC_STATUS = (
    "frozen six-doc set / freeze review passed / single-module orchestration build passed / "
    "full-chain dry-run passed / full-chain day bounded proof passed / one-year strategy "
    "behavior replay authorization scope freeze passed / year replay prepared"
)
PIPELINE_MALF_REPAIR_PREPARED_DOC_STATUS = (
    "frozen six-doc set / freeze review passed / single-module orchestration build passed / "
    "full-chain dry-run passed / full-chain day bounded proof passed / one-year strategy "
    "behavior replay blocked / coverage gap diagnosis executed / MALF natural-year coverage "
    "repair prepared"
)
PIPELINE_CURRENT_DOC_STATUS = (
    "frozen six-doc set / freeze review passed / single-module orchestration build passed / "
    "full-chain dry-run passed / full-chain day bounded proof passed / one-year strategy "
    "behavior replay blocked / coverage gap diagnosis executed / MALF natural-year coverage "
    "repair passed / year replay rerun blocked / alpha-signal coverage repair passed / "
    "downstream coverage gap evidence closeout passed / position 2024 coverage repair "
    "passed / portfolio_plan 2024 coverage repair passed / trade 2024 coverage repair "
    "passed / system_readout 2024 coverage repair handoff passed / pipeline year replay "
    "source-selection repair passed / live next card moved to pipeline disposition decision"
)
PIPELINE_FULL_CHAIN_PREPARED_DOC_STATUS = (
    "frozen six-doc set / freeze review passed / single-module orchestration build passed / "
    "full-chain dry-run prepared"
)
PIPELINE_FULL_CHAIN_PASSED_DOC_STATUS = PIPELINE_DRY_RUN_PASSED_DOC_STATUS
PIPELINE_PREPARED_DOC_STATUS = (
    "frozen six-doc set / freeze review passed / single-module orchestration build prepared / "
    "build not executed"
)
PIPELINE_RELEASE_CONCLUSION = (
    f'release_conclusion = "docs/04-execution/records/pipeline/{PIPELINE_RUN_ID}.conclusion.md"'
)
PIPELINE_DRY_RUN_RELEASE_CONCLUSION = (
    "release_conclusion = "
    f'"docs/04-execution/records/pipeline/{PIPELINE_DRY_RUN_CARD_RUN_ID}.conclusion.md"'
)
PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_CONCLUSION = (
    "release_conclusion = "
    f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID}.conclusion.md"'
)
PIPELINE_SCOPE_FREEZE_CONCLUSION = (
    f"release_conclusion = "
    f'"docs/04-execution/records/pipeline/{PIPELINE_SCOPE_FREEZE_RUN_ID}.conclusion.md"'
)
PIPELINE_RELEASE_EVIDENCE_INDEX = (
    f'evidence_index = "docs/04-execution/records/pipeline/{PIPELINE_RUN_ID}.evidence-index.md"'
)
PIPELINE_DRY_RUN_RELEASE_EVIDENCE_INDEX = (
    "evidence_index = "
    f'"docs/04-execution/records/pipeline/{PIPELINE_DRY_RUN_CARD_RUN_ID}.evidence-index.md"'
)
PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_EVIDENCE_INDEX = (
    "evidence_index = "
    f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID}.evidence-index.md"'
)
PIPELINE_SCOPE_FREEZE_EVIDENCE_INDEX = (
    f"evidence_index = "
    f'"docs/04-execution/records/pipeline/{PIPELINE_SCOPE_FREEZE_RUN_ID}.evidence-index.md"'
)
PIPELINE_DRY_RUN_GATE_STATE = (
    "single_module_orchestration_build_passed; full_chain_dry_run_passed; "
    "full_chain_bounded_proof_not_opened"
)
PIPELINE_BOUNDED_PROOF_GATE_STATE = (
    "single_module_orchestration_build_passed; full_chain_dry_run_passed; "
    "full_chain_day_bounded_proof_passed; one_year_strategy_behavior_replay_not_opened"
)
PIPELINE_MALF_REPAIR_PREPARED_GATE_STATE = (
    "single_module_orchestration_build_passed; full_chain_dry_run_passed; "
    "full_chain_day_bounded_proof_passed; one_year_strategy_behavior_replay_blocked; "
    "coverage_gap_diagnosis_executed; malf_2024_natural_year_coverage_repair_prepared"
)
PIPELINE_CURRENT_GATE_STATE = (
    "single_module_orchestration_build_passed; full_chain_dry_run_passed; "
    "full_chain_day_bounded_proof_passed; one_year_strategy_behavior_replay_blocked; "
    "coverage_gap_diagnosis_executed; malf_2024_natural_year_coverage_repair_passed; "
    "year_replay_rerun_blocked; alpha_signal_2024_coverage_repair_passed; "
    "coverage_gap_evidence_incomplete_closeout_passed; position_2024_coverage_repair_passed; "
    "portfolio_plan_2024_coverage_repair_passed; trade_2024_coverage_repair_passed; "
    "system_readout_2024_coverage_repair_handoff_passed; "
    "year_replay_source_selection_repair_passed"
)
PIPELINE_PREPARED_GATE_STATE = (
    "single_module_orchestration_build_passed; full_chain_dry_run_prepared; full_chain_not_executed"
)
PIPELINE_DRY_RUN_FORMAL_DB_PERMISSION = (
    "released_full_chain_dry_run_ledger_only; bounded_proof_requires_new_card"
)
PIPELINE_BOUNDED_PROOF_FORMAL_DB_PERMISSION = (
    "released_full_chain_bounded_proof_ledger_only; "
    "one_year_strategy_behavior_replay_requires_new_card"
)
PIPELINE_MALF_REPAIR_PREPARED_FORMAL_DB_PERMISSION = (
    "released_full_chain_bounded_proof_ledger_only; "
    "one_year_strategy_behavior_replay_blocked_incomplete_natural_year_coverage; "
    "coverage_gap_diagnosis_executed; malf_2024_natural_year_coverage_repair_prepared; "
    "full_rebuild_requires_new_card"
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
    "year_replay_disposition_decision_requires_new_card; full_rebuild_requires_new_card"
)
PIPELINE_PREPARED_FORMAL_DB_PERMISSION = (
    "released_single_module_orchestration_ledger_only; "
    "full_chain_dry_run_prepared_not_executed; bounded_proof_requires_new_card"
)
PIPELINE_DRY_RUN_INPUT_BOUNDARY = (
    'input_boundary = "orchestration_metadata_only; '
    'released_full_chain_day_bounded_surfaces_dry_run_only"'
)
PIPELINE_BOUNDED_INPUT_BOUNDARY = (
    'input_boundary = "orchestration_metadata_only; released_full_chain_day_bounded_surfaces"'
)
