from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2
from typing import Any

from asteria.alpha.contracts import AlphaBuildSummary


def write_alpha_evidence(
    report_root: Path,
    validated_root: Path,
    run_id: str,
    summaries: list[AlphaBuildSummary],
    stage: str,
) -> None:
    report_dir = report_root / "alpha" / _utc_now().date().isoformat() / run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": run_id,
        "module": "alpha",
        "stage": stage,
        "hard_fail_count": sum(summary.hard_fail_count for summary in summaries),
        "timeframes": sorted({summary.timeframe for summary in summaries}),
        "families": [summary.as_dict() for summary in summaries],
        "generated_at": _utc_now().isoformat(),
    }
    manifest_path = report_dir / "manifest.json"
    closeout_path = report_dir / "closeout.md"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    closeout_path.write_text(_closeout_text(manifest), encoding="utf-8")
    zip_path = validated_root / f"Asteria-{run_id}.zip"
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(manifest_path, manifest_path.name)
        archive.write(closeout_path, closeout_path.name)
        for summary in summaries:
            if summary.report_path:
                report_path = Path(summary.report_path)
                if report_path.exists():
                    archive.write(report_path, f"family/{report_path.name}")
    copy2(
        manifest_path,
        report_root / "alpha" / _utc_now().date().isoformat() / f"{run_id}-summary.json",
    )


def _closeout_text(manifest: dict[str, Any]) -> str:
    lines = [
        f"# Alpha {manifest['stage']} closeout: {manifest['run_id']}",
        "",
        f"- status: {'passed' if manifest['hard_fail_count'] == 0 else 'failed'}",
        f"- hard_fail_count: {manifest['hard_fail_count']}",
        f"- timeframes: {', '.join(manifest['timeframes'])}",
        "- forbidden downstream scope: Signal / Position / Portfolio / Trade / System / Pipeline",
    ]
    return "\n".join(lines) + "\n"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
