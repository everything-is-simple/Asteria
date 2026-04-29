from __future__ import annotations

from pathlib import Path

import duckdb

SIGNAL_TABLES = (
    "signal_run",
    "signal_schema_version",
    "signal_rule_version",
    "signal_input_snapshot",
    "formal_signal_ledger",
    "signal_component_ledger",
    "signal_audit",
)


def bootstrap_signal_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table if not exists signal_run (
                run_id varchar,
                runner_name varchar,
                mode varchar,
                timeframe varchar,
                status varchar,
                source_alpha_root varchar,
                input_candidate_count bigint,
                formal_signal_count bigint,
                component_count bigint,
                hard_fail_count bigint,
                schema_version varchar,
                signal_rule_version varchar,
                source_alpha_release_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists signal_schema_version (
                schema_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists signal_rule_version (
                signal_rule_version varchar,
                rule_scope varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists signal_input_snapshot (
                signal_input_snapshot_id varchar,
                signal_run_id varchar,
                alpha_family varchar,
                alpha_candidate_id varchar,
                alpha_event_id varchar,
                symbol varchar,
                timeframe varchar,
                bar_dt date,
                candidate_type varchar,
                candidate_state varchar,
                opportunity_bias varchar,
                confidence_bucket varchar,
                reason_code varchar,
                candidate_score double,
                alpha_rule_version varchar,
                source_malf_service_version varchar,
                source_alpha_release_version varchar,
                schema_version varchar,
                signal_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists formal_signal_ledger (
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
                support_count bigint,
                conflict_count bigint,
                rejected_component_count bigint,
                source_alpha_release_version varchar,
                run_id varchar,
                schema_version varchar,
                signal_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists signal_component_ledger (
                signal_component_id varchar,
                signal_id varchar,
                signal_run_id varchar,
                alpha_family varchar,
                alpha_candidate_id varchar,
                component_role varchar,
                component_weight double,
                alpha_rule_version varchar,
                signal_rule_version varchar,
                source_alpha_release_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists signal_audit (
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
