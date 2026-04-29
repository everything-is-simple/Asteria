from __future__ import annotations

from pathlib import Path

import duckdb

ALPHA_TABLES = (
    "alpha_family_run",
    "alpha_schema_version",
    "alpha_rule_version",
    "alpha_event_ledger",
    "alpha_score_ledger",
    "alpha_signal_candidate",
    "alpha_source_audit",
)


def bootstrap_alpha_family_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table if not exists alpha_family_run (
                run_id varchar,
                runner_name varchar,
                mode varchar,
                timeframe varchar,
                alpha_family varchar,
                status varchar,
                source_malf_db varchar,
                input_row_count bigint,
                event_count bigint,
                score_count bigint,
                candidate_count bigint,
                schema_version varchar,
                alpha_rule_version varchar,
                source_malf_service_version varchar,
                source_malf_run_id varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists alpha_schema_version (
                schema_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists alpha_rule_version (
                alpha_family varchar,
                alpha_rule_version varchar,
                rule_scope varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists alpha_event_ledger (
                alpha_event_id varchar,
                alpha_family varchar,
                symbol varchar,
                timeframe varchar,
                bar_dt date,
                event_type varchar,
                opportunity_state varchar,
                source_wave_position_key varchar,
                source_malf_service_version varchar,
                source_malf_run_id varchar,
                run_id varchar,
                schema_version varchar,
                alpha_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists alpha_score_ledger (
                alpha_score_id varchar,
                alpha_event_id varchar,
                alpha_family varchar,
                score_name varchar,
                score_value double,
                score_direction varchar,
                score_bucket varchar,
                source_malf_service_version varchar,
                source_malf_run_id varchar,
                run_id varchar,
                schema_version varchar,
                alpha_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists alpha_signal_candidate (
                alpha_candidate_id varchar,
                alpha_event_id varchar,
                alpha_family varchar,
                symbol varchar,
                timeframe varchar,
                bar_dt date,
                candidate_type varchar,
                candidate_state varchar,
                opportunity_bias varchar,
                confidence_bucket varchar,
                reason_code varchar,
                candidate_score double,
                source_malf_service_version varchar,
                source_malf_run_id varchar,
                run_id varchar,
                schema_version varchar,
                alpha_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists alpha_source_audit (
                audit_id varchar,
                run_id varchar,
                alpha_family varchar,
                check_name varchar,
                severity varchar,
                status varchar,
                failed_count bigint,
                sample_payload varchar,
                created_at timestamp
            )
            """
        )
