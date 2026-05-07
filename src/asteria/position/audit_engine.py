from __future__ import annotations

from datetime import datetime
from typing import Any

import duckdb

from asteria.position.contracts import PositionBuildRequest
from asteria.position.schema import POSITION_TABLES

FORBIDDEN_POSITION_COLUMNS = {
    "target_weight",
    "target_exposure",
    "portfolio_allocation",
    "order_intent",
    "order_intent_id",
    "fill_id",
}


def build_position_audit_rows(
    request: PositionBuildRequest,
    created_at: datetime,
) -> tuple[list[tuple[object, ...]], dict[str, Any]]:
    checks = [
        _source_signal_tables_check(request, created_at),
        _signal_hard_audit_check(request, created_at),
        _source_signal_run_id_check(request, created_at),
        _table_surface_check(request, created_at),
        _query_check(
            request,
            created_at,
            "position_candidate_rows_present",
            "select case when count(*) > 0 then 0 else 1 end from position_candidate_ledger",
        ),
        _query_check(
            request,
            created_at,
            "position_candidate_natural_key_unique",
            """
            select count(*) from (
                select signal_id, candidate_type, position_rule_version, count(*) row_count
                from position_candidate_ledger
                group by 1, 2, 3
                having row_count > 1
            )
            """,
        ),
        _query_check(
            request,
            created_at,
            "position_entry_plan_natural_key_unique",
            """
            select count(*) from (
                select position_candidate_id, entry_plan_type,
                       position_rule_version, count(*) row_count
                from position_entry_plan
                group by 1, 2, 3
                having row_count > 1
            )
            """,
        ),
        _query_check(
            request,
            created_at,
            "position_exit_plan_natural_key_unique",
            """
            select count(*) from (
                select position_candidate_id, exit_plan_type,
                       position_rule_version, count(*) row_count
                from position_exit_plan
                group by 1, 2, 3
                having row_count > 1
            )
            """,
        ),
        _query_check(
            request,
            created_at,
            "planned_candidate_has_entry_plan",
            """
            select count(*)
            from position_candidate_ledger c
            left join position_entry_plan e
              on c.position_candidate_id = e.position_candidate_id
            where c.candidate_state = 'planned'
              and e.position_candidate_id is null
            """,
        ),
        _query_check(
            request,
            created_at,
            "planned_candidate_has_exit_plan",
            """
            select count(*)
            from position_candidate_ledger c
            left join position_exit_plan x
              on c.position_candidate_id = x.position_candidate_id
            where c.candidate_state = 'planned'
              and x.position_candidate_id is null
            """,
        ),
        _query_check(
            request,
            created_at,
            "entry_plan_traces_to_candidate",
            """
            select count(*)
            from position_entry_plan e
            left join position_candidate_ledger c
              on e.position_candidate_id = c.position_candidate_id
            where c.position_candidate_id is null
            """,
        ),
        _query_check(
            request,
            created_at,
            "exit_plan_traces_to_candidate",
            """
            select count(*)
            from position_exit_plan x
            left join position_candidate_ledger c
              on x.position_candidate_id = c.position_candidate_id
            where c.position_candidate_id is null
            """,
        ),
        _query_check(
            request,
            created_at,
            "position_rule_version_traceable",
            """
            select count(*) from (
                select position_rule_version from position_signal_snapshot
                union
                select position_rule_version from position_candidate_ledger
                union
                select position_rule_version from position_entry_plan
                union
                select position_rule_version from position_exit_plan
            ) versions
            where not exists (
                select 1 from position_rule_version rules
                where rules.position_rule_version = versions.position_rule_version
            )
            """,
        ),
        _query_check(
            request,
            created_at,
            "rejected_candidate_reason_recorded",
            """
            select count(*)
            from position_candidate_ledger
            where candidate_state = 'rejected'
              and (reason_code is null or reason_code = '')
            """,
        ),
        _query_check(
            request,
            created_at,
            "entry_plan_validity_not_before_candidate",
            """
            select count(*)
            from position_entry_plan e
            join position_candidate_ledger c
              on e.position_candidate_id = c.position_candidate_id
            where e.entry_valid_from < c.candidate_dt
            """,
        ),
        _query_check(
            request,
            created_at,
            "exit_plan_validity_not_before_candidate",
            """
            select count(*)
            from position_exit_plan x
            join position_candidate_ledger c
              on x.position_candidate_id = c.position_candidate_id
            where x.exit_valid_from < c.candidate_dt
            """,
        ),
        _forbidden_position_columns_check(request, created_at),
    ]
    hard_fail_count = sum(_as_int(row[5]) for row in checks if row[3] == "hard")
    payload = {
        "run_id": request.run_id,
        "timeframe": request.timeframe,
        "schema_version": request.schema_version,
        "position_rule_version": request.position_rule_version,
        "source_signal_release_version": request.source_signal_release_version,
        "source_signal_run_id": request.source_signal_run_id,
        "hard_fail_count": hard_fail_count,
        "input_signal_count": _count_scoped_rows(request, "position_signal_snapshot"),
        "position_candidate_count": _count_scoped_rows(
            request,
            "position_candidate_ledger",
        ),
        "entry_plan_count": _count_scoped_rows(request, "position_entry_plan"),
        "exit_plan_count": _count_scoped_rows(request, "position_exit_plan"),
        "checks": [_audit_payload(row) for row in checks],
        "generated_at": created_at.isoformat(),
    }
    return checks, payload


