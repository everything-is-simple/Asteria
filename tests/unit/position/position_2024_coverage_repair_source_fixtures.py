from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb
from tests.unit.position.position_2024_coverage_repair_support import (
    ALPHA_FAMILIES,
    ALPHA_RUN_ID,
    FOCUS_DATES,
    MALF_RUN_ID,
    SIGNAL_RUN_ID,
    created_at,
)


def seed_data_foundation(data_root: Path, dates: list[date]) -> None:
    data_root.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(data_root / "market_base_day.duckdb")) as con:
        con.execute("create table market_base_bar (code varchar, bar_dt date, timeframe varchar)")
        con.executemany(
            "insert into market_base_bar values ('600000.SH', ?, 'day')",
            [[bar_dt] for bar_dt in dates],
        )
    with duckdb.connect(str(data_root / "market_meta.duckdb")) as con:
        con.execute("create table trade_calendar (trade_date date)")
        con.execute("create table tradability_fact (symbol varchar, trade_date date)")
        con.executemany("insert into trade_calendar values (?)", [[bar_dt] for bar_dt in dates])
        con.executemany(
            "insert into tradability_fact values ('600000.SH', ?)",
            [[bar_dt] for bar_dt in dates],
        )


def seed_malf_db(path: Path, dates: list[date]) -> None:
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table malf_service_run (
                run_id varchar,
                runner_name varchar,
                timeframe varchar,
                status varchar,
                source_market_db varchar,
                row_count bigint,
                hard_fail_count bigint,
                schema_version varchar,
                created_at timestamp
            )
            """
        )
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
        con.execute(
            """
            create table malf_wave_position (
                symbol varchar,
                bar_dt date,
                wave_id varchar,
                wave_core_state varchar,
                system_state varchar,
                timeframe varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            insert into malf_service_run
            values (?, 'malf_build', 'day', 'completed', 'market_base_day.duckdb', ?, 0,
                    'malf-wave-position-dense-v1', ?)
            """,
            [MALF_RUN_ID, len(dates), created_at()],
        )
        con.execute(
            """
            insert into malf_interface_audit
            values ('malf-audit', ?, 'hard_audit_zero', 'hard', 'pass', 0, '{}', ?)
            """,
            [MALF_RUN_ID, created_at()],
        )
        con.executemany(
            (
                "insert into malf_wave_position "
                "values ('600000.SH', ?, 'wave-1', 'ok', 'ok', 'day', ?)"
            ),
            [[bar_dt, MALF_RUN_ID] for bar_dt in dates],
        )


def seed_alpha_family_dbs(data_root: Path, dates: list[date]) -> None:
    for family in ALPHA_FAMILIES:
        path = data_root / f"alpha_{family}.duckdb"
        with duckdb.connect(str(path)) as con:
            con.execute(
                """
                create table alpha_family_run (
                    run_id varchar,
                    runner_name varchar,
                    alpha_family varchar,
                    mode varchar,
                    timeframe varchar,
                    status varchar,
                    source_malf_db varchar,
                    input_count bigint,
                    candidate_count bigint,
                    audit_count bigint,
                    hard_fail_count bigint,
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
                create table alpha_source_audit (
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
                create table alpha_signal_candidate (
                    alpha_candidate_id varchar,
                    symbol varchar,
                    timeframe varchar,
                    bar_dt date,
                    run_id varchar,
                    source_malf_run_id varchar
                )
                """
            )
            con.execute(
                """
                insert into alpha_family_run
                values (?, 'alpha_build', ?, 'full', 'day', 'completed', 'malf_service_day.duckdb',
                        ?, ?, 1, 0, 'alpha-bounded-proof-v1', 'alpha-minimal-v1',
                        'malf-wave-position-dense-v1', ?, ?)
                """,
                [ALPHA_RUN_ID, family.upper(), len(dates), len(dates), MALF_RUN_ID, created_at()],
            )
            con.execute(
                """
                insert into alpha_source_audit
                values ('alpha-audit', ?, 'hard_audit_zero', 'hard', 'pass', 0, '{}', ?)
                """,
                [ALPHA_RUN_ID, created_at()],
            )
            con.executemany(
                "insert into alpha_signal_candidate values (?, '600000.SH', 'day', ?, ?, ?)",
                [
                    [f"{family}-{bar_dt.isoformat()}", bar_dt, ALPHA_RUN_ID, MALF_RUN_ID]
                    for bar_dt in dates
                ],
            )


def seed_signal_db(path: Path, dates: list[date]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table signal_run (
                run_id varchar,
                runner_name varchar,
                mode varchar,
                timeframe varchar,
                status varchar,
                source_alpha_db varchar,
                alpha_candidate_count bigint,
                signal_count bigint,
                component_count bigint,
                hard_fail_count bigint,
                signal_rule_version varchar,
                schema_version varchar,
                source_alpha_release_version varchar,
                source_alpha_run_id varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table formal_signal_ledger (
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
            create table signal_component_ledger (
                signal_component_id varchar,
                signal_id varchar,
                alpha_candidate_id varchar
            )
            """
        )
        con.execute(
            """
            create table signal_input_snapshot (
                signal_input_snapshot_id varchar,
                signal_run_id varchar,
                timeframe varchar,
                source_alpha_run_id varchar
            )
            """
        )
        con.execute(
            """
            create table signal_audit (
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
            insert into signal_run
            values (?, 'signal_build', 'full', 'day', 'completed', 'alpha-root', ?, ?, ?, 0,
                    'signal-alpha-aggregation-minimal-v1', 'signal-bounded-proof-v1', ?, ?, ?)
            """,
            [
                SIGNAL_RUN_ID,
                len(dates),
                len(dates),
                len(dates),
                ALPHA_RUN_ID,
                ALPHA_RUN_ID,
                created_at(),
            ],
        )
        con.execute(
            """
            insert into signal_audit
            values ('signal-audit', ?, 'hard_audit_zero', 'hard', 'pass', 0, '{}', ?)
            """,
            [SIGNAL_RUN_ID, created_at()],
        )
        rows = []
        component_rows = []
        snapshot_rows = []
        for index, bar_dt in enumerate(dates, start=1):
            signal_id = f"sig-{bar_dt.isoformat()}"
            state = "active" if bar_dt in FOCUS_DATES else ("active" if index % 4 else "rejected")
            signal_type = (
                "directional_opportunity" if state == "active" else "conflict_or_weak_signal"
            )
            reason_code = (
                "alpha_candidate_support"
                if state == "active"
                else "signal_strength_below_threshold"
            )
            rows.append(
                (
                    signal_id,
                    "600000.SH",
                    "day",
                    bar_dt,
                    signal_type,
                    state,
                    ("up_opportunity" if index % 2 else "down_opportunity")
                    if state == "active"
                    else "neutral",
                    0.8,
                    "high",
                    reason_code,
                    1,
                    0,
                    0,
                    ALPHA_RUN_ID,
                    SIGNAL_RUN_ID,
                    "signal-bounded-proof-v1",
                    "signal-alpha-aggregation-minimal-v1",
                    created_at(),
                )
            )
            component_rows.append((f"component-{signal_id}", signal_id, f"alpha-{index}"))
            snapshot_rows.append((f"snapshot-{signal_id}", SIGNAL_RUN_ID, "day", ALPHA_RUN_ID))
        con.executemany(
            """
            insert into formal_signal_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        con.executemany("insert into signal_component_ledger values (?, ?, ?)", component_rows)
        con.executemany("insert into signal_input_snapshot values (?, ?, ?, ?)", snapshot_rows)
