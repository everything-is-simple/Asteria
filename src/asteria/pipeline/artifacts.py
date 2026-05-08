from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from asteria.pipeline.contracts import PipelineBuildRequest, PipelineBuildSummary


def write_bounded_proof_evidence(
    request: PipelineBuildRequest,
    summary: PipelineBuildSummary,
) -> dict[str, str]:
    report_dir = request.report_root / "pipeline" / utc_now().date().isoformat() / request.run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": request.run_id,
        "module": "pipeline",
        "stage": "single_module_orchestration_build",
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
    closeout_path = report_dir / "closeout.md"
    closeout_path.write_text(
        "\n".join(
            [
                "# Pipeline Single-Module Orchestration Build Closeout",
                "",
                f"- run_id: `{request.run_id}`",
                f"- status: `{manifest['status']}`",
                f"- module_scope: `{request.module_scope}`",
                f"- step_count: `{summary.step_count}`",
                f"- hard_fail_count: `{summary.hard_fail_count}`",
            ]
        ),
        encoding="utf-8",
    )
    validated_zip = request.validated_root / f"Asteria-{request.run_id}.zip"
    validated_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(validated_zip, "w") as archive:
        archive.write(manifest_path, arcname="manifest.json")
        archive.write(closeout_path, arcname="closeout.md")
        if request.target_pipeline_db.exists():
            archive.write(request.target_pipeline_db, arcname="pipeline.duckdb")
    return {
        "manifest_path": str(manifest_path),
        "closeout_path": str(closeout_path),
        "validated_zip": str(validated_zip),
    }


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
