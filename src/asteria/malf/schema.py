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
                pivot_detection_rule_version varchar,
                core_event_ordering_version varchar,
                price_compare_policy varchar,
                epsilon_policy varchar,
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
                confirmed_dt date,
                pivot_type varchar,
                pivot_price double,
                pivot_seq_in_bar bigint,
                source_bar_dt date,
                run_id varchar,
                schema_version varchar,
                core_rule_version varchar,
                pivot_detection_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_structure_ledger (
                primitive_id varchar,
                pivot_id varchar,
                structure_context varchar,
                reference_pivot_id varchar,
                reference_price double,
                primitive varchar,
                direction_context varchar,
                symbol varchar,
                timeframe varchar,
                pivot_dt date,
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
                birth_type varchar,
                start_pivot_id varchar,
                candidate_guard_pivot_id varchar,
                confirm_pivot_id varchar,
                confirm_dt date,
                wave_core_state varchar,
                terminated_dt date,
                terminated_by_break_id varchar,
                final_progress_extreme_pivot_id varchar,
                final_progress_extreme_price double,
                final_guard_pivot_id varchar,
                final_guard_price double,
                run_id varchar,
                schema_version varchar,
                core_rule_version varchar,
                created_at timestamp,
                current_effective_guard_pivot_id varchar,
                current_effective_guard_price double
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_break_ledger (
                break_id varchar,
                wave_id varchar,
                direction varchar,
                guard_pivot_id varchar,
                break_dt date,
                break_price double,
                system_state_after varchar,
                run_id varchar,
                schema_version varchar,
                core_rule_version varchar,
                created_at timestamp,
                broken_guard_pivot_id varchar
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_transition_ledger (
                transition_id varchar,
                old_wave_id varchar,
                break_id varchar,
                old_direction varchar,
                old_progress_extreme_pivot_id varchar,
                old_progress_extreme_price double,
                break_dt date,
                state varchar,
                confirmed_dt date,
                new_wave_id varchar,
                run_id varchar,
                schema_version varchar,
                core_rule_version varchar,
                created_at timestamp,
                broken_guard_pivot_id varchar,
                transition_boundary_high double,
                transition_boundary_low double
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
                candidate_dt date,
                is_active_at_close boolean,
                invalidated_by_candidate_id varchar,
                reference_progress_extreme_price double,
                confirmed_by_pivot_id varchar,
                confirmed_wave_id varchar,
                run_id varchar,
                schema_version varchar,
                core_rule_version varchar,
                created_at timestamp,
                candidate_status varchar,
                confirmation_pivot_id varchar,
                new_wave_id varchar,
                candidate_event_type varchar
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_core_state_snapshot (
                snapshot_id varchar,
                symbol varchar,
                timeframe varchar,
                bar_dt date,
                system_state varchar,
                wave_id varchar,
                old_wave_id varchar,
                wave_core_state varchar,
                direction varchar,
                progress_updated boolean,
                transition_span bigint,
                guard_boundary_price double,
                current_effective_guard_pivot_id varchar,
                current_effective_guard_price double,
                transition_id varchar,
                break_id varchar,
                transition_boundary_high double,
                transition_boundary_low double,
                active_candidate_id varchar,
                active_candidate_guard_pivot_id varchar,
                confirmation_pivot_id varchar,
                new_wave_id varchar,
                run_id varchar,
                schema_version varchar,
                core_rule_version varchar,
                pivot_detection_rule_version varchar,
                core_event_ordering_version varchar,
                price_compare_policy varchar,
                epsilon_policy varchar,
                created_at timestamp
            )
            """
        )
        _ensure_columns(
            con,
            "malf_core_run",
            [
                ("pivot_detection_rule_version", "varchar"),
                ("core_event_ordering_version", "varchar"),
                ("price_compare_policy", "varchar"),
                ("epsilon_policy", "varchar"),
            ],
        )
        _ensure_columns(
            con,
            "malf_pivot_ledger",
            [("pivot_detection_rule_version", "varchar")],
        )
        _ensure_columns(
            con,
            "malf_wave_ledger",
            [
                ("current_effective_guard_pivot_id", "varchar"),
                ("current_effective_guard_price", "double"),
            ],
        )
        _ensure_columns(con, "malf_break_ledger", [("broken_guard_pivot_id", "varchar")])
        _ensure_columns(
            con,
            "malf_transition_ledger",
            [
                ("broken_guard_pivot_id", "varchar"),
                ("transition_boundary_high", "double"),
                ("transition_boundary_low", "double"),
            ],
        )
        _ensure_columns(
            con,
            "malf_candidate_ledger",
            [
                ("candidate_status", "varchar"),
                ("confirmation_pivot_id", "varchar"),
                ("new_wave_id", "varchar"),
                ("candidate_event_type", "varchar"),
            ],
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
                pivot_detection_rule_version varchar,
                core_event_ordering_version varchar,
                price_compare_policy varchar,
                epsilon_policy varchar,
                created_at timestamp
            )
            """
        )
        _ensure_columns(
            con,
            "malf_lifespan_run",
            [
                ("pivot_detection_rule_version", "varchar"),
                ("core_event_ordering_version", "varchar"),
                ("price_compare_policy", "varchar"),
                ("epsilon_policy", "varchar"),
            ],
        )
        con.execute(
            """
            create table if not exists malf_lifespan_snapshot (
                snapshot_id varchar,
                wave_id varchar,
                old_wave_id varchar,
                symbol varchar,
                timeframe varchar,
                bar_dt date,
                wave_core_state varchar,
                system_state varchar,
                direction varchar,
                progress_updated boolean,
                new_count bigint,
                no_new_span bigint,
                transition_span bigint,
                life_state varchar,
                position_quadrant varchar,
                update_rank double,
                stagnation_rank double,
                guard_boundary_price double,
                run_id varchar,
                schema_version varchar,
                lifespan_rule_version varchar,
                sample_version varchar,
                created_at timestamp,
                transition_boundary_high double,
                transition_boundary_low double,
                active_candidate_guard_pivot_id varchar,
                confirmation_pivot_id varchar,
                new_wave_id varchar,
                birth_type varchar,
                candidate_wait_span bigint,
                candidate_replacement_count bigint,
                confirmation_distance_abs double,
                confirmation_distance_pct double
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
                sample_cutoff date,
                sample_size bigint,
                p25 double,
                p50 double,
                p75 double,
                p90 double,
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
                universe varchar,
                timeframe varchar,
                direction varchar,
                birth_type varchar,
                sample_cutoff_rule varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists malf_rule_version (
                lifespan_rule_version varchar,
                low_update_threshold double,
                high_update_threshold double,
                high_stagnation_threshold double,
                created_at timestamp
            )
            """
        )
        _ensure_columns(
            con,
            "malf_lifespan_snapshot",
            _V13_TRACE_COLUMNS,
        )


def bootstrap_malf_service_day_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wave_position_columns = """
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
        created_at timestamp,
        transition_boundary_high double,
        transition_boundary_low double,
        active_candidate_guard_pivot_id varchar,
        confirmation_pivot_id varchar,
        new_wave_id varchar,
        birth_type varchar,
        candidate_wait_span bigint,
        candidate_replacement_count bigint,
        confirmation_distance_abs double,
        confirmation_distance_pct double
    """
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
                pivot_detection_rule_version varchar,
                core_event_ordering_version varchar,
                price_compare_policy varchar,
                epsilon_policy varchar,
                created_at timestamp
            )
            """
        )
        _ensure_columns(
            con,
            "malf_service_run",
            [
                ("pivot_detection_rule_version", "varchar"),
                ("core_event_ordering_version", "varchar"),
                ("price_compare_policy", "varchar"),
                ("epsilon_policy", "varchar"),
            ],
        )
        con.execute(f"create table if not exists malf_wave_position ({wave_position_columns})")
        con.execute(
            f"create table if not exists malf_wave_position_latest ({wave_position_columns})"
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
        _ensure_columns(con, "malf_wave_position", _V13_TRACE_COLUMNS)
        _ensure_columns(con, "malf_wave_position_latest", _V13_TRACE_COLUMNS)


_V13_TRACE_COLUMNS = [
    ("transition_boundary_high", "double"),
    ("transition_boundary_low", "double"),
    ("active_candidate_guard_pivot_id", "varchar"),
    ("confirmation_pivot_id", "varchar"),
    ("new_wave_id", "varchar"),
    ("birth_type", "varchar"),
    ("candidate_wait_span", "bigint"),
    ("candidate_replacement_count", "bigint"),
    ("confirmation_distance_abs", "double"),
    ("confirmation_distance_pct", "double"),
]


def _ensure_columns(
    con: duckdb.DuckDBPyConnection, table_name: str, columns: list[tuple[str, str]]
) -> None:
    for column_name, column_type in columns:
        con.execute(
            f"alter table {table_name} add column if not exists {column_name} {column_type}"
        )
