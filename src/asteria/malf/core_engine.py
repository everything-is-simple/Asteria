from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import duckdb

from asteria.malf.contracts import MalfDayRequest
from asteria.malf.core_runtime_support import (
    candidate_event_type,
)
from asteria.malf.core_runtime_support import (
    candidate_from_pivot as _candidate_from_pivot,
)
from asteria.malf.core_runtime_support import (
    confirm_candidate as _confirm_candidate,
)
from asteria.malf.core_runtime_support import (
    seed_active_wave_context as _seed_active_wave_context,
)
from asteria.malf.core_runtime_support import (
    snapshot_row as _snapshot_row,
)
from asteria.malf.core_runtime_support import (
    structure_rows_for_pivot as _structure_rows_for_pivot,
)
from asteria.malf.core_types import Bar, Candidate, Pivot, Transition, Wave
from asteria.malf.source_contract import market_base_day_clauses

_candidate_event_type = candidate_event_type


@dataclass(frozen=True)
class CoreBuildRows:
    pivots: list[Pivot]
    structures: list[tuple[object, ...]]
    waves: list[Wave]
    breaks: list[tuple[object, ...]]
    transitions: list[Transition]
    candidates: list[Candidate]
    snapshots: list[tuple[object, ...]]


@dataclass(frozen=True)
class _SymbolResult:
    structures: list[tuple[object, ...]]
    waves: list[Wave]
    breaks: list[tuple[object, ...]]
    transitions: list[Transition]
    candidates: list[Candidate]
    snapshots: list[tuple[object, ...]]


def build_core_rows(
    request: MalfDayRequest,
    created_at: datetime,
    source_market_base_run_id: str | None = None,
) -> CoreBuildRows:
    bars_by_symbol = _load_bars(request.source_db, request)
    all_pivots: list[Pivot] = []
    structures: list[tuple[object, ...]] = []
    waves: list[Wave] = []
    breaks: list[tuple[object, ...]] = []
    transitions: list[Transition] = []
    candidates: list[Candidate] = []
    snapshots: list[tuple[object, ...]] = []

    for symbol, bars in bars_by_symbol.items():
        pivots = _detect_pivots(symbol, bars, request)
        all_pivots.extend(pivots)
        result = _build_symbol_core(
            bars,
            pivots,
            request,
            created_at,
            source_market_base_run_id,
        )
        structures.extend(result.structures)
        waves.extend(result.waves)
        breaks.extend(result.breaks)
        transitions.extend(result.transitions)
        candidates.extend(result.candidates)
        snapshots.extend(result.snapshots)

    return CoreBuildRows(
        pivots=all_pivots,
        structures=structures,
        waves=waves,
        breaks=breaks,
        transitions=transitions,
        candidates=candidates,
        snapshots=snapshots,
    )


def _load_bars(source_db: Path, request: MalfDayRequest) -> dict[str, list[Bar]]:
    clauses, params = market_base_day_clauses(request)

    symbol_clause = ""
    if request.symbol_limit is not None and not request.symbols:
        with duckdb.connect(str(source_db), read_only=True) as con:
            symbols = [
                row[0]
                for row in con.execute(
                    f"""
                    select distinct symbol
                    from market_base_bar
                    where {" and ".join(clauses)}
                    order by symbol
                    limit ?
                    """,
                    [*params, request.symbol_limit],
                ).fetchall()
            ]
        if not symbols:
            return {}
        symbol_clause = f" and symbol in ({', '.join(['?'] * len(symbols))})"
        params.extend(symbols)

    query = f"""
        select symbol, bar_dt, high_px, low_px
        from market_base_bar
        where {" and ".join(clauses)}{symbol_clause}
        order by symbol, bar_dt
    """
    output: dict[str, list[Bar]] = {}
    with duckdb.connect(str(source_db), read_only=True) as con:
        for symbol, bar_dt, high, low in con.execute(query, params).fetchall():
            output.setdefault(str(symbol), []).append(
                Bar(str(symbol), bar_dt, float(high), float(low))
            )
    return output


def _detect_pivots(symbol: str, bars: list[Bar], request: MalfDayRequest) -> list[Pivot]:
    raw: list[Pivot] = []
    seq_by_bar: dict[tuple[date, str], int] = {}
    for idx in range(1, len(bars) - 1):
        prev_bar, bar, next_bar = bars[idx - 1], bars[idx], bars[idx + 1]
        if bar.high > prev_bar.high and bar.high >= next_bar.high:
            raw.append(_pivot(symbol, bar, next_bar.bar_dt, "H", bar.high, seq_by_bar, request))
        if bar.low < prev_bar.low and bar.low <= next_bar.low:
            raw.append(_pivot(symbol, bar, next_bar.bar_dt, "L", bar.low, seq_by_bar, request))
    raw.sort(
        key=lambda item: (
            item.confirmed_dt,
            item.pivot_dt,
            item.pivot_seq_in_bar,
            0 if item.pivot_type == "H" else 1,
        )
    )

    collapsed: list[Pivot] = []
    for pivot in raw:
        if not collapsed or collapsed[-1].pivot_type != pivot.pivot_type:
            collapsed.append(pivot)
            continue
        previous = collapsed[-1]
        if (
            pivot.pivot_type == "H"
            and pivot.pivot_price >= previous.pivot_price
            or pivot.pivot_type == "L"
            and pivot.pivot_price <= previous.pivot_price
        ):
            collapsed[-1] = pivot
    return collapsed


