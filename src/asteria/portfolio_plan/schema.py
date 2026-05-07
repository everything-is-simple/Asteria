from __future__ import annotations

from pathlib import Path

import duckdb

PORTFOLIO_PLAN_TABLES = (
    "portfolio_plan_run",
    "portfolio_plan_schema_version",
    "portfolio_plan_rule_version",
    "portfolio_position_snapshot",
    "portfolio_constraint_ledger",
    "portfolio_admission_ledger",
    "portfolio_target_exposure",
    "portfolio_trim_ledger",
    "portfolio_plan_audit",
)


def bootstrap_portfolio_plan_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table if not exists portfolio_plan_run (
                run_id varchar,
                runner_name varchar,
                mode varchar,
                timeframe varchar,
                status varchar,
                source_position_db varchar,
                input_position_count bigint,
                admission_count bigint,
                target_exposure_count bigint,
                trim_count bigint,
                hard_fail_count bigint,
                schema_version varchar,
                portfolio_plan_rule_version varchar,
                source_position_release_version varchar,
                source_position_run_id varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists portfolio_plan_schema_version (
                schema_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists portfolio_plan_rule_version (
                portfolio_plan_rule_version varchar,
                rule_scope varchar,
                max_active_symbols bigint,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists portfolio_position_snapshot (
                portfolio_position_snapshot_id varchar,
                portfolio_run_id varchar,
                position_candidate_id varchar,
                symbol varchar,
                timeframe varchar,
                candidate_dt date,
                candidate_state varchar,
                position_bias varchar,
                entry_plan_id varchar,
                exit_plan_id varchar,
                position_rule_version varchar,
                source_position_release_version varchar,
                source_position_run_id varchar,
                schema_version varchar,
                portfolio_plan_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists portfolio_constraint_ledger (
                constraint_id varchar,
                constraint_scope varchar,
                constraint_name varchar,
                constraint_type varchar,
                constraint_value double,
                constraint_state varchar,
                run_id varchar,
                schema_version varchar,
                portfolio_plan_rule_version varchar,
                source_position_release_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists portfolio_admission_ledger (
                portfolio_admission_id varchar,
                position_candidate_id varchar,
                symbol varchar,
                timeframe varchar,
                plan_dt date,
                admission_state varchar,
                admission_reason varchar,
                source_position_release_version varchar,
                run_id varchar,
                schema_version varchar,
                portfolio_plan_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists portfolio_target_exposure (
                target_exposure_id varchar,
                portfolio_admission_id varchar,
                exposure_type varchar,
                target_weight double,
                target_notional double,
                target_quantity_hint double,
                exposure_valid_from date,
                exposure_valid_until date,
                run_id varchar,
                schema_version varchar,
                portfolio_plan_rule_version varchar,
                source_position_release_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists portfolio_trim_ledger (
                portfolio_trim_id varchar,
                portfolio_admission_id varchar,
                trim_reason varchar,
                pre_trim_exposure double,
                post_trim_exposure double,
                constraint_name varchar,
                run_id varchar,
                schema_version varchar,
                portfolio_plan_rule_version varchar,
                source_position_release_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists portfolio_plan_audit (
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
