from __future__ import annotations

from pathlib import Path

import duckdb
import pytest
from tests.unit.pipeline.support import (
    PIPELINE_DRY_RUN_CARD_RUN_ID,
    SYSTEM_SOURCE_RUN_ID,
    build_full_chain_dry_run_prepared_repo,
    seed_system_source,
)

from asteria.pipeline.bootstrap import run_pipeline_build
from asteria.pipeline.contracts import PipelineBuildRequest


def build_request(
    tmp_path: Path,
    *,
    repo_root: Path | None = None,
    mode: str = "dry-run",
    module_scope: str = "full_chain_day",
) -> PipelineBuildRequest:
    return PipelineBuildRequest(
        repo_root=(repo_root or Path(__file__).resolve().parents[3]),
        source_system_db=tmp_path / "data" / "system.duckdb",
        target_pipeline_db=tmp_path / "data" / "pipeline.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id=PIPELINE_DRY_RUN_CARD_RUN_ID,
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
    with pytest.raises(ValueError, match="requires dry-run/resume/audit-only mode"):
        build_request(tmp_path, mode="bounded", module_scope="full_chain_day")
