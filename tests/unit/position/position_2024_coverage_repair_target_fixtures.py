from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb
from tests.unit.position.position_2024_coverage_repair_support import (
    PORTFOLIO_RUN_ID,
    POSITION_RUN_ID,
    TRADE_RUN_ID,
    created_at,
)
from tests.unit.position.position_2024_coverage_repair_system_fixtures import signal_input

from asteria.position.contracts import (
    POSITION_RULE_VERSION,
    POSITION_SCHEMA_VERSION,
    PositionBuildRequest,
)
from asteria.position.rules import build_position_rows
from asteria.position.schema import bootstrap_position_database


def seed_position_release_db(
    path: Path,
    *,
    released_dates: list[date],
    released_run_id: str,
    signal_run_id: str,
    include_week_row: bool,
) -> None:
    bootstrap_position_database(path)
    request = PositionBuildRequest(
        source_signal_db=Path("signal.duckdb"),
        target_position_db=path,
        report_root=Path("report"),
        validated_root=Path("validated"),
        temp_root=Path("temp"),
        run_id=released_run_id,
        mode="bounded",
        source_signal_release_version=signal_run_id,
        source_signal_run_id=signal_run_id,
        start_dt="2024-01-01",
        end_dt="2024-12-31",
    )
    signals = [
        signal_input(
            signal_id=f"seed-{bar_dt.isoformat()}",
            signal_dt=bar_dt,
            signal_state="active",
            signal_bias="up_opportunity",
        )
        for bar_dt in released_dates
    ]
    rows = build_position_rows(signals, request, created_at())
    with duckdb.connect(str(path)) as con:
        con.execute("delete from position_run where run_id = ?", [released_run_id])
        con.execute(
            """
            insert into position_run
            values (?, 'position_build', 'bounded', 'day', 'completed', 'signal.duckdb',
                    ?, ?, ?, ?, 0, ?, ?, ?, ?, ?)
            """,
            [
                released_run_id,
                len(rows.snapshots) + (1 if include_week_row else 0),
                len(rows.candidates) + (1 if include_week_row else 0),
                len(rows.entries) + (1 if include_week_row else 0),
                len(rows.exits) + (1 if include_week_row else 0),
                POSITION_SCHEMA_VERSION,
                POSITION_RULE_VERSION,
                signal_run_id,
                signal_run_id,
                created_at(),
            ],
        )
        con.execute(
            "delete from position_schema_version where schema_version = ?",
            [POSITION_SCHEMA_VERSION],
        )
        con.execute(
            "insert into position_schema_version values (?, ?)",
            [POSITION_SCHEMA_VERSION, created_at()],
        )
        con.execute(
            "delete from position_rule_version where position_rule_version = ?",
            [POSITION_RULE_VERSION],
        )
        con.execute(
            "insert into position_rule_version values (?, 'signal_to_position_plan', ?)",
            [POSITION_RULE_VERSION, created_at()],
        )
        con.executemany(
            (
                "insert into position_signal_snapshot "
                "values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            ),
            rows.snapshots,
        )
        con.executemany(
            (
                "insert into position_candidate_ledger "
                "values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            ),
            rows.candidates,
        )
        con.executemany(
            "insert into position_entry_plan values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows.entries,
        )
        con.executemany(
            "insert into position_exit_plan values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows.exits,
        )
        con.execute(
            """
            insert into position_audit
            values (?, ?, 'position_seed_ok', 'hard', 'pass', 0, '{}', ?)
            """,
            [f"{released_run_id}|day|seed", released_run_id, created_at()],
        )
        if include_week_row:
            insert_week_position_rows(con, released_run_id, signal_run_id)


def insert_week_position_rows(
    con: duckdb.DuckDBPyConnection,
    released_run_id: str,
    signal_run_id: str,
) -> None:
    week_dt = date(2024, 1, 31)
    created = created_at()
    candidate_id = f"week-signal|directional_position_candidate|{POSITION_RULE_VERSION}"
    con.execute(
        """
        insert into position_signal_snapshot
        values (?, ?, 'week-signal', '600000.SH', 'week', ?, 'directional_opportunity', 'active',
                'up_opportunity', 0.9, 'high', 'alpha_candidate_support',
                'signal-alpha-aggregation-minimal-v1', ?, ?, ?, ?, ?)
        """,
        [
            f"{released_run_id}|week-signal",
            released_run_id,
            week_dt,
            signal_run_id,
            signal_run_id,
            POSITION_SCHEMA_VERSION,
            POSITION_RULE_VERSION,
            created,
        ],
    )
    con.execute(
        """
        insert into position_candidate_ledger
        values (
            ?, 'week-signal', '600000.SH', 'week', ?, 'directional_position_candidate',
            'planned', 'long_candidate', 'signal_released_for_position', ?, ?, ?, ?, ?
        )
        """,
        [
            candidate_id,
            week_dt,
            signal_run_id,
            released_run_id,
            POSITION_SCHEMA_VERSION,
            POSITION_RULE_VERSION,
            created,
        ],
    )
    con.execute(
        """
        insert into position_entry_plan
        values (?, ?, 'signal_follow_entry', 'next_session_open_plan', ?, ?, null, 'planned',
                ?, ?, ?, ?, ?)
        """,
        [
            f"{candidate_id}|signal_follow_entry|{POSITION_RULE_VERSION}",
            candidate_id,
            week_dt,
            week_dt,
            released_run_id,
            POSITION_SCHEMA_VERSION,
            POSITION_RULE_VERSION,
            signal_run_id,
            created,
        ],
    )
    con.execute(
        """
        insert into position_exit_plan
        values (
            ?, ?, 'signal_invalidation_exit', 'signal_invalidated_or_expired', ?,
            ?, null, 'planned', ?, ?, ?, ?, ?
        )
        """,
        [
            f"{candidate_id}|signal_invalidation_exit|{POSITION_RULE_VERSION}",
            candidate_id,
            week_dt,
            week_dt,
            released_run_id,
            POSITION_SCHEMA_VERSION,
            POSITION_RULE_VERSION,
            signal_run_id,
            created,
        ],
    )


def seed_portfolio_plan_db(path: Path, dates: list[date]) -> None:
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
                admission_count bigint,
                exposure_count bigint,
                trim_count bigint,
                hard_fail_count bigint,
                portfolio_plan_version varchar,
                schema_version varchar,
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
                symbol varchar,
                timeframe varchar,
                plan_dt date,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            create table portfolio_target_exposure (
                target_exposure_id varchar,
                symbol varchar,
                timeframe varchar,
                exposure_valid_from date,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            insert into portfolio_plan_run
            values (?, 'portfolio_plan_build', 'bounded', 'day', 'completed', 'position.duckdb',
                    ?, ?, 0, 0, 'portfolio-plan-day-bounded-v1', 'portfolio-plan-bounded-proof-v1',
                    ?, ?, ?)
            """,
            [
                PORTFOLIO_RUN_ID,
                len(dates),
                len(dates),
                POSITION_RUN_ID,
                POSITION_RUN_ID,
                created_at(),
            ],
        )
        con.execute(
            """
            insert into portfolio_plan_audit
            values ('portfolio-audit', ?, 'hard_audit_zero', 'hard', 'pass', 0, '{}', ?)
            """,
            [PORTFOLIO_RUN_ID, created_at()],
        )
        con.executemany(
            "insert into portfolio_admission_ledger values (?, '600000.SH', 'day', ?, ?)",
            [[f"admission-{bar_dt.isoformat()}", bar_dt, PORTFOLIO_RUN_ID] for bar_dt in dates],
        )
        con.executemany(
            "insert into portfolio_target_exposure values (?, '600000.SH', 'day', ?, ?)",
            [[f"exposure-{bar_dt.isoformat()}", bar_dt, PORTFOLIO_RUN_ID] for bar_dt in dates],
        )


def seed_trade_db(path: Path, dates: list[date]) -> None:
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
                intent_count bigint,
                execution_plan_count bigint,
                rejection_count bigint,
                fill_count bigint,
                hard_fail_count bigint,
                schema_version varchar,
                trade_rule_version varchar,
                source_portfolio_release_version varchar,
                source_portfolio_run_id varchar,
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
            create table order_intent_ledger (
                order_intent_id varchar,
                symbol varchar,
                timeframe varchar,
                intent_dt date,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            create table execution_plan_ledger (
                execution_plan_id varchar,
                symbol varchar,
                timeframe varchar,
                execution_valid_from date,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            create table order_rejection_ledger (
                order_rejection_id varchar,
                symbol varchar,
                timeframe varchar,
                rejection_dt date,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            create table fill_ledger (
                fill_id varchar,
                symbol varchar,
                timeframe varchar,
                execution_dt date,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            insert into trade_run
            values (?, 'trade_build', 'bounded', 'day', 'completed', 'portfolio_plan.duckdb',
                    ?, ?, ?, 0, 0, 'trade-bounded-proof-v1', 'trade-day-bounded-v1',
                    ?, ?, ?)
            """,
            [
                TRADE_RUN_ID,
                len(dates),
                len(dates),
                len(dates),
                PORTFOLIO_RUN_ID,
                PORTFOLIO_RUN_ID,
                created_at(),
            ],
        )
        con.execute(
            """
            insert into trade_audit
            values ('trade-audit', ?, 'hard_audit_zero', 'hard', 'pass', 0, '{}', ?)
            """,
            [TRADE_RUN_ID, created_at()],
        )
        con.executemany(
            "insert into order_intent_ledger values (?, '600000.SH', 'day', ?, ?)",
            [[f"intent-{bar_dt.isoformat()}", bar_dt, TRADE_RUN_ID] for bar_dt in dates],
        )
        con.executemany(
            "insert into execution_plan_ledger values (?, '600000.SH', 'day', ?, ?)",
            [[f"plan-{bar_dt.isoformat()}", bar_dt, TRADE_RUN_ID] for bar_dt in dates],
        )
        con.executemany(
            "insert into order_rejection_ledger values (?, '600000.SH', 'day', ?, ?)",
            [[f"reject-{bar_dt.isoformat()}", bar_dt, TRADE_RUN_ID] for bar_dt in dates],
        )
