from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb
from tests.unit.system_readout.support_upstream import (
    PORTFOLIO_RUN_ID,
    POSITION_RUN_ID,
    SIGNAL_RUN_ID,
    TRADE_RUN_ID,
)


def seed_position_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table position_run (
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
            create table position_audit (
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
        con.execute(
            """
            create table position_candidate_ledger (
                position_candidate_id varchar,
                signal_id varchar,
                symbol varchar,
                timeframe varchar,
                candidate_dt date,
                candidate_type varchar,
                candidate_state varchar,
                position_bias varchar,
                source_signal_release_version varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            create table position_entry_plan (
                entry_plan_id varchar,
                position_candidate_id varchar,
                entry_plan_type varchar,
                entry_trigger_type varchar,
                entry_reference_dt date,
                entry_valid_from date,
                entry_valid_until date,
                entry_state varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            create table position_exit_plan (
                exit_plan_id varchar,
                position_candidate_id varchar,
                exit_plan_type varchar,
                exit_trigger_type varchar,
                exit_reference_dt date,
                exit_valid_from date,
                exit_valid_until date,
                exit_state varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            insert into position_run
            values (?, 'position_build', 'bounded', 'day', 'completed',
                    'H:\\Asteria-data\\signal.duckdb', 2, 2, 2, 2, 0,
                    'position-bounded-proof-v1', 'position-signal-plan-minimal-v1',
                    ?, ?, now())
            """,
            [POSITION_RUN_ID, SIGNAL_RUN_ID, SIGNAL_RUN_ID],
        )
        con.execute(
            """
            insert into position_audit
            values ('position-unit|audit', ?, 'unit_seed_ok', 'hard', 'pass', 0, '{}', now())
            """,
            [POSITION_RUN_ID],
        )
        candidates = [
            ("pc-600000", "sig-600000", "600000.SH", date(2024, 1, 2)),
            ("pc-600001", "sig-600001", "600001.SH", date(2024, 1, 3)),
        ]
        con.executemany(
            """
            insert into position_candidate_ledger
            values (?, ?, ?, 'day', ?, 'directional_position_candidate', 'planned',
                    'long_candidate', ?, ?)
            """,
            [
                (candidate_id, signal_id, symbol, bar_dt, SIGNAL_RUN_ID, POSITION_RUN_ID)
                for candidate_id, signal_id, symbol, bar_dt in candidates
            ],
        )
        con.executemany(
            """
            insert into position_entry_plan
            values (?, ?, 'signal_follow_entry', 'next_session_open_plan', ?, ?, null, 'planned', ?)
            """,
            [
                (f"entry-{candidate_id}", candidate_id, bar_dt, bar_dt, POSITION_RUN_ID)
                for candidate_id, _, _, bar_dt in candidates
            ],
        )
        con.executemany(
            """
            insert into position_exit_plan
            values (
                ?, ?, 'signal_invalidation_exit', 'signal_invalidated_or_expired',
                ?, ?, null, 'planned', ?
            )
            """,
            [
                (f"exit-{candidate_id}", candidate_id, bar_dt, bar_dt, POSITION_RUN_ID)
                for candidate_id, _, _, bar_dt in candidates
            ],
        )


def seed_portfolio_plan_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table portfolio_plan_run (
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
            create table portfolio_plan_audit (
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
        con.execute(
            """
            create table portfolio_admission_ledger (
                portfolio_admission_id varchar,
                position_candidate_id varchar,
                symbol varchar,
                timeframe varchar,
                plan_dt date,
                admission_state varchar,
                admission_reason varchar,
                source_position_release_version varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            create table portfolio_target_exposure (
                target_exposure_id varchar,
                portfolio_admission_id varchar,
                exposure_type varchar,
                target_weight double,
                target_notional double,
                target_quantity_hint double,
                exposure_valid_from date,
                exposure_valid_until date,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            create table portfolio_trim_ledger (
                portfolio_trim_id varchar,
                portfolio_admission_id varchar,
                trim_reason varchar,
                pre_trim_exposure double,
                post_trim_exposure double,
                constraint_name varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            insert into portfolio_plan_run
            values (?, 'portfolio_plan_build', 'bounded', 'day', 'completed',
                    'H:\\Asteria-data\\position.duckdb', 2, 2, 2, 0, 0,
                    'portfolio-plan-bounded-proof-v1', 'portfolio-position-capacity-minimal-v1',
                    ?, ?, now())
            """,
            [PORTFOLIO_RUN_ID, POSITION_RUN_ID, POSITION_RUN_ID],
        )
        con.execute(
            """
            insert into portfolio_plan_audit
            values ('portfolio-unit|audit', ?, 'unit_seed_ok', 'hard', 'pass', 0, '{}', now())
            """,
            [PORTFOLIO_RUN_ID],
        )
        admissions = [
            ("adm-600000", "pc-600000", "600000.SH", date(2024, 1, 2), "admitted"),
            ("adm-600001", "pc-600001", "600001.SH", date(2024, 1, 3), "admitted"),
        ]
        con.executemany(
            """
            insert into portfolio_admission_ledger
            values (?, ?, ?, 'day', ?, ?, 'within_capacity_constraint', ?, ?)
            """,
            [
                (
                    admission_id,
                    candidate_id,
                    symbol,
                    plan_dt,
                    state,
                    POSITION_RUN_ID,
                    PORTFOLIO_RUN_ID,
                )
                for admission_id, candidate_id, symbol, plan_dt, state in admissions
            ],
        )
        con.executemany(
            """
            insert into portfolio_target_exposure
            values (?, ?, 'target_weight', ?, ?, ?, ?, null, ?)
            """,
            [
                (
                    "exp-600000",
                    "adm-600000",
                    0.25,
                    100000.0,
                    100.0,
                    date(2024, 1, 2),
                    PORTFOLIO_RUN_ID,
                ),
                (
                    "exp-600001",
                    "adm-600001",
                    0.20,
                    80000.0,
                    80.0,
                    date(2024, 1, 3),
                    PORTFOLIO_RUN_ID,
                ),
            ],
        )


def seed_trade_db(path: Path, *, hard_fail_count: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table trade_run (
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
            create table trade_audit (
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
        con.execute(
            """
            create table trade_portfolio_snapshot (
                trade_portfolio_snapshot_id varchar,
                trade_run_id varchar,
                portfolio_admission_id varchar,
                position_candidate_id varchar,
                symbol varchar,
                timeframe varchar,
                plan_dt date,
                admission_state varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            create table order_intent_ledger (
                order_intent_id varchar,
                trade_run_id varchar,
                portfolio_admission_id varchar,
                position_candidate_id varchar,
                symbol varchar,
                timeframe varchar,
                intent_dt date,
                order_side varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            create table execution_plan_ledger (
                execution_plan_id varchar,
                trade_run_id varchar,
                order_intent_id varchar,
                execution_plan_type varchar,
                execution_price_line varchar,
                execution_valid_from date,
                execution_valid_until date,
                execution_state varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            create table fill_ledger (
                fill_id varchar,
                trade_run_id varchar,
                order_intent_id varchar,
                execution_plan_id varchar,
                execution_dt date,
                fill_seq bigint,
                fill_price double,
                fill_quantity double,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            create table order_rejection_ledger (
                order_rejection_id varchar,
                trade_run_id varchar,
                order_intent_id varchar,
                rejection_dt date,
                rejection_reason varchar,
                rejection_stage varchar,
                source_portfolio_plan_release_version varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            insert into trade_run
            values (?, 'trade_build', 'bounded', 'day', 'completed',
                    'H:\\Asteria-data\\portfolio_plan.duckdb', 2, 1, 1, 0, 1, ?,
                    'trade-bounded-proof-v1', 'trade-portfolio-plan-minimal-v1', ?, ?, now())
            """,
            [TRADE_RUN_ID, hard_fail_count, PORTFOLIO_RUN_ID, PORTFOLIO_RUN_ID],
        )
        con.execute(
            """
            insert into trade_audit
            values ('trade-unit|audit', ?, 'unit_seed', 'hard', ?, ?, '{}', now())
            """,
            [TRADE_RUN_ID, "fail" if hard_fail_count else "pass", hard_fail_count],
        )
        con.executemany(
            """
            insert into trade_portfolio_snapshot
            values (?, ?, ?, ?, ?, 'day', ?, 'admitted', ?)
            """,
            [
                (
                    "snapshot-600000",
                    TRADE_RUN_ID,
                    "adm-600000",
                    "pc-600000",
                    "600000.SH",
                    date(2024, 1, 2),
                    TRADE_RUN_ID,
                ),
                (
                    "snapshot-600001",
                    TRADE_RUN_ID,
                    "adm-600001",
                    "pc-600001",
                    "600001.SH",
                    date(2024, 1, 3),
                    TRADE_RUN_ID,
                ),
            ],
        )
        con.execute(
            """
            insert into order_intent_ledger
            values (
                'intent-600000', ?, 'adm-600000', 'pc-600000',
                '600000.SH', 'day', '2024-01-02', 'buy', ?
            )
            """,
            [TRADE_RUN_ID, TRADE_RUN_ID],
        )
        con.execute(
            """
            insert into execution_plan_ledger
            values (
                'plan-600000', ?, 'intent-600000', 'portfolio_plan_target',
                null, '2024-01-02', '2024-01-02', 'planned', ?
            )
            """,
            [TRADE_RUN_ID, TRADE_RUN_ID],
        )
        con.execute(
            """
            insert into order_rejection_ledger
            values ('reject-600001', ?, null, '2024-01-03', 'not_tradeable', 'intent', ?, ?)
            """,
            [TRADE_RUN_ID, PORTFOLIO_RUN_ID, TRADE_RUN_ID],
        )
