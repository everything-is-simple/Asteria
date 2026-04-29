from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb

from asteria.alpha.contracts import AlphaFamilyRequest
from asteria.alpha.schema import ALPHA_TABLES

FORBIDDEN_CANDIDATE_COLUMNS = {"position_size", "target_weight", "order_intent_id"}


def build_alpha_audit_rows(
    request: AlphaFamilyRequest,
    created_at: datetime,
) -> tuple[list[tuple[object, ...]], dict[str, Any]]:
    checks = [
        _source_check(request, created_at),
        _malf_interface_check(request, created_at),
        _table_surface_check(request, created_at),
        _duplicate_check(
            request,
            created_at,
            "event_natural_key_unique",
            """
            select count(*) from (
                select alpha_family, symbol, timeframe, bar_dt, event_type,
                       alpha_rule_version, count(*) row_count
                from alpha_event_ledger
                group by 1, 2, 3, 4, 5, 6
                having row_count > 1
            )
            """,
        ),
        _duplicate_check(
            request,
            created_at,
            "score_natural_key_unique",
            """
            select count(*) from (
                select alpha_event_id, score_name, alpha_rule_version, count(*) row_count
                from alpha_score_ledger
                group by 1, 2, 3
                having row_count > 1
            )
            """,
        ),
        _duplicate_check(
            request,
            created_at,
            "candidate_natural_key_unique",
            """
            select count(*) from (
                select alpha_event_id, candidate_type, alpha_rule_version, count(*) row_count
                from alpha_signal_candidate
                group by 1, 2, 3
                having row_count > 1
            )
            """,
        ),
        _family_match_check(request, created_at, "alpha_event_ledger"),
        _family_match_check(request, created_at, "alpha_score_ledger"),
        _family_match_check(request, created_at, "alpha_signal_candidate"),
        _rule_version_check(request, created_at),
        _forbidden_candidate_columns_check(request, created_at),
    ]
    hard_fail_count = sum(_as_int(row[6]) for row in checks if row[4] == "hard")
    payload = {
        "run_id": request.run_id,
        "alpha_family": request.alpha_family,
        "timeframe": request.timeframe,
        "schema_version": request.schema_version,
        "alpha_rule_version": request.alpha_rule_version,
        "hard_fail_count": hard_fail_count,
        "event_count": _count_rows(request.target_alpha_db, "alpha_event_ledger"),
        "score_count": _count_rows(request.target_alpha_db, "alpha_score_ledger"),
        "candidate_count": _count_rows(request.target_alpha_db, "alpha_signal_candidate"),
        "checks": [_audit_payload(row) for row in checks],
        "generated_at": created_at.isoformat(),
    }
    return checks, payload


def _source_check(
    request: AlphaFamilyRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    failed_count = 0
    sample = "{}"
    if not request.source_malf_db.exists():
        failed_count = 1
        sample = '{"missing": "source_malf_db"}'
    else:
        with duckdb.connect(str(request.source_malf_db), read_only=True) as con:
            tables = _table_names(con)
            required = {"malf_wave_position", "malf_wave_position_latest", "malf_interface_audit"}
            missing = sorted(required - tables)
            failed_count = len(missing)
            if missing:
                sample = f'{{"missing_tables": {missing!r}}}'
    return _row(request, created_at, "source_malf_tables_readable", failed_count, sample)


def _malf_interface_check(
    request: AlphaFamilyRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    failed_count = 1
    if request.source_malf_db.exists():
        with duckdb.connect(str(request.source_malf_db), read_only=True) as con:
            row = con.execute(
                """
                select coalesce(sum(failed_count), 0)
                from malf_interface_audit
                where severity = 'hard' and status = 'fail'
                """
            ).fetchone()
            failed_count = 0 if row is None else int(row[0])
    return _row(request, created_at, "malf_interface_hard_fail_zero", failed_count)


def _table_surface_check(
    request: AlphaFamilyRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    if not request.target_alpha_db.exists():
        return _row(request, created_at, "alpha_table_surface_limited", 1)
    with duckdb.connect(str(request.target_alpha_db), read_only=True) as con:
        actual = _table_names(con)
    expected = set(ALPHA_TABLES)
    unexpected = sorted(actual - expected)
    missing = sorted(expected - actual)
    failed_count = len(unexpected) + len(missing)
    sample = (
        "{}" if failed_count == 0 else f'{{"unexpected": {unexpected!r}, "missing": {missing!r}}}'
    )
    return _row(request, created_at, "alpha_table_surface_limited", failed_count, sample)


def _duplicate_check(
    request: AlphaFamilyRequest,
    created_at: datetime,
    check_name: str,
    query: str,
) -> tuple[object, ...]:
    return _query_check(request, created_at, check_name, query)


def _family_match_check(
    request: AlphaFamilyRequest,
    created_at: datetime,
    table_name: str,
) -> tuple[object, ...]:
    return _query_check(
        request,
        created_at,
        f"{table_name}_family_matches_target",
        f"select count(*) from {table_name} where alpha_family <> ?",
        [request.alpha_family],
    )


def _rule_version_check(
    request: AlphaFamilyRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    return _query_check(
        request,
        created_at,
        "rule_version_traceable",
        """
        select count(*) from (
            select alpha_rule_version from alpha_event_ledger
            union
            select alpha_rule_version from alpha_score_ledger
            union
            select alpha_rule_version from alpha_signal_candidate
        ) versions
        where not exists (
            select 1 from alpha_rule_version rules
            where rules.alpha_family = ?
              and rules.alpha_rule_version = versions.alpha_rule_version
        )
        """,
        [request.alpha_family],
    )


def _forbidden_candidate_columns_check(
    request: AlphaFamilyRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    if not request.target_alpha_db.exists():
        return _row(request, created_at, "candidate_forbidden_columns", 1)
    with duckdb.connect(str(request.target_alpha_db), read_only=True) as con:
        rows = con.execute("describe alpha_signal_candidate").fetchall()
    columns = {str(row[0]) for row in rows}
    forbidden = sorted(columns.intersection(FORBIDDEN_CANDIDATE_COLUMNS))
    sample = "{}" if not forbidden else f'{{"forbidden_columns": {forbidden!r}}}'
    return _row(request, created_at, "candidate_forbidden_columns", len(forbidden), sample)


def _query_check(
    request: AlphaFamilyRequest,
    created_at: datetime,
    check_name: str,
    query: str,
    params: list[object] | None = None,
) -> tuple[object, ...]:
    failed_count = 1
    if request.target_alpha_db.exists():
        with duckdb.connect(str(request.target_alpha_db), read_only=True) as con:
            row = con.execute(query, params or []).fetchone()
            failed_count = 0 if row is None else int(row[0])
    return _row(request, created_at, check_name, failed_count)


def _row(
    request: AlphaFamilyRequest,
    created_at: datetime,
    check_name: str,
    failed_count: int,
    sample_payload: str | None = None,
) -> tuple[object, ...]:
    sample = sample_payload if sample_payload is not None else "{}"
    return (
        f"{request.run_id}|{request.alpha_family}|{check_name}",
        request.run_id,
        request.alpha_family,
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


def _audit_payload(row: tuple[object, ...]) -> dict[str, object]:
    return {
        "audit_id": row[0],
        "alpha_family": row[2],
        "check_name": row[3],
        "severity": row[4],
        "status": row[5],
        "failed_count": row[6],
        "sample_payload": row[7],
    }


def _as_int(value: object) -> int:
    if isinstance(value, int):
        return value
    return int(str(value))
