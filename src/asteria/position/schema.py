from __future__ import annotations

from pathlib import Path

import duckdb

POSITION_TABLES = (
    "position_run",
    "position_schema_version",
    "position_rule_version",
    "position_signal_snapshot",
    "position_candidate_ledger",
    "position_entry_plan",
    "position_exit_plan",
    "position_audit",
)


def bootstrap_position_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table if not exists position_run (
                run_id varchar,
                runner_name varchar,
                mode varchar,
                timeframe varchar,
                status varchar,
                source_signal_db varchar,
                input_signal_count bigint,
                position_candidate_count bigint,
                entry_plan_count bigint,
                exit_plan_count bigint,
                hard_fail_count bigint,
                schema_version varchar,
                position_rule_version varchar,
                source_signal_release_version varchar,
                source_signal_run_id varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists position_schema_version (
                schema_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists position_rule_version (
                position_rule_version varchar,
                rule_scope varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists position_signal_snapshot (
                position_signal_snapshot_id varchar,
                position_run_id varchar,
                signal_id varchar,
                symbol varchar,
                timeframe varchar,
                signal_dt date,
                signal_type varchar,
                signal_state varchar,
                signal_bias varchar,
                signal_strength double,
                confidence_bucket varchar,
                reason_code varchar,
                signal_rule_version varchar,
                source_signal_release_version varchar,
                source_signal_run_id varchar,
                schema_version varchar,
                position_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists position_candidate_ledger (
                position_candidate_id varchar,
                signal_id varchar,
                symbol varchar,
                timeframe varchar,
                candidate_dt date,
                candidate_type varchar,
                candidate_state varchar,
                position_bias varchar,
                reason_code varchar,
                source_signal_release_version varchar,
                run_id varchar,
                schema_version varchar,
                position_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists position_entry_plan (
                entry_plan_id varchar,
                position_candidate_id varchar,
                entry_plan_type varchar,
                entry_trigger_type varchar,
                entry_reference_dt date,
                entry_valid_from date,
                entry_valid_until date,
                entry_state varchar,
                run_id varchar,
                schema_version varchar,
                position_rule_version varchar,
                source_signal_release_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists position_exit_plan (
                exit_plan_id varchar,
                position_candidate_id varchar,
                exit_plan_type varchar,
                exit_trigger_type varchar,
                exit_reference_dt date,
                exit_valid_from date,
                exit_valid_until date,
                exit_state varchar,
                run_id varchar,
                schema_version varchar,
                position_rule_version varchar,
                source_signal_release_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists position_audit (
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
