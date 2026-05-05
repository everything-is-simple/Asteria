from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb

from asteria.malf.contracts import MalfDayRequest
from asteria.malf.source_contract import market_base_day_clauses

_TRACE_FIELDS = (
    "transition_boundary_high",
    "transition_boundary_low",
    "active_candidate_guard_pivot_id",
    "confirmation_pivot_id",
    "new_wave_id",
    "birth_type",
    "candidate_wait_span",
    "candidate_replacement_count",
    "confirmation_distance_abs",
    "confirmation_distance_pct",
)


def _count(db_path: Path, table_name: str) -> int:
    if not db_path.exists():
        return 0
    with duckdb.connect(str(db_path), read_only=True) as con:
        row = con.execute(f"select count(*) from {table_name}").fetchone()
        return 0 if row is None else int(row[0])


def _count_for_run(db_path: Path, table_name: str, run_id: str | None) -> int:
    if run_id is None or not db_path.exists():
        return 0
    with duckdb.connect(str(db_path), read_only=True) as con:
        row = con.execute(
            f"select count(*) from {table_name} where run_id = ?", [run_id]
        ).fetchone()
        return 0 if row is None else int(row[0])


def _missing_run_count(db_path: Path, table_name: str, run_id: str | None) -> int:
    return 0 if _count_for_run(db_path, table_name, run_id) > 0 else 1


def _resolve_audit_source_runs(
    core_db: Path,
    lifespan_db: Path,
    service_db: Path,
    request: MalfDayRequest,
) -> tuple[str | None, str | None]:
    service_row = _service_source_runs(service_db, request.run_id)
    if service_row is not None:
        return service_row
    lifespan_core_run_id = _lifespan_source_core_run(lifespan_db, request.run_id)
    if lifespan_core_run_id is not None:
        return lifespan_core_run_id, request.run_id
    if _count_for_run(core_db, "malf_wave_ledger", request.run_id) > 0:
        return request.run_id, request.run_id
    return None, None


def _lifespan_dense_missing_count(
    core_db: Path,
    lifespan_db: Path,
    request: MalfDayRequest,
    source_core_run_id: str | None,
    source_lifespan_run_id: str | None,
) -> int:
    if source_core_run_id is None or source_lifespan_run_id is None:
        return 1
    expected = _expected_lifespan_dense_keys(core_db, request, source_core_run_id)
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
                [source_lifespan_run_id],
            ).fetchall()
        }
    return len(expected - actual)


def _service_dense_missing_count(
    lifespan_db: Path,
    service_db: Path,
    request: MalfDayRequest,
    source_lifespan_run_id: str | None,
) -> int:
    if source_lifespan_run_id is None:
        return 1
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
                [source_lifespan_run_id],
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


def _transition_semantics_failure_count(
    core_db: Path,
    service_db: Path,
    run_id: str,
    source_core_run_id: str | None,
) -> int:
    if source_core_run_id is None:
        return 1
    with duckdb.connect(str(core_db), read_only=True) as con:
        old_directions = {
            str(row[0]): str(row[1])
            for row in con.execute(
                """
                select old_wave_id, old_direction
                from malf_transition_ledger
                where run_id = ?
                """,
                [source_core_run_id],
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


def _service_v13_trace_mismatch_count(
    lifespan_db: Path,
    service_db: Path,
    service_run_id: str,
    lifespan_run_id: str | None,
) -> int:
    if lifespan_run_id is None or not lifespan_db.exists() or not service_db.exists():
        return 0
    lifespan_rows: dict[tuple[object, ...], tuple[object, ...]] = {}
    with duckdb.connect(str(lifespan_db), read_only=True) as con:
        for row in con.execute(
            f"""
            select symbol, timeframe, bar_dt, system_state, wave_id, {", ".join(_TRACE_FIELDS)}
            from malf_lifespan_snapshot
            where run_id = ?
            """,
            [lifespan_run_id],
        ).fetchall():
            lifespan_rows[(row[0], row[1], row[2], row[3], row[4])] = tuple(row[5:])
    failed = 0
    with duckdb.connect(str(service_db), read_only=True) as con:
        for row in con.execute(
            f"""
            select symbol, timeframe, bar_dt, system_state,
                   coalesce(wave_id, old_wave_id), {", ".join(_TRACE_FIELDS)}
            from malf_wave_position
            where run_id = ?
            """,
            [service_run_id],
        ).fetchall():
            expected = lifespan_rows.get((row[0], row[1], row[2], row[3], row[4]))
            if expected is None or expected != tuple(row[5:]):
                failed += 1
    return failed


def _as_int(value: object) -> int:
    if isinstance(value, int):
        return value
    return int(str(value))


def _service_source_runs(service_db: Path, run_id: str) -> tuple[str | None, str | None] | None:
    if not service_db.exists():
        return None
    with duckdb.connect(str(service_db), read_only=True) as con:
        row = con.execute(
            """
            select source_core_run_id, source_lifespan_run_id
            from malf_service_run
            where run_id = ?
            order by created_at desc
            limit 1
            """,
            [run_id],
        ).fetchone()
    if row is None:
        return None
    return (None if row[0] is None else str(row[0]), None if row[1] is None else str(row[1]))


def _lifespan_source_core_run(lifespan_db: Path, run_id: str) -> str | None:
    if not lifespan_db.exists():
        return None
    with duckdb.connect(str(lifespan_db), read_only=True) as con:
        row = con.execute(
            """
            select source_core_run_id
            from malf_lifespan_run
            where run_id = ?
            order by created_at desc
            limit 1
            """,
            [run_id],
        ).fetchone()
    return None if row is None or row[0] is None else str(row[0])


def _expected_lifespan_dense_keys(
    core_db: Path, request: MalfDayRequest, source_core_run_id: str
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
            where run_id = ?
            """,
            [source_core_run_id],
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
             and w.run_id = t.run_id
            where t.run_id = ?
            """,
            [source_core_run_id],
        ).fetchall():
            for bar_dt in bar_dates.get((str(symbol), str(timeframe)), []):
                if bar_dt >= break_dt and (confirmed_dt is None or bar_dt < confirmed_dt):
                    expected.add(
                        (str(old_wave_id), str(symbol), str(timeframe), bar_dt, "transition")
                    )
    return expected


def _source_bar_dates(request: MalfDayRequest) -> dict[tuple[str, str], list[date]]:
    clauses, params = market_base_day_clauses(request)
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
