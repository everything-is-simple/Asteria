from __future__ import annotations

from dataclasses import replace
from datetime import date
from pathlib import Path

import duckdb
from tests.unit.alpha.test_alpha_bounded_proof_runner import _seed_malf_service
from tests.unit.system_readout.support import build_request as build_system_request
from tests.unit.system_readout.support_downstream import (
    seed_portfolio_plan_db,
    seed_position_db,
    seed_trade_db,
)

from asteria.alpha.bootstrap import run_alpha_family_build
from asteria.alpha.contracts import AlphaFamilyRequest
from asteria.pipeline.alpha_signal_2024_coverage_repair import (
    AlphaSignalCoverageRepairRequest,
)
from asteria.signal.bootstrap import run_signal_build
from asteria.signal.contracts import SignalBuildRequest
from asteria.system_readout.bootstrap import run_system_readout_build

BASELINE_MALF_RUN_ID = "malf-v1-4-core-runtime-sync-implementation-20260505-01"
REPAIRED_MALF_RUN_ID = "malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001"
ALPHA_RELEASED_RUN_ID = "alpha-production-builder-hardening-20260506-01"
SIGNAL_RELEASED_RUN_ID = "signal-production-builder-hardening-20260506-01"
SYSTEM_RELEASED_RUN_ID = "system-readout-bounded-proof-build-card-20260508-01"
MALF_SERVICE_VERSION = "malf-wave-position-dense-v1"
MALF_SAMPLE_VERSION = "malf-day-formal-2024-s20-v14"
ALPHA_FAMILIES = ("BOF", "TST", "PB", "CPB", "BPB")


def repair_request(
    tmp_path: Path,
    *,
    followup: bool,
    repo_root: Path | None = None,
) -> AlphaSignalCoverageRepairRequest:
    return AlphaSignalCoverageRepairRequest(
        repo_root=repo_root or (tmp_path / "repo"),
        source_system_db=tmp_path / "data" / "system.duckdb",
        baseline_malf_service_db=tmp_path / "data" / "malf_service_day.duckdb",
        repaired_malf_service_db=tmp_path / "data" / "malf_service_day.duckdb",
        target_data_root=tmp_path / "data",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="alpha-signal-2024-coverage-repair-card-20260509-01",
        baseline_malf_run_id=BASELINE_MALF_RUN_ID,
        repaired_malf_run_id=REPAIRED_MALF_RUN_ID,
        released_alpha_run_id=ALPHA_RELEASED_RUN_ID,
        released_signal_run_id=SIGNAL_RELEASED_RUN_ID,
        source_chain_release_version=SYSTEM_RELEASED_RUN_ID,
        run_followup_checks=followup,
    )


