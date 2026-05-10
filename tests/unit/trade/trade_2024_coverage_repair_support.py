from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

import duckdb

from asteria.trade.bootstrap import run_trade_build
from asteria.trade.contracts import TradeBuildRequest
from asteria.trade.coverage_repair_contracts import Trade2024CoverageRepairRequest

MALF_RUN_ID = "malf-v1-4-core-runtime-sync-implementation-20260505-01"
REPAIRED_MALF_RUN_ID = "malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001"
ALPHA_RUN_ID = "alpha-production-builder-hardening-20260506-01"
SIGNAL_RUN_ID = "signal-production-builder-hardening-20260506-01"
POSITION_RUN_ID = "position-bounded-proof-build-card-20260506-01"
PORTFOLIO_RUN_ID = "portfolio-plan-bounded-proof-build-card-20260507-01"
TRADE_RUN_ID = "trade-bounded-proof-build-card-20260507-01"
SYSTEM_RUN_ID = "system-readout-bounded-proof-build-card-20260508-01"
ALPHA_FAMILIES = ("bof", "tst", "pb", "cpb", "bpb")


def build_request(tmp_path: Path, *, repo_root: Path) -> Trade2024CoverageRepairRequest:
    return Trade2024CoverageRepairRequest(
        repo_root=repo_root,
        source_system_db=tmp_path / "data" / "system.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="trade-2024-coverage-repair-card-20260509-01",
    )


