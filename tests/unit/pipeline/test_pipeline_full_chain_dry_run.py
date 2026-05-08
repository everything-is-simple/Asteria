from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb
import pytest
from tests.unit.pipeline.support import (
    PIPELINE_BOUNDED_PROOF_CARD_RUN_ID,
    PIPELINE_DRY_RUN_CARD_RUN_ID,
    SYSTEM_SOURCE_RUN_ID,
    build_bounded_proof_authorized_repo,
    build_full_chain_dry_run_prepared_repo,
    build_year_replay_authorized_repo,
    seed_system_source,
)

from asteria.pipeline.bootstrap import run_pipeline_bounded_proof, run_pipeline_build
from asteria.pipeline.contracts import PipelineBuildRequest


def build_request(
    tmp_path: Path,
    *,
    repo_root: Path | None = None,
    mode: str = "dry-run",
    module_scope: str = "full_chain_day",
    run_id: str = PIPELINE_DRY_RUN_CARD_RUN_ID,
) -> PipelineBuildRequest:
    return PipelineBuildRequest(
        repo_root=(repo_root or Path(__file__).resolve().parents[3]),
        source_system_db=tmp_path / "data" / "system.duckdb",
        target_pipeline_db=tmp_path / "data" / "pipeline.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id=run_id,
        mode=mode,
        module_scope=module_scope,
        source_chain_release_version=SYSTEM_SOURCE_RUN_ID,
    )


def test_full_chain_dry_run_build_records_released_day_chain_steps(tmp_path: Path) -> None:
    seed_system_source(tmp_path)
    repo_root = build_full_chain_dry_run_prepared_repo(tmp_path)

    summary = run_pipeline_build(build_request(tmp_path, repo_root=repo_root))

    assert summary.status == "completed"
    assert summary.module_scope == "full_chain_day"
    assert summary.step_count == 7
    assert summary.gate_snapshot_count >= 10
    assert summary.manifest_count >= 11
    with duckdb.connect(str(tmp_path / "data" / "pipeline.duckdb"), read_only=True) as con:
        step_rows = con.execute(
            """
            select step_seq, module_name, step_name, step_status
            from pipeline_step_run
            where pipeline_run_id = ?
            order by step_seq
            """,
            [PIPELINE_DRY_RUN_CARD_RUN_ID],
        ).fetchall()
        run_row = con.execute(
            """
            select module_scope, run_mode, source_release_version, step_count
            from pipeline_run
            where pipeline_run_id = ?
            """,
            [PIPELINE_DRY_RUN_CARD_RUN_ID],
        ).fetchone()
        gate_rows = con.execute(
            """
            select module_name, gate_name
            from module_gate_snapshot
            where pipeline_run_id = ?
            """,
            [PIPELINE_DRY_RUN_CARD_RUN_ID],
        ).fetchall()

    assert run_row == ("full_chain_day", "dry-run", SYSTEM_SOURCE_RUN_ID, 7)
    assert step_rows == [
        (1, "malf", "full_chain_dry_run", "promoted"),
        (2, "alpha", "full_chain_dry_run", "promoted"),
        (3, "signal", "full_chain_dry_run", "promoted"),
        (4, "position", "full_chain_dry_run", "promoted"),
        (5, "portfolio_plan", "full_chain_dry_run", "promoted"),
        (6, "trade", "full_chain_dry_run", "promoted"),
        (7, "system_readout", "full_chain_dry_run", "promoted"),
    ]
    assert ("registry", "current_allowed_next_card") in gate_rows
    assert ("pipeline", "next_card") in gate_rows
    assert ("system_readout", "proof_status") in gate_rows


def test_request_rejects_mixing_single_module_and_full_chain_modes(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="does not support dry-run mode"):
        build_request(tmp_path, mode="dry-run", module_scope="system_readout")
    with pytest.raises(ValueError, match="does not support dry-run mode"):
        PipelineBuildRequest(
            repo_root=Path(__file__).resolve().parents[3],
            source_system_db=tmp_path / "data" / "system.duckdb",
            target_pipeline_db=tmp_path / "data" / "pipeline.duckdb",
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id="pipeline-one-year-strategy-behavior-replay-build-card-20260508-01",
            mode="dry-run",
            module_scope="year_replay",
            source_chain_release_version=SYSTEM_SOURCE_RUN_ID,
            target_year=2024,
        )


