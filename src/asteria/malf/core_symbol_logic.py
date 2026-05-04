from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from asteria.malf.contracts import MalfDayRequest
from asteria.malf.core_models import Bar, Candidate, Pivot, Transition, Wave
from asteria.malf.core_transition_logic import (
    bar_breaks_wave,
    break_transition,
    candidate_from_pivot,
    confirm_candidate,
    replace_active_candidate,
    snapshot_row,
)


@dataclass(frozen=True)
class SymbolBuildRows:
    structures: list[tuple[object, ...]]
    waves: list[Wave]
    breaks: list[tuple[object, ...]]
    transitions: list[Transition]
    candidates: list[Candidate]
    snapshots: list[tuple[object, ...]]


def build_symbol_rows(
    symbol: str,
    bars: list[Bar],
    pivots: list[Pivot],
    request: MalfDayRequest,
    created_at: datetime,
) -> SymbolBuildRows:
    confirmed_by_bar: dict[date, list[Pivot]] = {}
    for pivot in pivots:
        confirmed_by_bar.setdefault(pivot.confirmed_dt, []).append(pivot)
    for pivot_list in confirmed_by_bar.values():
        pivot_list.sort(key=lambda item: (item.pivot_dt, 0 if item.pivot_type == "H" else 1))

    structures: list[tuple[object, ...]] = []
    waves: list[Wave] = []
    breaks: list[tuple[object, ...]] = []
    transitions: list[Transition] = []
    candidates: list[Candidate] = []
    snapshots: list[tuple[object, ...]] = []
    pivot_history: list[Pivot] = []
    initial_references: dict[str, Pivot] = {}
    active_wave: Wave | None = None
    active_transition: Transition | None = None
    active_candidate: Candidate | None = None
    wave_seq = 0

    for bar in bars:
        progress_updated = False
        confirmation_pivot_id: str | None = None
        new_wave_id: str | None = None
        birth_transition: Transition | None = None
        birth_candidate: Candidate | None = None

        for pivot in confirmed_by_bar.get(bar.bar_dt, []):
            if active_wave is None and active_transition is None:
                structures.extend(
                    _initial_structure_rows(
                        pivot, initial_references.get(pivot.pivot_type), request, created_at
                    )
                )
                initial_references[pivot.pivot_type] = pivot
                pivot_history.append(pivot)
                initial_wave = _try_initial_wave(pivot_history, request, wave_seq + 1)
                if initial_wave is not None:
                    active_wave = initial_wave
                    waves.append(initial_wave)
                    wave_seq += 1
                    progress_updated = True
                    confirmation_pivot_id = initial_wave.confirm_pivot_id
                    new_wave_id = initial_wave.wave_id
                continue

            pivot_history.append(pivot)
            if active_wave is not None:
                structure_row, updated = _advance_wave_with_pivot(
                    active_wave, pivot, request, created_at
                )
                if structure_row is not None:
                    structures.append(structure_row)
                progress_updated = progress_updated or updated
                continue

            if active_transition is None:
                continue
            structure_row = _transition_structure_row(
                active_transition, active_candidate, pivot, request, created_at
            )
            if structure_row is not None:
                structures.append(structure_row)

            confirmed_direction = confirm_candidate(active_transition, active_candidate, pivot)
            if confirmed_direction and active_candidate is not None:
                wave_seq += 1
                birth_type = (
                    "same_direction_after_break"
                    if confirmed_direction == active_transition.old_direction
                    else "opposite_direction_after_break"
                )
                new_wave = _new_wave(
                    symbol,
                    wave_seq,
                    confirmed_direction,
                    birth_type,
                    active_candidate.guard,
                    pivot,
                    request,
                )
                active_transition.state = "confirmed"
                active_transition.confirmed_dt = bar.bar_dt
                active_transition.new_wave_id = new_wave.wave_id
                active_candidate.confirmed_by_pivot_id = pivot.pivot_id
                active_candidate.confirmed_wave_id = new_wave.wave_id
                active_candidate.event_type = "confirmed"
                active_wave = new_wave
                waves.append(new_wave)
                progress_updated = True
                confirmation_pivot_id = pivot.pivot_id
                new_wave_id = new_wave.wave_id
                birth_transition = active_transition
                birth_candidate = active_candidate
                active_transition = None
                active_candidate = None
                continue

            new_candidate = candidate_from_pivot(active_transition, pivot, request)
            if new_candidate is None:
                continue
            if active_candidate is not None and active_candidate.confirmed_wave_id is None:
                replace_active_candidate(active_candidate, new_candidate)
            candidates.append(new_candidate)
            active_candidate = new_candidate

        if active_wave is not None and bar_breaks_wave(active_wave, bar):
            break_row, transition = break_transition(active_wave, bar, request, created_at)
            breaks.append(break_row)
            transitions.append(transition)
            active_transition = transition
            active_wave = None
            active_candidate = None
            progress_updated = False

        snapshot = snapshot_row(
            symbol=symbol,
            bar=bar,
            active_wave=active_wave,
            active_transition=active_transition,
            active_candidate=active_candidate,
            progress_updated=progress_updated,
            request=request,
            created_at=created_at,
            confirmation_pivot_id=confirmation_pivot_id,
            new_wave_id=new_wave_id,
            birth_transition=birth_transition,
            birth_candidate=birth_candidate,
        )
        if snapshot is not None:
            snapshots.append(snapshot)

    return SymbolBuildRows(structures, waves, breaks, transitions, candidates, snapshots)


