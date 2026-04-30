from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import cast

import duckdb

from asteria.malf.contracts import MalfDayRequest


@dataclass(frozen=True)
class WaveRow:
    wave_id: str
    symbol: str
    timeframe: str
    direction: str
    confirm_dt: date
    state: str
    terminated_dt: date | None
    confirm_pivot_id: str
    final_guard_price: float | None


@dataclass(frozen=True)
class TransitionRow:
    transition_id: str
    old_wave_id: str
    symbol: str
    old_direction: str
    old_progress_extreme_price: float
    break_dt: date
    confirmed_dt: date | None
    candidate_dates: list[date]


@dataclass(frozen=True)
class Snapshot:
    row: tuple[object, ...]
    new_count: int
    no_new_span: int


def build_lifespan_rows(
    core_db: Path, request: MalfDayRequest, created_at: datetime
) -> tuple[list[tuple[object, ...]], list[tuple[object, ...]]]:
    waves = _load_waves(core_db)
    symbols = {wave.symbol for wave in waves}
    bar_dates = _load_bar_dates(request, symbols)
    progress_pivots = _load_progress_pivots(core_db)
    pivot_dates = _load_pivot_dates(core_db)
    pivot_ids_by_date = _load_pivot_ids_by_date(core_db)
    transitions = _load_transitions(core_db)
    snapshots: list[Snapshot] = []
    final_stats: dict[str, Snapshot] = {}

    for wave in waves:
        symbol_dates = bar_dates.get(wave.symbol, pivot_dates.get(wave.symbol, []))
        dates = [
            dt
            for dt in symbol_dates
            if dt >= wave.confirm_dt and (wave.terminated_dt is None or dt < wave.terminated_dt)
        ]
        can_publish_confirm_bar = wave.terminated_dt is None or wave.confirm_dt < wave.terminated_dt
        if wave.confirm_dt not in dates and can_publish_confirm_bar:
            dates.insert(0, wave.confirm_dt)
        new_count = 0
        no_new_span = 0
        wave_progress = {wave.confirm_pivot_id, *progress_pivots.get(wave.wave_id, set())}
        for bar_dt in sorted(set(dates)):
            pivot_ids = pivot_ids_by_date.get((wave.symbol, bar_dt), set())
            progress_updated = bool(wave_progress.intersection(pivot_ids))
            if progress_updated:
                new_count += 1
                no_new_span = 0
            else:
                no_new_span += 1
            snapshot = _snapshot(
                request,
                created_at,
                wave.wave_id,
                None,
                wave.symbol,
                wave.timeframe,
                bar_dt,
                "alive",
                f"{wave.direction}_alive",
                wave.direction,
                progress_updated,
                new_count,
                no_new_span,
                0,
                wave.final_guard_price,
            )
            snapshots.append(snapshot)
            final_stats[wave.wave_id] = snapshot
        if wave.wave_id not in final_stats:
            final_stats[wave.wave_id] = _snapshot(
                request,
                created_at,
                wave.wave_id,
                None,
                wave.symbol,
                wave.timeframe,
                wave.confirm_dt,
                "alive",
                f"{wave.direction}_alive",
                wave.direction,
                True,
                1,
                0,
                0,
                wave.final_guard_price,
            )

    for transition in transitions:
        frozen = final_stats.get(transition.old_wave_id)
        if frozen is None:
            continue
        symbol_dates = bar_dates.get(transition.symbol, pivot_dates.get(transition.symbol, []))
        dates = [
            dt
            for dt in symbol_dates
            if dt >= transition.break_dt
            and (transition.confirmed_dt is None or dt < transition.confirmed_dt)
        ]
        if not dates:
            dates = [transition.break_dt, *transition.candidate_dates]
            if transition.confirmed_dt is not None:
                dates = [dt for dt in dates if dt < transition.confirmed_dt]
        for index, bar_dt in enumerate(sorted(set(dates)), start=1):
            snapshots.append(
                _snapshot(
                    request,
                    created_at,
                    transition.old_wave_id,
                    transition.old_wave_id,
                    transition.symbol,
                    request.timeframe,
                    bar_dt,
                    "terminated",
                    "transition",
                    transition.old_direction,
                    False,
                    frozen.new_count,
                    frozen.no_new_span,
                    index,
                    transition.old_progress_extreme_price,
                )
            )

    ranked_rows = _rank_snapshots(snapshots)
    profiles = _profiles(request, created_at, ranked_rows)
    return [item.row for item in ranked_rows], profiles


