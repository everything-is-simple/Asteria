from __future__ import annotations

from datetime import datetime

from asteria.malf.contracts import MalfDayRequest
from asteria.malf.core_models import Bar, Candidate, Pivot, Transition, Wave


def bar_breaks_wave(wave: Wave, bar: Bar) -> bool:
    return (
        bar.low < wave.final_guard.pivot_price
        if wave.direction == "up"
        else bar.high > wave.final_guard.pivot_price
    )


def break_transition(
    wave: Wave,
    bar: Bar,
    request: MalfDayRequest,
    created_at: datetime,
) -> tuple[tuple[object, ...], Transition]:
    break_price = bar.low if wave.direction == "up" else bar.high
    break_id = f"{wave.wave_id}|break|{bar.bar_dt.isoformat()}"
    wave.wave_core_state = "terminated"
    wave.terminated_dt = bar.bar_dt
    wave.terminated_by_break_id = break_id
    transition = Transition(
        transition_id=f"{break_id}|transition",
        old_wave_id=wave.wave_id,
        break_id=break_id,
        old_direction=wave.direction,
        old_progress=wave.final_progress,
        old_guard=wave.final_guard,
        break_dt=bar.bar_dt,
        transition_boundary_high=max(wave.final_progress.pivot_price, wave.final_guard.pivot_price),
        transition_boundary_low=min(wave.final_progress.pivot_price, wave.final_guard.pivot_price),
    )
    return (
        (
            break_id,
            wave.wave_id,
            wave.direction,
            wave.final_guard.pivot_id,
            bar.bar_dt,
            break_price,
            "transition",
            request.run_id,
            request.schema_version,
            request.core_rule_version,
            created_at,
            wave.final_guard.pivot_id,
        ),
        transition,
    )


def confirm_candidate(
    transition: Transition, candidate: Candidate | None, pivot: Pivot
) -> str | None:
    if candidate is None or pivot.confirmed_dt <= candidate.guard.confirmed_dt:
        return None
    if (
        candidate.direction == "up"
        and pivot.pivot_type == "H"
        and pivot.pivot_price > transition.transition_boundary_high
    ):
        return "up"
    if (
        candidate.direction == "down"
        and pivot.pivot_type == "L"
        and pivot.pivot_price < transition.transition_boundary_low
    ):
        return "down"
    return None


def candidate_from_pivot(
    transition: Transition, pivot: Pivot, request: MalfDayRequest
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
        f"{transition.transition_id}|candidate|{pivot.pivot_id}|{direction}|"
        f"{request.core_rule_version}"
    )
    return Candidate(candidate_id, transition.transition_id, pivot, direction, reference)


def replace_active_candidate(active_candidate: Candidate, new_candidate: Candidate) -> None:
    active_candidate.is_active_at_close = False
    active_candidate.invalidated_by_candidate_id = new_candidate.candidate_id
    active_candidate.event_type = (
        "same_direction_candidate_refresh"
        if active_candidate.direction == new_candidate.direction
        else "opposite_direction_candidate_replacement"
    )


def snapshot_row(
    symbol: str,
    bar: Bar,
    active_wave: Wave | None,
    active_transition: Transition | None,
    active_candidate: Candidate | None,
    progress_updated: bool,
    request: MalfDayRequest,
    created_at: datetime,
    confirmation_pivot_id: str | None,
    new_wave_id: str | None,
    birth_transition: Transition | None,
    birth_candidate: Candidate | None,
) -> tuple[object, ...] | None:
    if active_wave is None and active_transition is None:
        return None
    if active_transition is not None:
        active_transition.span += 1
        return (
            f"{symbol}|{bar.bar_dt.isoformat()}|transition|{request.core_rule_version}",
            symbol,
            request.timeframe,
            bar.bar_dt,
            "transition",
            None,
            active_transition.old_wave_id,
            "terminated",
            active_transition.old_direction,
            False,
            active_transition.span,
            active_transition.old_progress.pivot_price,
            active_transition.old_guard.pivot_id,
            active_transition.old_guard.pivot_price,
            active_transition.transition_id,
            active_transition.break_id,
            active_transition.transition_boundary_high,
            active_transition.transition_boundary_low,
            None if active_candidate is None else active_candidate.candidate_id,
            None if active_candidate is None else active_candidate.guard.pivot_id,
            None,
            None,
            request.run_id,
            request.schema_version,
            request.core_rule_version,
            request.pivot_detection_rule_version,
            request.core_event_ordering_version,
            request.price_compare_policy,
            request.epsilon_policy,
            created_at,
        )
    if active_wave is None:
        return None
    trace_transition = birth_transition
    trace_candidate = birth_candidate
    return (
        f"{symbol}|{bar.bar_dt.isoformat()}|{active_wave.wave_id}|{request.core_rule_version}",
        symbol,
        request.timeframe,
        bar.bar_dt,
        f"{active_wave.direction}_alive",
        active_wave.wave_id,
        None,
        active_wave.wave_core_state,
        active_wave.direction,
        progress_updated,
        0,
        active_wave.final_guard.pivot_price,
        active_wave.final_guard.pivot_id,
        active_wave.final_guard.pivot_price,
        None,
        active_wave.terminated_by_break_id,
        None if trace_transition is None else trace_transition.transition_boundary_high,
        None if trace_transition is None else trace_transition.transition_boundary_low,
        None if trace_candidate is None else trace_candidate.candidate_id,
        None if trace_candidate is None else trace_candidate.guard.pivot_id,
        confirmation_pivot_id,
        new_wave_id,
        request.run_id,
        request.schema_version,
        request.core_rule_version,
        request.pivot_detection_rule_version,
        request.core_event_ordering_version,
        request.price_compare_policy,
        request.epsilon_policy,
        created_at,
    )
