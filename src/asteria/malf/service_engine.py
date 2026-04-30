from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import cast

import duckdb

from asteria.malf.contracts import MalfDayRequest

SAMPLE_SCOPE = "market_all_eligible_by_timeframe_direction"


def build_wave_position_rows(
    lifespan_db: Path,
    source_core_run_id: str | None,
    source_lifespan_run_id: str | None,
    request: MalfDayRequest,
    created_at: datetime,
) -> tuple[list[tuple[object, ...]], list[tuple[object, ...]]]:
    rows: list[tuple[object, ...]] = []
    with duckdb.connect(str(lifespan_db), read_only=True) as con:
        snapshots = con.execute(
            """
            select wave_id, old_wave_id, symbol, timeframe, bar_dt, wave_core_state,
                   system_state, direction, new_count, no_new_span, transition_span,
                   update_rank, stagnation_rank, life_state, position_quadrant,
                   guard_boundary_price, sample_version, lifespan_rule_version
            from malf_lifespan_snapshot
            where run_id = ?
            order by symbol, bar_dt, snapshot_id
            """,
            [request.run_id],
        ).fetchall()

    for snapshot in snapshots:
        (
            wave_id,
            old_wave_id,
            symbol,
            timeframe,
            bar_dt,
            wave_core_state,
            system_state,
            direction,
            new_count,
            no_new_span,
            transition_span,
            update_rank,
            stagnation_rank,
            life_state,
            position_quadrant,
            guard_boundary_price,
            sample_version,
            lifespan_rule_version,
        ) = snapshot
        publish_wave_id = None if system_state == "transition" else wave_id
        publish_old_wave_id = old_wave_id if system_state == "transition" else None
        rows.append(
            (
                symbol,
                timeframe,
                bar_dt,
                system_state,
                publish_wave_id,
                publish_old_wave_id,
                wave_core_state,
                direction,
                new_count,
                no_new_span,
                transition_span,
                update_rank,
                stagnation_rank,
                life_state,
                position_quadrant,
                guard_boundary_price,
                SAMPLE_SCOPE,
                sample_version,
                lifespan_rule_version,
                request.service_version,
                request.run_id,
                request.schema_version,
                source_core_run_id,
                source_lifespan_run_id,
                created_at,
            )
        )

    latest: dict[tuple[object, object, object], tuple[object, ...]] = {}
    for row in rows:
        key = (row[0], row[1], row[19])
        previous = latest.get(key)
        if previous is None or cast(date, row[2]) >= cast(date, previous[2]):
            latest[key] = row
    return rows, list(latest.values())