def _load_bar_dates(request: MalfDayRequest, symbols: set[str]) -> dict[str, list[date]]:
    if not symbols or not request.source_db.exists():
        return {}
    clauses = ["timeframe = ?"]
    params: list[object] = [request.timeframe]
    if request.start_date:
        clauses.append("bar_dt >= ?")
        params.append(request.start_date)
    if request.end_date:
        clauses.append("bar_dt <= ?")
        params.append(request.end_date)
    symbol_list = sorted(symbols)
    clauses.append(f"symbol in ({', '.join(['?'] * len(symbol_list))})")
    params.extend(symbol_list)

    output: dict[str, list[date]] = {}
    with duckdb.connect(str(request.source_db), read_only=True) as con:
        for symbol, bar_dt in con.execute(
            f"""
            select symbol, bar_dt
            from market_base_bar
            where {" and ".join(clauses)}
            order by symbol, bar_dt
            """,
            params,
        ).fetchall():
            output.setdefault(str(symbol), []).append(cast(date, bar_dt))
    return output


def _load_waves(core_db: Path) -> list[WaveRow]:
    with duckdb.connect(str(core_db), read_only=True) as con:
        return [
            WaveRow(
                str(row[0]),
                str(row[1]),
                str(row[2]),
                str(row[3]),
                cast(date, row[4]),
                str(row[5]),
                cast(date | None, row[6]),
                str(row[7]),
                cast(float | None, row[8]),
            )
            for row in con.execute(
                """
                select wave_id, symbol, timeframe, direction, confirm_dt, wave_core_state,
                       terminated_dt, confirm_pivot_id, final_guard_price
                from malf_wave_ledger
                order by symbol, wave_seq
                """
            ).fetchall()
        ]


def _load_progress_pivots(core_db: Path) -> dict[str, set[str]]:
    query = """
        select w.wave_id, s.pivot_id
        from malf_wave_ledger w
        join malf_structure_ledger s
          on s.symbol = w.symbol and s.timeframe = w.timeframe
        where ((w.direction = 'up' and s.primitive = 'HH')
            or (w.direction = 'down' and s.primitive = 'LL'))
          and s.pivot_dt >= w.confirm_dt
          and (w.terminated_dt is null or s.pivot_dt < w.terminated_dt)
    """
    output: dict[str, set[str]] = {}
    with duckdb.connect(str(core_db), read_only=True) as con:
        for wave_id, pivot_id in con.execute(query).fetchall():
            output.setdefault(str(wave_id), set()).add(str(pivot_id))
    return output


def _load_pivot_dates(core_db: Path) -> dict[str, list[date]]:
    output: dict[str, list[date]] = {}
    with duckdb.connect(str(core_db), read_only=True) as con:
        for symbol, pivot_dt in con.execute(
            "select symbol, pivot_dt from malf_pivot_ledger order by symbol, pivot_dt"
        ).fetchall():
            output.setdefault(str(symbol), []).append(cast(date, pivot_dt))
    return output


def _load_pivot_ids_by_date(core_db: Path) -> dict[tuple[str, date], set[str]]:
    output: dict[tuple[str, date], set[str]] = {}
    with duckdb.connect(str(core_db), read_only=True) as con:
        for symbol, pivot_dt, pivot_id in con.execute(
            """
            select symbol, pivot_dt, pivot_id
            from malf_pivot_ledger
            order by symbol, pivot_dt, pivot_id
            """
        ).fetchall():
            output.setdefault((str(symbol), cast(date, pivot_dt)), set()).add(str(pivot_id))
    return output


def _pivot_ids_at(core_db: Path, symbol: str, pivot_dt: date) -> set[str]:
    with duckdb.connect(str(core_db), read_only=True) as con:
        return {
            str(row[0])
            for row in con.execute(
                """
                select pivot_id from malf_pivot_ledger
                where symbol = ? and pivot_dt = ?
                """,
                [symbol, pivot_dt],
            ).fetchall()
        }


def _load_transitions(core_db: Path) -> list[TransitionRow]:
    query = """
        select t.transition_id, t.old_wave_id, w.symbol, t.old_direction,
               t.old_progress_extreme_price, t.break_dt, t.confirmed_dt
        from malf_transition_ledger t
        join malf_wave_ledger w on w.wave_id = t.old_wave_id
        order by w.symbol, t.break_dt
    """
    output: list[TransitionRow] = []
    with duckdb.connect(str(core_db), read_only=True) as con:
        for row in con.execute(query).fetchall():
            transition_id = str(row[0])
            candidate_dates = [
                cast(date, item[0])
                for item in con.execute(
                    """
                    select candidate_dt
                    from malf_candidate_ledger
                    where transition_id = ?
                    order by candidate_dt
                    """,
                    [transition_id],
                ).fetchall()
            ]
            output.append(
                TransitionRow(
                    transition_id,
                    str(row[1]),
                    str(row[2]),
                    str(row[3]),
                    float(row[4]),
                    cast(date, row[5]),
                    cast(date | None, row[6]),
                    candidate_dates,
                )
            )
    return output