def seed_repo_root(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    governance_root = repo_root / "governance"
    governance_root.mkdir(parents=True, exist_ok=True)
    (governance_root / "module_gate_registry.toml").write_text(
        'current_allowed_next_card = "trade_2024_coverage_repair_card"\n',
        encoding="utf-8",
    )
    return repo_root


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


def seed_malf_db_with_stale_manifest_source(
    path: Path,
    *,
    baseline_dates: list[date],
    repaired_dates: list[date],
) -> None:
    with duckdb.connect(str(path)) as con:
        con.execute("create table malf_wave_position (bar_dt date, run_id varchar)")
        con.execute(
            """
            create table malf_service_run (
                run_id varchar,
                status varchar,
                timeframe varchar,
                created_at timestamp
            )
            """
        )
        con.executemany(
            "insert into malf_wave_position values (?, ?)",
            [[bar_dt, MALF_RUN_ID] for bar_dt in baseline_dates],
        )
        con.executemany(
            "insert into malf_wave_position values (?, ?)",
            [[bar_dt, REPAIRED_MALF_RUN_ID] for bar_dt in repaired_dates],
        )
        con.executemany(
            "insert into malf_service_run values (?, 'completed', 'day', ?)",
            [
                [MALF_RUN_ID, datetime(2026, 5, 5, 22, 22, 3)],
                [REPAIRED_MALF_RUN_ID, datetime(2026, 5, 9, 15, 57, 18)],
            ],
        )


def seed_alpha_db(path: Path, dates: list[date]) -> None:
    with duckdb.connect(str(path)) as con:
        con.execute("create table alpha_signal_candidate (bar_dt date, run_id varchar)")
        con.executemany(
            "insert into alpha_signal_candidate values (?, ?)",
            [[bar_dt, ALPHA_RUN_ID] for bar_dt in dates],
        )


def seed_signal_db(path: Path, dates: list[date]) -> None:
    with duckdb.connect(str(path)) as con:
        con.execute("create table formal_signal_ledger (signal_dt date, run_id varchar)")
        con.executemany(
            "insert into formal_signal_ledger values (?, ?)",
            [[bar_dt, SIGNAL_RUN_ID] for bar_dt in dates],
        )


def seed_position_db(path: Path, dates: list[date]) -> None:
    with duckdb.connect(str(path)) as con:
        con.execute("create table position_candidate_ledger (candidate_dt date, run_id varchar)")
        con.execute("create table position_entry_plan (entry_reference_dt date, run_id varchar)")
        con.execute("create table position_exit_plan (exit_reference_dt date, run_id varchar)")
        con.executemany(
            "insert into position_candidate_ledger values (?, ?)",
            [[bar_dt, POSITION_RUN_ID] for bar_dt in dates],
        )
        con.executemany(
            "insert into position_entry_plan values (?, ?)",
            [[bar_dt, POSITION_RUN_ID] for bar_dt in dates],
        )
        con.executemany(
            "insert into position_exit_plan values (?, ?)",
            [[bar_dt, POSITION_RUN_ID] for bar_dt in dates],
        )


def seed_portfolio_plan_db(path: Path, dates: list[date]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        create_portfolio_plan_tables(con)
        con.execute(
            """
            insert into portfolio_plan_run
            values (?, 'portfolio_plan_build', 'bounded', 'day', 'completed', 'position.duckdb',
                    ?, ?, 0, 0, 'portfolio-plan-bounded-proof-v1',
                    'portfolio-plan-minimal-v1', ?, ?, ?)
            """,
            [
                PORTFOLIO_RUN_ID,
                len(dates),
                len([bar_dt for bar_dt in dates if bar_dt >= date(2024, 1, 5)]),
                POSITION_RUN_ID,
                POSITION_RUN_ID,
                created_at(),
            ],
        )
        con.execute(
            (
                "insert into portfolio_plan_audit values "
                "('portfolio-audit', ?, 'hard_audit_zero', 'hard', 'pass', 0, '{}', ?)"
            ),
            [PORTFOLIO_RUN_ID, created_at()],
        )
        admissions = []
        exposures = []
        for bar_dt in dates:
            symbol = "600000.SH"
            admission_id = f"adm-{bar_dt.isoformat()}"
            if bar_dt < date(2024, 1, 5):
                state = "rejected"
                reason = "no_target_exposure_before_first_admitted_day"
            else:
                state = "admitted"
                reason = "within_capacity_constraint"
                exposures.append(
                    (
                        f"exp-{bar_dt.isoformat()}",
                        admission_id,
                        "target_weight",
                        0.25,
                        125000.0,
                        100.0,
                        bar_dt,
                        None,
                        PORTFOLIO_RUN_ID,
                        "portfolio-plan-bounded-proof-v1",
                        "portfolio-plan-minimal-v1",
                        POSITION_RUN_ID,
                        created_at(),
                    )
                )
            admissions.append(
                (
                    admission_id,
                    f"pc-{bar_dt.isoformat()}",
                    symbol,
                    "day",
                    bar_dt,
                    state,
                    reason,
                    POSITION_RUN_ID,
                    PORTFOLIO_RUN_ID,
                    "portfolio-plan-bounded-proof-v1",
                    "portfolio-plan-minimal-v1",
                    created_at(),
                )
            )
        con.executemany(
            "insert into portfolio_admission_ledger values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            admissions,
        )
        con.executemany(
            "insert into portfolio_target_exposure values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            exposures,
        )


def create_portfolio_plan_tables(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        create table portfolio_plan_run (
            run_id varchar, runner_name varchar, mode varchar, timeframe varchar, status varchar,
            source_position_db varchar, admission_count bigint, target_exposure_count bigint,
            trim_count bigint, hard_fail_count bigint, schema_version varchar,
            portfolio_plan_rule_version varchar, source_position_release_version varchar,
            source_position_run_id varchar, created_at timestamp
        )
        """
    )
    con.execute(
        """
        create table portfolio_plan_audit (
            audit_id varchar, run_id varchar, check_name varchar, severity varchar,
            status varchar, failed_count bigint, sample_payload varchar, created_at timestamp
        )
        """
    )
    con.execute(
        """
        create table portfolio_admission_ledger (
            portfolio_admission_id varchar, position_candidate_id varchar, symbol varchar,
            timeframe varchar, plan_dt date, admission_state varchar, admission_reason varchar,
            source_position_release_version varchar, run_id varchar, schema_version varchar,
            portfolio_plan_rule_version varchar, created_at timestamp
        )
        """
    )
    con.execute(
        """
        create table portfolio_target_exposure (
            target_exposure_id varchar, portfolio_admission_id varchar, exposure_type varchar,
            target_weight double, target_notional double, target_quantity_hint double,
            exposure_valid_from date, exposure_valid_until date, run_id varchar,
            schema_version varchar, portfolio_plan_rule_version varchar,
            source_position_release_version varchar, created_at timestamp
        )
        """
    )
    con.execute(
        """
        create table portfolio_trim_ledger (
            portfolio_trim_id varchar, portfolio_admission_id varchar, trim_reason varchar,
            pre_trim_exposure double, post_trim_exposure double, constraint_name varchar,
            run_id varchar, schema_version varchar, portfolio_plan_rule_version varchar,
            source_position_release_version varchar, created_at timestamp
        )
        """
    )


def seed_trade_from_late_portfolio_source(tmp_path: Path, late_dates: list[date]) -> None:
    data_root = tmp_path / "data"
    late_source = tmp_path / "late-source" / "portfolio_plan.duckdb"
    seed_portfolio_plan_db(late_source, late_dates)
    summary = run_trade_build(
        TradeBuildRequest(
            source_portfolio_plan_db=late_source,
            target_trade_db=data_root / "trade.duckdb",
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id=TRADE_RUN_ID,
            mode="bounded",
            source_portfolio_plan_release_version=PORTFOLIO_RUN_ID,
            source_portfolio_plan_run_id=PORTFOLIO_RUN_ID,
            start_dt="2024-01-01",
            end_dt="2024-12-31",
        )
    )
    assert summary.hard_fail_count == 0


def seed_system_db(path: Path, data_root: Path, dates: list[date]) -> None:
    with duckdb.connect(str(path)) as con:
        con.execute(
            "create table system_readout_run (run_id varchar, status varchar, created_at timestamp)"
        )
        con.execute(
            """
            create table system_source_manifest (
                system_readout_run_id varchar, module_name varchar, source_db varchar,
                source_run_id varchar, source_release_version varchar
            )
            """
        )
        con.execute(
            "create table system_chain_readout (system_readout_run_id varchar, readout_dt date)"
        )
        con.execute(
            "insert into system_readout_run values (?, 'completed', ?)",
            [SYSTEM_RUN_ID, created_at()],
        )
        manifest_rows = [
            [
                SYSTEM_RUN_ID,
                "malf",
                str(data_root / "malf_service_day.duckdb"),
                MALF_RUN_ID,
                MALF_RUN_ID,
            ],
            [
                SYSTEM_RUN_ID,
                "signal",
                str(data_root / "signal.duckdb"),
                SIGNAL_RUN_ID,
                SIGNAL_RUN_ID,
            ],
            [
                SYSTEM_RUN_ID,
                "position",
                str(data_root / "position.duckdb"),
                POSITION_RUN_ID,
                POSITION_RUN_ID,
            ],
            [
                SYSTEM_RUN_ID,
                "portfolio_plan",
                str(data_root / "portfolio_plan.duckdb"),
                PORTFOLIO_RUN_ID,
                PORTFOLIO_RUN_ID,
            ],
            [
                SYSTEM_RUN_ID,
                "trade",
                str(data_root / "trade.duckdb"),
                TRADE_RUN_ID,
                TRADE_RUN_ID,
            ],
        ]
        manifest_rows.extend(
            [
                [
                    SYSTEM_RUN_ID,
                    f"alpha_{family}",
                    str(data_root / f"alpha_{family}.duckdb"),
                    ALPHA_RUN_ID,
                    ALPHA_RUN_ID,
                ]
                for family in ALPHA_FAMILIES
            ]
        )
        con.executemany(
            "insert into system_source_manifest values (?, ?, ?, ?, ?)",
            manifest_rows,
        )
        con.executemany(
            "insert into system_chain_readout values (?, ?)",
            [[SYSTEM_RUN_ID, bar_dt] for bar_dt in dates],
        )


def trading_dates(*, start: str = "2024-01-02") -> list[date]:
    start_dt = date.fromisoformat(start)
    current = start_dt
    dates: list[date] = []
    while current <= date(2024, 12, 31):
        if current.weekday() < 5 and current.isoformat() != "2024-01-01":
            dates.append(current)
        current += timedelta(days=1)
    return dates


def created_at() -> datetime:
    return datetime(2026, 5, 10, 12, 0, 0)
