from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import duckdb

from asteria.malf.contracts import MalfDayRequest


@dataclass(frozen=True)
class Bar:
    symbol: str
    bar_dt: date
    high: float
    low: float


@dataclass
class Pivot:
    pivot_id: str
    symbol: str
    pivot_dt: date
    confirmed_dt: date
    pivot_type: str
    pivot_price: float
    pivot_seq_in_bar: int


@dataclass
class Wave:
    wave_id: str
    symbol: str
    wave_seq: int
    direction: str
    birth_type: str
    start_pivot_id: str
    candidate_guard_pivot_id: str
    confirm_pivot_id: str
    confirm_dt: date
    wave_core_state: str
    final_progress: Pivot
    final_guard: Pivot
    terminated_dt: date | None = None
    terminated_by_break_id: str | None = None


@dataclass
class Transition:
    transition_id: str
    old_wave_id: str
    break_id: str
    old_direction: str
    old_progress: Pivot
    old_guard: Pivot
    break_dt: date
    transition_boundary_high: float
    transition_boundary_low: float
    state: str = "open"
    confirmed_dt: date | None = None
    new_wave_id: str | None = None


@dataclass
class Candidate:
    candidate_id: str
    transition_id: str
    guard: Pivot
    direction: str
    reference_price: float
    is_active_at_close: bool = True
    invalidated_by_candidate_id: str | None = None
    confirmed_by_pivot_id: str | None = None
    confirmed_wave_id: str | None = None

    @property
    def status(self) -> str:
        if self.confirmed_wave_id is not None:
            return "confirmed"
        if self.invalidated_by_candidate_id is not None:
            return "invalidated"
        return "active"


@dataclass(frozen=True)
class CoreBuildRows:
    pivots: list[Pivot]
    structures: list[tuple[object, ...]]
    waves: list[Wave]
    breaks: list[tuple[object, ...]]
    transitions: list[Transition]
    candidates: list[Candidate]


def build_core_rows(request: MalfDayRequest, created_at: datetime) -> CoreBuildRows:
    bars_by_symbol = _load_bars(request.source_db, request)
    all_pivots: list[Pivot] = []
    structures: list[tuple[object, ...]] = []
    waves: list[Wave] = []
    breaks: list[tuple[object, ...]] = []
    transitions: list[Transition] = []
    candidates: list[Candidate] = []

    for symbol, bars in bars_by_symbol.items():
        pivots = _detect_pivots(symbol, bars, request)
        all_pivots.extend(pivots)
        result = _build_symbol_core(pivots, request, created_at)
        structures.extend(
            _derive_structures(pivots, result.structure_contexts, request, created_at)
        )
        waves.extend(result.waves)
        breaks.extend(result.breaks)
        transitions.extend(result.transitions)
        candidates.extend(result.candidates)

    return CoreBuildRows(all_pivots, structures, waves, breaks, transitions, candidates)


def _load_bars(source_db: Path, request: MalfDayRequest) -> dict[str, list[Bar]]:
    clauses = ["timeframe = ?"]
    params: list[object] = [request.timeframe]
    if request.start_date:
        clauses.append("bar_dt >= ?")
        params.append(request.start_date)
    if request.end_date:
        clauses.append("bar_dt <= ?")
        params.append(request.end_date)

    symbol_clause = ""
    if request.symbol_limit is not None:
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
    raw.sort(key=lambda item: (item.pivot_dt, 0 if item.pivot_type == "H" else 1))

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


