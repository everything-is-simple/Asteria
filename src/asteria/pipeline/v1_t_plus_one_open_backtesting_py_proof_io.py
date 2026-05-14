from __future__ import annotations

import json
import zipfile
from datetime import date
from pathlib import Path
from typing import Any

from asteria.pipeline.v1_t_plus_one_open_backtesting_py_proof_contracts import (
    TPlusOneOpenBacktestingPyProofRequest,
)
from asteria.pipeline.v1_t_plus_one_open_backtesting_py_proof_render import (
    closeout_markdown,
    manifest_payload,
    report_markdown,
)


def write_tplus1_backtesting_py_artifacts(
    *,
    request: TPlusOneOpenBacktestingPyProofRequest,
    status: str,
    live_next_card: str,
    selected_symbols: list[str],
    signal_symbol_count: int,
    start_date: date,
    end_date: date,
    symbol_results: list[dict[str, Any]],
    aggregate: dict[str, Any],
    skip_reason_distribution: list[dict[str, Any]],
    issues: list[str],
    next_route_card: str,
) -> tuple[Path, Path, Path, Path, Path]:
    request.report_dir.mkdir(parents=True, exist_ok=True)
    request.temp_dir.mkdir(parents=True, exist_ok=True)
    manifest = manifest_payload(
        request,
        status=status,
        live_next_card=live_next_card,
        selected_symbols=selected_symbols,
        signal_symbol_count=signal_symbol_count,
        date_window={"start": start_date.isoformat(), "end": end_date.isoformat()},
        symbol_results=symbol_results,
        aggregate=aggregate,
        skip_reason_distribution=skip_reason_distribution,
        issues=issues,
        next_route_card=next_route_card,
    )
    manifest_path = request.report_dir / "t-plus-one-open-backtesting-py-manifest.json"
    report_path = request.report_dir / "t-plus-one-open-backtesting-py-report.md"
    closeout_path = request.report_dir / "closeout.md"
    temp_manifest_path = request.temp_dir / "t-plus-one-open-backtesting-py-temp-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    temp_manifest_path.write_text(
        json.dumps(
            {
                "run_id": request.run_id,
                "status": status,
                "report_manifest": str(manifest_path),
                "formal_db_mutation": "no",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    report_path.write_text(report_markdown(manifest), encoding="utf-8")
    closeout_path.write_text(closeout_markdown(manifest), encoding="utf-8")
    validated_zip = request.validated_root / f"Asteria-{request.run_id}.zip"
    request.validated_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(validated_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in (manifest_path, report_path, closeout_path, temp_manifest_path):
            archive.write(path, arcname=path.name)
    return manifest_path, report_path, closeout_path, temp_manifest_path, validated_zip
