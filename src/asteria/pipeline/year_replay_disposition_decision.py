from __future__ import annotations

import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from asteria.pipeline.released_source_selection import (
    ReleasedYearReplaySourceSelection,
    resolve_released_year_replay_source_selection,
)
from asteria.pipeline.year_replay_disposition_decision_contracts import (
    PIPELINE_DISPOSITION_DECISION_ACTION,
    PIPELINE_DISPOSITION_DECISION_CARD,
    PIPELINE_DISPOSITION_DECISION_OUTCOME,
    PIPELINE_STAGE11_PROTOCOL_ACTION,
    PIPELINE_STAGE11_PROTOCOL_CARD,
    PipelineYearReplayDispositionDecisionRequest,
    PipelineYearReplayDispositionDecisionSummary,
)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

FOLLOWUP_ATTRIBUTION_PATTERN = re.compile(
    r"\|\s*follow-up attribution\s*\|\s*`(?P<value>[^`]+)`\s*\|"
)


def run_pipeline_year_replay_disposition_decision(
    request: PipelineYearReplayDispositionDecisionRequest,
) -> PipelineYearReplayDispositionDecisionSummary:
    selection = resolve_released_year_replay_source_selection(
        request.source_system_db,
        target_year=request.target_year,
    )
    governance_snapshot = _load_governance_snapshot(request.repo_root)
    followup_attribution = _load_followup_attribution(request.repo_root)
    _assert_stage11_card_is_registered(request.repo_root)

    full_year_audit_still_requires_full_natural_year = not _full_year_coverage_ok(
        selection,
        target_year=request.target_year,
    )
    status = "failed"
    decision = "repair_line_not_closed"
    closeout_allowed = False
    rerun_recommended = False
    next_card = PIPELINE_DISPOSITION_DECISION_CARD
    next_action = PIPELINE_DISPOSITION_DECISION_ACTION

    if not selection.source_lock_clean:
        decision = "repair_line_not_closed"
    elif followup_attribution != "calendar_semantic_gap_only":
        decision = "followup_surface_gap_not_closed"
    elif full_year_audit_still_requires_full_natural_year:
        status = "completed"
        decision = PIPELINE_DISPOSITION_DECISION_OUTCOME
        closeout_allowed = True
        next_card = PIPELINE_STAGE11_PROTOCOL_CARD
        next_action = PIPELINE_STAGE11_PROTOCOL_ACTION
    else:
        decision = "full_year_gate_no_longer_blocked"

    manifest_path, closeout_path, validated_zip = _write_disposition_artifacts(
        request=request,
        selection=selection,
        governance_snapshot=governance_snapshot,
        followup_attribution=followup_attribution,
        full_year_audit_still_requires_full_natural_year=(
            full_year_audit_still_requires_full_natural_year
        ),
        status=status,
        decision=decision,
        closeout_allowed=closeout_allowed,
        rerun_recommended=rerun_recommended,
        next_card=next_card,
        next_action=next_action,
    )
    return PipelineYearReplayDispositionDecisionSummary(
        run_id=request.run_id,
        status=status,
        decision=decision,
        released_system_run_id=selection.released_system_run_id,
        observed_start=selection.observed_start,
        observed_end=selection.observed_end,
        source_lock_clean=selection.source_lock_clean,
        followup_attribution=followup_attribution,
        full_year_audit_still_requires_full_natural_year=(
            full_year_audit_still_requires_full_natural_year
        ),
        closeout_allowed=closeout_allowed,
        rerun_recommended=rerun_recommended,
        next_card=next_card,
        next_action=next_action,
        manifest_path=str(manifest_path),
        closeout_path=str(closeout_path),
        validated_zip=str(validated_zip),
    )