def test_request_allows_full_chain_bounded_and_year_replay_scope(tmp_path: Path) -> None:
    bounded_request = build_request(tmp_path, mode="bounded", module_scope="full_chain_day")

    year_replay_request = PipelineBuildRequest(
        repo_root=Path(__file__).resolve().parents[3],
        source_system_db=tmp_path / "data" / "system.duckdb",
        target_pipeline_db=tmp_path / "data" / "pipeline.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="pipeline-one-year-strategy-behavior-replay-build-card-20260508-01",
        mode="bounded",
        module_scope="year_replay",
        source_chain_release_version=SYSTEM_SOURCE_RUN_ID,
        target_year=2024,
    )

    assert bounded_request.schema_version == "pipeline-full-chain-bounded-proof-v1"
    assert bounded_request.pipeline_version == "pipeline-full-chain-day-bounded-proof-v1"
    assert year_replay_request.schema_version == "pipeline-one-year-strategy-behavior-replay-v1"
    assert year_replay_request.pipeline_version == "pipeline-one-year-strategy-behavior-replay-v1"


def test_full_chain_bounded_proof_build_records_released_day_chain_steps(tmp_path: Path) -> None:
    seed_system_source(tmp_path)
    repo_root = build_bounded_proof_authorized_repo(tmp_path)

    summary = run_pipeline_build(
        build_request(
            tmp_path,
            repo_root=repo_root,
            mode="bounded",
            run_id=PIPELINE_BOUNDED_PROOF_CARD_RUN_ID,
        )
    )

    assert summary.status == "completed"
    assert summary.module_scope == "full_chain_day"
    assert summary.hard_fail_count == 0
    with duckdb.connect(str(tmp_path / "data" / "pipeline.duckdb"), read_only=True) as con:
        run_row = con.execute(
            """
            select module_scope, run_mode, source_release_version, step_count,
                   schema_version, pipeline_version
            from pipeline_run
            where pipeline_run_id = ?
            """,
            [PIPELINE_BOUNDED_PROOF_CARD_RUN_ID],
        ).fetchone()
        step_rows = con.execute(
            """
            select step_seq, module_name, step_name, step_status
            from pipeline_step_run
            where pipeline_run_id = ?
            order by step_seq
            """,
            [PIPELINE_BOUNDED_PROOF_CARD_RUN_ID],
        ).fetchall()

    assert run_row == (
        "full_chain_day",
        "bounded",
        SYSTEM_SOURCE_RUN_ID,
        7,
        "pipeline-full-chain-bounded-proof-v1",
        "pipeline-full-chain-day-bounded-proof-v1",
    )
    assert step_rows == [
        (1, "malf", "full_chain_bounded_proof", "promoted"),
        (2, "alpha", "full_chain_bounded_proof", "promoted"),
        (3, "signal", "full_chain_bounded_proof", "promoted"),
        (4, "position", "full_chain_bounded_proof", "promoted"),
        (5, "portfolio_plan", "full_chain_bounded_proof", "promoted"),
        (6, "trade", "full_chain_bounded_proof", "promoted"),
        (7, "system_readout", "full_chain_bounded_proof", "promoted"),
    ]


def test_year_replay_writes_behavior_summary_and_flags_incomplete_natural_year_coverage(
    tmp_path: Path,
) -> None:
    seed_system_source(tmp_path)
    repo_root = build_year_replay_authorized_repo(tmp_path)

    summary = run_pipeline_bounded_proof(
        repo_root=repo_root,
        source_system_db=tmp_path / "data" / "system.duckdb",
        target_pipeline_db=tmp_path / "data" / "pipeline.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="pipeline-one-year-strategy-behavior-replay-build-card-20260508-01",
        source_chain_release_version=SYSTEM_SOURCE_RUN_ID,
        module_scope="year_replay",
        target_year=2024,
    )

    assert summary.status == "failed"
    assert summary.module_scope == "year_replay"
    assert summary.hard_fail_count > 0
    assert Path(summary.validated_zip or "").exists()
    assert (
        tmp_path
        / "report"
        / "pipeline"
        / date.today().isoformat()
        / "pipeline-one-year-strategy-behavior-replay-build-card-20260508-01"
        / "behavior-summary.json"
    ).exists()
