from __future__ import annotations

from pathlib import Path

import duckdb


def bootstrap_malf_core_day_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table if not exists malf_core_run (
                run_id varchar,
                runner_name varchar,
                mode varchar,
                timeframe varchar,
                status varchar,
                source_db varchar,
                input_row_count bigint,
                schema_version varchar,
                core_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_schema_version (
                schema_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_pivot_ledger (
                pivot_id varchar,
                symbol varchar,
                timeframe varchar,
                pivot_dt date,
                pivot_type varchar,
                pivot_seq_in_bar bigint,
                run_id varchar,
                schema_version varchar,
                core_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_structure_ledger (
                structure_id varchar,
                pivot_id varchar,
                structure_context varchar,
                reference_pivot_id varchar,
                run_id varchar,
                schema_version varchar,
                core_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_wave_ledger (
                wave_id varchar,
                symbol varchar,
                timeframe varchar,
                wave_seq bigint,
                direction varchar,
                run_id varchar,
                schema_version varchar,
                core_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_break_ledger (
                break_id varchar,
                wave_id varchar,
                break_dt date,
                guard_pivot_id varchar,
                run_id varchar,
                schema_version varchar,
                core_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_transition_ledger (
                transition_id varchar,
                old_wave_id varchar,
                break_id varchar,
                transition_dt date,
                run_id varchar,
                schema_version varchar,
                core_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_candidate_ledger (
                candidate_id varchar,
                transition_id varchar,
                candidate_guard_pivot_id varchar,
                candidate_direction varchar,
                run_id varchar,
                schema_version varchar,
                core_rule_version varchar,
                created_at timestamp
            )
            """
        )


def bootstrap_malf_lifespan_day_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table if not exists malf_lifespan_run (
                run_id varchar,
                runner_name varchar,
                mode varchar,
                timeframe varchar,
                status varchar,
                source_core_run_id varchar,
                input_wave_count bigint,
                schema_version varchar,
                lifespan_rule_version varchar,
                sample_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_lifespan_snapshot (
                snapshot_id varchar,
                wave_id varchar,
                bar_dt date,
                new_count bigint,
                no_new_span bigint,
                transition_span bigint,
                life_state varchar,
                position_quadrant varchar,
                update_rank double,
                stagnation_rank double,
                run_id varchar,
                schema_version varchar,
                lifespan_rule_version varchar,
                sample_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_lifespan_profile (
                profile_id varchar,
                timeframe varchar,
                direction varchar,
                sample_version varchar,
                metric_name varchar,
                sample_cutoff varchar,
                metric_value double,
                run_id varchar,
                schema_version varchar,
                lifespan_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_sample_version (
                sample_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_rule_version (
                lifespan_rule_version varchar,
                created_at timestamp
            )
            """
        )


def bootstrap_malf_service_day_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table if not exists malf_service_run (
                run_id varchar,
                runner_name varchar,
                mode varchar,
                timeframe varchar,
                status varchar,
                source_core_run_id varchar,
                source_lifespan_run_id varchar,
                published_row_count bigint,
                schema_version varchar,
                service_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_wave_position (
                symbol varchar,
                timeframe varchar,
                bar_dt date,
                system_state varchar,
                wave_id varchar,
                old_wave_id varchar,
                wave_core_state varchar,
                direction varchar,
                new_count bigint,
                no_new_span bigint,
                transition_span bigint,
                update_rank double,
                stagnation_rank double,
                life_state varchar,
                position_quadrant varchar,
                guard_boundary_price double,
                sample_scope varchar,
                sample_version varchar,
                lifespan_rule_version varchar,
                service_version varchar,
                run_id varchar,
                schema_version varchar,
                source_core_run_id varchar,
                source_lifespan_run_id varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_wave_position_latest (
                symbol varchar,
                timeframe varchar,
                service_version varchar,
                latest_bar_dt date,
                run_id varchar,
                schema_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_interface_audit (
                audit_id varchar,
                run_id varchar,
                check_name varchar,
                severity varchar,
                status varchar,
                failed_count bigint,
                sample_payload varchar,
                created_at timestamp
            )
            """
        )