def _load_governance_snapshot(repo_root: Path) -> dict[str, str]:
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    pipeline_contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    with pipeline_contract_path.open("rb") as handle:
        pipeline_contract = tomllib.load(handle)
    modules = {module["module_id"]: module for module in registry["modules"]}
    pipeline_module = modules["pipeline"]
    system_readout_module = modules["system_readout"]
    current_allowed_next_card = str(registry["current_allowed_next_card"])
    pipeline_next_card = str(pipeline_module["next_card"])
    pipeline_contract_next_allowed_action = str(pipeline_contract["next_allowed_action"])
    system_readout_next_card = str(system_readout_module["next_card"])
    if (
        current_allowed_next_card != PIPELINE_DISPOSITION_DECISION_ACTION
        or pipeline_next_card != PIPELINE_DISPOSITION_DECISION_ACTION
        or pipeline_contract_next_allowed_action != PIPELINE_DISPOSITION_DECISION_ACTION
        or system_readout_next_card != PIPELINE_DISPOSITION_DECISION_ACTION
    ):
        raise ValueError("pipeline disposition decision is not the live allowed next card")
    return {
        "current_allowed_next_card": current_allowed_next_card,
        "pipeline_next_card": pipeline_next_card,
        "pipeline_contract_next_allowed_action": pipeline_contract_next_allowed_action,
        "system_readout_next_card": system_readout_next_card,
    }


def _load_followup_attribution(repo_root: Path) -> str:
    conclusion_path = (
        repo_root
        / "docs"
        / "04-execution"
        / "records"
        / "pipeline"
        / "pipeline-year-replay-source-selection-repair-card-20260509-01.conclusion.md"
    )
    text = conclusion_path.read_text(encoding="utf-8")
    match = FOLLOWUP_ATTRIBUTION_PATTERN.search(text)
    if match is None:
        raise ValueError("missing follow-up attribution in source-selection repair conclusion")
    return match.group("value")


def _assert_stage11_card_is_registered(repo_root: Path) -> None:
    roadmap_path = repo_root / "docs" / "03-refactor" / "04-asteria-full-system-roadmap-v1.md"
    roadmap_text = roadmap_path.read_text(encoding="utf-8")
    if PIPELINE_STAGE11_PROTOCOL_CARD not in roadmap_text:
        raise ValueError("missing Stage 11 protocol card in roadmap")


def _full_year_coverage_ok(
    selection: ReleasedYearReplaySourceSelection,
    *,
    target_year: int,
) -> bool:
    return (
        selection.year_observed_start == f"{target_year}-01-01"
        and selection.year_observed_end == f"{target_year}-12-31"
    )


def _write_disposition_artifacts(
    *,
    request: PipelineYearReplayDispositionDecisionRequest,
    selection: ReleasedYearReplaySourceSelection,
    governance_snapshot: dict[str, str],
    followup_attribution: str,
    full_year_audit_still_requires_full_natural_year: bool,
    status: str,
    decision: str,
    closeout_allowed: bool,
    rerun_recommended: bool,
    next_card: str,
    next_action: str,
) -> tuple[Path, Path, Path]:
    report_dir = request.report_root / "pipeline" / _utc_now().date().isoformat() / request.run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = report_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "run_id": request.run_id,
                "module": "pipeline",
                "stage": "year_replay_disposition_decision",
                "status": status,
                "decision": decision,
                "target_year": request.target_year,
                "released_source_selection": selection.as_dict(),
                "followup_attribution": followup_attribution,
                "full_year_audit_still_requires_full_natural_year": (
                    full_year_audit_still_requires_full_natural_year
                ),
                "closeout_allowed": closeout_allowed,
                "rerun_recommended": rerun_recommended,
                "next_card": next_card,
                "next_action": next_action,
                "governance_snapshot": governance_snapshot,
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
                "# Pipeline Year Replay Disposition Decision",
                "",
                f"- run_id: `{request.run_id}`",
                f"- released_system_run_id: `{selection.released_system_run_id}`",
                f"- released_system_observed_start: `{selection.observed_start}`",
                f"- released_system_observed_end: `{selection.observed_end}`",
                f"- source_lock_clean: `{selection.source_lock_clean}`",
                f"- followup_attribution: `{followup_attribution}`",
                (
                    "- full_year_audit_still_requires_full_natural_year: "
                    f"`{full_year_audit_still_requires_full_natural_year}`"
                ),
                f"- closeout_allowed: `{closeout_allowed}`",
                f"- rerun_recommended: `{rerun_recommended}`",
                f"- decision: `{decision}`",
                f"- next_card: `{next_card}`",
                f"- next_action: `{next_action}`",
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
