from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb

from asteria.portfolio_plan.contracts import PortfolioPlanBuildRequest
from asteria.portfolio_plan.schema import PORTFOLIO_PLAN_TABLES

FORBIDDEN_PORTFOLIO_PLAN_COLUMNS = {
    "broker_order_id",
    "execution_price",
    "fill",
    "fill_id",
    "order_intent",
    "order_intent_id",
    "system_readout_id",
}


def build_portfolio_plan_audit_rows(
    request: PortfolioPlanBuildRequest,
    created_at: datetime,
    audit_db_path: Path | None = None,
) -> tuple[list[tuple[object, ...]], dict[str, Any]]:
    db_path = audit_db_path or request.target_portfolio_plan_db
    checks = [
        _source_position_tables_check(request, created_at),
        _position_hard_audit_check(request, created_at),
        _source_position_run_id_check(request, created_at, db_path),
        _table_surface_check(request, created_at, db_path),
        _query_check(
            request,
            created_at,
            db_path,
            "portfolio_admission_rows_present",
            "select case when count(*) > 0 then 0 else 1 end from portfolio_admission_ledger",
        ),
        _query_check(
            request,
            created_at,
            db_path,
            "portfolio_admission_natural_key_unique",
            """
            select count(*) from (
                select position_candidate_id, portfolio_plan_rule_version, count(*) row_count
                from portfolio_admission_ledger
                group by 1, 2
                having row_count > 1
            )
            """,
        ),
        _query_check(
            request,
            created_at,
            db_path,
            "portfolio_target_exposure_natural_key_unique",
            """
            select count(*) from (
                select portfolio_admission_id, exposure_type,
                       portfolio_plan_rule_version, count(*) row_count
                from portfolio_target_exposure
                group by 1, 2, 3
                having row_count > 1
            )
            """,
        ),
        _query_check(
            request,
            created_at,
            db_path,
            "portfolio_trim_natural_key_unique",
            """
            select count(*) from (
                select portfolio_admission_id, trim_reason,
                       portfolio_plan_rule_version, count(*) row_count
                from portfolio_trim_ledger
                group by 1, 2, 3
                having row_count > 1
            )
            """,
        ),
        _query_check(
            request,
            created_at,
            db_path,
            "admitted_or_trimmed_has_target_exposure",
            """
            select count(*)
            from portfolio_admission_ledger a
            left join portfolio_target_exposure e
              on a.portfolio_admission_id = e.portfolio_admission_id
            where a.admission_state in ('admitted', 'trimmed')
              and e.portfolio_admission_id is null
            """,
        ),
        _query_check(
            request,
            created_at,
            db_path,
            "target_exposure_traces_to_admission",
            """
            select count(*)
            from portfolio_target_exposure e
            left join portfolio_admission_ledger a
              on e.portfolio_admission_id = a.portfolio_admission_id
            where a.portfolio_admission_id is null
            """,
        ),
        _query_check(
            request,
            created_at,
            db_path,
            "trim_traces_to_admission",
            """
            select count(*)
            from portfolio_trim_ledger t
            left join portfolio_admission_ledger a
              on t.portfolio_admission_id = a.portfolio_admission_id
            where a.portfolio_admission_id is null
            """,
        ),
        _query_check(
            request,
            created_at,
            db_path,
            "portfolio_plan_rule_version_traceable",
            """
            select count(*) from (
                select portfolio_plan_rule_version from portfolio_position_snapshot
                union
                select portfolio_plan_rule_version from portfolio_constraint_ledger
                union
                select portfolio_plan_rule_version from portfolio_admission_ledger
                union
                select portfolio_plan_rule_version from portfolio_target_exposure
                union
                select portfolio_plan_rule_version from portfolio_trim_ledger
            ) versions
            where not exists (
                select 1 from portfolio_plan_rule_version rules
                where rules.portfolio_plan_rule_version = versions.portfolio_plan_rule_version
            )
            """,
        ),
        _query_check(
            request,
            created_at,
            db_path,
            "rejected_admission_reason_recorded",
            """
            select count(*)
            from portfolio_admission_ledger
            where admission_state = 'rejected'
              and (admission_reason is null or admission_reason = '')
            """,
        ),
        _query_check(
            request,
            created_at,
            db_path,
            "trim_constraint_name_recorded",
            """
            select count(*)
            from portfolio_trim_ledger
            where constraint_name is null or constraint_name = ''
            """,
        ),
        _state_present_check(request, created_at, db_path, "admitted"),
        _state_present_check(request, created_at, db_path, "rejected"),
        _state_present_check(request, created_at, db_path, "trimmed"),
        _state_present_check(request, created_at, db_path, "expired"),
        _forbidden_columns_check(request, created_at, db_path),
    ]
    hard_fail_count = sum(_as_int(row[5]) for row in checks if row[3] == "hard")
    payload = {
        "run_id": request.run_id,
        "timeframe": request.timeframe,
        "schema_version": request.schema_version,
        "portfolio_plan_rule_version": request.portfolio_plan_rule_version,
        "source_position_release_version": request.source_position_release_version,
        "source_position_run_id": request.source_position_run_id,
        "hard_fail_count": hard_fail_count,
        "input_position_count": _count_scoped_rows(
            db_path, request.run_id, "portfolio_position_snapshot"
        ),
        "admission_count": _count_scoped_rows(
            db_path, request.run_id, "portfolio_admission_ledger"
        ),
        "target_exposure_count": _count_scoped_rows(
            db_path, request.run_id, "portfolio_target_exposure"
        ),
        "trim_count": _count_scoped_rows(db_path, request.run_id, "portfolio_trim_ledger"),
        "checks": [_audit_payload(row) for row in checks],
        "generated_at": created_at.isoformat(),
    }
    return checks, payload


