from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

from asteria.pipeline.contracts import (
    PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID,
    YEAR_REPLAY_MODULE_SCOPES,
    PipelineBuildRequest,
    PipelineBuildSummary,
)


def write_pipeline_evidence(
    request: PipelineBuildRequest,
    summary: PipelineBuildSummary,
) -> dict[str, str]:
    report_dir = request.report_root / "pipeline" / utc_now().date().isoformat() / request.run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    stage_name, title = _stage_metadata(request)
    manifest = {
        "run_id": request.run_id,
        "module": "pipeline",
        "stage": stage_name,
        "status": "passed" if summary.hard_fail_count == 0 else "failed",
        "module_scope": request.module_scope,
        "hard_fail_count": summary.hard_fail_count,
        "step_count": summary.step_count,
        "gate_snapshot_count": summary.gate_snapshot_count,
        "manifest_count": summary.manifest_count,
        "audit_count": summary.audit_count,
        "source_chain_release_version": request.source_chain_release_version,
        "source_system_db": str(request.source_system_db),
        "target_pipeline_db": str(request.target_pipeline_db),
    }
    manifest_path = report_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    behavior_summary_path = _write_behavior_summary(report_dir, request)
    closeout_path = report_dir / "closeout.md"
    closeout_path.write_text(
        "\n".join(
            [
                title,
                "",
                f"- run_id: `{request.run_id}`",
                f"- status: `{manifest['status']}`",
                f"- module_scope: `{request.module_scope}`",
                f"- step_count: `{summary.step_count}`",
                f"- hard_fail_count: `{summary.hard_fail_count}`",
                (
                    f"- behavior_summary: `{behavior_summary_path}`"
                    if behavior_summary_path is not None
                    else ""
                ),
            ]
        ),
        encoding="utf-8",
    )
    validated_zip = request.validated_root / f"Asteria-{request.run_id}.zip"
    validated_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(validated_zip, "w") as archive:
        archive.write(manifest_path, arcname="manifest.json")
        archive.write(closeout_path, arcname="closeout.md")
        if behavior_summary_path is not None:
            archive.write(behavior_summary_path, arcname="behavior-summary.json")
        if request.target_pipeline_db.exists():
            archive.write(request.target_pipeline_db, arcname="pipeline.duckdb")
    return {
        "manifest_path": str(manifest_path),
        "closeout_path": str(closeout_path),
        "validated_zip": str(validated_zip),
    }


def _stage_metadata(request: PipelineBuildRequest) -> tuple[str, str]:
    if request.module_scope == "system_readout":
        return (
            "single_module_orchestration_build",
            "# Pipeline Single-Module Orchestration Build Closeout",
        )
    if request.module_scope == "year_replay":
        return (
            "one_year_strategy_behavior_replay",
            "# Pipeline One-Year Strategy Behavior Replay Closeout",
        )
    if request.module_scope == "year_replay_rerun":
        return (
            "one_year_strategy_behavior_replay_rerun",
            "# Pipeline One-Year Strategy Behavior Replay Rerun Closeout",
        )
    if request.mode == "bounded":
        return "full_chain_bounded_proof", "# Pipeline Full-Chain Bounded Proof Closeout"
    return "full_chain_dry_run", "# Pipeline Full-Chain Dry-Run Closeout"


def _write_behavior_summary(report_dir: Path, request: PipelineBuildRequest) -> Path | None:
    if request.module_scope not in YEAR_REPLAY_MODULE_SCOPES or request.target_year is None:
        return None

    summary_path = report_dir / "behavior-summary.json"
    year_start = f"{request.target_year}-01-01"
    year_end = f"{request.target_year}-12-31"
    with duckdb.connect(str(request.source_system_db), read_only=True) as con:
        coverage_row = con.execute(
            """
            select min(readout_dt), max(readout_dt), count(*)
            from system_chain_readout
            where system_readout_run_id = ?
              and readout_dt >= ?
              and readout_dt <= ?
            """,
            [request.source_chain_release_version, year_start, year_end],
        ).fetchone()
        readout_status_rows = con.execute(
            """
            select readout_status, count(*)
            from system_chain_readout
            where system_readout_run_id = ?
              and readout_dt >= ?
              and readout_dt <= ?
            group by readout_status
            order by readout_status
            """,
            [request.source_chain_release_version, year_start, year_end],
        ).fetchall()
        manifest_rows = con.execute(
            """
            select module_name, source_db, source_run_id
            from system_source_manifest
            where system_readout_run_id = ?
            """,
            [request.source_chain_release_version],
        ).fetchall()

    source_map = {str(row[0]): (str(row[1]), str(row[2])) for row in manifest_rows}
    source_manifest = {
        str(row[0]): {"source_db": str(row[1]), "source_run_id": str(row[2])}
        for row in manifest_rows
    }
    malf_source_run_id = source_manifest.get("malf", {}).get("source_run_id")
    observed_start: str | None = None
    observed_end: str | None = None
    readout_count = 0
    full_year_covered = False
    if coverage_row is not None:
        observed_start = None if coverage_row[0] is None else str(coverage_row[0])
        observed_end = None if coverage_row[1] is None else str(coverage_row[1])
        readout_count = 0 if coverage_row[2] is None else int(coverage_row[2])
        full_year_covered = observed_start == year_start and observed_end == year_end

    payload = {
        "run_id": request.run_id,
        "target_year": request.target_year,
        "coverage": {
            "required_start": year_start,
            "required_end": year_end,
            "observed_start": observed_start,
            "observed_end": observed_end,
            "readout_count": readout_count,
            "full_year_covered": full_year_covered,
        },
        "system_readout": {
            "status_counts": {str(status): int(count) for status, count in readout_status_rows},
        },
        "source_manifest": source_manifest,
        "rerun_source_lock": (
            {
                "expected_malf_source_run_id": (PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID),
                "observed_malf_source_run_id": malf_source_run_id,
                "locked": malf_source_run_id == PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID,
            }
            if request.module_scope == "year_replay_rerun"
            else None
        ),
        "behavior": _load_behavior_counts(source_map, request.target_year),
    }
    summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary_path


