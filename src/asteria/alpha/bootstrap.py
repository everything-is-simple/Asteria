from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

from asteria.alpha.audit_engine import build_alpha_audit_rows
from asteria.alpha.contracts import (
    ALPHA_RULE_VERSION,
    ALPHA_SCHEMA_VERSION,
    AlphaBuildSummary,
    AlphaFamilyRequest,
)
from asteria.alpha.evidence import write_alpha_evidence
from asteria.alpha.rules import build_alpha_rows, wave_position_from_row
from asteria.alpha.schema import bootstrap_alpha_family_database

ALPHA_FAMILIES = ("BOF", "TST", "PB", "CPB", "BPB")
ALPHA_FAMILY_DATABASES = {
    "BOF": "alpha_bof.duckdb",
    "TST": "alpha_tst.duckdb",
    "PB": "alpha_pb.duckdb",
    "CPB": "alpha_cpb.duckdb",
    "BPB": "alpha_bpb.duckdb",
}
ALPHA_PRODUCTION_SOURCES = {
    "day": (
        "malf_service_day.duckdb",
        "malf-wave-position-dense-v1",
        "malf-v1-4-core-runtime-sync-implementation-20260505-01",
        "malf-day-formal-2024-s20-v14",
    ),
    "week": (
        "malf_service_week.duckdb",
        "malf-wave-position-week-v1",
        "malf-week-bounded-proof-build-20260506-01",
        "malf-week-formal-2024-s20-v1",
    ),
    "month": (
        "malf_service_month.duckdb",
        "malf-wave-position-month-v1",
        "malf-month-bounded-proof-build-20260506-01",
        "malf-month-formal-2024-s20-v1",
    ),
}


def run_alpha_family_build(request: AlphaFamilyRequest) -> AlphaBuildSummary:
    checkpoint = _load_completed_checkpoint(request, "build")
    if checkpoint:
        return checkpoint
    if request.mode == "audit-only":
        return run_alpha_family_audit(request)

    rows = _load_wave_positions(request)
    created_at = _utc_now()
    alpha_rows = build_alpha_rows(rows, request, created_at)
    bootstrap_alpha_family_database(request.target_alpha_db)
    source_run_id = rows[0].run_id if rows else None
    with duckdb.connect(str(request.target_alpha_db)) as con:
        con.execute("begin transaction")
        _delete_run(con, request)
        con.execute(
            "delete from alpha_schema_version where schema_version = ?", [request.schema_version]
        )
        con.execute(
            "delete from alpha_rule_version where alpha_family = ? and alpha_rule_version = ?",
            [request.alpha_family, request.alpha_rule_version],
        )
        con.execute(
            "insert into alpha_schema_version values (?, ?)", [request.schema_version, created_at]
        )
        con.execute(
            "insert into alpha_rule_version values (?, ?, ?, ?)",
            [request.alpha_family, request.alpha_rule_version, "waveposition_only", created_at],
        )
        if alpha_rows.events:
            con.executemany(
                """
                insert into alpha_event_ledger (
                    alpha_event_id, alpha_family, symbol, timeframe, bar_dt, event_type,
                    opportunity_state, source_wave_position_key, source_malf_service_version,
                    source_malf_run_id, run_id, schema_version, alpha_rule_version, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                alpha_rows.events,
            )
        if alpha_rows.scores:
            con.executemany(
                """
                insert into alpha_score_ledger (
                    alpha_score_id, alpha_event_id, alpha_family, score_name, score_value,
                    score_direction, score_bucket, source_malf_service_version,
                    source_malf_run_id, run_id, schema_version, alpha_rule_version, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                alpha_rows.scores,
            )
        if alpha_rows.candidates:
            con.executemany(
                """
                insert into alpha_signal_candidate (
                    alpha_candidate_id, alpha_event_id, alpha_family, symbol, timeframe, bar_dt,
                    candidate_type, candidate_state, opportunity_bias, confidence_bucket,
                    reason_code, candidate_score, source_malf_service_version, source_malf_run_id,
                    run_id, schema_version, alpha_rule_version, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                alpha_rows.candidates,
            )
        con.execute(
            """
            insert into alpha_family_run (
                run_id, runner_name, mode, timeframe, alpha_family, status, source_malf_db,
                input_row_count, event_count, score_count, candidate_count, schema_version,
                alpha_rule_version, source_malf_service_version, source_malf_run_id, created_at
            )
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                request.run_id,
                "alpha_family_build",
                request.mode,
                request.timeframe,
                request.alpha_family,
                "completed",
                str(request.source_malf_db),
                len(rows),
                len(alpha_rows.events),
                len(alpha_rows.scores),
                len(alpha_rows.candidates),
                request.schema_version,
                request.alpha_rule_version,
                request.source_malf_service_version,
                source_run_id,
                created_at,
            ],
        )
        con.execute("commit")

    audit = run_alpha_family_audit(request)
    summary = AlphaBuildSummary(
        run_id=request.run_id,
        alpha_family=request.alpha_family,
        stage="build",
        status="completed" if audit.hard_fail_count == 0 else "failed",
        timeframe=request.timeframe,
        event_count=len(alpha_rows.events),
        score_count=len(alpha_rows.scores),
        candidate_count=len(alpha_rows.candidates),
        hard_fail_count=audit.hard_fail_count,
        report_path=audit.report_path,
    )
    _save_checkpoint(request.checkpoint_path("build"), summary)
    return summary


