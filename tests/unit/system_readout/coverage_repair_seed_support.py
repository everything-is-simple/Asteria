from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb
from tests.unit.system_readout.support_upstream import ALPHA_FAMILIES


def seed_data_foundation(data_root: Path) -> None:
    with duckdb.connect(str(data_root / "market_base_day.duckdb")) as con:
        con.execute(
            """
            create table market_base_bar (
                symbol varchar,
                timeframe varchar,
                bar_dt date
            )
            """
        )
        con.executemany(
            "insert into market_base_bar values (?, 'day', ?)",
            [
                ("600000.SH", date(2024, 1, 2)),
                ("600001.SH", date(2024, 1, 3)),
                ("600000.SH", date(2024, 1, 4)),
                ("600000.SH", date(2024, 1, 5)),
            ],
        )
    with duckdb.connect(str(data_root / "market_meta.duckdb")) as con:
        con.execute("create table trade_calendar (trade_date date)")
        con.execute("create table tradability_fact (trade_date date)")
        rows = [
            (date(2024, 1, 2),),
            (date(2024, 1, 3),),
            (date(2024, 1, 4),),
            (date(2024, 1, 5),),
        ]
        con.executemany("insert into trade_calendar values (?)", rows)
        con.executemany("insert into tradability_fact values (?)", rows)


def clear_seed_day(data_root: Path, *, target_dt: date) -> None:
    with duckdb.connect(str(data_root / "malf_service_day.duckdb")) as con:
        con.execute("delete from malf_wave_position where bar_dt = ?", [target_dt])
    for family in ALPHA_FAMILIES:
        with duckdb.connect(str(data_root / f"alpha_{family}.duckdb")) as con:
            con.execute("delete from alpha_signal_candidate where bar_dt = ?", [target_dt])
            con.execute(
                """
                delete from alpha_score_ledger
                where alpha_event_id in (
                    select alpha_event_id
                    from alpha_event_ledger
                    where bar_dt = ?
                )
                """,
                [target_dt],
            )
            con.execute("delete from alpha_event_ledger where bar_dt = ?", [target_dt])
    with duckdb.connect(str(data_root / "signal.duckdb")) as con:
        con.execute(
            """
            delete from signal_component_ledger
            where signal_id in (
                select signal_id from formal_signal_ledger where signal_dt = ?
            )
            """,
            [target_dt],
        )
        con.execute("delete from formal_signal_ledger where signal_dt = ?", [target_dt])
    with duckdb.connect(str(data_root / "position.duckdb")) as con:
        con.execute("delete from position_entry_plan where entry_reference_dt = ?", [target_dt])
        con.execute("delete from position_exit_plan where exit_reference_dt = ?", [target_dt])
        con.execute("delete from position_candidate_ledger where candidate_dt = ?", [target_dt])
    with duckdb.connect(str(data_root / "portfolio_plan.duckdb")) as con:
        con.execute(
            "delete from portfolio_target_exposure where exposure_valid_from = ?",
            [target_dt],
        )
        con.execute("delete from portfolio_admission_ledger where plan_dt = ?", [target_dt])
    with duckdb.connect(str(data_root / "trade.duckdb")) as con:
        con.execute("delete from fill_ledger where execution_dt = ?", [target_dt])
        con.execute(
            "delete from execution_plan_ledger where execution_valid_from = ?",
            [target_dt],
        )
        con.execute("delete from order_intent_ledger where intent_dt = ?", [target_dt])
        con.execute("delete from order_rejection_ledger where rejection_dt = ?", [target_dt])
        con.execute("delete from trade_portfolio_snapshot where plan_dt = ?", [target_dt])
