from __future__ import annotations

from datetime import datetime

from asteria.malf.contracts import MalfDayRequest
from asteria.malf.core_types import Bar, Candidate, Pivot, Transition, Wave


def structure_rows_for_pivot(
    pivot: Pivot,
    context: str,
    refs_by_type: dict[str, Pivot],
    request: MalfDayRequest,
    created_at: datetime,
) -> list[tuple[object, ...]]:
    reference = refs_by_type.get(pivot.pivot_type)
    refs_by_type[pivot.pivot_type] = pivot
    if reference is None:
        return []
    if pivot.pivot_type == "H":
        primitive = "HH" if pivot.pivot_price > reference.pivot_price else "LH"
        direction_context = "up" if primitive == "HH" else "down"
    else:
        primitive = "HL" if pivot.pivot_price > reference.pivot_price else "LL"
        direction_context = "up" if primitive == "HL" else "down"
    return [
        (
            f"{pivot.pivot_id}|{primitive}|{reference.pivot_id}",
            pivot.pivot_id,
            context,
            reference.pivot_id,
            reference.pivot_price,
            primitive,
            direction_context,
            pivot.symbol,
            request.timeframe,
            pivot.pivot_dt,
            request.run_id,
            request.schema_version,
            request.core_rule_version,
            created_at,
        )
    ]


def seed_active_wave_context(refs_by_type: dict[str, Pivot], wave: Wave) -> None:
    refs_by_type["H"] = wave.final_progress if wave.direction == "up" else wave.final_guard
    refs_by_type["L"] = wave.final_guard if wave.direction == "up" else wave.final_progress


def candidate_event_type(active_candidate: Candidate | None, direction: str) -> str:
    if active_candidate is None:
        return "candidate_created"
    if active_candidate.direction == direction:
        return "same_direction_candidate_refresh"
    return "opposite_direction_candidate_replacement"


def confirm_candidate(candidate: Candidate | None, pivot: Pivot) -> str | None:
    if candidate is None or pivot.pivot_dt <= candidate.guard.pivot_dt:
        return None
    if (
        candidate.direction == "up"
        and pivot.pivot_type == "H"
        and pivot.pivot_price > candidate.reference_price
    ):
        return "up"
    if (
        candidate.direction == "down"
        and pivot.pivot_type == "L"
        and pivot.pivot_price < candidate.reference_price
    ):
        return "down"
    return None


def candidate_from_pivot(
    transition: Transition,
    pivot: Pivot,
    request: MalfDayRequest,
    active_candidate: Candidate | None,
) -> Candidate | None:
    if pivot.pivot_type not in {"H", "L"}:
        return None
    direction = "up" if pivot.pivot_type == "L" else "down"
    reference = (
        transition.transition_boundary_high
        if direction == "up"
        else transition.transition_boundary_low
    )
    candidate_id = (
        f"{transition.transition_id}|candidate|{pivot.pivot_id}|"
        f"{direction}|{request.core_rule_version}"
    )
    return Candidate(
        candidate_id=candidate_id,
        transition_id=transition.transition_id,
        guard=pivot,
        direction=direction,
        reference_price=reference,
        event_type=candidate_event_type(active_candidate, direction),
    )


def snapshot_row(
    bar: Bar,
    active_wave: Wave | None,
    active_transition: Transition | None,
    active_candidate: Candidate | None,
    progress_updated: bool,
    confirmation_pivot_id: str | None,
    new_wave_id: str | None,
    request: MalfDayRequest,
    source_market_base_run_id: str | None,
    created_at: datetime,
) -> tuple[object, ...]:
    if active_wave is not None:
        system_state = f"{active_wave.direction}_alive"
        wave_core_state = "alive"
        wave_id = active_wave.wave_id
        old_wave_id = None
        direction = active_wave.direction
        transition_span = 0
        guard_boundary_price = active_wave.final_guard.pivot_price
        current_guard_pivot_id = active_wave.final_guard.pivot_id
        current_guard_price = active_wave.final_guard.pivot_price
        transition_id = None
        break_id = None
        transition_boundary_high = None
        transition_boundary_low = None
    elif active_transition is not None:
        system_state = "transition"
        wave_core_state = "terminated"
        wave_id = None
        old_wave_id = active_transition.old_wave_id
        direction = active_transition.old_direction
        transition_span = active_transition.transition_span
        guard_boundary_price = active_transition.old_guard.pivot_price
        current_guard_pivot_id = active_transition.old_guard.pivot_id
        current_guard_price = active_transition.old_guard.pivot_price
        transition_id = active_transition.transition_id
        break_id = active_transition.break_id
        transition_boundary_high = active_transition.transition_boundary_high
        transition_boundary_low = active_transition.transition_boundary_low
    else:
        system_state = "uninitialized"
        wave_core_state = "alive"
        wave_id = None
        old_wave_id = None
        direction = None
        transition_span = 0
        guard_boundary_price = None
        current_guard_pivot_id = None
        current_guard_price = None
        transition_id = None
        break_id = None
        transition_boundary_high = None
        transition_boundary_low = None

    snapshot_id = f"{bar.symbol}|{request.timeframe}|{bar.bar_dt.isoformat()}|{request.run_id}"
    return (
        snapshot_id,
        bar.symbol,
        request.timeframe,
        bar.bar_dt,
        system_state,
        wave_id,
        old_wave_id,
        wave_core_state,
        direction,
        progress_updated,
        transition_span,
        guard_boundary_price,
        current_guard_pivot_id,
        current_guard_price,
        transition_id,
        break_id,
        transition_boundary_high,
        transition_boundary_low,
        None if active_candidate is None else active_candidate.candidate_id,
        None if active_candidate is None else active_candidate.guard.pivot_id,
        confirmation_pivot_id,
        new_wave_id,
        request.run_id,
        request.schema_version,
        request.core_rule_version,
        request.pivot_detection_rule_version,
        request.core_event_ordering_version,
        request.price_compare_policy,
        request.epsilon_policy,
        source_market_base_run_id,
        created_at,
    )