def _pivot(
    symbol: str,
    bar: Bar,
    confirmed_dt: date,
    pivot_type: str,
    price: float,
    seq_by_bar: dict[tuple[date, str], int],
    request: MalfDayRequest,
) -> Pivot:
    key = (bar.bar_dt, pivot_type)
    seq = seq_by_bar.get(key, 0)
    seq_by_bar[key] = seq + 1
    pivot_id = (
        f"{symbol}|{request.timeframe}|{bar.bar_dt.isoformat()}|"
        f"{pivot_type}|{seq}|{request.core_rule_version}"
    )
    return Pivot(pivot_id, symbol, bar.bar_dt, confirmed_dt, pivot_type, price, seq)


def _build_symbol_core(
    bars: list[Bar],
    pivots: list[Pivot],
    request: MalfDayRequest,
    created_at: datetime,
    source_market_base_run_id: str | None,
) -> _SymbolResult:
    pivots_by_confirmed_dt: dict[date, list[Pivot]] = {}
    for pivot in pivots:
        pivots_by_confirmed_dt.setdefault(pivot.confirmed_dt, []).append(pivot)
    for confirmed_dt in pivots_by_confirmed_dt:
        pivots_by_confirmed_dt[confirmed_dt].sort(
            key=lambda item: (
                item.pivot_dt,
                item.pivot_seq_in_bar,
                0 if item.pivot_type == "H" else 1,
            )
        )

    structures: list[tuple[object, ...]] = []
    waves: list[Wave] = []
    breaks: list[tuple[object, ...]] = []
    transitions: list[Transition] = []
    candidates: list[Candidate] = []
    snapshots: list[tuple[object, ...]] = []

    context_refs: dict[str, dict[str, Pivot]] = {
        "initial_candidate": {},
        "active_wave": {},
        "transition_candidate": {},
    }
    seen_pivots: list[Pivot] = []
    active_wave: Wave | None = None
    active_transition: Transition | None = None
    active_candidate: Candidate | None = None
    wave_seq = 0

    for bar in bars:
        progress_updated = False
        confirmation_pivot_id: str | None = None
        new_wave_id: str | None = None
        confirmed_pivots = pivots_by_confirmed_dt.get(bar.bar_dt, [])
        if active_transition is None:
            for pivot in confirmed_pivots:
                seen_pivots.append(pivot)
                if active_wave is None:
                    structures.extend(
                        _structure_rows_for_pivot(
                            pivot,
                            "initial_candidate",
                            context_refs["initial_candidate"],
                            request,
                            created_at,
                        )
                    )
                    initial = _try_initial_wave(
                        seen_pivots,
                        len(seen_pivots) - 1,
                        request,
                        wave_seq + 1,
                    )
                    if initial is not None:
                        wave_seq += 1
                        active_wave = initial
                        waves.append(initial)
                        _seed_active_wave_context(context_refs["active_wave"], active_wave)
                        progress_updated = True
                    continue
                structures.extend(
                    _structure_rows_for_pivot(
                        pivot,
                        "active_wave",
                        context_refs["active_wave"],
                        request,
                        created_at,
                    )
                )
                progress_updated = _apply_active_wave_pivot(active_wave, pivot) or progress_updated

        if active_wave is not None:
            opened = _break_transition_from_bar(active_wave, bar, request, created_at)
            if opened is not None:
                break_row, active_transition = opened
                breaks.append(break_row)
                transitions.append(active_transition)
                active_wave = None
                active_candidate = None

        if active_transition is not None:
            for pivot in confirmed_pivots:
                if pivot.pivot_dt < active_transition.break_dt:
                    continue
                structures.extend(
                    _structure_rows_for_pivot(
                        pivot,
                        "transition_candidate",
                        context_refs["transition_candidate"],
                        request,
                        created_at,
                    )
                )
                confirmed_direction = _confirm_candidate(active_candidate, pivot)
                if confirmed_direction is not None and active_candidate is not None:
                    wave_seq += 1
                    birth_type = (
                        "same_direction_after_break"
                        if confirmed_direction == active_transition.old_direction
                        else "opposite_direction_after_break"
                    )
                    active_wave = _new_wave(
                        pivot.symbol,
                        wave_seq,
                        confirmed_direction,
                        birth_type,
                        active_candidate.guard,
                        pivot,
                        request,
                    )
                    waves.append(active_wave)
                    _seed_active_wave_context(context_refs["active_wave"], active_wave)
                    active_transition.state = "confirmed"
                    active_transition.confirmed_dt = pivot.pivot_dt
                    active_transition.new_wave_id = active_wave.wave_id
                    active_candidate.confirmed_by_pivot_id = pivot.pivot_id
                    active_candidate.confirmed_wave_id = active_wave.wave_id
                    active_candidate.event_type = "confirmed"
                    confirmation_pivot_id = pivot.pivot_id
                    new_wave_id = active_wave.wave_id
                    progress_updated = True
                    active_transition = None
                    active_candidate = None
                    break

                new_candidate = _candidate_from_pivot(
                    active_transition, pivot, request, active_candidate
                )
                if new_candidate is None:
                    continue
                if active_candidate is not None and active_candidate.confirmed_wave_id is None:
                    active_candidate.is_active_at_close = False
                    active_candidate.invalidated_by_candidate_id = new_candidate.candidate_id
                candidates.append(new_candidate)
                active_candidate = new_candidate

        if active_transition is not None and bar.bar_dt > active_transition.break_dt:
            active_transition.transition_span += 1

        snapshots.append(
            _snapshot_row(
                bar,
                active_wave,
                active_transition,
                active_candidate,
                progress_updated,
                confirmation_pivot_id,
                new_wave_id,
                request,
                source_market_base_run_id,
                created_at,
            )
        )

    return _SymbolResult(
        structures=structures,
        waves=waves,
        breaks=breaks,
        transitions=transitions,
        candidates=candidates,
        snapshots=snapshots,
    )


