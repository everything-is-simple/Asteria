from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

import duckdb

from asteria.pipeline.year_replay_coverage_gap_diagnosis import (
    YearReplayCoverageGapDiagnosisRequest,
    run_year_replay_coverage_gap_diagnosis,
)

MALF_RUN_ID = "malf-v1-4-core-runtime-sync-implementation-20260505-01"
ALPHA_RUN_ID = "alpha-production-builder-hardening-20260506-01"
SIGNAL_RUN_ID = "signal-production-builder-hardening-20260506-01"
POSITION_RUN_ID = "position-bounded-proof-build-card-20260506-01"
PORTFOLIO_RUN_ID = "portfolio-plan-bounded-proof-build-card-20260507-01"
TRADE_RUN_ID = "trade-bounded-proof-build-card-20260507-01"
SYSTEM_RUN_ID = "system-readout-bounded-proof-build-card-20260508-01"
ALPHA_FAMILIES = ("bof", "tst", "pb", "cpb", "bpb")
TARGET_YEAR = 2024


def test_recommends_malf_repair_when_data_covers_trading_start_but_malf_starts_late(
    tmp_path: Path,
) -> None:
    request = _seed_scenario(
        tmp_path,
        data_dates=_trading_dates(),
        malf_dates=_trading_dates(start="2024-01-08"),
        alpha_dates=_trading_dates(start="2024-01-08"),
        signal_dates=_trading_dates(start="2024-01-08"),
        position_dates=_trading_dates(start="2024-01-08"),
        portfolio_dates=_trading_dates(start="2024-01-08"),
        trade_dates=_trading_dates(start="2024-01-08"),
        system_dates=_trading_dates(start="2024-01-08"),
    )

    summary = run_year_replay_coverage_gap_diagnosis(request)

    assert (
        summary.recommended_next_card == "malf-2024-natural-year-coverage-repair-card-20260509-01"
    )
    matrix = json.loads(Path(summary.coverage_matrix_path).read_text(encoding="utf-8"))
    assert matrix["calendar_semantic_dates"] == ["2024-01-01", "2024-01-06", "2024-01-07"]
    assert matrix["focus_trading_dates"] == [
        "2024-01-02",
        "2024-01-03",
        "2024-01-04",
        "2024-01-05",
    ]


def test_recommends_pipeline_semantic_repair_when_released_surfaces_cover_all_trading_dates(
    tmp_path: Path,
) -> None:
    dates = _trading_dates()
    request = _seed_scenario(
        tmp_path,
        data_dates=dates,
        malf_dates=dates,
        alpha_dates=dates,
        signal_dates=dates,
        position_dates=dates,
        portfolio_dates=dates,
        trade_dates=dates,
        system_dates=dates,
    )

    summary = run_year_replay_coverage_gap_diagnosis(request)

    assert (
        summary.recommended_next_card
        == "pipeline-year-replay-source-selection-repair-card-20260509-01"
    )
    attribution = Path(summary.coverage_attribution_path).read_text(encoding="utf-8")
    assert "trading-day surface gap" in attribution
    assert "calendar-semantic gap" in attribution


def test_recommends_data_maintenance_when_foundation_misses_trading_start(
    tmp_path: Path,
) -> None:
    late_dates = _trading_dates(start="2024-01-08")
    request = _seed_scenario(
        tmp_path,
        data_dates=late_dates,
        malf_dates=late_dates,
        alpha_dates=late_dates,
        signal_dates=late_dates,
        position_dates=late_dates,
        portfolio_dates=late_dates,
        trade_dates=late_dates,
        system_dates=late_dates,
    )

    summary = run_year_replay_coverage_gap_diagnosis(request)

    assert (
        summary.recommended_next_card
        == "data-2024-natural-year-coverage-maintenance-card-20260509-01"
    )


def test_recommends_system_readout_repair_when_upstream_covers_trading_dates_but_system_does_not(
    tmp_path: Path,
) -> None:
    full_dates = _trading_dates()
    request = _seed_scenario(
        tmp_path,
        data_dates=full_dates,
        malf_dates=full_dates,
        alpha_dates=full_dates,
        signal_dates=full_dates,
        position_dates=full_dates,
        portfolio_dates=full_dates,
        trade_dates=full_dates,
        system_dates=_trading_dates(start="2024-01-08"),
    )

    summary = run_year_replay_coverage_gap_diagnosis(request)

    assert summary.recommended_next_card == "system-readout-2024-coverage-repair-card-20260509-01"


def test_falls_back_to_evidence_incomplete_when_manifest_cannot_lock_unique_break(
    tmp_path: Path,
) -> None:
    full_dates = _trading_dates()
    request = _seed_scenario(
        tmp_path,
        data_dates=full_dates,
        malf_dates=full_dates,
        alpha_dates=full_dates,
        signal_dates=full_dates,
        position_dates=full_dates,
        portfolio_dates=full_dates,
        trade_dates=full_dates,
        system_dates=full_dates,
    )
    _delete_signal_manifest_row(request.source_system_db)

    summary = run_year_replay_coverage_gap_diagnosis(request)

    assert (
        summary.recommended_next_card
        == "coverage-gap-evidence-incomplete-closeout-card-20260509-01"
    )


