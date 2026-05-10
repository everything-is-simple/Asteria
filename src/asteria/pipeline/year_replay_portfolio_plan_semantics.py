from __future__ import annotations

from pathlib import Path

import duckdb

from asteria.pipeline.year_replay_coverage_gap_contracts import CoverageMatrixRow


def evaluate_portfolio_plan_focus_window(
    *,
    portfolio_rows: list[CoverageMatrixRow],
    portfolio_db: Path,
    portfolio_run_id: str,
    focus_dates: list[str],
) -> bool:
    if len(portfolio_rows) != 2:
        return False

    row_map = {row.surface_name: row for row in portfolio_rows}
    admission_row = row_map.get("portfolio_admission_ledger")
    exposure_row = row_map.get("portfolio_target_exposure")
    if admission_row is None or exposure_row is None:
        return False
    if sorted(admission_row.missing_focus_dates):
        return False

    required_exposure_dates = load_required_portfolio_exposure_focus_dates(
        portfolio_db=portfolio_db,
        portfolio_run_id=portfolio_run_id,
        focus_dates=focus_dates,
    )
    missing_required = sorted(
        set(required_exposure_dates).intersection(exposure_row.missing_focus_dates)
    )
    return not missing_required


def load_required_portfolio_exposure_focus_dates(
    *,
    portfolio_db: Path,
    portfolio_run_id: str,
    focus_dates: list[str],
) -> list[str]:
    with duckdb.connect(str(portfolio_db), read_only=True) as con:
        columns = {
            str(row[0]) for row in con.execute("describe portfolio_admission_ledger").fetchall()
        }
        if "admission_state" not in columns:
            return list(focus_dates)
        rows = con.execute(
            """
            select distinct plan_dt
            from portfolio_admission_ledger
            where run_id = ?
              and plan_dt >= ?
              and plan_dt <= ?
              and admission_state in ('admitted', 'trimmed')
            order by 1
            """,
            [portfolio_run_id, min(focus_dates), max(focus_dates)],
        ).fetchall()
    return [str(row[0]) for row in rows]
