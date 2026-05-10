from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import duckdb
from tests.unit.pipeline.support import (
    PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID,
    SYSTEM_SOURCE_RUN_ID,
    build_year_replay_rerun_authorized_repo,
    seed_system_source,
)
from tests.unit.pipeline.test_year_replay_coverage_gap_diagnosis import (
    MALF_RUN_ID,
    _seed_scenario,
    _trading_dates,
)

from asteria.pipeline.bootstrap import run_pipeline_bounded_proof
from asteria.pipeline.released_source_selection import (
    resolve_released_year_replay_source_selection,
)
from asteria.pipeline.year_replay_source_selection_repair import (
    run_pipeline_year_replay_source_selection_repair,
)
from asteria.pipeline.year_replay_source_selection_repair_contracts import (
    PIPELINE_DISPOSITION_DECISION_CARD,
    PipelineYearReplaySourceSelectionRepairRequest,
)


def test_resolver_reads_repaired_released_truth_from_current_system_run(tmp_path: Path) -> None:
    full_dates = _trading_dates()
    request = _seed_scenario(
        tmp_path,
        data_dates=full_dates,
        malf_dates=full_dates,
        alpha_dates=full_dates,
        signal_dates=full_dates,
        position_dates=full_dates,
        portfolio_dates=full_dates,
        trade_dates=full_dates,
        system_dates=full_dates,
    )
    with duckdb.connect(str(request.source_system_db)) as con:
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
        tmp_path / "data" / "malf_service_day.duckdb",
        full_dates,
    )

    summary = resolve_released_year_replay_source_selection(
        request.source_system_db,
        target_year=2024,
    )

    assert summary.released_system_run_id == "system-readout-bounded-proof-build-card-20260508-01"
    assert summary.observed_start == "2024-01-02"
    assert summary.observed_end == "2024-12-31"
    assert summary.manifest["malf"].source_run_id == PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID
    assert summary.source_lock_clean is True


def test_year_replay_rerun_audit_uses_repaired_live_manifest_for_source_lock(
    tmp_path: Path,
) -> None:
    seed_system_source(tmp_path)
    repo_root = build_year_replay_rerun_authorized_repo(tmp_path)
    with duckdb.connect(str(tmp_path / "data" / "system.duckdb")) as con:
        con.execute(
            """
            update system_source_manifest
            set source_run_id = ?, source_release_version = ?
            where system_readout_run_id = ? and module_name = 'malf'
            """,
            [
                PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID,
                PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID,
                SYSTEM_SOURCE_RUN_ID,
            ],
        )

    summary = run_pipeline_bounded_proof(
        repo_root=repo_root,
        source_system_db=tmp_path / "data" / "system.duckdb",
        target_pipeline_db=tmp_path / "data" / "pipeline.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01",
        source_chain_release_version=SYSTEM_SOURCE_RUN_ID,
        module_scope="year_replay_rerun",
        target_year=2024,
    )

    assert summary.status == "failed"
    report_payload = json.loads(Path(summary.report_path or "").read_text(encoding="utf-8"))
    check_statuses = {row["check_name"]: row["status"] for row in report_payload["checks"]}
    assert check_statuses["pipeline_year_replay_rerun_malf_source_locked"] == "pass"
    assert check_statuses["pipeline_year_replay_full_year_coverage"] == "fail"


def test_source_selection_repair_promotes_disposition_decision_when_truth_is_clean(
    tmp_path: Path,
) -> None:
    full_dates = _trading_dates()
    diagnosis_request = _seed_scenario(
        tmp_path,
        data_dates=full_dates,
        malf_dates=full_dates,
        alpha_dates=full_dates,
        signal_dates=full_dates,
        position_dates=full_dates,
        portfolio_dates=full_dates,
        trade_dates=full_dates,
        system_dates=full_dates,
    )
    with duckdb.connect(str(diagnosis_request.source_system_db)) as con:
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
        tmp_path / "data" / "malf_service_day.duckdb",
        full_dates,
    )

    summary = run_pipeline_year_replay_source_selection_repair(
        PipelineYearReplaySourceSelectionRepairRequest(
            repo_root=tmp_path / "repo",
            source_system_db=diagnosis_request.source_system_db,
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id="pipeline-year-replay-source-selection-repair-card-20260509-01",
            target_year=2024,
        )
    )

    assert summary.status == "completed"
    assert summary.released_system_run_id == "system-readout-bounded-proof-build-card-20260508-01"
    assert summary.observed_start == "2024-01-02"
    assert summary.observed_end == "2024-12-31"
    assert summary.source_lock_clean is True
    assert summary.followup_attribution == "calendar_semantic_gap_only"
    assert summary.next_card == PIPELINE_DISPOSITION_DECISION_CARD
    assert Path(summary.validated_zip).exists()
    assert (
        tmp_path
        / "report"
        / "pipeline"
        / date.today().isoformat()
        / "pipeline-year-replay-source-selection-repair-card-20260509-01"
        / "manifest.json"
    ).exists()


def _seed_repaired_malf_run(db_path: Path, dates: list[date]) -> None:
    with duckdb.connect(str(db_path)) as con:
        con.executemany(
            "insert into malf_wave_position values (?, ?)",
            [[bar_dt, PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID] for bar_dt in dates],
        )
        con.execute(
            "delete from malf_wave_position where run_id = ?",
            [MALF_RUN_ID],
        )