def _snapshot(
    request: MalfDayRequest,
    created_at: datetime,
    wave_id: str,
    old_wave_id: str | None,
    symbol: str,
    timeframe: str,
    bar_dt: date,
    wave_core_state: str,
    system_state: str,
    direction: str,
    progress_updated: bool,
    new_count: int,
    no_new_span: int,
    transition_span: int,
    guard_boundary_price: float | None,
) -> Snapshot:
    life_state = _life_state(wave_core_state, 0.0, 0.0)
    position_quadrant = "developing"
    snapshot_id = f"{wave_id}|{old_wave_id or 'alive'}|{bar_dt}|{request.lifespan_rule_version}"
    return Snapshot(
        (
            snapshot_id,
            wave_id,
            old_wave_id,
            symbol,
            timeframe,
            bar_dt,
            wave_core_state,
            system_state,
            direction,
            progress_updated,
            new_count,
            no_new_span,
            transition_span,
            life_state,
            position_quadrant,
            0.0,
            0.0,
            guard_boundary_price,
            request.run_id,
            request.schema_version,
            request.lifespan_rule_version,
            request.sample_version,
            created_at,
        ),
        new_count,
        no_new_span,
    )


def _rank_snapshots(snapshots: list[Snapshot]) -> list[Snapshot]:
    ranked: list[Snapshot] = []
    by_direction: dict[str, list[Snapshot]] = {}
    for snapshot in sorted(snapshots, key=lambda item: (str(item.row[8]), str(item.row[5]))):
        direction = str(snapshot.row[8])
        sample = by_direction.setdefault(direction, [])
        sample.append(snapshot)
        update_rank = _percentile([item.new_count for item in sample], snapshot.new_count)
        stagnation_rank = _percentile([item.no_new_span for item in sample], snapshot.no_new_span)
        life_state = _life_state(str(snapshot.row[6]), update_rank, stagnation_rank)
        quadrant = _quadrant(update_rank, stagnation_rank)
        row = list(snapshot.row)
        row[13] = life_state
        row[14] = quadrant
        row[15] = update_rank
        row[16] = stagnation_rank
        ranked.append(Snapshot(tuple(row), snapshot.new_count, snapshot.no_new_span))
    return sorted(
        ranked,
        key=lambda item: (str(item.row[3]), str(item.row[5]), str(item.row[0])),
    )


def _percentile(values: list[int], value: int) -> float:
    if not values:
        return 0.0
    return round(sum(1 for item in values if item <= value) / len(values), 6)


def _life_state(wave_core_state: str, update_rank: float, stagnation_rank: float) -> str:
    if wave_core_state == "terminated":
        return "terminal"
    if stagnation_rank >= 0.75:
        return "stagnant"
    if update_rank >= 0.75:
        return "extended"
    if update_rank < 0.25:
        return "early"
    return "developing"


def _quadrant(update_rank: float, stagnation_rank: float) -> str:
    if update_rank < 0.25 and stagnation_rank < 0.75:
        return "early_active"
    if update_rank >= 0.75 and stagnation_rank < 0.75:
        return "extended_active"
    if update_rank < 0.25 and stagnation_rank >= 0.75:
        return "early_stagnant"
    if update_rank >= 0.75 and stagnation_rank >= 0.75:
        return "extended_stagnant"
    return "developing"


def _profiles(
    request: MalfDayRequest, created_at: datetime, snapshots: list[Snapshot]
) -> list[tuple[object, ...]]:
    rows: list[tuple[object, ...]] = []
    for direction in sorted({str(item.row[8]) for item in snapshots}):
        for metric_name in ("new_count", "no_new_span"):
            values = sorted(
                float(item.new_count if metric_name == "new_count" else item.no_new_span)
                for item in snapshots
                if item.row[8] == direction
            )
            if not values:
                continue
            cutoff = max(cast(date, item.row[5]) for item in snapshots if item.row[8] == direction)
            rows.append(
                (
                    f"{request.timeframe}|{direction}|{request.sample_version}|{metric_name}",
                    request.timeframe,
                    direction,
                    request.sample_version,
                    metric_name,
                    cutoff,
                    len(values),
                    _quantile(values, 0.25),
                    _quantile(values, 0.50),
                    _quantile(values, 0.75),
                    _quantile(values, 0.90),
                    request.run_id,
                    request.schema_version,
                    request.lifespan_rule_version,
                    created_at,
                )
            )
    return rows


def _quantile(values: list[float], q: float) -> float:
    index = min(len(values) - 1, int(round((len(values) - 1) * q)))
    return values[index]
