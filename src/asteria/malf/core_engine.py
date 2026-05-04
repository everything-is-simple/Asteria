from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import duckdb

from asteria.malf.bootstrap_support import market_base_source_filters
from asteria.malf.contracts import MalfDayRequest
from asteria.malf.core_models import Bar, Candidate, CoreBuildRows, Pivot, Transition
from asteria.malf.core_symbol_logic import build_symbol_rows
from asteria.malf.core_transition_logic import (
    candidate_from_pivot as _candidate_from_pivot,
)
from asteria.malf.core_transition_logic import (
    replace_active_candidate as _replace_active_candidate,
)

__all__ = [
    "Candidate",
    "Pivot",
    "Transition",
    "build_core_rows",
    "_candidate_from_pivot",
    "_replace_active_candidate",
]


def build_core_rows(request: MalfDayRequest, created_at: datetime) -> CoreBuildRows:
    bars_by_symbol = _load_bars(request.source_db, request)
    pivots: list[Pivot] = []
    structures: list[tuple[object, ...]] = []
    waves = []
    breaks = []
    transitions = []
    candidates = []
    snapshots = []

    for symbol, bars in bars_by_symbol.items():
        symbol_pivots = _detect_pivots(symbol, bars, request)
        pivots.extend(symbol_pivots)
        result = build_symbol_rows(symbol, bars, symbol_pivots, request, created_at)
        structures.extend(result.structures)
        waves.extend(result.waves)
        breaks.extend(result.breaks)
        transitions.extend(result.transitions)
        candidates.extend(result.candidates)
        snapshots.extend(result.snapshots)

    return CoreBuildRows(pivots, structures, waves, breaks, transitions, candidates, snapshots)


def _load_bars(source_db: Path, request: MalfDayRequest) -> dict[str, list[Bar]]:
    clauses, params = market_base_source_filters(request)

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
    return _collapse_same_type_pivots(raw)


def _collapse_same_type_pivots(pivots: list[Pivot]) -> list[Pivot]:
    collapsed: list[Pivot] = []
    for pivot in pivots:
        if not collapsed or collapsed[-1].pivot_type != pivot.pivot_type:
            collapsed.append(pivot)
            continue
        previous = collapsed[-1]
        is_stronger = (pivot.pivot_type == "H" and pivot.pivot_price >= previous.pivot_price) or (
            pivot.pivot_type == "L" and pivot.pivot_price <= previous.pivot_price
        )
        if is_stronger:
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
        f"{symbol}|{request.timeframe}|{bar.bar_dt.isoformat()}|{pivot_type}|{seq}|"
        f"{request.core_rule_version}"
    )
    return Pivot(pivot_id, symbol, bar.bar_dt, confirmed_dt, pivot_type, price, seq)