def _derive_structures(
    pivots: list[Pivot],
    structure_contexts: dict[str, str],
    request: MalfDayRequest,
    created_at: datetime,
) -> list[tuple[object, ...]]:
    latest_by_type: dict[str, Pivot] = {}
    rows: list[tuple[object, ...]] = []
    for pivot in pivots:
        reference = latest_by_type.get(pivot.pivot_type)
        if reference is None:
            latest_by_type[pivot.pivot_type] = pivot
            continue
        if pivot.pivot_type == "H":
            primitive = "HH" if pivot.pivot_price > reference.pivot_price else "LH"
            direction_context = "up" if primitive == "HH" else "down"
        else:
            primitive = "HL" if pivot.pivot_price > reference.pivot_price else "LL"
            direction_context = "up" if primitive == "HL" else "down"
        rows.append(
            (
                f"{pivot.pivot_id}|{primitive}|{reference.pivot_id}",
                pivot.pivot_id,
                structure_contexts.get(pivot.pivot_id, "initial_candidate"),
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
        )
        latest_by_type[pivot.pivot_type] = pivot
    return rows


@dataclass(frozen=True)
class _SymbolResult:
    waves: list[Wave]
    breaks: list[tuple[object, ...]]
    transitions: list[Transition]
    candidates: list[Candidate]
    structure_contexts: dict[str, str]


def _build_symbol_core(
    pivots: list[Pivot], request: MalfDayRequest, created_at: datetime
) -> _SymbolResult:
    waves: list[Wave] = []
    breaks: list[tuple[object, ...]] = []
    transitions: list[Transition] = []
    candidates: list[Candidate] = []
    active_wave: Wave | None = None
    active_transition: Transition | None = None
    active_candidate: Candidate | None = None
    structure_contexts: dict[str, str] = {}
    wave_seq = 0

    for index, pivot in enumerate(pivots):
        if active_wave is None and active_transition is None:
            structure_contexts[pivot.pivot_id] = "initial_candidate"
            initial = _try_initial_wave(pivots, index, request, wave_seq + 1)
            if initial:
                active_wave = initial
                wave_seq += 1
                waves.append(initial)
            continue

        if active_wave is not None:
            structure_contexts[pivot.pivot_id] = "active_wave"
            opened = _advance_or_break(active_wave, pivot, request, created_at)
            if opened is None:
                continue
            break_row, transition = opened
            breaks.append(break_row)
            transitions.append(transition)
            active_transition = transition
            active_wave = None
            active_candidate = None
            continue

        if active_transition is None:
            continue
        structure_contexts[pivot.pivot_id] = "transition_candidate"
        confirmed = _confirm_candidate(active_transition, active_candidate, pivot)
        if confirmed:
            if active_candidate is None:
                raise RuntimeError("candidate confirmation requires an active candidate")
            wave_seq += 1
            birth_type = (
                "same_direction_after_break"
                if confirmed == active_transition.old_direction
                else "opposite_direction_after_break"
            )
            active_wave = _new_wave(
                pivot.symbol,
                wave_seq,
                confirmed,
                birth_type,
                active_candidate.guard,
                pivot,
                request,
            )
            waves.append(active_wave)
            active_transition.state = "confirmed"
            active_transition.confirmed_dt = pivot.pivot_dt
            active_transition.new_wave_id = active_wave.wave_id
            active_candidate.confirmed_by_pivot_id = pivot.pivot_id
            active_candidate.confirmed_wave_id = active_wave.wave_id
            active_candidate.is_active_at_close = True
            active_transition = None
            active_candidate = None
            continue

        new_candidate = _candidate_from_pivot(active_transition, pivot, request)
        if new_candidate is None:
            continue
        if active_candidate is not None and active_candidate.confirmed_wave_id is None:
            active_candidate.is_active_at_close = False
            active_candidate.invalidated_by_candidate_id = new_candidate.candidate_id
        candidates.append(new_candidate)
        active_candidate = new_candidate
    return _SymbolResult(waves, breaks, transitions, candidates, structure_contexts)


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


def _advance_or_break(
    wave: Wave, pivot: Pivot, request: MalfDayRequest, created_at: datetime
) -> tuple[tuple[object, ...], Transition] | None:
    if wave.direction == "up":
        if pivot.pivot_type == "H" and pivot.pivot_price > wave.final_progress.pivot_price:
            wave.final_progress = pivot
        elif pivot.pivot_type == "L":
            if pivot.pivot_price < wave.final_guard.pivot_price:
                return _break_transition(wave, pivot, request, created_at)
            if pivot.pivot_price > wave.final_guard.pivot_price:
                wave.final_guard = pivot
    else:
        if pivot.pivot_type == "L" and pivot.pivot_price < wave.final_progress.pivot_price:
            wave.final_progress = pivot
        elif pivot.pivot_type == "H":
            if pivot.pivot_price > wave.final_guard.pivot_price:
                return _break_transition(wave, pivot, request, created_at)
            if pivot.pivot_price < wave.final_guard.pivot_price:
                wave.final_guard = pivot
    return None


def _break_transition(
    wave: Wave, pivot: Pivot, request: MalfDayRequest, created_at: datetime
) -> tuple[tuple[object, ...], Transition]:
    break_id = f"{wave.wave_id}|break|{pivot.pivot_dt.isoformat()}"
    transition_id = f"{break_id}|transition"
    wave.wave_core_state = "terminated"
    wave.terminated_dt = pivot.pivot_dt
    wave.terminated_by_break_id = break_id
    break_row = (
        break_id,
        wave.wave_id,
        wave.direction,
        wave.final_guard.pivot_id,
        pivot.pivot_dt,
        pivot.pivot_price,
        "transition",
        request.run_id,
        request.schema_version,
        request.core_rule_version,
        created_at,
        wave.final_guard.pivot_id,
    )
    boundary_prices = (wave.final_progress.pivot_price, wave.final_guard.pivot_price)
    boundary_high = max(boundary_prices)
    boundary_low = min(boundary_prices)
    transition = Transition(
        transition_id,
        wave.wave_id,
        break_id,
        wave.direction,
        wave.final_progress,
        wave.final_guard,
        pivot.pivot_dt,
        boundary_high,
        boundary_low,
    )
    return break_row, transition


def _confirm_candidate(
    transition: Transition, candidate: Candidate | None, pivot: Pivot
) -> str | None:
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


def _candidate_from_pivot(
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
        f"{transition.transition_id}|candidate|{pivot.pivot_id}|"
        f"{direction}|{request.core_rule_version}"
    )
    return Candidate(
        candidate_id,
        transition.transition_id,
        pivot,
        direction,
        reference,
    )
