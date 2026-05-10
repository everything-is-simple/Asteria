from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from asteria.pipeline.released_source_selection import (
    resolve_released_year_replay_source_selection,
)
from asteria.pipeline.year_replay_coverage_gap_contracts import (
    PIPELINE_REPAIR_CARD,
    YearReplayCoverageGapDiagnosisRequest,
)
from asteria.pipeline.year_replay_coverage_gap_diagnosis import (
    run_year_replay_coverage_gap_diagnosis,
)
from asteria.pipeline.year_replay_source_selection_repair_contracts import (
    PIPELINE_DISPOSITION_DECISION_CARD,
    PipelineYearReplaySourceSelectionRepairRequest,
    PipelineYearReplaySourceSelectionRepairSummary,
)


def run_pipeline_year_replay_source_selection_repair(
    request: PipelineYearReplaySourceSelectionRepairRequest,
) -> PipelineYearReplaySourceSelectionRepairSummary:
    selection = resolve_released_year_replay_source_selection(
        request.source_system_db,
        target_year=request.target_year,
    )
    diagnosis = run_year_replay_coverage_gap_diagnosis(
        YearReplayCoverageGapDiagnosisRequest(
            repo_root=request.repo_root,
            source_system_db=request.source_system_db,
            report_root=request.report_root,
            validated_root=request.validated_root,
            run_id=f"{request.run_id}-followup-diagnosis",
            target_year=request.target_year,
        )
    )
    status = "completed"
    next_card = PIPELINE_DISPOSITION_DECISION_CARD
    if diagnosis.recommended_next_card != PIPELINE_REPAIR_CARD or not selection.source_lock_clean:
        status = "failed"
        next_card = diagnosis.recommended_next_card
    manifest_path, closeout_path, validated_zip = _write_repair_artifacts(
        request=request,
        selection=selection,
        diagnosis=diagnosis,
        status=status,
        next_card=next_card,
    )
    return PipelineYearReplaySourceSelectionRepairSummary(
        run_id=request.run_id,
        status=status,
        released_system_run_id=selection.released_system_run_id,
        observed_start=selection.observed_start,
        observed_end=selection.observed_end,
        source_lock_clean=selection.source_lock_clean,
        followup_attribution=diagnosis.attribution,
        diagnosis_next_card=diagnosis.recommended_next_card,
        next_card=next_card,
        manifest_path=str(manifest_path),
        closeout_path=str(closeout_path),
        validated_zip=str(validated_zip),
    )


def _write_repair_artifacts(
    *,
    request: PipelineYearReplaySourceSelectionRepairRequest,
    selection,
    diagnosis,
    status: str,
    next_card: str,
) -> tuple[Path, Path, Path]:
    report_dir = request.report_root / "pipeline" / _utc_now().date().isoformat() / request.run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = report_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "run_id": request.run_id,
                "module": "pipeline",
                "stage": "year_replay_source_selection_repair",
                "status": status,
                "target_year": request.target_year,
                "released_source_selection": selection.as_dict(),
                "diagnosis_run_id": diagnosis.run_id,
                "diagnosis_next_card": diagnosis.recommended_next_card,
                "followup_attribution": diagnosis.attribution,
                "next_card": next_card,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    closeout_path = report_dir / "closeout.md"
    closeout_path.write_text(
        "\n".join(
            [
                "# Pipeline Year Replay Source Selection Repair",
                "",
                f"- run_id: `{request.run_id}`",
                f"- released_system_run_id: `{selection.released_system_run_id}`",
                f"- released_system_observed_start: `{selection.observed_start}`",
                f"- released_system_observed_end: `{selection.observed_end}`",
                f"- source_lock_clean: `{selection.source_lock_clean}`",
                f"- diagnosis_next_card: `{diagnosis.recommended_next_card}`",
                f"- followup_attribution: `{diagnosis.attribution}`",
                f"- next_card: `{next_card}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    validated_zip = request.validated_root / f"Asteria-{request.run_id}.zip"
    validated_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(validated_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(manifest_path, arcname="manifest.json")
        archive.write(closeout_path, arcname="closeout.md")
    return manifest_path, closeout_path, validated_zip


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