def run_alpha_family_audit(request: AlphaFamilyRequest) -> AlphaBuildSummary:
    bootstrap_alpha_family_database(request.target_alpha_db)
    created_at = _utc_now()
    audit_rows, payload = build_alpha_audit_rows(request, created_at)
    with duckdb.connect(str(request.target_alpha_db)) as con:
        con.execute("begin transaction")
        con.execute(
            "delete from alpha_source_audit where run_id = ? and alpha_family = ?",
            [request.run_id, request.alpha_family],
        )
        con.executemany(
            "insert into alpha_source_audit values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            audit_rows,
        )
        con.execute("commit")

    report_path = _report_path(
        request.report_root,
        request.run_id,
        request.alpha_family,
        request.timeframe,
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = AlphaBuildSummary(
        run_id=request.run_id,
        alpha_family=request.alpha_family,
        stage="audit",
        status="completed" if payload["hard_fail_count"] == 0 else "failed",
        timeframe=request.timeframe,
        event_count=int(payload["event_count"]),
        score_count=int(payload["score_count"]),
        candidate_count=int(payload["candidate_count"]),
        hard_fail_count=int(payload["hard_fail_count"]),
        report_path=str(report_path),
    )
    _save_checkpoint(request.checkpoint_path("audit"), summary)
    return summary


def run_alpha_bounded_proof(
    source_malf_db: Path,
    target_data_root: Path,
    report_root: Path,
    validated_root: Path,
    temp_root: Path,
    run_id: str,
    start_dt: str | None,
    end_dt: str | None,
    symbol_limit: int | None,
    source_malf_service_version: str = "service-v1",
    source_malf_run_id: str | None = None,
    source_malf_sample_version: str | None = None,
    schema_version: str = ALPHA_SCHEMA_VERSION,
    alpha_rule_version: str = ALPHA_RULE_VERSION,
    mode: str = "bounded",
    timeframe: str = "day",
) -> list[AlphaBuildSummary]:
    summaries: list[AlphaBuildSummary] = []
    for family in ALPHA_FAMILIES:
        request = AlphaFamilyRequest(
            source_malf_db=source_malf_db,
            target_alpha_db=target_data_root / ALPHA_FAMILY_DATABASES[family],
            report_root=report_root,
            validated_root=validated_root,
            temp_root=temp_root,
            run_id=run_id,
            mode=mode,
            alpha_family=family,
            source_malf_service_version=source_malf_service_version,
            source_malf_run_id=source_malf_run_id,
            source_malf_sample_version=source_malf_sample_version,
            schema_version=schema_version,
            alpha_rule_version=alpha_rule_version,
            timeframe=timeframe,
            start_dt=start_dt,
            end_dt=end_dt,
            symbol_limit=symbol_limit,
        )
        summaries.append(run_alpha_family_build(request))
    write_alpha_evidence(report_root, validated_root, run_id, summaries, "bounded_proof")
    return summaries


def run_alpha_production_builder(
    source_malf_dbs: Mapping[str, Path] | None,
    source_malf_service_versions: Mapping[str, str] | None,
    target_data_root: Path,
    report_root: Path,
    validated_root: Path,
    temp_root: Path,
    run_id: str,
    mode: str,
    source_malf_run_ids: Mapping[str, str] | None = None,
    source_malf_sample_versions: Mapping[str, str] | None = None,
    start_dt: str | None = None,
    end_dt: str | None = None,
    symbol_limit: int | None = None,
    schema_version: str = ALPHA_SCHEMA_VERSION,
    alpha_rule_version: str = ALPHA_RULE_VERSION,
    timeframes: tuple[str, ...] = ("day", "week", "month"),
) -> list[AlphaBuildSummary]:
    summaries: list[AlphaBuildSummary] = []
    for timeframe in timeframes:
        (
            default_db_name,
            default_service_version,
            default_run_id,
            default_sample_version,
        ) = ALPHA_PRODUCTION_SOURCES[timeframe]
        has_custom_source = source_malf_dbs is not None and timeframe in source_malf_dbs
        if has_custom_source:
            assert source_malf_dbs is not None
            source_malf_db = source_malf_dbs[timeframe]
        else:
            source_malf_db = target_data_root / default_db_name
        if source_malf_service_versions is not None and timeframe in source_malf_service_versions:
            source_version = source_malf_service_versions[timeframe]
        else:
            source_version = default_service_version
        source_run_id: str | None
        if source_malf_run_ids is not None and timeframe in source_malf_run_ids:
            source_run_id = source_malf_run_ids[timeframe]
        else:
            source_run_id = None if has_custom_source else default_run_id
        source_sample_version: str | None
        if source_malf_sample_versions is not None and timeframe in source_malf_sample_versions:
            source_sample_version = source_malf_sample_versions[timeframe]
        else:
            source_sample_version = None if has_custom_source else default_sample_version
        for family in ALPHA_FAMILIES:
            request = AlphaFamilyRequest(
                source_malf_db=source_malf_db,
                target_alpha_db=target_data_root / ALPHA_FAMILY_DATABASES[family],
                report_root=report_root,
                validated_root=validated_root,
                temp_root=temp_root,
                run_id=run_id,
                mode=mode,
                alpha_family=family,
                source_malf_service_version=source_version,
                source_malf_run_id=source_run_id,
                source_malf_sample_version=source_sample_version,
                schema_version=schema_version,
                alpha_rule_version=alpha_rule_version,
                timeframe=timeframe,
                start_dt=start_dt,
                end_dt=end_dt,
                symbol_limit=symbol_limit,
            )
            summaries.append(run_alpha_family_build(request))
    write_alpha_evidence(
        report_root,
        validated_root,
        run_id,
        summaries,
        "production_builder_hardening",
    )
    return summaries


def _load_wave_positions(request: AlphaFamilyRequest) -> list[Any]:
    if not request.source_malf_db.exists():
        raise FileNotFoundError(f"Missing MALF service DB: {request.source_malf_db}")
    clauses = ["timeframe = ?", "service_version = ?"]
    params: list[object] = [request.timeframe, request.source_malf_service_version]
    if request.source_malf_run_id:
        clauses.append("run_id = ?")
        params.append(request.source_malf_run_id)
    if request.source_malf_sample_version:
        clauses.append("sample_version = ?")
        params.append(request.source_malf_sample_version)
    if request.start_date:
        clauses.append("bar_dt >= ?")
        params.append(request.start_date)
    if request.end_date:
        clauses.append("bar_dt <= ?")
        params.append(request.end_date)
    limit_clause = ""
    limit_params: list[object] = []
    if request.symbol_limit is not None:
        limit_clause = "where symbol in (select symbol from symbol_scope)"
        limit_params.append(request.symbol_limit)
    query = f"""
        with base as (
            select symbol, timeframe, bar_dt, system_state, wave_core_state, direction,
                   new_count, no_new_span, transition_span, update_rank, stagnation_rank,
                   life_state, position_quadrant, service_version, run_id
            from malf_wave_position
            where {" and ".join(clauses)}
        ),
        symbol_scope as (
            select symbol
            from base
            group by symbol
            order by symbol
            limit ?
        ),
        scoped as (
            select *
            from base
            {limit_clause}
        ),
        canonical as (
            select *,
                   row_number() over (
                       partition by symbol, timeframe, bar_dt
                       order by
                           case when system_state = 'transition' then 1 else 0 end,
                           transition_span desc,
                           run_id
                   ) as row_rank
            from scoped
        )
        select symbol, timeframe, bar_dt, system_state, wave_core_state, direction,
               new_count, no_new_span, transition_span, update_rank, stagnation_rank,
               life_state, position_quadrant, service_version, run_id
        from canonical
        where row_rank = 1
        order by symbol, bar_dt
    """
    with duckdb.connect(str(request.source_malf_db), read_only=True) as con:
        all_params = params + limit_params
        if request.symbol_limit is None:
            all_params = params + [9223372036854775807]
        return [wave_position_from_row(row) for row in con.execute(query, all_params).fetchall()]


def _delete_run(con: duckdb.DuckDBPyConnection, request: AlphaFamilyRequest) -> None:
    con.execute(
        """
        delete from alpha_score_ledger
        where run_id = ?
          and alpha_family = ?
          and alpha_event_id in (
              select alpha_event_id
              from alpha_event_ledger
              where run_id = ?
                and alpha_family = ?
                and timeframe = ?
          )
        """,
        [
            request.run_id,
            request.alpha_family,
            request.run_id,
            request.alpha_family,
            request.timeframe,
        ],
    )
    for table in ["alpha_family_run", "alpha_event_ledger", "alpha_signal_candidate"]:
        con.execute(
            f"delete from {table} where run_id = ? and alpha_family = ? and timeframe = ?",
            [request.run_id, request.alpha_family, request.timeframe],
        )
    con.execute(
        "delete from alpha_source_audit where audit_id like ?",
        [f"{request.run_id}|{request.alpha_family}|{request.timeframe}|%"],
    )


def _report_path(report_root: Path, run_id: str, family: str, timeframe: str) -> Path:
    return (
        report_root
        / "alpha"
        / _utc_now().date().isoformat()
        / f"{run_id}-{family.lower()}-{timeframe}-audit-summary.json"
    )


def _load_completed_checkpoint(request: AlphaFamilyRequest, stage: str) -> AlphaBuildSummary | None:
    if request.mode != "resume":
        return None
    checkpoint = _load_checkpoint(request.checkpoint_path(stage))
    if checkpoint and checkpoint.get("status") == "completed":
        summary = AlphaBuildSummary(**checkpoint["summary"])
        return AlphaBuildSummary(**{**summary.as_dict(), "resume_reused": True})
    return None


def _load_checkpoint(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _save_checkpoint(path: Path, summary: AlphaBuildSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": summary.status,
        "summary": summary.as_dict(),
        "created_at": _utc_now().isoformat(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
