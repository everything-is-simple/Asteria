from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from asteria.system_readout.contracts import SystemReadoutBuildRequest, SystemReadoutBuildSummary


def write_bounded_proof_evidence(
    request: SystemReadoutBuildRequest,
    summary: SystemReadoutBuildSummary,
) -> dict[str, str]:
    report_dir = (
        request.report_root / "system_readout" / utc_now().date().isoformat() / request.run_id
    )
    report_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": request.run_id,
        "module": "system_readout",
        "stage": "bounded_proof",
        "status": "passed" if summary.hard_fail_count == 0 else "failed",
        "hard_fail_count": summary.hard_fail_count,
        "source_manifest_count": summary.source_manifest_count,
        "module_status_count": summary.module_status_count,
        "readout_count": summary.readout_count,
        "summary_count": summary.summary_count,
        "audit_snapshot_count": summary.audit_snapshot_count,
        "source_chain_release_version": request.source_chain_release_version,
        "target_system_db": str(request.target_system_db),
    }
    manifest_path = report_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    closeout_path = report_dir / "closeout.md"
    closeout_path.write_text(
        "\n".join(
            [
                "# System Readout Bounded Proof Closeout",
                "",
                f"- run_id: `{request.run_id}`",
                f"- status: `{manifest['status']}`",
                f"- readout_count: `{summary.readout_count}`",
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
        if request.target_system_db.exists():
            archive.write(request.target_system_db, arcname="system.duckdb")
    return {
        "manifest_path": str(manifest_path),
        "closeout_path": str(closeout_path),
        "validated_zip": str(validated_zip),
    }


def load_completed_checkpoint(
    request: SystemReadoutBuildRequest,
    stage: str,
) -> SystemReadoutBuildSummary | None:
    if request.mode != "resume":
        return None
    path = request.checkpoint_path(stage)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return SystemReadoutBuildSummary(**{**payload, "resume_reused": True})


def save_checkpoint(path: Path, summary: SystemReadoutBuildSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary.as_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def report_path(report_root: Path, run_id: str, timeframe: str) -> Path:
    return (
        report_root
        / "system_readout"
        / utc_now().date().isoformat()
        / f"{run_id}-{timeframe}-audit-summary.json"
    )


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
