from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

import duckdb

from asteria.pipeline.downstream_coverage_gap_closeout import (
    resolve_downstream_closeout_decision,
)
from asteria.pipeline.year_replay_coverage_gap_diagnosis import (
    YearReplayCoverageGapDiagnosisRequest,
    run_year_replay_coverage_gap_diagnosis,
)
from asteria.position.coverage_repair_contracts import (
    FOCUS_DATES,
    Position2024CoverageRepairRequest,
)
from asteria.position.coverage_repair_shared import (
    build_earliest_day_map,
    position_report_dir,
    summary_status,
    utc_now,
)


def run_followup_closeout(
    *,
    request: Position2024CoverageRepairRequest,
    released_chain: dict[str, Any],
) -> tuple[str, str, dict[str, str]]:
    probe_system_db = build_probe_system_db(request, released_chain)
    diagnosis_run_id = f"{request.run_id}-followup-diagnosis"
    diagnosis_summary = run_year_replay_coverage_gap_diagnosis(
        YearReplayCoverageGapDiagnosisRequest(
            repo_root=request.repo_root,
            source_system_db=probe_system_db,
            report_root=request.report_root,
            validated_root=request.validated_root,
            run_id=diagnosis_run_id,
            target_year=request.target_year,
            data_root=request.data_root,
        )
    )
    matrix_payload = json.loads(
        Path(diagnosis_summary.coverage_matrix_path).read_text(encoding="utf-8")
    )
    decision = resolve_downstream_closeout_decision(
        layer_statuses={
            key: bool(value) for key, value in matrix_payload["layer_statuses"].items()
        },
        evidence_issues=list(matrix_payload["evidence_issues"]),
    )
    return (
        decision.next_card,
        decision.attribution,
        {
            "probe_system_db": str(probe_system_db),
            "coverage_matrix_path": diagnosis_summary.coverage_matrix_path,
            "coverage_attribution_path": diagnosis_summary.coverage_attribution_path,
            "diagnosis_closeout_path": diagnosis_summary.closeout_path,
            "diagnosis_manifest_path": diagnosis_summary.manifest_path,
        },
    )


def build_probe_system_db(
    request: Position2024CoverageRepairRequest,
    released_chain: dict[str, Any],
) -> Path:
    probe_root = request.run_root / "followup-system-probe"
    probe_root.mkdir(parents=True, exist_ok=True)
    probe_system_db = probe_root / "system-probe.duckdb"
    if probe_system_db.exists():
        probe_system_db.unlink()
    probe_run_id = f"{request.run_id}-system-probe"
    with duckdb.connect(str(request.source_system_db), read_only=True) as source:
        readout_dates = source.execute(
            """
            select readout_dt
            from system_chain_readout
            where system_readout_run_id = ?
            order by readout_dt
            """,
            [released_chain["released_system_run_id"]],
        ).fetchall()
    with duckdb.connect(str(probe_system_db)) as con:
        con.execute(
            "create table system_readout_run (run_id varchar, status varchar, created_at timestamp)"
        )
        con.execute(
            """
            create table system_source_manifest (
                system_readout_run_id varchar,
                module_name varchar,
                source_db varchar,
                source_run_id varchar,
                source_release_version varchar
            )
            """
        )
        con.execute(
            "create table system_chain_readout (system_readout_run_id varchar, readout_dt date)"
        )
        con.execute(
            "insert into system_readout_run values (?, 'completed', ?)",
            [probe_run_id, utc_now()],
        )
        con.executemany(
            "insert into system_source_manifest values (?, ?, ?, ?, ?)",
            [
                [
                    probe_run_id,
                    row["module_name"],
                    row["source_db"],
                    row["source_run_id"],
                    row["source_release_version"],
                ]
                for row in released_chain["manifest_rows"]
            ],
        )
        con.executemany(
            "insert into system_chain_readout values (?, ?)",
            [[probe_run_id, row[0]] for row in readout_dates],
        )
    return probe_system_db


def write_repair_evidence(
    *,
    request: Position2024CoverageRepairRequest,
    released_system_run_id: str,
    released_position_run_id: str,
    released_signal_run_id: str,
    followup_next_card: str,
    followup_attribution: str,
    audit_report_path: Path,
    audit_payload: dict[str, Any],
    followup_artifacts: dict[str, str],
) -> tuple[Path, Path, Path]:
    report_dir = position_report_dir(request.report_root, request.run_id)
    report_dir.mkdir(parents=True, exist_ok=True)
    matrix_payload = json.loads(
        Path(followup_artifacts["coverage_matrix_path"]).read_text(encoding="utf-8")
    )
    earliest_days = build_earliest_day_map(matrix_payload["rows"])
    manifest = {
        "run_id": request.run_id,
        "module": "position",
        "stage": "position_2024_coverage_repair",
        "status": summary_status(
            hard_fail_count=int(audit_payload["hard_fail_count"]),
            followup_next_card=followup_next_card,
            followup_attribution=followup_attribution,
        ),
        "released_system_run_id": released_system_run_id,
        "released_position_run_id": released_position_run_id,
        "released_signal_run_id": released_signal_run_id,
        "focus_dates": list(FOCUS_DATES),
        "hard_fail_count": audit_payload["hard_fail_count"],
        "input_signal_count": audit_payload["input_signal_count"],
        "position_candidate_count": audit_payload["position_candidate_count"],
        "entry_plan_count": audit_payload["entry_plan_count"],
        "exit_plan_count": audit_payload["exit_plan_count"],
        "followup_next_card": followup_next_card,
        "followup_attribution": followup_attribution,
        "followup_probe_system_db": followup_artifacts["probe_system_db"],
    }
    manifest_path = report_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    closeout_lines = [
        "# Position 2024 Released Day Surface Repair",
        "",
        f"- run_id: `{request.run_id}`",
        f"- released_system_run_id: `{released_system_run_id}`",
        f"- released_position_run_id: `{released_position_run_id}`",
        f"- released_signal_run_id: `{released_signal_run_id}`",
        f"- focus_trading_dates: `{', '.join(FOCUS_DATES)}`",
        f"- hard_fail_count: `{audit_payload['hard_fail_count']}`",
        f"- followup_next_card: `{followup_next_card}`",
        f"- followup_attribution: `{followup_attribution}`",
        "",
        "## Earliest Days",
        "",
        f"- released Signal earliest day: `{earliest_days.get('signal', 'none')}`",
        f"- released Position earliest day: `{earliest_days.get('position', 'none')}`",
        (
            f"- released Portfolio Plan earliest day: "
            f"`{earliest_days.get('portfolio_plan', 'none')}`"
        ),
        f"- released Trade earliest day: `{earliest_days.get('trade', 'none')}`",
    ]
    closeout_path = report_dir / "closeout.md"
    closeout_path.write_text("\n".join(closeout_lines) + "\n", encoding="utf-8")
    validated_zip = request.validated_root / f"Asteria-{request.run_id}.zip"
    validated_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(validated_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(manifest_path, arcname="manifest.json")
        archive.write(closeout_path, arcname="closeout.md")
        archive.write(audit_report_path, arcname="position-day-audit-summary.json")
        archive.write(followup_artifacts["coverage_matrix_path"], arcname="coverage-matrix.json")
        archive.write(
            followup_artifacts["coverage_attribution_path"],
            arcname="coverage-attribution.md",
        )
    return manifest_path, closeout_path, validated_zip
