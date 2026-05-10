from __future__ import annotations

from pathlib import Path

from tests.unit.pipeline import constants as pipeline_constants
from tests.unit.pipeline import support_repo_builders as repo_builders
from tests.unit.pipeline.constants import *  # noqa: F403
from tests.unit.system_readout.support import build_request as build_system_request
from tests.unit.system_readout.support import seed_chain

from asteria.system_readout.bootstrap import run_system_readout_build

build_bounded_proof_authorized_repo = repo_builders.build_bounded_proof_authorized_repo
build_full_chain_dry_run_prepared_repo = repo_builders.build_full_chain_dry_run_prepared_repo
build_governance_repo = repo_builders.build_governance_repo
build_prepared_pipeline_repo = repo_builders.build_prepared_pipeline_repo
build_year_replay_authorized_repo = repo_builders.build_year_replay_authorized_repo
build_year_replay_rerun_authorized_repo = repo_builders.build_year_replay_rerun_authorized_repo

CURRENT_ACTIVE_MAINLINE_MODULE = pipeline_constants.CURRENT_ACTIVE_MAINLINE_MODULE
PIPELINE_FULL_CHAIN_PASSED_DOC_STATUS = pipeline_constants.PIPELINE_FULL_CHAIN_PASSED_DOC_STATUS
PIPELINE_ALPHA_SIGNAL_REPAIR_RUN_ID = pipeline_constants.PIPELINE_ALPHA_SIGNAL_REPAIR_RUN_ID
PIPELINE_SOURCE_SELECTION_REPAIR_RUN_ID = pipeline_constants.PIPELINE_SOURCE_SELECTION_REPAIR_RUN_ID
PIPELINE_DISPOSITION_DECISION_RUN_ID = pipeline_constants.PIPELINE_DISPOSITION_DECISION_RUN_ID
PIPELINE_COVERAGE_GAP_EVIDENCE_INCOMPLETE_CLOSEOUT_RUN_ID = (
    pipeline_constants.PIPELINE_COVERAGE_GAP_EVIDENCE_INCOMPLETE_CLOSEOUT_RUN_ID
)
PIPELINE_COVERAGE_GAP_EVIDENCE_INCOMPLETE_CLOSEOUT_ACTION = (
    pipeline_constants.PIPELINE_COVERAGE_GAP_EVIDENCE_INCOMPLETE_CLOSEOUT_ACTION
)
PIPELINE_SOURCE_SELECTION_REPAIR_ACTION = pipeline_constants.PIPELINE_SOURCE_SELECTION_REPAIR_ACTION
PIPELINE_YEAR_REPLAY_CARD_RUN_ID = pipeline_constants.PIPELINE_YEAR_REPLAY_CARD_RUN_ID
PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID = (
    pipeline_constants.PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID
)
SYSTEM_SOURCE_RUN_ID = pipeline_constants.SYSTEM_SOURCE_RUN_ID
CURRENT_ALLOWED_NEXT_CARD_ACTION = pipeline_constants.CURRENT_ALLOWED_NEXT_CARD_ACTION


def seed_system_source(tmp_path: Path) -> Path:
    seed_chain(tmp_path)
    summary = run_system_readout_build(build_system_request(tmp_path))
    if summary.hard_fail_count != 0:
        raise AssertionError(f"seed system source failed: {summary.as_dict()}")
    return tmp_path / "data" / "system.duckdb"
