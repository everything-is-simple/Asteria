from __future__ import annotations

from pathlib import Path

import duckdb

from asteria.pipeline.year_replay_coverage_gap_contracts import CoverageMatrixRow


def evaluate_position_focus_window(
    *,
    position_rows: list[CoverageMatrixRow],
    focus_dates: list[str],
    planned_signal_focus_dates: list[str],
) -> bool:
    if len(position_rows) != 3:
        return False

    row_map = {row.surface_name: row for row in position_rows}
    required_focus_dates = {
        "position_candidate_ledger": set(focus_dates),
        "position_entry_plan": set(planned_signal_focus_dates),
        "position_exit_plan": set(planned_signal_focus_dates),
    }
    ok = True
    for surface_name, required_dates in required_focus_dates.items():
        row = row_map.get(surface_name)
        if row is None:
            ok = False
            continue
        missing_required = sorted(required_dates.intersection(row.missing_focus_dates))
        if missing_required:
            ok = False
    return ok


def load_planned_signal_focus_dates(
    *,
    signal_db: Path,
    signal_run_id: str,
    focus_dates: list[str],
) -> list[str]:
    if not focus_dates:
        return []

    with duckdb.connect(str(signal_db), read_only=True) as con:
        columns = {str(row[0]) for row in con.execute("describe formal_signal_ledger").fetchall()}
        if not {"signal_dt", "signal_state", "signal_type", "run_id"}.issubset(columns):
            return list(focus_dates)
        placeholders = ", ".join("?" for _ in focus_dates)
        rows = con.execute(
            f"""
            select distinct signal_dt
            from formal_signal_ledger
            where run_id = ?
              and signal_state = 'active'
              and signal_type = 'directional_opportunity'
              and signal_dt in ({placeholders})
            order by signal_dt
            """,
            [signal_run_id, *focus_dates],
        ).fetchall()
    return [str(row[0]) for row in rows]
