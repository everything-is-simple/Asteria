from __future__ import annotations

import json
from pathlib import Path

import duckdb
from tests.unit.malf.test_v14_runtime_sync_code import (
    _request_v14,
    _seed_market_base_day,
)

from asteria.malf.bootstrap import (
    run_malf_day_audit,
    run_malf_day_core_build,
    run_malf_day_lifespan_build,
    run_malf_day_service_build,
)
from asteria.malf.schema import (
    bootstrap_malf_core_day_database,
    bootstrap_malf_lifespan_day_database,
    bootstrap_malf_service_day_database,
)


def test_malf_v14_runner_handles_legacy_promoted_day_tables(tmp_path: Path) -> None:
    _seed_market_base_day(
        tmp_path / "asteria-data" / "market_base_day.duckdb",
        symbols=("UPCASE.SH", "REPLACE.SH"),
    )
    request = _request_v14(tmp_path, "malf-v14-legacy-promoted-run-001")

    _create_legacy_promoted_core_day_tables(request.core_db)
    _create_legacy_promoted_lifespan_day_tables(request.lifespan_db)
    _create_legacy_promoted_service_day_tables(request.service_db)

    bootstrap_malf_core_day_database(request.core_db)
    bootstrap_malf_lifespan_day_database(request.lifespan_db)
    bootstrap_malf_service_day_database(request.service_db)

    run_malf_day_core_build(request)
    run_malf_day_lifespan_build(request)
    run_malf_day_service_build(request)
    audit_summary = run_malf_day_audit(request)

    with duckdb.connect(str(request.core_db), read_only=True) as con:
        core_pivot_row = con.execute(
            """
            select pivot_detection_rule_version, created_at
            from malf_pivot_ledger
            where run_id = ?
            limit 1
            """,
            [request.run_id],
        ).fetchone()
        assert core_pivot_row is not None
        assert core_pivot_row[0] == request.pivot_detection_rule_version
        assert core_pivot_row[1] is not None

        core_run_row = con.execute(
            """
            select pivot_detection_rule_version, core_event_ordering_version,
                   price_compare_policy, epsilon_policy, created_at
            from malf_core_run
            where run_id = ?
            """,
            [request.run_id],
        ).fetchone()
        assert core_run_row is not None
        assert core_run_row[:4] == (
            request.pivot_detection_rule_version,
            request.core_event_ordering_version,
            request.price_compare_policy,
            request.epsilon_policy,
        )
        assert core_run_row[4] is not None

    with duckdb.connect(str(request.lifespan_db), read_only=True) as con:
        lifespan_run_row = con.execute(
            """
            select pivot_detection_rule_version, core_event_ordering_version,
                   price_compare_policy, epsilon_policy, created_at
            from malf_lifespan_run
            where run_id = ?
            """,
            [request.run_id],
        ).fetchone()
        assert lifespan_run_row is not None
        assert lifespan_run_row[:4] == (
            request.pivot_detection_rule_version,
            request.core_event_ordering_version,
            request.price_compare_policy,
            request.epsilon_policy,
        )
        assert lifespan_run_row[4] is not None

    with duckdb.connect(str(request.service_db), read_only=True) as con:
        service_run_row = con.execute(
            """
            select pivot_detection_rule_version, core_event_ordering_version,
                   price_compare_policy, epsilon_policy, created_at
            from malf_service_run
            where run_id = ?
            """,
            [request.run_id],
        ).fetchone()
        assert service_run_row is not None
        assert service_run_row[:4] == (
            request.pivot_detection_rule_version,
            request.core_event_ordering_version,
            request.price_compare_policy,
            request.epsilon_policy,
        )
        assert service_run_row[4] is not None

        audit_count_row = con.execute(
            "select count(*) from malf_interface_audit where run_id = ?",
            [request.run_id],
        ).fetchone()
        assert audit_count_row is not None
        assert audit_count_row[0] > 0

        failed_audit_row = con.execute(
            """
            select count(*)
            from malf_interface_audit
            where run_id = ? and status <> 'pass'
            """,
            [request.run_id],
        ).fetchone()
        assert failed_audit_row == (0,)

    payload = json.loads(Path(audit_summary.report_path).read_text(encoding="utf-8"))
    assert payload["pivot_detection_rule_version"] == request.pivot_detection_rule_version
    assert payload["core_event_ordering_version"] == request.core_event_ordering_version
    assert payload["price_compare_policy"] == request.price_compare_policy
    assert payload["epsilon_policy"] == request.epsilon_policy


def _create_legacy_promoted_core_day_tables(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table malf_core_run (
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
            create table malf_schema_version (
                schema_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table malf_pivot_ledger (
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
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table malf_structure_ledger (
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
            create table malf_wave_ledger (
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
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table malf_break_ledger (
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
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table malf_transition_ledger (
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
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table malf_candidate_ledger (
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
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table malf_core_state_snapshot (
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
                run_id varchar,
                schema_version varchar,
                core_rule_version varchar,
                created_at timestamp
            )
            """
        )


def _create_legacy_promoted_lifespan_day_tables(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table malf_lifespan_run (
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
            create table malf_lifespan_snapshot (
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
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table malf_lifespan_profile (
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
            create table malf_sample_version (
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
            create table malf_rule_version (
                lifespan_rule_version varchar,
                low_update_threshold double,
                high_update_threshold double,
                high_stagnation_threshold double,
                created_at timestamp
            )
            """
        )


def _create_legacy_promoted_service_day_tables(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table malf_service_run (
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
            created_at timestamp
        """
        con.execute(f"create table malf_wave_position ({wave_position_columns})")
        con.execute(f"create table malf_wave_position_latest ({wave_position_columns})")
        con.execute(
            """
            create table malf_interface_audit (
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
