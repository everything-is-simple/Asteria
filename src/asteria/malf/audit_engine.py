from __future__ import annotations

from datetime import datetime
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
    ]
    hard_fail_count = sum(_as_int(row[5]) for row in checks)
    payload = {
        "run_id": request.run_id,
        "timeframe": request.timeframe,
        "schema_version": request.schema_version,
        "hard_fail_count": hard_fail_count,
        "published_row_count": _count(service_db, "malf_wave_position"),
        "core_wave_count": _count(core_db, "malf_wave_ledger"),
        "lifespan_snapshot_count": _count(lifespan_db, "malf_lifespan_snapshot"),
        "service_audit_rows": len(checks),
        "generated_at": created_at.isoformat(),
    }
    return checks, payload


def _check(
    db_path: Path,
    request: MalfDayRequest,
    created_at: datetime,
    check_name: str,
    failure_query: str,
) -> tuple[object, ...]:
    failed_count = 0
    if db_path.exists():
        with duckdb.connect(str(db_path), read_only=True) as con:
            row = con.execute(failure_query).fetchone()
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


def _as_int(value: object) -> int:
    if isinstance(value, int):
        return value
    return int(str(value))
