from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb

from asteria.signal.bootstrap_constants import SIGNAL_FAMILY_DATABASES
from asteria.signal.contracts import SignalBuildRequest
from asteria.signal.schema import SIGNAL_TABLES

FORBIDDEN_SIGNAL_COLUMNS = {
    "position_size",
    "target_weight",
    "portfolio_allocation",
    "order_intent",
    "order_intent_id",
    "fill_id",
}


def build_signal_audit_rows(
    request: SignalBuildRequest,
    created_at: datetime,
) -> tuple[list[tuple[object, ...]], dict[str, Any]]:
    checks = [
        _source_alpha_tables_check(request, created_at),
        _alpha_hard_audit_check(request, created_at),
        _source_alpha_run_id_check(request, created_at),
        _table_surface_check(request, created_at),
        _query_check(
            request,
            created_at,
            "formal_signal_rows_present",
            "select case when count(*) > 0 then 0 else 1 end from formal_signal_ledger",
        ),
        _query_check(
            request,
            created_at,
            "formal_signal_natural_key_unique",
            """
            select count(*) from (
                select symbol, timeframe, signal_dt, signal_type,
                       signal_rule_version, count(*) row_count
                from formal_signal_ledger
                group by 1, 2, 3, 4, 5
                having row_count > 1
            )
            """,
        ),
        _query_check(
            request,
            created_at,
            "component_natural_key_unique",
            """
            select count(*) from (
                select signal_id, alpha_family, alpha_candidate_id,
                       signal_rule_version, count(*) row_count
                from signal_component_ledger
                group by 1, 2, 3, 4
                having row_count > 1
            )
            """,
        ),
        _query_check(
            request,
            created_at,
            "formal_signal_has_component",
            """
            select count(*)
            from formal_signal_ledger f
            left join signal_component_ledger c on f.signal_id = c.signal_id
            where c.signal_id is null
            """,
        ),
        _query_check(
            request,
            created_at,
            "component_traces_to_alpha_snapshot",
            """
            select count(*)
            from signal_component_ledger c
            left join signal_input_snapshot s
              on c.signal_run_id = s.signal_run_id
             and c.alpha_family = s.alpha_family
             and c.alpha_candidate_id = s.alpha_candidate_id
            where s.alpha_candidate_id is null
            """,
        ),
        _query_check(
            request,
            created_at,
            "signal_rule_version_traceable",
            """
            select count(*) from (
                select signal_rule_version from formal_signal_ledger
                union
                select signal_rule_version from signal_component_ledger
                union
                select signal_rule_version from signal_input_snapshot
            ) versions
            where not exists (
                select 1 from signal_rule_version rules
                where rules.signal_rule_version = versions.signal_rule_version
            )
            """,
        ),
        _query_check(
            request,
            created_at,
            "conflict_components_recorded",
            """
            select count(*)
            from formal_signal_ledger
            where conflict_count > 0
              and not exists (
                  select 1
                  from signal_component_ledger
                  where component_role = 'conflict'
              )
            """,
        ),
        _query_check(
            request,
            created_at,
            "rejected_signal_reason_recorded",
            """
            select count(*)
            from formal_signal_ledger
            where signal_state = 'rejected'
              and (reason_code is null or reason_code = '')
            """,
        ),
        _forbidden_signal_columns_check(request, created_at),
    ]
    hard_fail_count = sum(_as_int(row[5]) for row in checks if row[3] == "hard")
    payload = {
        "run_id": request.run_id,
        "timeframe": request.timeframe,
        "schema_version": request.schema_version,
        "signal_rule_version": request.signal_rule_version,
        "source_alpha_release_version": request.source_alpha_release_version,
        "source_alpha_run_id": request.source_alpha_run_id,
        "hard_fail_count": hard_fail_count,
        "input_candidate_count": _count_scoped_rows(request, "signal_input_snapshot"),
        "formal_signal_count": _count_scoped_rows(request, "formal_signal_ledger"),
        "component_count": _count_scoped_rows(request, "signal_component_ledger"),
        "checks": [_audit_payload(row) for row in checks],
        "generated_at": created_at.isoformat(),
    }
    return checks, payload