def _load_behavior_counts(
    source_map: dict[str, tuple[str, str]], target_year: int
) -> dict[str, object]:
    year_start = f"{target_year}-01-01"
    year_end = f"{target_year}-12-31"
    signal_db, signal_run_id = source_map["signal"]
    position_db, position_run_id = source_map["position"]
    portfolio_db, portfolio_run_id = source_map["portfolio_plan"]
    trade_db, trade_run_id = source_map["trade"]

    with duckdb.connect(signal_db, read_only=True) as con:
        signal_count = con.execute(
            """
            select count(*)
            from formal_signal_ledger
            where run_id = ? and signal_dt >= ? and signal_dt <= ?
            """,
            [signal_run_id, year_start, year_end],
        ).fetchone()

    with duckdb.connect(position_db, read_only=True) as con:
        position_candidate_count_row = con.execute(
            """
            select count(*)
            from position_candidate_ledger
            where run_id = ? and candidate_dt >= ? and candidate_dt <= ?
            """,
            [position_run_id, year_start, year_end],
        ).fetchone()
        entry_plan_count_row = con.execute(
            """
            select count(*)
            from position_entry_plan
            where run_id = ? and entry_reference_dt >= ? and entry_reference_dt <= ?
            """,
            [position_run_id, year_start, year_end],
        ).fetchone()
        exit_plan_count_row = con.execute(
            """
            select count(*)
            from position_exit_plan
            where run_id = ? and exit_reference_dt >= ? and exit_reference_dt <= ?
            """,
            [position_run_id, year_start, year_end],
        ).fetchone()

    with duckdb.connect(portfolio_db, read_only=True) as con:
        portfolio_admission_count_row = con.execute(
            """
            select count(*)
            from portfolio_admission_ledger
            where run_id = ? and plan_dt >= ? and plan_dt <= ?
            """,
            [portfolio_run_id, year_start, year_end],
        ).fetchone()
        target_exposure_count_row = con.execute(
            """
            select count(*)
            from portfolio_target_exposure
            where run_id = ? and exposure_valid_from >= ? and exposure_valid_from <= ?
            """,
            [portfolio_run_id, year_start, year_end],
        ).fetchone()
        trim_count_row = con.execute(
            """
            select count(*)
            from portfolio_trim_ledger
            where run_id = ?
            """,
            [portfolio_run_id],
        ).fetchone()

    with duckdb.connect(trade_db, read_only=True) as con:
        order_intent_count_row = con.execute(
            """
            select count(*)
            from order_intent_ledger
            where run_id = ? and intent_dt >= ? and intent_dt <= ?
            """,
            [trade_run_id, year_start, year_end],
        ).fetchone()
        execution_plan_count_row = con.execute(
            """
            select count(*)
            from execution_plan_ledger
            where run_id = ? and execution_valid_from >= ? and execution_valid_from <= ?
            """,
            [trade_run_id, year_start, year_end],
        ).fetchone()
        fill_count_row = con.execute(
            """
            select count(*)
            from fill_ledger
            where run_id = ? and execution_dt >= ? and execution_dt <= ?
            """,
            [trade_run_id, year_start, year_end],
        ).fetchone()
        rejection_count_row = con.execute(
            """
            select count(*)
            from order_rejection_ledger
            where run_id = ? and rejection_dt >= ? and rejection_dt <= ?
            """,
            [trade_run_id, year_start, year_end],
        ).fetchone()
        rejection_reason_rows = con.execute(
            """
            select rejection_reason, count(*)
            from order_rejection_ledger
            where run_id = ? and rejection_dt >= ? and rejection_dt <= ?
            group by rejection_reason
            order by count(*) desc, rejection_reason asc
            """,
            [trade_run_id, year_start, year_end],
        ).fetchall()

    return {
        "signal_count": _first_int(signal_count),
        "position_candidate_count": _first_int(position_candidate_count_row),
        "entry_plan_count": _first_int(entry_plan_count_row),
        "exit_plan_count": _first_int(exit_plan_count_row),
        "portfolio_admission_count": _first_int(portfolio_admission_count_row),
        "portfolio_target_exposure_count": _first_int(target_exposure_count_row),
        "portfolio_trim_count": _first_int(trim_count_row),
        "order_intent_count": _first_int(order_intent_count_row),
        "execution_plan_count": _first_int(execution_plan_count_row),
        "fill_count": _first_int(fill_count_row),
        "rejection_count": _first_int(rejection_count_row),
        "rejection_reason_counts": {
            str(reason): int(count) for reason, count in rejection_reason_rows
        },
    }


def _first_int(row: tuple[Any, ...] | None) -> int:
    if row is None or row[0] is None:
        return 0
    return int(row[0])


def load_completed_checkpoint(
    request: PipelineBuildRequest,
    stage: str,
) -> PipelineBuildSummary | None:
    if request.mode != "resume":
        return None
    path = request.checkpoint_path(stage)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return PipelineBuildSummary(**{**payload, "resume_reused": True})


def save_checkpoint(path: Path, summary: PipelineBuildSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def report_path(report_root: Path, run_id: str) -> Path:
    return report_root / "pipeline" / utc_now().date().isoformat() / f"{run_id}-audit-summary.json"


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
