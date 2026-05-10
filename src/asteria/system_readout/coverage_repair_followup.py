from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

from asteria.pipeline.year_replay_coverage_gap_diagnosis import (
    YearReplayCoverageGapDiagnosisRequest,
    run_year_replay_coverage_gap_diagnosis,
)
from asteria.system_readout.coverage_repair_contracts import (
    FOCUS_DATES,
    SystemReadout2024CoverageRepairRequest,
)
from asteria.system_readout.coverage_repair_shared import (
    build_earliest_day_map,
    summary_status,
    system_readout_report_dir,
)


def run_followup_diagnosis(
    *,
    request: SystemReadout2024CoverageRepairRequest,
) -> tuple[str, str, dict[str, str]]:
    diagnosis_run_id = f"{request.run_id}-followup-diagnosis"
    diagnosis_summary = run_year_replay_coverage_gap_diagnosis(
        YearReplayCoverageGapDiagnosisRequest(
            repo_root=request.repo_root,
            source_system_db=request.source_system_db,
            report_root=request.report_root,
            validated_root=request.validated_root,
            run_id=diagnosis_run_id,
            target_year=request.target_year,
            data_root=request.data_root,
        )
    )
    return (
        diagnosis_summary.recommended_next_card,
        diagnosis_summary.attribution,
        {
            "coverage_matrix_path": diagnosis_summary.coverage_matrix_path,
            "coverage_attribution_path": diagnosis_summary.coverage_attribution_path,
            "diagnosis_closeout_path": diagnosis_summary.closeout_path,
            "diagnosis_manifest_path": diagnosis_summary.manifest_path,
            "diagnosis_validated_zip": diagnosis_summary.validated_zip,
        },
    )


def write_repair_evidence(
    *,
    request: SystemReadout2024CoverageRepairRequest,
    released_system_run_id: str,
    audit_report_path: Path,
    audit_payload: dict[str, Any],
    followup_next_card: str,
    followup_attribution: str,
    followup_artifacts: dict[str, str],
) -> tuple[Path, Path, Path]:
    report_dir = system_readout_report_dir(request.report_root, request.run_id)
    report_dir.mkdir(parents=True, exist_ok=True)
    matrix_payload = json.loads(
        Path(followup_artifacts["coverage_matrix_path"]).read_text(encoding="utf-8")
    )
    earliest_days = build_earliest_day_map(matrix_payload["rows"])
    manifest = {
        "run_id": request.run_id,
        "module": "system_readout",
        "stage": "system_readout_2024_coverage_repair",
        "status": summary_status(
            hard_fail_count=int(audit_payload["hard_fail_count"]),
            followup_next_card=followup_next_card,
            followup_attribution=followup_attribution,
        ),
        "released_system_run_id": released_system_run_id,
        "focus_dates": list(FOCUS_DATES),
        "hard_fail_count": audit_payload["hard_fail_count"],
        "source_manifest_count": audit_payload["source_manifest_count"],
        "module_status_count": audit_payload["module_status_count"],
        "readout_count": audit_payload["readout_count"],
        "summary_count": audit_payload["summary_count"],
        "audit_snapshot_count": audit_payload["audit_snapshot_count"],
        "followup_next_card": followup_next_card,
        "followup_attribution": followup_attribution,
        "source_system_db": str(request.source_system_db),
    }
    manifest_path = report_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    closeout_lines = [
        "# System Readout 2024 Released Day Surface Repair",
        "",
        f"- run_id: `{request.run_id}`",
        f"- released_system_run_id: `{released_system_run_id}`",
        f"- focus_trading_dates: `{', '.join(FOCUS_DATES)}`",
        f"- hard_fail_count: `{audit_payload['hard_fail_count']}`",
        f"- followup_next_card: `{followup_next_card}`",
        f"- followup_attribution: `{followup_attribution}`",
        "",
        "## Earliest Days",
        "",
        f"- released MALF earliest day: `{earliest_days.get('malf', 'none')}`",
        f"- released Alpha earliest day: `{earliest_days.get('alpha', 'none')}`",
        f"- released Signal earliest day: `{earliest_days.get('signal', 'none')}`",
        f"- released Position earliest day: `{earliest_days.get('position', 'none')}`",
        f"- released Portfolio Plan earliest day: `{earliest_days.get('portfolio_plan', 'none')}`",
        f"- released Trade earliest day: `{earliest_days.get('trade', 'none')}`",
        f"- released System earliest day: `{earliest_days.get('system_readout', 'none')}`",
    ]
    closeout_path = report_dir / "closeout.md"
    closeout_path.write_text("\n".join(closeout_lines) + "\n", encoding="utf-8")
    validated_zip = request.validated_root / f"Asteria-{request.run_id}.zip"
    validated_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(validated_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(manifest_path, arcname="manifest.json")
        archive.write(closeout_path, arcname="closeout.md")
        archive.write(audit_report_path, arcname="system-readout-day-audit-summary.json")
        archive.write(followup_artifacts["coverage_matrix_path"], arcname="coverage-matrix.json")
        archive.write(
            followup_artifacts["coverage_attribution_path"],
            arcname="coverage-attribution.md",
        )
    return manifest_path, closeout_path, validated_zip