def seed_live_released_chain(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    data_root.mkdir(parents=True, exist_ok=True)
    _seed_data_foundation(data_root)
    day_db = data_root / "malf_service_day.duckdb"
    week_db = data_root / "malf_service_week.duckdb"
    month_db = data_root / "malf_service_month.duckdb"
    _seed_malf_service(
        day_db,
        service_version=MALF_SERVICE_VERSION,
        sample_version=MALF_SAMPLE_VERSION,
    )
    _seed_malf_service(
        week_db,
        timeframe="week",
        service_version="malf-wave-position-week-v1",
        sample_version="malf-week-formal-2024-s20-v1",
    )
    _seed_malf_service(
        month_db,
        timeframe="month",
        service_version="malf-wave-position-month-v1",
        sample_version="malf-month-formal-2024-s20-v1",
    )
    ensure_malf_run_tables(day_db, BASELINE_MALF_RUN_ID, MALF_SERVICE_VERSION)
    ensure_malf_run_tables(
        week_db,
        "malf-week-bounded-proof-build-20260506-01",
        "malf-wave-position-week-v1",
    )
    ensure_malf_run_tables(
        month_db,
        "malf-month-bounded-proof-build-20260506-01",
        "malf-wave-position-month-v1",
    )
    with duckdb.connect(str(day_db)) as con:
        con.execute("update malf_wave_position set run_id = ?", [BASELINE_MALF_RUN_ID])
        con.execute("update malf_wave_position_latest set run_id = ?", [BASELINE_MALF_RUN_ID])
        con.execute("update malf_interface_audit set run_id = ?", [BASELINE_MALF_RUN_ID])
        con.executemany(
            f"insert into malf_wave_position values ({', '.join(['?'] * 25)})",
            [
                (
                    "000020.SZ",
                    "day",
                    date(2024, 1, 2),
                    "up_alive",
                    "repair-wave-1",
                    None,
                    "alive",
                    "up",
                    1,
                    0,
                    0,
                    0.95,
                    0.15,
                    "developing",
                    "developing",
                    11.0,
                    "repair-scope",
                    MALF_SAMPLE_VERSION,
                    "lifespan-rule-v1",
                    MALF_SERVICE_VERSION,
                    REPAIRED_MALF_RUN_ID,
                    "malf-schema-v1",
                    "repair-core-run",
                    "repair-lifespan-run",
                    "2026-05-09 00:00:00",
                ),
            ],
        )
        con.execute(
            """
            insert into malf_service_run
            select ?, runner_name, mode, timeframe, status, source_core_run_id,
                   source_lifespan_run_id, published_row_count, schema_version,
                   service_version, created_at
            from malf_service_run
            limit 1
            """,
            [REPAIRED_MALF_RUN_ID],
        )
        con.execute(
            """
            insert into malf_interface_audit
            select replace(audit_id, ?, ?), ?, check_name, severity, status, failed_count,
                   sample_payload, created_at
            from malf_interface_audit
            where run_id = ?
            """,
            [
                BASELINE_MALF_RUN_ID,
                REPAIRED_MALF_RUN_ID,
                REPAIRED_MALF_RUN_ID,
                BASELINE_MALF_RUN_ID,
            ],
        )

    for family in ALPHA_FAMILIES:
        run_alpha_family_build(
            AlphaFamilyRequest(
                source_malf_db=day_db,
                target_alpha_db=data_root / f"alpha_{family.lower()}.duckdb",
                report_root=tmp_path / "report",
                validated_root=tmp_path / "validated",
                temp_root=tmp_path / "temp",
                run_id=ALPHA_RELEASED_RUN_ID,
                mode="full",
                alpha_family=family,
                source_malf_service_version=MALF_SERVICE_VERSION,
                source_malf_run_id=BASELINE_MALF_RUN_ID,
                source_malf_sample_version=MALF_SAMPLE_VERSION,
                timeframe="day",
            )
        )
        run_alpha_family_build(
            AlphaFamilyRequest(
                source_malf_db=week_db,
                target_alpha_db=data_root / f"alpha_{family.lower()}.duckdb",
                report_root=tmp_path / "report",
                validated_root=tmp_path / "validated",
                temp_root=tmp_path / "temp",
                run_id=ALPHA_RELEASED_RUN_ID,
                mode="full",
                alpha_family=family,
                source_malf_service_version="malf-wave-position-week-v1",
                timeframe="week",
            )
        )

    run_signal_build(
        SignalBuildRequest(
            source_alpha_root=data_root,
            target_signal_db=data_root / "signal.duckdb",
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id=SIGNAL_RELEASED_RUN_ID,
            mode="full",
            source_alpha_release_version=ALPHA_RELEASED_RUN_ID,
            source_alpha_run_id=ALPHA_RELEASED_RUN_ID,
            timeframe="day",
        )
    )
    run_signal_build(
        SignalBuildRequest(
            source_alpha_root=data_root,
            target_signal_db=data_root / "signal.duckdb",
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id=SIGNAL_RELEASED_RUN_ID,
            mode="full",
            source_alpha_release_version=ALPHA_RELEASED_RUN_ID,
            source_alpha_run_id=ALPHA_RELEASED_RUN_ID,
            timeframe="week",
        )
    )

    seed_position_db(data_root / "position.duckdb")
    seed_portfolio_plan_db(data_root / "portfolio_plan.duckdb")
    seed_trade_db(data_root / "trade.duckdb", hard_fail_count=0)
    run_system_readout_build(
        replace(
            build_system_request(tmp_path),
            run_id=SYSTEM_RELEASED_RUN_ID,
        )
    )


def ensure_malf_run_tables(db_path: Path, run_id: str, service_version: str) -> None:
    with duckdb.connect(str(db_path)) as con:
        con.execute(
            """
            create table if not exists malf_service_run (
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
        con.execute("delete from malf_service_run")
        con.execute(
            """
            insert into malf_service_run
            values (?, 'malf_day_service_build', 'bounded', 'day', 'completed',
                    ?, ?, 8, 'malf-day-bounded-proof-v1', ?, now())
            """,
            [run_id, run_id, run_id, service_version],
        )


def _seed_data_foundation(data_root: Path) -> None:
    focus_dates = [
        date(2024, 1, 2),
        date(2024, 1, 3),
        date(2024, 1, 4),
        date(2024, 1, 5),
        date(2024, 1, 8),
    ]
    with duckdb.connect(str(data_root / "market_base_day.duckdb")) as con:
        con.execute(
            """
            create table market_base_bar (
                code varchar,
                bar_dt date,
                timeframe varchar
            )
            """
        )
        con.executemany(
            "insert into market_base_bar values ('600000.SH', ?, 'day')",
            [[bar_dt] for bar_dt in focus_dates],
        )
    with duckdb.connect(str(data_root / "market_meta.duckdb")) as con:
        con.execute("create table trade_calendar (trade_date date)")
        con.execute(
            """
            create table tradability_fact (
                symbol varchar,
                trade_date date
            )
            """
        )
        con.executemany(
            "insert into trade_calendar values (?)",
            [[bar_dt] for bar_dt in focus_dates],
        )
        con.executemany(
            "insert into tradability_fact values ('600000.SH', ?)",
            [[bar_dt] for bar_dt in focus_dates],
        )
