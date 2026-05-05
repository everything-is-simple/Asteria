from __future__ import annotations

import json

import duckdb

from asteria.malf.audit_engine import build_audit_rows
from asteria.malf.bootstrap_support import (
    CORE_SNAPSHOT_INSERT_SQL,
    count_market_base_rows,
    count_rows_for_run,
    delete_run,
    executemany_if_rows,
    insert_core_run,
    insert_lifespan_run,
    insert_service_run,
    insert_values_sql,
    latest_run_id,
    load_completed_checkpoint,
    report_path,
    require,
    require_build_mode,
    resolve_source_market_base_run_id,
    save_checkpoint,
    utc_now,
)
from asteria.malf.contracts import MalfBuildSummary, MalfDayRequest
from asteria.malf.core_engine import build_core_rows
from asteria.malf.lifespan_engine import build_lifespan_rows
from asteria.malf.schema import (
    bootstrap_malf_core_day_database,
    bootstrap_malf_lifespan_day_database,
    bootstrap_malf_service_day_database,
)
from asteria.malf.service_engine import build_wave_position_rows


def run_malf_day_core_build(request: MalfDayRequest) -> MalfBuildSummary:
    require_build_mode(request, "core")
    require(request.core_rule_version, "core_rule_version")
    checkpoint = load_completed_checkpoint(request, "core")
    if checkpoint:
        return checkpoint

    input_row_count = count_market_base_rows(request)
    bootstrap_malf_core_day_database(request.core_db)
    now = utc_now()
    source_market_base_run_id = resolve_source_market_base_run_id(request)
    rows = build_core_rows(request, now, source_market_base_run_id)
    with duckdb.connect(str(request.core_db)) as con:
        con.execute("begin transaction")
        delete_run(con, request.run_id, _CORE_RUN_TABLES)
        con.execute(
            "delete from malf_schema_version where schema_version = ?",
            [request.schema_version],
        )
        executemany_if_rows(
            con,
            """
            insert into malf_pivot_ledger (
                pivot_id, symbol, timeframe, pivot_dt, confirmed_dt, pivot_type, pivot_price,
                pivot_seq_in_bar, source_bar_dt, run_id, schema_version, core_rule_version,
                pivot_detection_rule_version, created_at
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    item.pivot_id,
                    item.symbol,
                    request.timeframe,
                    item.pivot_dt,
                    item.confirmed_dt,
                    item.pivot_type,
                    item.pivot_price,
                    item.pivot_seq_in_bar,
                    item.pivot_dt,
                    request.run_id,
                    request.schema_version,
                    request.core_rule_version,
                    request.pivot_detection_rule_version,
                    now,
                )
                for item in rows.pivots
            ],
        )
        executemany_if_rows(
            con,
            "insert into malf_structure_ledger values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows.structures,
        )
        executemany_if_rows(
            con,
            """
            insert into malf_wave_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    item.wave_id,
                    item.symbol,
                    request.timeframe,
                    item.wave_seq,
                    item.direction,
                    item.birth_type,
                    item.start_pivot_id,
                    item.candidate_guard_pivot_id,
                    item.confirm_pivot_id,
                    item.confirm_dt,
                    item.wave_core_state,
                    item.terminated_dt,
                    item.terminated_by_break_id,
                    item.final_progress.pivot_id,
                    item.final_progress.pivot_price,
                    item.final_guard.pivot_id,
                    item.final_guard.pivot_price,
                    request.run_id,
                    request.schema_version,
                    request.core_rule_version,
                    now,
                    item.final_guard.pivot_id,
                    item.final_guard.pivot_price,
                )
                for item in rows.waves
            ],
        )
        executemany_if_rows(
            con,
            "insert into malf_break_ledger values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows.breaks,
        )
        executemany_if_rows(
            con,
            insert_values_sql("malf_transition_ledger", 17),
            [
                (
                    item.transition_id,
                    item.old_wave_id,
                    item.break_id,
                    item.old_direction,
                    item.old_progress.pivot_id,
                    item.old_progress.pivot_price,
                    item.break_dt,
                    item.state,
                    item.confirmed_dt,
                    item.new_wave_id,
                    request.run_id,
                    request.schema_version,
                    request.core_rule_version,
                    now,
                    item.old_guard.pivot_id,
                    item.transition_boundary_high,
                    item.transition_boundary_low,
                )
                for item in rows.transitions
            ],
        )
        executemany_if_rows(
            con,
            """
            insert into malf_candidate_ledger (
                candidate_id, transition_id, candidate_guard_pivot_id, candidate_direction,
                candidate_dt, is_active_at_close, invalidated_by_candidate_id,
                reference_progress_extreme_price, confirmed_by_pivot_id, confirmed_wave_id,
                run_id, schema_version, core_rule_version, created_at, candidate_status,
                confirmation_pivot_id, new_wave_id, candidate_event_type
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    item.candidate_id,
                    item.transition_id,
                    item.guard.pivot_id,
                    item.direction,
                    item.guard.pivot_dt,
                    item.is_active_at_close,
                    item.invalidated_by_candidate_id,
                    item.reference_price,
                    item.confirmed_by_pivot_id,
                    item.confirmed_wave_id,
                    request.run_id,
                    request.schema_version,
                    request.core_rule_version,
                    now,
                    item.status,
                    item.confirmed_by_pivot_id,
                    item.confirmed_wave_id,
                    item.event_type,
                )
                for item in rows.candidates
            ],
        )
        executemany_if_rows(con, CORE_SNAPSHOT_INSERT_SQL, rows.snapshots)
        insert_core_run(con, request, input_row_count, source_market_base_run_id, now)
        con.execute("insert into malf_schema_version values (?, ?)", [request.schema_version, now])
        con.execute("commit")

    summary = MalfBuildSummary(
        run_id=request.run_id,
        stage="core",
        status="completed",
        input_row_count=input_row_count,
        input_wave_count=len(rows.waves),
    )
    save_checkpoint(request.checkpoint_path("core"), summary)
    return summary


def run_malf_day_lifespan_build(request: MalfDayRequest) -> MalfBuildSummary:
    require_build_mode(request, "lifespan")
    require(request.lifespan_rule_version, "lifespan_rule_version")
    require(request.sample_version, "sample_version")
    checkpoint = load_completed_checkpoint(request, "lifespan")
    if checkpoint:
        return checkpoint

    bootstrap_malf_lifespan_day_database(request.lifespan_db)
    source_core_run_id = latest_run_id(request.core_db, "malf_core_run")
    core_run_id = source_core_run_id or request.run_id
    input_wave_count = count_rows_for_run(request.core_db, "malf_wave_ledger", core_run_id)
    now = utc_now()
    snapshots, profiles = build_lifespan_rows(request.core_db, request, now, core_run_id)
    with duckdb.connect(str(request.lifespan_db)) as con:
        con.execute("begin transaction")
        delete_run(con, request.run_id, _LIFESPAN_RUN_TABLES)
        con.executemany(
            insert_values_sql("malf_lifespan_snapshot", 33),
            snapshots,
        )
        con.executemany(
            """
            insert into malf_lifespan_profile
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            profiles,
        )
        con.execute(
            "delete from malf_sample_version where sample_version = ?",
            [request.sample_version],
        )
        con.execute(
            "delete from malf_rule_version where lifespan_rule_version = ?",
            [request.lifespan_rule_version],
        )
        con.execute(
            "insert into malf_sample_version values (?, ?, ?, ?, ?, ?, ?)",
            [
                request.sample_version,
                "all_eligible_symbols",
                request.timeframe,
                "both",
                "all",
                "<= current bar_dt",
                now,
            ],
        )
        con.execute(
            "insert into malf_rule_version values (?, ?, ?, ?, ?)",
            [request.lifespan_rule_version, 0.25, 0.75, 0.75, now],
        )
        insert_lifespan_run(con, request, source_core_run_id, input_wave_count, now)
        con.execute("commit")

    summary = MalfBuildSummary(
        run_id=request.run_id,
        stage="lifespan",
        status="completed",
        input_wave_count=input_wave_count,
    )
    save_checkpoint(request.checkpoint_path("lifespan"), summary)
    return summary


