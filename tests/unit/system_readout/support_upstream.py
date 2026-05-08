from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb

MALF_RUN_ID = "malf-v1-4-core-runtime-sync-implementation-20260505-01"
ALPHA_RUN_ID = "alpha-production-builder-hardening-20260506-01"
SIGNAL_RUN_ID = "signal-production-builder-hardening-20260506-01"
POSITION_RUN_ID = "position-bounded-proof-build-card-20260506-01"
PORTFOLIO_RUN_ID = "portfolio-plan-bounded-proof-build-card-20260507-01"
TRADE_RUN_ID = "trade-bounded-proof-build-card-20260507-01"
ALPHA_FAMILIES = ("bof", "tst", "pb", "cpb", "bpb")


def seed_malf_db(path: Path) -> None:
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
                timeframe varchar,
                bar_dt date,
                system_state varchar,
                wave_id varchar,
                old_wave_id varchar,
                wave_core_state varchar,
                direction varchar,
                service_version varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            insert into malf_service_run
            values (?, 'malf_day_service_build', 'bounded', 'day', 'completed',
                    ?, ?, 2, 'malf-day-bounded-proof-v1', 'malf-wave-position-dense-v1', now())
            """,
            [MALF_RUN_ID, MALF_RUN_ID, MALF_RUN_ID],
        )
        con.execute(
            """
            insert into malf_interface_audit
            values ('malf-unit|audit', ?, 'unit_seed_ok', 'hard', 'pass', 0, '{}', now())
            """,
            [MALF_RUN_ID],
        )
        con.executemany(
            """
            insert into malf_wave_position
            values (?, 'day', ?, ?, ?, null, ?, 'up', 'malf-wave-position-dense-v1', ?)
            """,
            [
                ("600000.SH", date(2024, 1, 2), "trend_up", "wave-600000", "impulse", MALF_RUN_ID),
                ("600001.SH", date(2024, 1, 3), "trend_up", "wave-600001", "impulse", MALF_RUN_ID),
            ],
        )


def seed_alpha_db(path: Path, family: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table alpha_family_run (
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
                source_malf_release_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table alpha_source_audit (
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
        con.execute(
            """
            create table alpha_event_ledger (
                alpha_event_id varchar,
                alpha_family varchar,
                symbol varchar,
                timeframe varchar,
                bar_dt date,
                event_type varchar,
                opportunity_state varchar,
                source_wave_position_key varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            create table alpha_score_ledger (
                alpha_score_id varchar,
                alpha_event_id varchar,
                alpha_family varchar,
                score_name varchar,
                score_value double,
                score_direction varchar,
                score_bucket varchar,
                source_malf_service_version varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            create table alpha_signal_candidate (
                alpha_candidate_id varchar,
                alpha_event_id varchar,
                alpha_family varchar,
                symbol varchar,
                timeframe varchar,
                bar_dt date,
                candidate_type varchar,
                candidate_state varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            insert into alpha_family_run
            values (?, 'alpha_family_build', 'full', 'day', ?, 'completed',
                    'H:\\Asteria-data\\malf_service_day.duckdb', 2, 2, 2, 2,
                    'alpha-family-schema-v1', 'alpha-waveposition-production-v1',
                    'malf-wave-position-dense-v1', ?, now())
            """,
            [ALPHA_RUN_ID, family, MALF_RUN_ID],
        )
        con.execute(
            """
            insert into alpha_source_audit
            values ('alpha-unit|audit', ?, ?, 'unit_seed_ok', 'hard', 'pass', 0, '{}', now())
            """,
            [ALPHA_RUN_ID, family],
        )
        rows = [
            (
                f"{family}-event-600000",
                family,
                "600000.SH",
                date(2024, 1, 2),
                f"{family}-candidate-600000",
            ),
            (
                f"{family}-event-600001",
                family,
                "600001.SH",
                date(2024, 1, 3),
                f"{family}-candidate-600001",
            ),
        ]
        con.executemany(
            """
            insert into alpha_event_ledger
            values (?, ?, ?, 'day', ?, 'directional_opportunity', 'active', 'wave-ref', ?)
            """,
            [
                (event_id, alpha_family, symbol, bar_dt, ALPHA_RUN_ID)
                for event_id, alpha_family, symbol, bar_dt, _ in rows
            ],
        )
        con.executemany(
            """
            insert into alpha_score_ledger
            values (
                ?, ?, ?, 'alpha_score', 0.8, 'positive', 'high',
                'malf-wave-position-dense-v1', ?
            )
            """,
            [
                (f"{event_id}|score", event_id, alpha_family, ALPHA_RUN_ID)
                for event_id, alpha_family, *_ in rows
            ],
        )
        con.executemany(
            """
            insert into alpha_signal_candidate
            values (?, ?, ?, ?, 'day', ?, 'directional_candidate', 'active', ?)
            """,
            [
                (candidate_id, event_id, alpha_family, symbol, bar_dt, ALPHA_RUN_ID)
                for event_id, alpha_family, symbol, bar_dt, candidate_id in rows
            ],
        )


def seed_signal_db(path: Path) -> None:
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
            create table formal_signal_ledger (
                signal_id varchar,
                symbol varchar,
                timeframe varchar,
                signal_dt date,
                signal_type varchar,
                signal_state varchar,
                signal_bias varchar,
                signal_strength double,
                source_alpha_release_version varchar,
                run_id varchar
            )
            """
        )
        con.execute(
            """
            create table signal_component_ledger (
                signal_component_id varchar,
                signal_id varchar,
                signal_run_id varchar,
                alpha_family varchar,
                alpha_candidate_id varchar,
                component_role varchar,
                component_weight double,
                alpha_rule_version varchar
            )
            """
        )
        con.execute(
            """
            insert into signal_run
            values (?, 'signal_build', 'full', 'day', 'completed', 'H:\\Asteria-data',
                    3, 3, 3, 0, 'signal-bounded-proof-v1', 'signal-alpha-aggregation-minimal-v1',
                    ?, now())
            """,
            [SIGNAL_RUN_ID, ALPHA_RUN_ID],
        )
        con.execute(
            """
            insert into signal_audit
            values ('signal-unit|audit', ?, 'unit_seed_ok', 'hard', 'pass', 0, '{}', now())
            """,
            [SIGNAL_RUN_ID],
        )
        con.executemany(
            """
            insert into formal_signal_ledger
            values (?, ?, 'day', ?, 'directional_opportunity', 'active', 'long_bias', 0.8, ?, ?)
            """,
            [
                ("sig-600000", "600000.SH", date(2024, 1, 2), ALPHA_RUN_ID, SIGNAL_RUN_ID),
                ("sig-600001", "600001.SH", date(2024, 1, 3), ALPHA_RUN_ID, SIGNAL_RUN_ID),
                ("sig-600002", "600002.SH", date(2024, 1, 4), ALPHA_RUN_ID, SIGNAL_RUN_ID),
            ],
        )
        con.executemany(
            """
            insert into signal_component_ledger
            values (?, ?, ?, ?, ?, 'support', 1.0, 'alpha-waveposition-production-v1')
            """,
            [
                ("component-600000", "sig-600000", SIGNAL_RUN_ID, "BOF", "BOF-candidate-600000"),
                ("component-600001", "sig-600001", SIGNAL_RUN_ID, "BOF", "BOF-candidate-600001"),
                ("component-600002", "sig-600002", SIGNAL_RUN_ID, "BOF", "BOF-candidate-missing"),
            ],
        )
