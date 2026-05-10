from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import duckdb
from tests.unit.position.position_2024_coverage_repair_support import (
    ALPHA_FAMILIES,
    ALPHA_RUN_ID,
    MALF_RUN_ID,
    PORTFOLIO_RUN_ID,
    POSITION_RUN_ID,
    SIGNAL_RUN_ID,
    SYSTEM_RUN_ID,
    TRADE_RUN_ID,
    trading_dates,
)

from asteria.position.rules import SignalInput


def seed_system_db(path: Path, data_root: Path) -> None:
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
        rows = [
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
        rows.extend(
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
        con.executemany("insert into system_source_manifest values (?, ?, ?, ?, ?)", rows)
        con.executemany(
            "insert into system_chain_readout values (?, ?)",
            [[SYSTEM_RUN_ID, bar_dt] for bar_dt in trading_dates(start="2024-01-09")],
        )


def signal_input(
    *,
    signal_id: str,
    signal_dt: date,
    signal_state: str,
    signal_bias: str,
) -> SignalInput:
    return SignalInput(
        signal_id=signal_id,
        symbol="600000.SH",
        timeframe="day",
        signal_dt=signal_dt,
        signal_type=(
            "directional_opportunity" if signal_state == "active" else "conflict_or_weak_signal"
        ),
        signal_state=signal_state,
        signal_bias=signal_bias if signal_state == "active" else "neutral",
        signal_strength=0.8,
        confidence_bucket="high",
        reason_code=(
            "alpha_candidate_support"
            if signal_state == "active"
            else "signal_strength_below_threshold"
        ),
        source_alpha_release_version=ALPHA_RUN_ID,
        run_id=SIGNAL_RUN_ID,
        schema_version="signal-bounded-proof-v1",
        signal_rule_version="signal-alpha-aggregation-minimal-v1",
    )
