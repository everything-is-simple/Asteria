from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import duckdb

from asteria.pipeline.year_replay_coverage_gap_contracts import CoverageMatrixRow


def all_focus_dates_present(rows: list[CoverageMatrixRow]) -> bool:
    return all(not row.missing_focus_dates for row in rows)


def load_first_week_focus_dates(target_year: int) -> tuple[list[str], list[str]]:
    week_start = date(target_year, 1, 1)
    week_dates = [week_start + timedelta(days=offset) for offset in range(7)]
    focus_trading_dates = [
        current.isoformat()
        for current in week_dates
        if current.isoformat()
        in {
            f"{target_year}-01-02",
            f"{target_year}-01-03",
            f"{target_year}-01-04",
            f"{target_year}-01-05",
        }
    ]
    trading_date_set = set(focus_trading_dates)
    calendar_semantic_dates = [
        current.isoformat() for current in week_dates if current.isoformat() not in trading_date_set
    ]
    return focus_trading_dates, calendar_semantic_dates


def system_full_year_gate_ok(system_db: Path, run_id: str, target_year: int) -> bool:
    with duckdb.connect(str(system_db), read_only=True) as con:
        row = con.execute(
            """
            select min(readout_dt), max(readout_dt)
            from system_chain_readout
            where system_readout_run_id = ?
              and readout_dt >= ?
              and readout_dt <= ?
            """,
            [run_id, f"{target_year}-01-01", f"{target_year}-12-31"],
        ).fetchone()
    if row is None or row[0] is None or row[1] is None:
        return False
    return str(row[0]) == f"{target_year}-01-01" and str(row[1]) == f"{target_year}-12-31"
