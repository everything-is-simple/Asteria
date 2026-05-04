from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import cast

import duckdb

from asteria.malf.birth_descriptors import BirthDescriptor, load_birth_descriptors
from asteria.malf.contracts import MalfDayRequest


@dataclass(frozen=True)
class CoreSnapshotRow:
    symbol: str
    timeframe: str
    bar_dt: date
    system_state: str
    wave_id: str | None
    old_wave_id: str | None
    wave_core_state: str
    direction: str
    progress_updated: bool
    transition_span: int
    guard_boundary_price: float | None
    transition_boundary_high: float | None
    transition_boundary_low: float | None
    active_candidate_guard_pivot_id: str | None
    confirmation_pivot_id: str | None
    new_wave_id: str | None


@dataclass(frozen=True)
class Snapshot:
    row: tuple[object, ...]
    new_count: int
    no_new_span: int


def build_lifespan_rows(
    core_db: Path, request: MalfDayRequest, created_at: datetime, core_run_id: str | None = None
) -> tuple[list[tuple[object, ...]], list[tuple[object, ...]]]:
    source_core_run_id = core_run_id or request.run_id
    core_snapshots = _load_core_snapshots(core_db, source_core_run_id)
    descriptors = load_birth_descriptors(core_db, request, source_core_run_id)
    ranked_rows = _rank_snapshots(
        _build_snapshots_from_core(core_snapshots, descriptors, request, created_at)
    )
    profiles = _profiles(request, created_at, ranked_rows)
    return [item.row for item in ranked_rows], profiles


def _load_core_snapshots(core_db: Path, run_id: str) -> list[CoreSnapshotRow]:
    query = """
        select symbol, timeframe, bar_dt, system_state, wave_id, old_wave_id,
               wave_core_state, direction, progress_updated, transition_span,
               guard_boundary_price, transition_boundary_high, transition_boundary_low,
               active_candidate_guard_pivot_id, confirmation_pivot_id, new_wave_id
        from malf_core_state_snapshot
        where run_id = ?
        order by symbol, bar_dt, snapshot_id
    """
    with duckdb.connect(str(core_db), read_only=True) as con:
        return [
            CoreSnapshotRow(
                symbol=str(row[0]),
                timeframe=str(row[1]),
                bar_dt=row[2],
                system_state=str(row[3]),
                wave_id=None if row[4] is None else str(row[4]),
                old_wave_id=None if row[5] is None else str(row[5]),
                wave_core_state=str(row[6]),
                direction=str(row[7]),
                progress_updated=bool(row[8]),
                transition_span=int(row[9]),
                guard_boundary_price=None if row[10] is None else float(row[10]),
                transition_boundary_high=None if row[11] is None else float(row[11]),
                transition_boundary_low=None if row[12] is None else float(row[12]),
                active_candidate_guard_pivot_id=None if row[13] is None else str(row[13]),
                confirmation_pivot_id=None if row[14] is None else str(row[14]),
                new_wave_id=None if row[15] is None else str(row[15]),
            )
            for row in con.execute(query, [run_id]).fetchall()
        ]


def _build_snapshots_from_core(
    core_snapshots: list[CoreSnapshotRow],
    descriptors: dict[str, BirthDescriptor],
    request: MalfDayRequest,
    created_at: datetime,
) -> list[Snapshot]:
    rows: list[Snapshot] = []
    stats: dict[str, tuple[int, int]] = {}

    for item in core_snapshots:
        if item.system_state == "transition":
            if item.old_wave_id is None:
                continue
            new_count, no_new_span = stats.get(item.old_wave_id, (0, 0))
            trace = _trace_fields_for_transition(item, descriptors.get(item.old_wave_id))
            rows.append(
                _snapshot(
                    request=request,
                    created_at=created_at,
                    wave_id=item.old_wave_id,
                    old_wave_id=item.old_wave_id,
                    item=item,
                    progress_updated=False,
                    new_count=new_count,
                    no_new_span=no_new_span,
                    trace=trace,
                )
            )
            continue

        if item.wave_id is None:
            continue
        new_count, no_new_span = stats.get(item.wave_id, (0, 0))
        if item.progress_updated:
            new_count += 1
            no_new_span = 0
        else:
            no_new_span += 1
        stats[item.wave_id] = (new_count, no_new_span)
        rows.append(
            _snapshot(
                request=request,
                created_at=created_at,
                wave_id=item.wave_id,
                old_wave_id=None,
                item=item,
                progress_updated=item.progress_updated,
                new_count=new_count,
                no_new_span=no_new_span,
                trace=descriptors[item.wave_id],
            )
        )
    return rows


def _trace_fields_for_transition(
    item: CoreSnapshotRow, descriptor: BirthDescriptor | None
) -> BirthDescriptor:
    if item.transition_boundary_high is None and descriptor is not None:
        return descriptor
    return BirthDescriptor(
        boundary_high=item.transition_boundary_high,
        boundary_low=item.transition_boundary_low,
        active_candidate_guard_pivot_id=item.active_candidate_guard_pivot_id,
        confirmation_pivot_id=item.confirmation_pivot_id,
        new_wave_id=item.new_wave_id,
        birth_type="initial" if descriptor is None else descriptor.birth_type,
        candidate_wait_span=0 if descriptor is None else descriptor.candidate_wait_span,
        candidate_replacement_count=0
        if descriptor is None
        else descriptor.candidate_replacement_count,
        confirmation_distance_abs=0.0
        if descriptor is None
        else descriptor.confirmation_distance_abs,
        confirmation_distance_pct=0.0
        if descriptor is None
        else descriptor.confirmation_distance_pct,
    )


def _snapshot(
    request: MalfDayRequest,
    created_at: datetime,
    wave_id: str,
    old_wave_id: str | None,
    item: CoreSnapshotRow,
    progress_updated: bool,
    new_count: int,
    no_new_span: int,
    trace: BirthDescriptor,
) -> Snapshot:
    life_state = _life_state(item.wave_core_state, 0.0, 0.0)
    snapshot_id = (
        f"{wave_id}|{old_wave_id or 'alive'}|{item.bar_dt}|{request.lifespan_rule_version}"
    )
    return Snapshot(
        (
            snapshot_id,
            wave_id,
            old_wave_id,
            item.symbol,
            item.timeframe,
            item.bar_dt,
            item.wave_core_state,
            item.system_state,
            item.direction,
            progress_updated,
            new_count,
            no_new_span,
            item.transition_span,
            life_state,
            "developing",
            0.0,
            0.0,
            item.guard_boundary_price,
            request.run_id,
            request.schema_version,
            request.lifespan_rule_version,
            request.sample_version,
            created_at,
            *trace.as_row(),
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
        row = list(snapshot.row)
        row[13] = _life_state(str(snapshot.row[6]), update_rank, stagnation_rank)
        row[14] = _quadrant(update_rank, stagnation_rank)
        row[15] = update_rank
        row[16] = stagnation_rank
        ranked.append(Snapshot(tuple(row), snapshot.new_count, snapshot.no_new_span))
    return sorted(ranked, key=lambda item: (str(item.row[3]), str(item.row[5]), str(item.row[0])))


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
