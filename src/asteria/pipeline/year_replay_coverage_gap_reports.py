from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from asteria.pipeline.year_replay_coverage_gap_contracts import (
    CoverageMatrixRow,
    YearReplayCoverageGapDiagnosisRequest,
)


def write_diagnosis_artifacts(
    *,
    request: YearReplayCoverageGapDiagnosisRequest,
    released_system_run_id: str,
    recommended_next_card: str,
    attribution: str,
    focus_trading_dates: list[str],
    calendar_semantic_dates: list[str],
    layer_statuses: dict[str, bool],
    evidence_issues: list[str],
    full_year_gate_ok: bool,
    rows: list[CoverageMatrixRow],
) -> tuple[Path, Path, Path, Path, Path]:
    report_dir = request.report_root / "pipeline" / _utc_now().date().isoformat() / request.run_id
    report_dir.mkdir(parents=True, exist_ok=True)

    coverage_matrix_path = report_dir / "coverage-matrix.json"
    coverage_matrix_path.write_text(
        json.dumps(
            {
                "run_id": request.run_id,
                "target_year": request.target_year,
                "released_system_run_id": released_system_run_id,
                "focus_trading_dates": focus_trading_dates,
                "calendar_semantic_dates": calendar_semantic_dates,
                "full_year_gate_ok": full_year_gate_ok,
                "layer_statuses": layer_statuses,
                "evidence_issues": evidence_issues,
                "rows": [row.as_dict() for row in rows],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    coverage_attribution_path = report_dir / "coverage-attribution.md"
    coverage_attribution_path.write_text(
        _build_attribution_markdown(
            request=request,
            released_system_run_id=released_system_run_id,
            recommended_next_card=recommended_next_card,
            attribution=attribution,
            focus_trading_dates=focus_trading_dates,
            calendar_semantic_dates=calendar_semantic_dates,
            layer_statuses=layer_statuses,
            evidence_issues=evidence_issues,
            full_year_gate_ok=full_year_gate_ok,
        ),
        encoding="utf-8",
    )

    data_root = request.data_root
    if data_root is None:
        raise ValueError("data_root must be resolved before writing diagnosis artifacts")

    manifest_path = report_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "run_id": request.run_id,
                "module": "pipeline",
                "stage": "year_replay_coverage_gap_diagnosis",
                "status": "passed",
                "target_year": request.target_year,
                "released_system_run_id": released_system_run_id,
                "source_system_db": str(request.source_system_db),
                "data_root": str(data_root),
                "manifest_locked": True,
                "recommended_next_card": recommended_next_card,
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
                "# Pipeline Year Replay Coverage Gap Diagnosis Closeout",
                "",
                f"- run_id: `{request.run_id}`",
                f"- released_system_run_id: `{released_system_run_id}`",
                f"- target_year: `{request.target_year}`",
                f"- recommended_next_card: `{recommended_next_card}`",
                f"- attribution: `{attribution}`",
                f"- trading-day surface gap focus: `{', '.join(focus_trading_dates)}`",
                f"- calendar-semantic dates: `{', '.join(calendar_semantic_dates)}`",
            ]
        ),
        encoding="utf-8",
    )

    validated_zip = request.validated_root / f"Asteria-{request.run_id}.zip"
    validated_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(validated_zip, "w") as archive:
        archive.write(manifest_path, arcname="manifest.json")
        archive.write(coverage_matrix_path, arcname="coverage-matrix.json")
        archive.write(coverage_attribution_path, arcname="coverage-attribution.md")
        archive.write(closeout_path, arcname="closeout.md")

    return (
        manifest_path,
        coverage_matrix_path,
        coverage_attribution_path,
        closeout_path,
        validated_zip,
    )


def _build_attribution_markdown(
    *,
    request: YearReplayCoverageGapDiagnosisRequest,
    released_system_run_id: str,
    recommended_next_card: str,
    attribution: str,
    focus_trading_dates: list[str],
    calendar_semantic_dates: list[str],
    layer_statuses: dict[str, bool],
    evidence_issues: list[str],
    full_year_gate_ok: bool,
) -> str:
    return "\n".join(
        [
            "# Pipeline Year Replay Coverage Attribution",
            "",
            f"- run_id: `{request.run_id}`",
            f"- released_system_run_id: `{released_system_run_id}`",
            f"- recommended_next_card: `{recommended_next_card}`",
            f"- attribution: `{attribution}`",
            f"- trading-day surface gap focus: `{', '.join(focus_trading_dates)}`",
            f"- calendar-semantic gap: `{', '.join(calendar_semantic_dates)}`",
            (
                f"- year replay gate today: `min(readout_dt)=={request.target_year}-01-01 "
                f"and max(readout_dt)=={request.target_year}-12-31`"
            ),
            f"- full_year_gate_ok: `{full_year_gate_ok}`",
            "",
            "## Findings",
            "",
            f"- trading-day surface gap status: `{_surface_gap_summary(layer_statuses)}`",
            (
                f"- calendar-semantic gap status: "
                f"`{'present' if not full_year_gate_ok else 'cleared'}`"
            ),
            (
                f"- evidence issues: `{'; '.join(evidence_issues)}`"
                if evidence_issues
                else "- evidence issues: `none`"
            ),
        ]
    )


def _surface_gap_summary(layer_statuses: dict[str, bool]) -> str:
    for layer_name in (
        "data",
        "malf",
        "alpha",
        "signal",
        "position",
        "portfolio_plan",
        "trade",
        "system_readout",
    ):
        if not layer_statuses.get(layer_name, False):
            return f"break_at_{layer_name}"
    return "all_focus_trading_dates_covered"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
