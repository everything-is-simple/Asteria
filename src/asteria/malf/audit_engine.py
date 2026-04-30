from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb

from asteria.malf.audit_support import (
    _as_int,
    _count,
    _count_for_run,
    _lifespan_dense_missing_count,
    _missing_run_count,
    _resolve_audit_source_runs,
    _service_dense_missing_count,
    _transition_semantics_failure_count,
)
from asteria.malf.contracts import MalfDayRequest


def build_audit_rows(
    core_db: Path,
    lifespan_db: Path,
    service_db: Path,
    request: MalfDayRequest,
    created_at: datetime,
) -> tuple[list[tuple[object, ...]], dict[str, Any]]:
    source_core_run_id, source_lifespan_run_id = _resolve_audit_source_runs(
        core_db, lifespan_db, service_db, request
    )
    checks = [
        _check(
            service_db,
            request,
            created_at,
            "service_wave_core_state_not_transition",
            """
            select count(*) from malf_wave_position
            where run_id = ? and wave_core_state = 'transition'
            """,
            [request.run_id],
        ),
        _check(
            service_db,
            request,
            created_at,
            "service_transition_old_wave_required",
            """
            select count(*) from malf_wave_position
            where run_id = ?
              and system_state = 'transition'
              and (old_wave_id is null or wave_id is not null)
            """,
            [request.run_id],
        ),
        _check(
            service_db,
            request,
            created_at,
            "service_transition_direction_required",
            """
            select count(*) from malf_wave_position
            where run_id = ? and system_state = 'transition' and direction is null
            """,
            [request.run_id],
        ),
        _manual_check(
            request,
            created_at,
            "audit_source_core_run_bound",
            _missing_run_count(core_db, "malf_wave_ledger", source_core_run_id),
        ),
        _manual_check(
            request,
            created_at,
            "audit_source_lifespan_run_bound",
            _missing_run_count(lifespan_db, "malf_lifespan_snapshot", source_lifespan_run_id),
        ),
        _check(
            service_db,
            request,
            created_at,
            "service_wave_position_natural_key_unique",
            """
            select count(*) from (
                select symbol, timeframe, bar_dt, service_version, count(*) row_count
                from malf_wave_position
                where run_id = ?
                group by symbol, timeframe, bar_dt, service_version
                having row_count > 1
            )
            """,
            [request.run_id],
        ),
        _check(
            service_db,
            request,
            created_at,
            "service_latest_unique",
            """
            select count(*) from (
                select symbol, timeframe, service_version, count(*) row_count
                from malf_wave_position_latest
                where run_id = ?
                group by symbol, timeframe, service_version
                having row_count > 1
            )
            """,
            [request.run_id],
        ),
        _check(
            lifespan_db,
            request,
            created_at,
            "lifespan_confirmation_no_new_span_zero",
            """
            select count(*) from malf_lifespan_snapshot
            where run_id = ? and progress_updated and no_new_span <> 0
            """,
            [source_lifespan_run_id],
        ),
        _check(
            core_db,
            request,
            created_at,
            "core_terminated_wave_not_alive",
            """
            select count(*) from malf_wave_ledger
            where run_id = ?
              and (terminated_dt is not null or terminated_by_break_id is not null)
              and (
                  wave_core_state <> 'terminated'
                  or terminated_dt is null
                  or terminated_by_break_id is null
              )
            """,
            [source_core_run_id],
        ),
        _check(
            core_db,
            request,
            created_at,
            "core_break_does_not_extend_old_wave",
            """
            select count(*)
            from malf_wave_ledger w
            left join malf_pivot_ledger progress
              on progress.pivot_id = w.final_progress_extreme_pivot_id
            left join malf_pivot_ledger guard
              on guard.pivot_id = w.final_guard_pivot_id
            where w.run_id = ?
              and w.terminated_dt is not null
              and (
                  w.final_progress_extreme_pivot_id is null
                  or progress.pivot_dt is null
                  or progress.pivot_dt > w.terminated_dt
                  or w.final_guard_pivot_id is null
                  or guard.pivot_dt is null
                  or guard.pivot_dt > w.terminated_dt
              )
            """,
            [source_core_run_id],
        ),
        _check(
            core_db,
            request,
            created_at,
            "core_single_active_candidate_per_transition",
            """
            select count(*) from (
                select transition_id, count(*) row_count
                from malf_candidate_ledger
                where run_id = ? and is_active_at_close
                group by transition_id
                having row_count > 1
            )
            """,
            [source_core_run_id],
        ),
        _check(
            core_db,
            request,
            created_at,
            "core_new_candidate_replaces_previous",
            """
            with ordered_candidates as (
                select
                    candidate_id,
                    transition_id,
                    confirmed_wave_id,
                    is_active_at_close,
                    invalidated_by_candidate_id,
                    lead(candidate_id) over (
                        partition by transition_id
                        order by candidate_dt, candidate_id
                    ) as next_candidate_id
                from malf_candidate_ledger
                where run_id = ?
            )
            select count(*)
            from ordered_candidates
            where next_candidate_id is not null
              and confirmed_wave_id is null
              and (
                  is_active_at_close
                  or invalidated_by_candidate_id is null
                  or invalidated_by_candidate_id <> next_candidate_id
              )
            """,
            [source_core_run_id],
        ),
        _check(
            core_db,
            request,
            created_at,
            "core_new_wave_candidate_confirmation_required",
            """
            select count(*)
            from malf_wave_ledger w
            where w.run_id = ?
              and w.birth_type <> 'initial'
              and (
                  w.candidate_guard_pivot_id is null
                  or w.confirm_pivot_id is null
                  or not exists (
                      select 1
                      from malf_candidate_ledger c
                      where c.run_id = w.run_id
                        and c.confirmed_wave_id = w.wave_id
                        and c.candidate_guard_pivot_id = w.candidate_guard_pivot_id
                        and c.confirmed_by_pivot_id = w.confirm_pivot_id
                        and c.is_active_at_close
                  )
              )
            """,
            [source_core_run_id],
        ),
        _check(
            core_db,
            request,
            created_at,
            "core_candidate_confirmation_threshold",
            """
            select count(*)
            from malf_candidate_ledger c
            join malf_pivot_ledger p on p.pivot_id = c.confirmed_by_pivot_id
            where c.run_id = ?
              and c.confirmed_wave_id is not null
              and (
                  (
                      c.candidate_direction = 'up'
                      and (
                          p.pivot_type <> 'H'
                          or p.pivot_price <= c.reference_progress_extreme_price
                      )
                  )
                  or (
                      c.candidate_direction = 'down'
                      and (
                          p.pivot_type <> 'L'
                          or p.pivot_price >= c.reference_progress_extreme_price
                      )
                  )
              )
            """,
            [source_core_run_id],
        ),
        _check(
            core_db,
            request,
            created_at,
            "core_candidate_reference_matches_old_progress",
            """
            select count(*)
            from malf_candidate_ledger c
            join malf_transition_ledger t
              on t.transition_id = c.transition_id
             and t.run_id = c.run_id
            where c.run_id = ?
              and c.reference_progress_extreme_price <> t.old_progress_extreme_price
            """,
            [source_core_run_id],
        ),
        _check(
            core_db,
            request,
            created_at,
            "core_confirmed_transition_new_wave_required",
            """
            select count(*) from malf_transition_ledger
            where run_id = ? and state = 'confirmed' and new_wave_id is null
            """,
            [source_core_run_id],
        ),
        _check(
            core_db,
            request,
            created_at,
            "core_transition_old_wave_required",
            "select count(*) from malf_transition_ledger where run_id = ? and old_wave_id is null",
            [source_core_run_id],
        ),
        _manual_check(
            request,
            created_at,
            "lifespan_dense_source_bar_coverage",
            _lifespan_dense_missing_count(
                core_db, lifespan_db, request, source_core_run_id, source_lifespan_run_id
            ),
        ),
        _manual_check(
            request,
            created_at,
            "service_dense_lifespan_coverage",
            _service_dense_missing_count(lifespan_db, service_db, request, source_lifespan_run_id),
        ),
        _manual_check(
            request,
            created_at,
            "service_transition_semantics",
            _transition_semantics_failure_count(
                core_db, service_db, request.run_id, source_core_run_id
            ),
        ),
    ]
    hard_fail_count = sum(_as_int(row[5]) for row in checks)
    payload = {
        "run_id": request.run_id,
        "source_core_run_id": source_core_run_id,
        "source_lifespan_run_id": source_lifespan_run_id,
        "timeframe": request.timeframe,
        "schema_version": request.schema_version,
        "hard_fail_count": hard_fail_count,
        "published_row_count": _count_for_run(service_db, "malf_wave_position", request.run_id),
        "core_wave_count": _count(core_db, "malf_wave_ledger"),
        "lifespan_snapshot_count": _count_for_run(
            lifespan_db, "malf_lifespan_snapshot", source_lifespan_run_id
        ),
        "service_audit_rows": len(checks),
        "generated_at": created_at.isoformat(),
    }
    return checks, payload


def _manual_check(
    request: MalfDayRequest,
    created_at: datetime,
    check_name: str,
    failed_count: int,
) -> tuple[object, ...]:
    return (
        f"{request.run_id}|{check_name}",
        request.run_id,
        check_name,
        "hard",
        "pass" if failed_count == 0 else "fail",
        failed_count,
        "{}" if failed_count == 0 else f'{{"failed_count": {failed_count}}}',
        created_at,
    )


def _check(
    db_path: Path,
    request: MalfDayRequest,
    created_at: datetime,
    check_name: str,
    failure_query: str,
    params: list[object] | None = None,
) -> tuple[object, ...]:
    failed_count = 0
    if db_path.exists():
        with duckdb.connect(str(db_path), read_only=True) as con:
            row = con.execute(failure_query, params or []).fetchone()
            failed_count = 0 if row is None else int(row[0])
    return (
        f"{request.run_id}|{check_name}",
        request.run_id,
        check_name,
        "hard",
        "pass" if failed_count == 0 else "fail",
        failed_count,
        "{}" if failed_count == 0 else f'{{"failed_count": {failed_count}}}',
        created_at,
    )
