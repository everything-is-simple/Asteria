from __future__ import annotations

from pathlib import Path

import duckdb

from asteria.pipeline.year_replay_coverage_gap_contracts import CoverageMatrixRow


def evaluate_trade_focus_window(
    *,
    trade_rows: list[CoverageMatrixRow],
    trade_db: Path,
    trade_run_id: str,
    focus_dates: list[str],
) -> bool:
    if len(trade_rows) < 3:
        return False
    row_map = {row.surface_name: row for row in trade_rows}
    if "order_intent_ledger" not in row_map:
        return False
    if "execution_plan_ledger" not in row_map:
        return False
    if "order_rejection_ledger" not in row_map:
        return False

    intent_dates = _load_dates(
        trade_db=trade_db,
        table_name="order_intent_ledger",
        date_column="intent_dt",
        run_id=trade_run_id,
        focus_dates=focus_dates,
    )
    execution_dates = _load_dates(
        trade_db=trade_db,
        table_name="execution_plan_ledger",
        date_column="execution_valid_from",
        run_id=trade_run_id,
        focus_dates=focus_dates,
    )
    rejection_dates = _load_dates(
        trade_db=trade_db,
        table_name="order_rejection_ledger",
        date_column="rejection_dt",
        run_id=trade_run_id,
        focus_dates=focus_dates,
    )
    focus_set = set(focus_dates)
    return focus_set.issubset(intent_dates | rejection_dates) and intent_dates.issubset(
        execution_dates
    )


def _load_dates(
    *,
    trade_db: Path,
    table_name: str,
    date_column: str,
    run_id: str,
    focus_dates: list[str],
) -> set[str]:
    with duckdb.connect(str(trade_db), read_only=True) as con:
        columns = {str(row[0]) for row in con.execute(f"describe {table_name}").fetchall()}
        if "run_id" not in columns or date_column not in columns:
            return set()
        rows = con.execute(
            f"""
            select distinct {date_column}
            from {table_name}
            where run_id = ?
              and {date_column} >= ?
              and {date_column} <= ?
            """,
            [run_id, min(focus_dates), max(focus_dates)],
        ).fetchall()
    return {str(row[0]) for row in rows}
