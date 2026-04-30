from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import duckdb

from asteria.malf.contracts import MalfDayRequest


def build_audit_rows(
    core_db: Path,
    lifespan_db: Path,
    service_db: Path,
    request: MalfDayRequest,
    created_at: datetime,
) -> tuple[list[tuple[object, ...]], dict[str, Any]]:
    checks = [
        _check(
            service_db,
            request,
            created_at,
            "service_wave_core_state_not_transition",
            "select count(*) from malf_wave_position where wave_core_state = 'transition'",
        ),
        _check(
            service_db,
            request,
            created_at,
            "service_transition_old_wave_required",
            """
            select count(*) from malf_wave_position
            where system_state = 'transition'
              and (old_wave_id is null or wave_id is not null)
            """,
        ),
        _check(
            service_db,
            request,
            created_at,
            "service_transition_direction_required",
            """
            select count(*) from malf_wave_position
            where system_state = 'transition' and direction is null
            """,
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
                group by symbol, timeframe, service_version
                having row_count > 1
            )
            """,
        ),
        _check(
            lifespan_db,
            request,
            created_at,
            "lifespan_confirmation_no_new_span_zero",
            """
            select count(*) from malf_lifespan_snapshot
            where progress_updated and no_new_span <> 0
            """,
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
            [request.run_id],
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
                  or progress.pivot_dt >= w.terminated_dt
                  or w.final_guard_pivot_id is null
                  or guard.pivot_dt is null
                  or guard.pivot_dt >= w.terminated_dt
              )
            """,
            [request.run_id],
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
            [request.run_id],
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
            [request.run_id],
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
            [request.run_id],
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
            [request.run_id],
        ),
        _check(
            core_db,
            request,
            created_at,
            "core_confirmed_transition_new_wave_required",
            """
            select count(*) from malf_transition_ledger
            where state = 'confirmed' and new_wave_id is null
            """,
        ),
        _check(
            core_db,
            request,
            created_at,
            "core_transition_old_wave_required",
            "select count(*) from malf_transition_ledger where old_wave_id is null",
        ),
        _manual_check(
            request,
            created_at,
            "lifespan_dense_source_bar_coverage",
            _lifespan_dense_missing_count(core_db, lifespan_db, request),
        ),
        _manual_check(
            request,
            created_at,
            "service_dense_lifespan_coverage",
            _service_dense_missing_count(lifespan_db, service_db, request),
        ),
        _manual_check(
            request,
            created_at,
            "service_transition_semantics",
            _transition_semantics_failure_count(core_db, service_db, request.run_id),
        ),
    ]
    hard_fail_count = sum(_as_int(row[5]) for row in checks)
    payload = {
        "run_id": request.run_id,
        "timeframe": request.timeframe,
        "schema_version": request.schema_version,
        "hard_fail_count": hard_fail_count,
        "published_row_count": _count_for_run(service_db, "malf_wave_position", request.run_id),
        "core_wave_count": _count(core_db, "malf_wave_ledger"),
        "lifespan_snapshot_count": _count_for_run(
            lifespan_db, "malf_lifespan_snapshot", request.run_id
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


def _count(db_path: Path, table_name: str) -> int:
    if not db_path.exists():
        return 0
    with duckdb.connect(str(db_path), read_only=True) as con:
        row = con.execute(f"select count(*) from {table_name}").fetchone()
        return 0 if row is None else int(row[0])


def _count_for_run(db_path: Path, table_name: str, run_id: str) -> int:
    if not db_path.exists():
        return 0
    with duckdb.connect(str(db_path), read_only=True) as con:
        row = con.execute(
            f"select count(*) from {table_name} where run_id = ?", [run_id]
        ).fetchone()
        return 0 if row is None else int(row[0])


def _lifespan_dense_missing_count(core_db: Path, lifespan_db: Path, request: MalfDayRequest) -> int:
    expected = _expected_lifespan_dense_keys(core_db, request)
    if not expected:
        return 0
    with duckdb.connect(str(lifespan_db), read_only=True) as con:
        actual = {
            (str(row[0]), str(row[1]), str(row[2]), row[3], str(row[4]))
            for row in con.execute(
                """
                select wave_id, symbol, timeframe, bar_dt, system_state
                from malf_lifespan_snapshot
                where run_id = ?
                """,
                [request.run_id],
            ).fetchall()
        }
    return len(expected - actual)


def _expected_lifespan_dense_keys(
    core_db: Path, request: MalfDayRequest
) -> set[tuple[str, str, str, date, str]]:
    if not core_db.exists() or not request.source_db.exists():
        return set()
    bar_dates = _source_bar_dates(request)
    expected: set[tuple[str, str, str, date, str]] = set()
    with duckdb.connect(str(core_db), read_only=True) as con:
        for wave_id, symbol, timeframe, direction, confirm_dt, terminated_dt in con.execute(
            """
            select wave_id, symbol, timeframe, direction, confirm_dt, terminated_dt
            from malf_wave_ledger
            """
        ).fetchall():
            for bar_dt in bar_dates.get((str(symbol), str(timeframe)), []):
                if bar_dt >= confirm_dt and (terminated_dt is None or bar_dt < terminated_dt):
                    expected.add(
                        (str(wave_id), str(symbol), str(timeframe), bar_dt, f"{direction}_alive")
                    )
        for old_wave_id, symbol, timeframe, break_dt, confirmed_dt in con.execute(
            """
            select t.old_wave_id, w.symbol, w.timeframe, t.break_dt, t.confirmed_dt
            from malf_transition_ledger t
            join malf_wave_ledger w on w.wave_id = t.old_wave_id
            """
        ).fetchall():
            for bar_dt in bar_dates.get((str(symbol), str(timeframe)), []):
                if bar_dt >= break_dt and (confirmed_dt is None or bar_dt < confirmed_dt):
                    expected.add(
                        (str(old_wave_id), str(symbol), str(timeframe), bar_dt, "transition")
                    )
    return expected


def _source_bar_dates(request: MalfDayRequest) -> dict[tuple[str, str], list[date]]:
    clauses = ["timeframe = ?"]
    params: list[object] = [request.timeframe]
    if request.start_date:
        clauses.append("bar_dt >= ?")
        params.append(request.start_date)
    if request.end_date:
        clauses.append("bar_dt <= ?")
        params.append(request.end_date)
    query = f"""
        select symbol, timeframe, bar_dt
        from market_base_bar
        where {" and ".join(clauses)}
        order by symbol, timeframe, bar_dt
    """
    output: dict[tuple[str, str], list[date]] = {}
    with duckdb.connect(str(request.source_db), read_only=True) as con:
        for symbol, timeframe, bar_dt in con.execute(query, params).fetchall():
            output.setdefault((str(symbol), str(timeframe)), []).append(bar_dt)
    return output


def _service_dense_missing_count(
    lifespan_db: Path, service_db: Path, request: MalfDayRequest
) -> int:
    with duckdb.connect(str(lifespan_db), read_only=True) as con:
        expected = {
            (
                str(row[0]),
                str(row[1]),
                row[2],
                str(row[3]),
                None if str(row[3]) == "transition" else str(row[4]),
                str(row[5]) if str(row[3]) == "transition" else None,
            )
            for row in con.execute(
                """
                select symbol, timeframe, bar_dt, system_state, wave_id, old_wave_id
                from malf_lifespan_snapshot
                where run_id = ?
                """,
                [request.run_id],
            ).fetchall()
        }
    with duckdb.connect(str(service_db), read_only=True) as con:
        actual = {
            (str(row[0]), str(row[1]), row[2], str(row[3]), row[4], row[5])
            for row in con.execute(
                """
                select symbol, timeframe, bar_dt, system_state, wave_id, old_wave_id
                from malf_wave_position
                where run_id = ?
                """,
                [request.run_id],
            ).fetchall()
        }
    return len(expected - actual)


def _transition_semantics_failure_count(core_db: Path, service_db: Path, run_id: str) -> int:
    with duckdb.connect(str(core_db), read_only=True) as con:
        old_directions = {
            str(row[0]): str(row[1])
            for row in con.execute(
                "select old_wave_id, old_direction from malf_transition_ledger"
            ).fetchall()
        }
    with duckdb.connect(str(service_db), read_only=True) as con:
        transition_rows = con.execute(
            """
            select old_wave_id, wave_core_state, system_state, direction, transition_span
            from malf_wave_position
            where system_state = 'transition' and run_id = ?
            """,
            [run_id],
        ).fetchall()
    failed = 0
    for old_wave_id, wave_core_state, system_state, direction, transition_span in transition_rows:
        if (
            wave_core_state != "terminated"
            or system_state != "transition"
            or int(transition_span) < 1
            or old_directions.get(str(old_wave_id)) != direction
        ):
            failed += 1
    return failed


def _as_int(value: object) -> int:
    if isinstance(value, int):
        return value
    return int(str(value))