def _try_initial_wave(
    pivots: list[Pivot], index: int, request: MalfDayRequest, wave_seq: int
) -> Wave | None:
    if index < 2:
        return None
    first, guard, confirm = pivots[index - 2], pivots[index - 1], pivots[index]
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
        confirm_dt=confirm.pivot_dt,
        wave_core_state="alive",
        final_progress=confirm,
        final_guard=guard,
    )


def _apply_active_wave_pivot(wave: Wave, pivot: Pivot) -> bool:
    if wave.direction == "up":
        if pivot.pivot_type == "H" and pivot.pivot_price > wave.final_progress.pivot_price:
            wave.final_progress = pivot
            return True
        if pivot.pivot_type == "L" and pivot.pivot_price > wave.final_guard.pivot_price:
            wave.final_guard = pivot
            return True
        return False
    if pivot.pivot_type == "L" and pivot.pivot_price < wave.final_progress.pivot_price:
        wave.final_progress = pivot
        return True
    if pivot.pivot_type == "H" and pivot.pivot_price < wave.final_guard.pivot_price:
        wave.final_guard = pivot
        return True
    return False


def _break_transition_from_bar(
    wave: Wave,
    bar: Bar,
    request: MalfDayRequest,
    created_at: datetime,
) -> tuple[tuple[object, ...], Transition] | None:
    if wave.direction == "up":
        if bar.low >= wave.final_guard.pivot_price:
            return None
        break_price = bar.low
    else:
        if bar.high <= wave.final_guard.pivot_price:
            return None
        break_price = bar.high
    return _break_transition(wave, bar.bar_dt, break_price, request, created_at)


def _break_transition(
    wave: Wave,
    break_dt: date,
    break_price: float,
    request: MalfDayRequest,
    created_at: datetime,
) -> tuple[tuple[object, ...], Transition]:
    break_id = f"{wave.wave_id}|break|{break_dt.isoformat()}"
    transition_id = f"{break_id}|transition"
    wave.wave_core_state = "terminated"
    wave.terminated_dt = break_dt
    wave.terminated_by_break_id = break_id
    break_row = (
        break_id,
        wave.wave_id,
        wave.direction,
        wave.final_guard.pivot_id,
        break_dt,
        break_price,
        "transition",
        request.run_id,
        request.schema_version,
        request.core_rule_version,
        created_at,
        wave.final_guard.pivot_id,
    )
    boundary_prices = (wave.final_progress.pivot_price, wave.final_guard.pivot_price)
    transition = Transition(
        transition_id=transition_id,
        old_wave_id=wave.wave_id,
        break_id=break_id,
        old_direction=wave.direction,
        old_progress=wave.final_progress,
        old_guard=wave.final_guard,
        break_dt=break_dt,
        transition_boundary_high=max(boundary_prices),
        transition_boundary_low=min(boundary_prices),
    )
    return break_row, transition
