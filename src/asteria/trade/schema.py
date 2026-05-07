from __future__ import annotations

from pathlib import Path

import duckdb

TRADE_TABLES = (
    "trade_run",
    "trade_schema_version",
    "trade_rule_version",
    "trade_portfolio_snapshot",
    "order_intent_ledger",
    "execution_plan_ledger",
    "fill_ledger",
    "order_rejection_ledger",
    "trade_audit",
)


def bootstrap_trade_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table if not exists trade_run (
                run_id varchar,
                runner_name varchar,
                mode varchar,
                timeframe varchar,
                status varchar,
                source_portfolio_plan_db varchar,
                input_portfolio_plan_count bigint,
                order_intent_count bigint,
                execution_plan_count bigint,
                fill_count bigint,
                rejection_count bigint,
                hard_fail_count bigint,
                schema_version varchar,
                trade_rule_version varchar,
                source_portfolio_plan_release_version varchar,
                source_portfolio_plan_run_id varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists trade_schema_version (
                schema_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists trade_rule_version (
                trade_rule_version varchar,
                rule_scope varchar,
                fill_policy varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists trade_portfolio_snapshot (
                trade_portfolio_snapshot_id varchar,
                trade_run_id varchar,
                portfolio_admission_id varchar,
                position_candidate_id varchar,
                symbol varchar,
                timeframe varchar,
                plan_dt date,
                admission_state varchar,
                admission_reason varchar,
                target_exposure_id varchar,
                exposure_type varchar,
                target_weight double,
                target_notional double,
                target_quantity_hint double,
                portfolio_plan_rule_version varchar,
                source_position_release_version varchar,
                source_portfolio_plan_release_version varchar,
                run_id varchar,
                schema_version varchar,
                trade_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists order_intent_ledger (
                order_intent_id varchar,
                trade_run_id varchar,
                portfolio_admission_id varchar,
                position_candidate_id varchar,
                symbol varchar,
                timeframe varchar,
                intent_dt date,
                order_side varchar,
                order_intent_state varchar,
                target_quantity_hint double,
                target_weight double,
                target_notional double,
                source_position_release_version varchar,
                source_portfolio_plan_release_version varchar,
                run_id varchar,
                schema_version varchar,
                trade_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists execution_plan_ledger (
                execution_plan_id varchar,
                trade_run_id varchar,
                order_intent_id varchar,
                execution_plan_type varchar,
                execution_price_line varchar,
                execution_valid_from date,
                execution_valid_until date,
                execution_state varchar,
                source_portfolio_plan_release_version varchar,
                run_id varchar,
                schema_version varchar,
                trade_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists fill_ledger (
                fill_id varchar,
                trade_run_id varchar,
                order_intent_id varchar,
                execution_plan_id varchar,
                execution_dt date,
                fill_seq bigint,
                fill_price double,
                fill_quantity double,
                fill_amount double,
                source_portfolio_plan_release_version varchar,
                run_id varchar,
                schema_version varchar,
                trade_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists order_rejection_ledger (
                order_rejection_id varchar,
                trade_run_id varchar,
                order_intent_id varchar,
                rejection_dt date,
                rejection_reason varchar,
                rejection_stage varchar,
                source_portfolio_plan_release_version varchar,
                run_id varchar,
                schema_version varchar,
                trade_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists trade_audit (
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