def _source_alpha_tables_check(
    request: SignalBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    failed_count = 0
    missing: list[str] = []
    for db_name in SIGNAL_FAMILY_DATABASES.values():
        path = request.source_alpha_root / db_name
        if not path.exists():
            missing.append(str(path))
            continue
        with duckdb.connect(str(path), read_only=True) as con:
            tables = _table_names(con)
        for table_name in ["alpha_signal_candidate", "alpha_source_audit"]:
            if table_name not in tables:
                missing.append(f"{path}:{table_name}")
    failed_count = len(missing)
    sample = "{}" if not missing else f'{{"missing": {missing!r}}}'
    return _row(request, created_at, "source_alpha_tables_readable", failed_count, sample)


def _alpha_hard_audit_check(
    request: SignalBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    failed_count = 0
    for db_name in SIGNAL_FAMILY_DATABASES.values():
        path = request.source_alpha_root / db_name
        if not path.exists():
            failed_count += 1
            continue
        with duckdb.connect(str(path), read_only=True) as con:
            row = con.execute(
                """
                select coalesce(sum(failed_count), 0)
                from alpha_source_audit
                where severity = 'hard' and status = 'fail'
                """
            ).fetchone()
        failed_count += 0 if row is None else int(row[0])
    return _row(request, created_at, "alpha_hard_audit_zero", failed_count)


def _source_alpha_run_id_check(
    request: SignalBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    if not request.source_alpha_run_id:
        return _row(request, created_at, "source_alpha_run_id_locked", 0)
    if not request.target_signal_db.exists():
        return _row(request, created_at, "source_alpha_run_id_locked", 1)
    with duckdb.connect(str(request.target_signal_db), read_only=True) as con:
        row = con.execute(
            """
            select count(*)
            from signal_input_snapshot
            where signal_run_id = ?
              and timeframe = ?
              and source_alpha_run_id <> ?
            """,
            [request.run_id, request.timeframe, request.source_alpha_run_id],
        ).fetchone()
    failed_count = 0 if row is None else int(row[0])
    return _row(request, created_at, "source_alpha_run_id_locked", failed_count)


def _table_surface_check(
    request: SignalBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    if not request.target_signal_db.exists():
        return _row(request, created_at, "signal_table_surface_limited", 1)
    with duckdb.connect(str(request.target_signal_db), read_only=True) as con:
        actual = _table_names(con)
    expected = set(SIGNAL_TABLES)
    unexpected = sorted(actual - expected)
    missing = sorted(expected - actual)
    failed_count = len(unexpected) + len(missing)
    sample = (
        "{}" if failed_count == 0 else f'{{"unexpected": {unexpected!r}, "missing": {missing!r}}}'
    )
    return _row(request, created_at, "signal_table_surface_limited", failed_count, sample)


def _forbidden_signal_columns_check(
    request: SignalBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    if not request.target_signal_db.exists():
        return _row(request, created_at, "signal_forbidden_columns", 1)
    with duckdb.connect(str(request.target_signal_db), read_only=True) as con:
        columns: set[str] = set()
        for table in ["formal_signal_ledger", "signal_component_ledger", "signal_input_snapshot"]:
            rows = con.execute(f"describe {table}").fetchall()
            columns.update(str(row[0]) for row in rows)
    forbidden = sorted(columns.intersection(FORBIDDEN_SIGNAL_COLUMNS))
    sample = "{}" if not forbidden else f'{{"forbidden_columns": {forbidden!r}}}'
    return _row(request, created_at, "signal_forbidden_columns", len(forbidden), sample)


def _query_check(
    request: SignalBuildRequest,
    created_at: datetime,
    check_name: str,
    query: str,
) -> tuple[object, ...]:
    failed_count = 1
    if request.target_signal_db.exists():
        with duckdb.connect(str(request.target_signal_db), read_only=True) as con:
            row = con.execute(query).fetchone()
            failed_count = 0 if row is None else int(row[0])
    return _row(request, created_at, check_name, failed_count)


def _row(
    request: SignalBuildRequest,
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


def _count_rows(path: Path, table_name: str) -> int:
    if not path.exists():
        return 0
    with duckdb.connect(str(path), read_only=True) as con:
        row = con.execute(f"select count(*) from {table_name}").fetchone()
        return 0 if row is None else int(row[0])


def _count_scoped_rows(request: SignalBuildRequest, table_name: str) -> int:
    if not request.target_signal_db.exists():
        return 0
    with duckdb.connect(str(request.target_signal_db), read_only=True) as con:
        if table_name == "signal_input_snapshot":
            row = con.execute(
                """
                select count(*)
                from signal_input_snapshot
                where signal_run_id = ? and timeframe = ?
                """,
                [request.run_id, request.timeframe],
            ).fetchone()
        elif table_name == "formal_signal_ledger":
            row = con.execute(
                """
                select count(*)
                from formal_signal_ledger
                where run_id = ? and timeframe = ?
                """,
                [request.run_id, request.timeframe],
            ).fetchone()
        elif table_name == "signal_component_ledger":
            row = con.execute(
                """
                select count(*)
                from signal_component_ledger c
                join formal_signal_ledger f on c.signal_id = f.signal_id
                where c.signal_run_id = ? and f.run_id = ? and f.timeframe = ?
                """,
                [request.run_id, request.run_id, request.timeframe],
            ).fetchone()
        else:
            row = con.execute(f"select count(*) from {table_name}").fetchone()
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
