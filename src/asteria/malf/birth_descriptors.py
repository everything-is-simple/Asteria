from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import cast

import duckdb

from asteria.malf.contracts import MalfDayRequest


@dataclass(frozen=True)
class BirthDescriptor:
    boundary_high: float | None
    boundary_low: float | None
    active_candidate_guard_pivot_id: str | None
    confirmation_pivot_id: str | None
    new_wave_id: str | None
    birth_type: str
    candidate_wait_span: int
    candidate_replacement_count: int
    confirmation_distance_abs: float
    confirmation_distance_pct: float

    def as_row(self) -> tuple[object, ...]:
        return (
            self.boundary_high,
            self.boundary_low,
            self.active_candidate_guard_pivot_id,
            self.confirmation_pivot_id,
            self.new_wave_id,
            self.birth_type,
            self.candidate_wait_span,
            self.candidate_replacement_count,
            self.confirmation_distance_abs,
            self.confirmation_distance_pct,
        )


def load_birth_descriptors(core_db: Path, request: MalfDayRequest) -> dict[str, BirthDescriptor]:
    descriptors = _initial_birth_descriptors(core_db)
    query = """
        select w.wave_id, w.birth_type, w.symbol, w.timeframe,
               c.candidate_guard_pivot_id, c.candidate_dt, c.candidate_direction,
               c.confirmed_by_pivot_id, c.confirmed_wave_id, t.transition_id,
               t.transition_boundary_high, t.transition_boundary_low,
               p.pivot_dt, p.pivot_price
        from malf_wave_ledger w
        join malf_candidate_ledger c on c.confirmed_wave_id = w.wave_id
         and c.run_id = w.run_id
        join malf_transition_ledger t on t.transition_id = c.transition_id
         and t.run_id = c.run_id
        join malf_pivot_ledger p on p.pivot_id = c.confirmed_by_pivot_id
         and p.run_id = c.run_id
        where w.run_id = ? and w.birth_type <> 'initial'
    """
    with duckdb.connect(str(core_db), read_only=True) as con:
        for row in con.execute(query, [request.run_id]).fetchall():
            (
                wave_id,
                birth_type,
                symbol,
                timeframe,
                guard_pivot_id,
                candidate_dt,
                direction,
                confirmation_pivot_id,
                new_wave_id,
                transition_id,
                boundary_high,
                boundary_low,
                confirm_dt,
                confirm_price,
            ) = row
            replacements_row = con.execute(
                """
                select count(*) from malf_candidate_ledger
                where run_id = ? and transition_id = ?
                  and invalidated_by_candidate_id is not null
                """,
                [request.run_id, transition_id],
            ).fetchone()
            replacements = 0 if replacements_row is None else int(replacements_row[0])
            wait_span = _candidate_wait_span(
                request,
                str(symbol),
                str(timeframe),
                cast(date, candidate_dt),
                cast(date, confirm_dt),
            )
            distance = (
                float(confirm_price) - float(boundary_high)
                if str(direction) == "up"
                else float(boundary_low) - float(confirm_price)
            )
            boundary = float(boundary_high) if str(direction) == "up" else float(boundary_low)
            descriptors[str(wave_id)] = BirthDescriptor(
                float(boundary_high),
                float(boundary_low),
                str(guard_pivot_id),
                str(confirmation_pivot_id),
                str(new_wave_id),
                str(birth_type),
                wait_span,
                replacements,
                round(abs(distance), 6),
                0.0 if boundary == 0 else round(abs(distance) / abs(boundary), 6),
            )
    return descriptors


def _initial_birth_descriptors(core_db: Path) -> dict[str, BirthDescriptor]:
    output: dict[str, BirthDescriptor] = {}
    with duckdb.connect(str(core_db), read_only=True) as con:
        for wave_id, birth_type in con.execute(
            "select wave_id, birth_type from malf_wave_ledger"
        ).fetchall():
            output[str(wave_id)] = BirthDescriptor(
                None, None, None, None, str(wave_id), str(birth_type), 0, 0, 0.0, 0.0
            )
    return output


def _candidate_wait_span(
    request: MalfDayRequest,
    symbol: str,
    timeframe: str,
    candidate_dt: date,
    confirm_dt: date,
) -> int:
    if not request.source_db.exists():
        return max((confirm_dt - candidate_dt).days, 1)
    with duckdb.connect(str(request.source_db), read_only=True) as con:
        row = con.execute(
            """
            select count(*) from market_base_bar
            where symbol = ? and timeframe = ? and bar_dt > ? and bar_dt <= ?
            """,
            [symbol, timeframe, candidate_dt, confirm_dt],
        ).fetchone()
    return max(1, 0 if row is None else int(row[0]))