def _source_signal_tables_check(
    request: PositionBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    if not request.source_signal_db.exists():
        return _row(request, created_at, "source_signal_tables_readable", 1)
    with duckdb.connect(str(request.source_signal_db), read_only=True) as con:
        tables = _table_names(con)
    missing = sorted({"formal_signal_ledger", "signal_audit"} - tables)
    sample = "{}" if not missing else f'{{"missing": {missing!r}}}'
    return _row(request, created_at, "source_signal_tables_readable", len(missing), sample)


def _signal_hard_audit_check(
    request: PositionBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    if not request.source_signal_db.exists():
        return _row(request, created_at, "source_signal_hard_audit_zero", 1)
    query = "select coalesce(sum(failed_count), 0) from signal_audit where severity = 'hard'"
    params: list[object] = []
    if request.source_signal_run_id:
        query += " and run_id = ?"
        params.append(request.source_signal_run_id)
    query += " and status = 'fail'"
    with duckdb.connect(str(request.source_signal_db), read_only=True) as con:
        row = con.execute(query, params).fetchone()
    return _row(
        request,
        created_at,
        "source_signal_hard_audit_zero",
        0 if row is None else int(row[0]),
    )


def _source_signal_run_id_check(
    request: PositionBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    if not request.source_signal_run_id:
        return _row(request, created_at, "source_signal_run_id_locked", 0)
    if not request.target_position_db.exists():
        return _row(request, created_at, "source_signal_run_id_locked", 1)
    with duckdb.connect(str(request.target_position_db), read_only=True) as con:
        row = con.execute(
            """
            select count(*)
            from position_signal_snapshot
            where position_run_id = ?
              and timeframe = ?
              and source_signal_run_id <> ?
            """,
            [request.run_id, request.timeframe, request.source_signal_run_id],
        ).fetchone()
    return _row(
        request,
        created_at,
        "source_signal_run_id_locked",
        0 if row is None else int(row[0]),
    )


def _table_surface_check(
    request: PositionBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    if not request.target_position_db.exists():
        return _row(request, created_at, "position_table_surface_limited", 1)
    with duckdb.connect(str(request.target_position_db), read_only=True) as con:
        actual = _table_names(con)
    expected = set(POSITION_TABLES)
    unexpected = sorted(actual - expected)
    missing = sorted(expected - actual)
    failed_count = len(unexpected) + len(missing)
    sample = (
        "{}" if failed_count == 0 else f'{{"unexpected": {unexpected!r}, "missing": {missing!r}}}'
    )
    return _row(request, created_at, "position_table_surface_limited", failed_count, sample)


def _forbidden_position_columns_check(
    request: PositionBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    if not request.target_position_db.exists():
        return _row(request, created_at, "position_forbidden_columns", 1)
    columns: set[str] = set()
    with duckdb.connect(str(request.target_position_db), read_only=True) as con:
        for table_name in [
            "position_candidate_ledger",
            "position_entry_plan",
            "position_exit_plan",
        ]:
            rows = con.execute(f"describe {table_name}").fetchall()
            columns.update(str(row[0]) for row in rows)
    forbidden = sorted(columns.intersection(FORBIDDEN_POSITION_COLUMNS))
    sample = "{}" if not forbidden else f'{{"forbidden_columns": {forbidden!r}}}'
    return _row(request, created_at, "position_forbidden_columns", len(forbidden), sample)


def _query_check(
    request: PositionBuildRequest,
    created_at: datetime,
    check_name: str,
    query: str,
) -> tuple[object, ...]:
    failed_count = 1
    if request.target_position_db.exists():
        with duckdb.connect(str(request.target_position_db), read_only=True) as con:
            row = con.execute(query).fetchone()
            failed_count = 0 if row is None else int(row[0])
    return _row(request, created_at, check_name, failed_count)


def _row(
    request: PositionBuildRequest,
    created_at: datetime,
    check_name: str,
    failed_count: int,
    sample_payload: str | None = None,
) -> tuple[object, ...]:
    sample = sample_payload if sample_payload is not None else "{}"
    return (
        f"{request.run_id}|{request.timeframe}|{check_name}",
        request.run_id,
        check_name,
        "hard",
        "pass" if failed_count == 0 else "fail",
        failed_count,
        sample,
        created_at,
    )


def _table_names(con: duckdb.DuckDBPyConnection) -> set[str]:
    return {
        str(row[0])
        for row in con.execute(
            "select table_name from information_schema.tables where table_schema = 'main'"
        ).fetchall()
    }


def _count_scoped_rows(request: PositionBuildRequest, table_name: str) -> int:
    if not request.target_position_db.exists():
        return 0
    with duckdb.connect(str(request.target_position_db), read_only=True) as con:
        row = con.execute(
            f"select count(*) from {table_name} where run_id = ?"
            if table_name != "position_signal_snapshot"
            else "select count(*) from position_signal_snapshot where position_run_id = ?",
            [request.run_id],
        ).fetchone()
    return 0 if row is None else int(row[0])


def _audit_payload(row: tuple[object, ...]) -> dict[str, object]:
    return {
        "audit_id": row[0],
        "check_name": row[2],
        "severity": row[3],
        "status": row[4],
        "failed_count": row[5],
        "sample_payload": row[6],
    }


def _as_int(value: object) -> int:
    if isinstance(value, int):
        return value
    return int(str(value))
