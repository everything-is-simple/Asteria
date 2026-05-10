from __future__ import annotations

import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from asteria.pipeline.downstream_coverage_gap_closeout_contracts import (
    DownstreamCoverageGapCloseoutDecision,
    DownstreamCoverageGapCloseoutRequest,
    DownstreamCoverageGapCloseoutSummary,
)
from asteria.pipeline.system_probe_diagnosis import run_system_probe_diagnosis
from asteria.pipeline.year_replay_coverage_gap_contracts import (
    EVIDENCE_INCOMPLETE_CARD,
    PORTFOLIO_PLAN_REPAIR_CARD,
    POSITION_REPAIR_CARD,
    TRADE_REPAIR_CARD,
)


def resolve_downstream_closeout_decision(
    *,
    layer_statuses: dict[str, bool],
    evidence_issues: list[str],
) -> DownstreamCoverageGapCloseoutDecision:
    if evidence_issues:
        return DownstreamCoverageGapCloseoutDecision(
            next_card=EVIDENCE_INCOMPLETE_CARD,
            attribution="evidence_incomplete",
        )
    if not layer_statuses.get("position", False):
        return DownstreamCoverageGapCloseoutDecision(
            next_card=POSITION_REPAIR_CARD,
            attribution="downstream_surface_gap:position",
        )
    if not layer_statuses.get("portfolio_plan", False):
        return DownstreamCoverageGapCloseoutDecision(
            next_card=PORTFOLIO_PLAN_REPAIR_CARD,
            attribution="downstream_surface_gap:portfolio_plan",
        )
    if not layer_statuses.get("trade", False):
        return DownstreamCoverageGapCloseoutDecision(
            next_card=TRADE_REPAIR_CARD,
            attribution="downstream_surface_gap:trade",
        )
    return DownstreamCoverageGapCloseoutDecision(
        next_card=EVIDENCE_INCOMPLETE_CARD,
        attribution="no_unique_downstream_gap",
    )


def run_downstream_coverage_gap_closeout(
    request: DownstreamCoverageGapCloseoutRequest,
) -> DownstreamCoverageGapCloseoutSummary:
    data_root = request.data_root
    if data_root is None:
        raise ValueError("data_root must be resolved before closeout")

    probe_summary = run_system_probe_diagnosis(
        probe_root=request.run_root / "system-probe",
        repo_root=request.repo_root,
        data_root=data_root,
        run_id_prefix=request.run_id,
        target_year=request.target_year,
    )
    coverage_matrix = json.loads(
        Path(probe_summary.diagnosis_summary.coverage_matrix_path).read_text(encoding="utf-8")
    )
    decision = resolve_downstream_closeout_decision(
        layer_statuses={
            key: bool(value) for key, value in coverage_matrix["layer_statuses"].items()
        },
        evidence_issues=list(coverage_matrix["evidence_issues"]),
    )
    manifest_path, closeout_path, validated_zip = _write_closeout_artifacts(
        request=request,
        probe_summary=probe_summary,
        decision=decision,
    )
    return DownstreamCoverageGapCloseoutSummary(
        run_id=request.run_id,
        target_year=request.target_year,
        probe_system_db=probe_summary.probe_system_db,
        probe_diagnosis_run_id=probe_summary.diagnosis_summary.run_id,
        next_card=decision.next_card,
        attribution=decision.attribution,
        manifest_path=str(manifest_path),
        closeout_path=str(closeout_path),
        validated_zip=str(validated_zip),
    )


def _write_closeout_artifacts(
    *,
    request: DownstreamCoverageGapCloseoutRequest,
    probe_summary,
    decision: DownstreamCoverageGapCloseoutDecision,
) -> tuple[Path, Path, Path]:
    report_dir = request.report_root / "pipeline" / _utc_now().date().isoformat() / request.run_id
    report_dir.mkdir(parents=True, exist_ok=True)

    probe_manifest_path = Path(probe_summary.diagnosis_summary.manifest_path)
    probe_matrix_path = Path(probe_summary.diagnosis_summary.coverage_matrix_path)
    probe_attribution_path = Path(probe_summary.diagnosis_summary.coverage_attribution_path)

    copied_manifest_path = report_dir / "probe-manifest.json"
    copied_matrix_path = report_dir / "coverage-matrix.json"
    copied_attribution_path = report_dir / "coverage-attribution.md"
    shutil.copy2(probe_manifest_path, copied_manifest_path)
    shutil.copy2(probe_matrix_path, copied_matrix_path)
    shutil.copy2(probe_attribution_path, copied_attribution_path)

    manifest_path = report_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "run_id": request.run_id,
                "module": "pipeline",
                "stage": "downstream_coverage_gap_closeout",
                "status": "completed",
                "target_year": request.target_year,
                "probe_system_db": probe_summary.probe_system_db,
                "probe_diagnosis_run_id": probe_summary.diagnosis_summary.run_id,
                "decision": decision.as_dict(),
                "probe_recommended_next_card": (
                    probe_summary.diagnosis_summary.recommended_next_card
                ),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    matrix_payload = json.loads(copied_matrix_path.read_text(encoding="utf-8"))
    earliest_days = _build_earliest_day_map(matrix_payload["rows"])
    closeout_path = report_dir / "closeout.md"
    closeout_path.write_text(
        "\n".join(
            [
                "# Downstream Coverage Gap Closeout",
                "",
                f"- run_id: `{request.run_id}`",
                f"- probe_diagnosis_run_id: `{probe_summary.diagnosis_summary.run_id}`",
                f"- next_card: `{decision.next_card}`",
                f"- attribution: `{decision.attribution}`",
                f"- released Alpha earliest day: `{earliest_days['alpha']}`",
                f"- released Signal earliest day: `{earliest_days['signal']}`",
                f"- released Position earliest day: `{earliest_days['position']}`",
                f"- released Portfolio Plan earliest day: `{earliest_days['portfolio_plan']}`",
                f"- released Trade earliest day: `{earliest_days['trade']}`",
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
        archive.write(copied_manifest_path, arcname="probe-manifest.json")
        archive.write(copied_matrix_path, arcname="coverage-matrix.json")
        archive.write(copied_attribution_path, arcname="coverage-attribution.md")
    return manifest_path, closeout_path, validated_zip


def _build_earliest_day_map(rows: list[dict[str, object]]) -> dict[str, str]:
    mapped_rows: dict[str, list[str]] = {
        "alpha": [],
        "signal": [],
        "position": [],
        "portfolio_plan": [],
        "trade": [],
    }
    for row in rows:
        layer = str(row["layer"])
        observed_start = row["observed_start"]
        if observed_start is None or layer not in mapped_rows:
            continue
        mapped_rows[layer].append(str(observed_start))
    return {layer: min(values) if values else "none" for layer, values in mapped_rows.items()}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
