from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from typing import Any, TypedDict

from asteria.alpha.pas_contracts import PAS_SOURCE_CONCEPT_TRACE


@dataclass(frozen=True)
class PasWavePosition:
    symbol: str
    timeframe: str
    bar_dt: date
    system_state: str
    wave_core_state: str
    direction: str | None
    new_count: int
    no_new_span: int
    transition_span: int
    update_rank: float | None
    stagnation_rank: float | None
    life_state: str
    position_quadrant: str
    guard_boundary_price: float | None
    sample_version: str | None
    service_version: str
    run_id: str


class BaselineProfile(TypedDict):
    direction: str | None
    sample_count: int
    avg_update_rank: float
    basis: str


def wave_position_from_row(row: tuple[Any, ...]) -> PasWavePosition:
    return PasWavePosition(
        symbol=str(row[0]),
        timeframe=str(row[1]),
        bar_dt=coerce_date(row[2]),
        system_state=str(row[3]),
        wave_core_state=str(row[4]),
        direction=None if row[5] is None else str(row[5]),
        new_count=int(row[6] or 0),
        no_new_span=int(row[7] or 0),
        transition_span=int(row[8] or 0),
        update_rank=None if row[9] is None else float(row[9]),
        stagnation_rank=None if row[10] is None else float(row[10]),
        life_state=str(row[11]),
        position_quadrant=str(row[12]),
        guard_boundary_price=None if row[13] is None else float(row[13]),
        sample_version=None if row[14] is None else str(row[14]),
        service_version=str(row[15]),
        run_id=str(row[16]),
    )


def setup_family(source: PasWavePosition) -> str:
    if source.transition_span > 0:
        return "BPB"
    if source.no_new_span >= 2 and source.position_quadrant == "extended_stagnant":
        return "CPB"
    if source.no_new_span >= 1:
        return "TST"
    if source.new_count >= 2:
        return "BOF"
    return "PB"


def candidate_state(
    source: PasWavePosition,
    seen_terminal: set[str],
) -> tuple[str, str, str]:
    if source.system_state == "transition":
        return "invalidated", "transition_in_flight_invalidates_setup", "current_transition"
    if source.no_new_span >= 3:
        return "modified", "no_followthrough_requires_revision", "setup_modified"
    if source.symbol in seen_terminal and source.new_count > 0:
        return "reentry_candidate", "post_failure_reentry_visible", "prior_failure_preserved"
    if source.update_rank is not None and source.update_rank >= 0.65 and source.new_count > 0:
        return "triggered", "setup_time_trigger_visible", "none"
    if source.no_new_span > 0:
        return "cancelled", "setup_premise_removed_before_trigger", "stagnation_cancelled"
    return "waiting", "setup_not_triggered_yet", "waiting_for_trigger"


def completed_baseline(
    source: PasWavePosition,
    history: list[PasWavePosition],
) -> BaselineProfile:
    completed = [
        item
        for item in history
        if item.direction == source.direction and item.system_state != "transition"
    ]
    values = [value for item in completed if (value := item.update_rank) is not None]
    avg = round(sum(values) / len(values), 6) if values else 0.0
    return {
        "direction": source.direction,
        "sample_count": len(completed),
        "avg_update_rank": avg,
        "basis": "completed_same_direction_before_setup",
    }


def opposite_comparison(
    source: PasWavePosition,
    history: list[PasWavePosition],
) -> dict[str, object]:
    opposite = [item for item in history if item.direction != source.direction and item.direction]
    values = [value for item in opposite if (value := item.update_rank) is not None]
    avg = round(sum(values) / len(values), 6) if values else 0.0
    return {"sample_count": len(opposite), "avg_update_rank": avg}


def in_flight_confirmation(source: PasWavePosition) -> dict[str, object]:
    return {
        "system_state": source.system_state,
        "wave_core_state": source.wave_core_state,
        "transition_span": source.transition_span,
        "new_count": source.new_count,
        "no_new_span": source.no_new_span,
        "use": "confirmation_or_invalidation_only",
    }


def strength_score(baseline: BaselineProfile) -> float:
    score = baseline["avg_update_rank"]
    if baseline["sample_count"] == 0:
        return 0.0
    return round(max(0.0, min(1.0, score)), 6)


def strength_bucket(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def confidence(bucket: str, sample_count: int) -> str:
    if sample_count < 2:
        return "research_only_sparse"
    return bucket


def context_reason(source: PasWavePosition) -> str:
    return f"malf_{source.system_state}_{source.position_quadrant}"


def boundary_interaction(source: PasWavePosition) -> str:
    if source.guard_boundary_price is None:
        return "boundary_not_available"
    return "guard_boundary_visible"


def stagnation_evidence(source: PasWavePosition) -> str:
    if source.no_new_span > 0:
        return f"no_new_span={source.no_new_span}"
    return "no_stagnation_evidence"


def sparsity_label(sample_count: int) -> str:
    return "sparse" if sample_count < 3 else "usable"


def lineage(
    source: PasWavePosition,
    family: str,
    state: str,
    proof_run_id: str,
) -> dict[str, object]:
    return {
        "source": "MALF v1.4 WavePosition",
        "setup_family": family,
        "candidate_state": state,
        "source_run_id": proof_run_id,
        "malf_wave_position_run_id": source.run_id,
        "source_concept_trace": PAS_SOURCE_CONCEPT_TRACE,
    }


def lineage_json(payload: dict[str, object]) -> str:
    return json.dumps(payload, sort_keys=True)


def is_terminal(source: PasWavePosition) -> bool:
    return source.system_state == "transition" or source.wave_core_state == "terminated"


def coerce_date(value: object) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))
