from __future__ import annotations

from pathlib import Path

import duckdb
from tests.unit.pipeline.support import (
    PIPELINE_STAGE11_PROTOCOL_ACTION,
    PIPELINE_STAGE11_PROTOCOL_RUN_ID,
    PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID,
    build_year_replay_disposition_authorized_repo,
)
from tests.unit.pipeline.test_pipeline_year_replay_source_selection_repair import (
    _seed_repaired_malf_run,
)
from tests.unit.pipeline.test_year_replay_coverage_gap_diagnosis import (
    _seed_scenario,
    _trading_dates,
)

from asteria.pipeline.year_replay_disposition_decision import (
    run_pipeline_year_replay_disposition_decision,
)
from asteria.pipeline.year_replay_disposition_decision_contracts import (
    PIPELINE_DISPOSITION_DECISION_OUTCOME,
    PipelineYearReplayDispositionDecisionRequest,
)


def test_disposition_decides_truthful_closeout_and_stage11_handoff(
    tmp_path: Path,
) -> None:
    repo_root = build_year_replay_disposition_authorized_repo(tmp_path)
    full_dates = _trading_dates()
    seeded = _seed_scenario(
        tmp_path / "runtime",
        data_dates=full_dates,
        malf_dates=full_dates,
        alpha_dates=full_dates,
        signal_dates=full_dates,
        position_dates=full_dates,
        portfolio_dates=full_dates,
        trade_dates=full_dates,
        system_dates=full_dates,
    )
    with duckdb.connect(str(seeded.source_system_db)) as con:
        con.execute(
            """
            update system_source_manifest
            set source_run_id = ?, source_release_version = ?
            where system_readout_run_id = ? and module_name = 'malf'
            """,
            [
                PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID,
                PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID,
                "system-readout-bounded-proof-build-card-20260508-01",
            ],
        )
    _seed_repaired_malf_run(
        tmp_path / "runtime" / "data" / "malf_service_day.duckdb",
        full_dates,
    )

    summary = run_pipeline_year_replay_disposition_decision(
        PipelineYearReplayDispositionDecisionRequest(
            repo_root=repo_root,
            source_system_db=seeded.source_system_db,
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id="pipeline-year-replay-disposition-decision-card-20260510-01",
            target_year=2024,
        )
    )

    assert summary.status == "completed"
    assert summary.decision == PIPELINE_DISPOSITION_DECISION_OUTCOME
    assert summary.released_system_run_id == "system-readout-bounded-proof-build-card-20260508-01"
    assert summary.observed_start == "2024-01-02"
    assert summary.observed_end == "2024-12-31"
    assert summary.source_lock_clean is True
    assert summary.followup_attribution == "calendar_semantic_gap_only"
    assert summary.full_year_audit_still_requires_full_natural_year is True
    assert summary.closeout_allowed is True
    assert summary.rerun_recommended is False
    assert summary.next_card == PIPELINE_STAGE11_PROTOCOL_RUN_ID
    assert summary.next_action == PIPELINE_STAGE11_PROTOCOL_ACTION
    assert Path(summary.validated_zip).exists()
    assert Path(summary.manifest_path).exists()


def test_disposition_rejects_closeout_when_source_lock_is_not_clean(tmp_path: Path) -> None:
    repo_root = build_year_replay_disposition_authorized_repo(tmp_path)
    full_dates = _trading_dates()
    seeded = _seed_scenario(
        tmp_path / "runtime",
        data_dates=full_dates,
        malf_dates=full_dates,
        alpha_dates=full_dates,
        signal_dates=full_dates,
        position_dates=full_dates,
        portfolio_dates=full_dates,
        trade_dates=full_dates,
        system_dates=full_dates,
    )

    summary = run_pipeline_year_replay_disposition_decision(
        PipelineYearReplayDispositionDecisionRequest(
            repo_root=repo_root,
            source_system_db=seeded.source_system_db,
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id="pipeline-year-replay-disposition-decision-card-20260510-01",
            target_year=2024,
        )
    )

    assert summary.status == "failed"
    assert summary.source_lock_clean is False
    assert summary.closeout_allowed is False
    assert summary.rerun_recommended is False
    assert summary.next_card == "pipeline-year-replay-disposition-decision-card-20260510-01"
    assert summary.next_action == "pipeline_year_replay_disposition_decision_card"