def _seed_scenario(
    tmp_path: Path,
    *,
    data_dates: list[date],
    malf_dates: list[date],
    alpha_dates: list[date],
    signal_dates: list[date],
    position_dates: list[date],
    portfolio_dates: list[date],
    trade_dates: list[date],
    system_dates: list[date],
) -> YearReplayCoverageGapDiagnosisRequest:
    data_root = tmp_path / "data"
    data_root.mkdir(parents=True, exist_ok=True)
    _seed_data_foundation(data_root, data_dates)
    _seed_malf_db(data_root / "malf_service_day.duckdb", malf_dates)
    for family in ALPHA_FAMILIES:
        _seed_alpha_db(data_root / f"alpha_{family}.duckdb", alpha_dates)
    _seed_signal_db(data_root / "signal.duckdb", signal_dates)
    _seed_position_db(data_root / "position.duckdb", position_dates)
    _seed_portfolio_plan_db(data_root / "portfolio_plan.duckdb", portfolio_dates)
    _seed_trade_db(data_root / "trade.duckdb", trade_dates)
    _seed_system_db(data_root / "system.duckdb", data_root, system_dates)
    return YearReplayCoverageGapDiagnosisRequest(
        repo_root=tmp_path / "repo",
        source_system_db=data_root / "system.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        run_id="pipeline-year-replay-coverage-gap-diagnosis-unit-001",
        target_year=TARGET_YEAR,
    )


def _seed_data_foundation(data_root: Path, dates: list[date]) -> None:
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
            [[bar_dt] for bar_dt in dates],
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
        con.executemany("insert into trade_calendar values (?)", [[bar_dt] for bar_dt in dates])
        con.executemany(
            "insert into tradability_fact values ('600000.SH', ?)",
            [[bar_dt] for bar_dt in dates],
        )


def _seed_malf_db(path: Path, dates: list[date]) -> None:
    with duckdb.connect(str(path)) as con:
        con.execute("create table malf_wave_position (bar_dt date, run_id varchar)")
        con.executemany(
            "insert into malf_wave_position values (?, ?)",
            [[bar_dt, MALF_RUN_ID] for bar_dt in dates],
        )


def _seed_alpha_db(path: Path, dates: list[date]) -> None:
    with duckdb.connect(str(path)) as con:
        con.execute("create table alpha_signal_candidate (bar_dt date, run_id varchar)")
        con.executemany(
            "insert into alpha_signal_candidate values (?, ?)",
            [[bar_dt, ALPHA_RUN_ID] for bar_dt in dates],
        )


def _seed_signal_db(path: Path, dates: list[date]) -> None:
    with duckdb.connect(str(path)) as con:
        con.execute("create table formal_signal_ledger (signal_dt date, run_id varchar)")
        con.executemany(
            "insert into formal_signal_ledger values (?, ?)",
            [[bar_dt, SIGNAL_RUN_ID] for bar_dt in dates],
        )


def _seed_position_db(path: Path, dates: list[date]) -> None:
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


def _seed_portfolio_plan_db(path: Path, dates: list[date]) -> None:
    with duckdb.connect(str(path)) as con:
        con.execute("create table portfolio_admission_ledger (plan_dt date, run_id varchar)")
        con.execute(
            "create table portfolio_target_exposure (exposure_valid_from date, run_id varchar)"
        )
        con.executemany(
            "insert into portfolio_admission_ledger values (?, ?)",
            [[bar_dt, PORTFOLIO_RUN_ID] for bar_dt in dates],
        )
        con.executemany(
            "insert into portfolio_target_exposure values (?, ?)",
            [[bar_dt, PORTFOLIO_RUN_ID] for bar_dt in dates],
        )


def _seed_trade_db(path: Path, dates: list[date]) -> None:
    with duckdb.connect(str(path)) as con:
        con.execute("create table order_intent_ledger (intent_dt date, run_id varchar)")
        con.execute(
            "create table execution_plan_ledger (execution_valid_from date, run_id varchar)"
        )
        con.execute("create table order_rejection_ledger (rejection_dt date, run_id varchar)")
        con.execute("create table fill_ledger (execution_dt date, run_id varchar)")
        con.executemany(
            "insert into order_intent_ledger values (?, ?)",
            [[bar_dt, TRADE_RUN_ID] for bar_dt in dates],
        )
        con.executemany(
            "insert into execution_plan_ledger values (?, ?)",
            [[bar_dt, TRADE_RUN_ID] for bar_dt in dates],
        )
        con.executemany(
            "insert into order_rejection_ledger values (?, ?)",
            [[bar_dt, TRADE_RUN_ID] for bar_dt in dates],
        )


def _seed_system_db(path: Path, data_root: Path, dates: list[date]) -> None:
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table system_readout_run (
                run_id varchar,
                status varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table system_source_manifest (
                system_readout_run_id varchar,
                module_name varchar,
                source_db varchar,
                source_run_id varchar,
                source_release_version varchar
            )
            """
        )
        con.execute(
            """
            create table system_chain_readout (
                system_readout_run_id varchar,
                readout_dt date
            )
            """
        )
        con.execute(
            "insert into system_readout_run values (?, 'completed', ?)",
            [SYSTEM_RUN_ID, datetime(2026, 5, 8, 12, 0, 0)],
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
        con.executemany("insert into system_source_manifest values (?, ?, ?, ?, ?)", manifest_rows)
        con.executemany(
            "insert into system_chain_readout values (?, ?)",
            [[SYSTEM_RUN_ID, bar_dt] for bar_dt in dates],
        )


def _delete_signal_manifest_row(system_db: Path) -> None:
    with duckdb.connect(str(system_db)) as con:
        con.execute("delete from system_source_manifest where module_name = 'signal'")


def _trading_dates(*, start: str = "2024-01-02") -> list[date]:
    start_dt = date.fromisoformat(start)
    end_dt = date(TARGET_YEAR, 12, 31)
    current = start_dt
    dates: list[date] = []
    while current <= end_dt:
        if current.weekday() < 5 and current.isoformat() != "2024-01-01":
            dates.append(current)
        current += timedelta(days=1)
    return dates