def run_malf_day_service_build(request: MalfDayRequest) -> MalfBuildSummary:
    require_build_mode(request, "service")
    require(request.service_version, "service_version")
    checkpoint = load_completed_checkpoint(request, "service")
    if checkpoint:
        return checkpoint

    bootstrap_malf_service_day_database(request.service_db)
    source_core_run_id = latest_run_id(request.core_db, "malf_core_run")
    source_lifespan_run_id = latest_run_id(request.lifespan_db, "malf_lifespan_run")
    now = utc_now()
    rows, latest_rows = build_wave_position_rows(
        request.lifespan_db, source_core_run_id, source_lifespan_run_id, request, now
    )
    with duckdb.connect(str(request.service_db)) as con:
        con.execute("begin transaction")
        delete_run(con, request.run_id, _SERVICE_RUN_TABLES)
        con.executemany(
            insert_values_sql("malf_wave_position", 35),
            rows,
        )
        con.executemany(
            insert_values_sql("malf_wave_position_latest", 35),
            latest_rows,
        )
        insert_service_run(
            con,
            request,
            source_core_run_id,
            source_lifespan_run_id,
            len(rows),
            now,
        )
        con.execute("commit")

    summary = MalfBuildSummary(
        run_id=request.run_id,
        stage="service",
        status="completed",
        published_row_count=len(rows),
    )
    save_checkpoint(request.checkpoint_path("service"), summary)
    return summary


def run_malf_day_audit(request: MalfDayRequest) -> MalfBuildSummary:
    checkpoint = load_completed_checkpoint(request, "audit")
    if checkpoint:
        return checkpoint

    bootstrap_malf_service_day_database(request.service_db)
    now = utc_now()
    audit_rows, payload = build_audit_rows(
        request.core_db, request.lifespan_db, request.service_db, request, now
    )
    with duckdb.connect(str(request.service_db)) as con:
        con.execute("begin transaction")
        con.execute("delete from malf_interface_audit where run_id = ?", [request.run_id])
        con.executemany(
            "insert into malf_interface_audit values (?, ?, ?, ?, ?, ?, ?, ?)",
            audit_rows,
        )
        con.execute("commit")

    audit_report_path = report_path(request.report_root, request.run_id)
    audit_report_path.parent.mkdir(parents=True, exist_ok=True)
    audit_report_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary = MalfBuildSummary(
        run_id=request.run_id,
        stage="audit",
        status="completed",
        report_path=str(audit_report_path),
    )
    save_checkpoint(request.checkpoint_path("audit"), summary)
    return summary


_CORE_RUN_TABLES = (
    "malf_core_run",
    "malf_pivot_ledger",
    "malf_structure_ledger",
    "malf_wave_ledger",
    "malf_break_ledger",
    "malf_transition_ledger",
    "malf_candidate_ledger",
    "malf_core_state_snapshot",
)
_LIFESPAN_RUN_TABLES = (
    "malf_lifespan_run",
    "malf_lifespan_snapshot",
    "malf_lifespan_profile",
)
_SERVICE_RUN_TABLES = (
    "malf_service_run",
    "malf_wave_position",
    "malf_wave_position_latest",
    "malf_interface_audit",
)