def _source_position_tables_check(
    request: PortfolioPlanBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    if not request.source_position_db.exists():
        return _row(request, created_at, "source_position_tables_readable", 1)
    with duckdb.connect(str(request.source_position_db), read_only=True) as con:
        tables = _table_names(con)
    expected = {
        "position_audit",
        "position_candidate_ledger",
        "position_entry_plan",
        "position_exit_plan",
        "position_run",
    }
    missing = sorted(expected - tables)
    sample = "{}" if not missing else jsonish({"missing": missing})
    return _row(request, created_at, "source_position_tables_readable", len(missing), sample)


def _position_hard_audit_check(
    request: PortfolioPlanBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    if not request.source_position_db.exists():
        return _row(request, created_at, "source_position_hard_audit_zero", 1)
    query = "select coalesce(sum(failed_count), 0) from position_audit where severity = 'hard'"
    params: list[object] = []
    if request.source_position_run_id:
        query += " and run_id = ?"
        params.append(request.source_position_run_id)
    query += " and status = 'fail'"
    with duckdb.connect(str(request.source_position_db), read_only=True) as con:
        row = con.execute(query, params).fetchone()
    return _row(
        request,
        created_at,
        "source_position_hard_audit_zero",
        0 if row is None else int(row[0]),
    )


def _source_position_run_id_check(
    request: PortfolioPlanBuildRequest,
    created_at: datetime,
    db_path: Path,
) -> tuple[object, ...]:
    if not request.source_position_run_id:
        return _row(request, created_at, "source_position_run_id_locked", 0)
    if not db_path.exists():
        return _row(request, created_at, "source_position_run_id_locked", 1)
    with duckdb.connect(str(db_path), read_only=True) as con:
        row = con.execute(
            """
            select count(*)
            from portfolio_position_snapshot
            where portfolio_run_id = ?
              and source_position_run_id <> ?
            """,
            [request.run_id, request.source_position_run_id],
        ).fetchone()
    return _row(
        request,
        created_at,
        "source_position_run_id_locked",
        0 if row is None else int(row[0]),
    )


def _table_surface_check(
    request: PortfolioPlanBuildRequest,
    created_at: datetime,
    db_path: Path,
) -> tuple[object, ...]:
    if not db_path.exists():
        return _row(request, created_at, "portfolio_table_surface_limited", 1)
    with duckdb.connect(str(db_path), read_only=True) as con:
        actual = _table_names(con)
    expected = set(PORTFOLIO_PLAN_TABLES)
    unexpected = sorted(actual - expected)
    missing = sorted(expected - actual)
    failed_count = len(unexpected) + len(missing)
    sample = "{}" if failed_count == 0 else jsonish({"unexpected": unexpected, "missing": missing})
    return _row(request, created_at, "portfolio_table_surface_limited", failed_count, sample)


def _query_check(
    request: PortfolioPlanBuildRequest,
    created_at: datetime,
    db_path: Path,
    check_name: str,
    query: str,
) -> tuple[object, ...]:
    failed_count = 1
    if db_path.exists():
        with duckdb.connect(str(db_path), read_only=True) as con:
            row = con.execute(query).fetchone()
            failed_count = 0 if row is None else int(row[0])
    return _row(request, created_at, check_name, failed_count)


def _state_present_check(
    request: PortfolioPlanBuildRequest,
    created_at: datetime,
    db_path: Path,
    state: str,
) -> tuple[object, ...]:
    return _query_check(
        request,
        created_at,
        db_path,
        f"bounded_sample_has_{state}_admission",
        f"""
        select case when count(*) > 0 then 0 else 1 end
        from portfolio_admission_ledger
        where run_id = '{request.run_id}'
          and admission_state = '{state}'
        """,
    )


def _forbidden_columns_check(
    request: PortfolioPlanBuildRequest,
    created_at: datetime,
    db_path: Path,
) -> tuple[object, ...]:
    if not db_path.exists():
        return _row(request, created_at, "portfolio_forbidden_columns", 1)
    columns: set[str] = set()
    with duckdb.connect(str(db_path), read_only=True) as con:
        for table_name in [
            "portfolio_admission_ledger",
            "portfolio_target_exposure",
            "portfolio_trim_ledger",
        ]:
            rows = con.execute(f"describe {table_name}").fetchall()
            columns.update(str(row[0]) for row in rows)
    forbidden = sorted(columns.intersection(FORBIDDEN_PORTFOLIO_PLAN_COLUMNS))
    sample = "{}" if not forbidden else jsonish({"forbidden_columns": forbidden})
    return _row(request, created_at, "portfolio_forbidden_columns", len(forbidden), sample)


def _row(
    request: PortfolioPlanBuildRequest,
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


def _count_scoped_rows(db_path: Path, run_id: str, table_name: str) -> int:
    if not db_path.exists():
        return 0
    run_column = "portfolio_run_id" if table_name == "portfolio_position_snapshot" else "run_id"
    with duckdb.connect(str(db_path), read_only=True) as con:
        row = con.execute(
            f"select count(*) from {table_name} where {run_column} = ?",
            [run_id],
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


def jsonish(payload: dict[str, object]) -> str:
    return str(payload).replace("'", '"')