def _initial_structure_rows(
    pivot: Pivot,
    reference: Pivot | None,
    request: MalfDayRequest,
    created_at: datetime,
) -> list[tuple[object, ...]]:
    if reference is None:
        return []
    primitive, direction_context = _primitive_and_direction(
        pivot.pivot_type, pivot.pivot_price, reference
    )
    return [
        _structure_row(
            pivot=pivot,
            context="initial_candidate",
            reference=reference,
            primitive=primitive,
            direction_context=direction_context,
            request=request,
            created_at=created_at,
        )
    ]


def _advance_wave_with_pivot(
    wave: Wave,
    pivot: Pivot,
    request: MalfDayRequest,
    created_at: datetime,
) -> tuple[tuple[object, ...] | None, bool]:
    if wave.direction == "up":
        if pivot.pivot_type == "H":
            reference = wave.final_progress
            primitive = "HH" if pivot.pivot_price > reference.pivot_price else "LH"
            updated = pivot.pivot_price > reference.pivot_price
            if updated:
                wave.final_progress = pivot
        else:
            reference = wave.final_guard
            primitive = "HL" if pivot.pivot_price > reference.pivot_price else "LL"
            updated = False
            if pivot.pivot_price > reference.pivot_price:
                wave.final_guard = pivot
    else:
        if pivot.pivot_type == "L":
            reference = wave.final_progress
            primitive = "LL" if pivot.pivot_price < reference.pivot_price else "HL"
            updated = pivot.pivot_price < reference.pivot_price
            if updated:
                wave.final_progress = pivot
        else:
            reference = wave.final_guard
            primitive = "LH" if pivot.pivot_price < reference.pivot_price else "HH"
            updated = False
            if pivot.pivot_price < reference.pivot_price:
                wave.final_guard = pivot
    direction_context = "up" if primitive in {"HH", "HL"} else "down"
    return (
        _structure_row(
            pivot=pivot,
            context="active_wave",
            reference=reference,
            primitive=primitive,
            direction_context=direction_context,
            request=request,
            created_at=created_at,
        ),
        updated,
    )


def _transition_structure_row(
    transition: Transition,
    active_candidate: Candidate | None,
    pivot: Pivot,
    request: MalfDayRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    reference = (
        active_candidate.guard
        if active_candidate is not None
        and active_candidate.direction == ("down" if pivot.pivot_type == "H" else "up")
        else transition.boundary_high_pivot
        if pivot.pivot_type == "H"
        else transition.boundary_low_pivot
    )
    primitive, direction_context = _primitive_and_direction(
        pivot.pivot_type, pivot.pivot_price, reference
    )
    return _structure_row(
        pivot=pivot,
        context="transition_candidate",
        reference=reference,
        primitive=primitive,
        direction_context=direction_context,
        request=request,
        created_at=created_at,
    )


def _primitive_and_direction(
    pivot_type: str, pivot_price: float, reference: Pivot
) -> tuple[str, str]:
    if pivot_type == "H":
        primitive = "HH" if pivot_price > reference.pivot_price else "LH"
    else:
        primitive = "HL" if pivot_price > reference.pivot_price else "LL"
    return primitive, ("up" if primitive in {"HH", "HL"} else "down")


def _structure_row(
    pivot: Pivot,
    context: str,
    reference: Pivot,
    primitive: str,
    direction_context: str,
    request: MalfDayRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    return (
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


def _try_initial_wave(pivots: list[Pivot], request: MalfDayRequest, wave_seq: int) -> Wave | None:
    if len(pivots) < 3:
        return None
    first, guard, confirm = pivots[-3:]
    if (
        first.pivot_type == "H"
        and guard.pivot_type == "L"
        and confirm.pivot_type == "H"
        and confirm.pivot_price > first.pivot_price
    ):
        return _new_wave(first.symbol, wave_seq, "up", "initial", guard, confirm, request)
    if (
        first.pivot_type == "L"
        and guard.pivot_type == "H"
        and confirm.pivot_type == "L"
        and confirm.pivot_price < first.pivot_price
    ):
        return _new_wave(first.symbol, wave_seq, "down", "initial", guard, confirm, request)
    return None


def _new_wave(
    symbol: str,
    wave_seq: int,
    direction: str,
    birth_type: str,
    guard: Pivot,
    confirm: Pivot,
    request: MalfDayRequest,
) -> Wave:
    wave_id = f"{symbol}|{request.timeframe}|wave-{wave_seq}|{request.core_rule_version}"
    return Wave(
        wave_id=wave_id,
        symbol=symbol,
        wave_seq=wave_seq,
        direction=direction,
        birth_type=birth_type,
        start_pivot_id=guard.pivot_id,
        candidate_guard_pivot_id=guard.pivot_id,
        confirm_pivot_id=confirm.pivot_id,
        confirm_dt=confirm.confirmed_dt,
        wave_core_state="alive",
        final_progress=confirm,
        final_guard=guard,
    )
