from __future__ import annotations

import json

import duckdb

from asteria.malf.audit_engine import build_audit_rows
from asteria.malf.bootstrap_support import (
    CORE_RUN_TABLES,
    LIFESPAN_RUN_TABLES,
    SERVICE_RUN_TABLES,
    count_market_base_rows,
    count_rows_for_run,
    delete_run,
    insert_core_run,
    insert_lifespan_run,
    insert_service_run,
    insert_values_sql,
    latest_run_id,
    load_completed_checkpoint,
    report_path,
    require_build_mode,
    require_value,
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
    require_value(request.core_rule_version, "core_rule_version")
    checkpoint = load_completed_checkpoint(request, "core")
    if checkpoint:
        return checkpoint

    input_row_count = count_market_base_rows(request)
    bootstrap_malf_core_day_database(request.core_db)
    now = utc_now()
    rows = build_core_rows(request, now)
    with duckdb.connect(str(request.core_db)) as con:
        con.execute("begin transaction")
        delete_run(con, request.run_id, CORE_RUN_TABLES)
        con.execute(
            "delete from malf_schema_version where schema_version = ?", [request.schema_version]
        )
        con.executemany(
            "insert into malf_pivot_ledger values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
        con.executemany(insert_values_sql("malf_structure_ledger", 14), rows.structures)
        con.executemany(
            insert_values_sql("malf_wave_ledger", 23),
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
        con.executemany(insert_values_sql("malf_break_ledger", 12), rows.breaks)
        con.executemany(
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
        con.executemany(
            insert_values_sql("malf_candidate_ledger", 18),
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
        con.executemany(insert_values_sql("malf_core_state_snapshot", 30), rows.snapshots)
        insert_core_run(con, request, input_row_count, now)
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
    require_value(request.lifespan_rule_version, "lifespan_rule_version")
    require_value(request.sample_version, "sample_version")
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
        delete_run(con, request.run_id, LIFESPAN_RUN_TABLES)
        con.executemany(insert_values_sql("malf_lifespan_snapshot", 33), snapshots)
        con.executemany(insert_values_sql("malf_lifespan_profile", 15), profiles)
        con.execute(
            "delete from malf_sample_version where sample_version = ?", [request.sample_version]
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
    require_value(request.service_version, "service_version")
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
        delete_run(con, request.run_id, SERVICE_RUN_TABLES)
        con.executemany(insert_values_sql("malf_wave_position", 35), rows)
        con.executemany(insert_values_sql("malf_wave_position_latest", 35), latest_rows)
        insert_service_run(con, request, source_core_run_id, source_lifespan_run_id, len(rows), now)
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
            "insert into malf_interface_audit values (?, ?, ?, ?, ?, ?, ?, ?)", audit_rows
        )
        con.execute("commit")

    output_path = report_path(request.report_root, request.run_id)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = MalfBuildSummary(
        run_id=request.run_id,
        stage="audit",
        status="completed",
        report_path=str(output_path),
    )
    save_checkpoint(request.checkpoint_path("audit"), summary)
    return summary
