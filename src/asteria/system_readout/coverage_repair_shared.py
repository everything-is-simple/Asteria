from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

import duckdb

from asteria.pipeline.year_replay_coverage_gap_contracts import PIPELINE_REPAIR_CARD


def system_readout_report_dir(report_root: Path, run_id: str) -> Path:
    return report_root / "system_readout" / utc_now().date().isoformat() / run_id


def summary_status(
    *,
    hard_fail_count: int,
    followup_next_card: str,
    followup_attribution: str,
) -> str:
    if hard_fail_count != 0:
        return "failed"
    if followup_next_card != PIPELINE_REPAIR_CARD:
        return "failed"
    if followup_attribution != "calendar_semantic_gap_only":
        return "failed"
    return "completed"


def count_rows(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    key_name: str,
    run_id: str,
) -> int:
    row = con.execute(
        f"select count(*) from {table_name} where {key_name} = ?",
        [run_id],
    ).fetchone()
    return 0 if row is None or row[0] is None else int(row[0])


def key_in_focus_window(
    key: tuple[str, date],
    build_request_start: date | None,
    build_request_end: date | None,
) -> bool:
    _, row_date = key
    if build_request_start and row_date < build_request_start:
        return False
    return not (build_request_end and row_date > build_request_end)


def build_earliest_day_map(rows: list[dict[str, object]]) -> dict[str, str]:
    mapped: dict[str, list[str]] = {}
    for row in rows:
        layer = str(row["layer"])
        observed_start = row["observed_start"]
        if observed_start is None:
            continue
        mapped.setdefault(layer, []).append(str(observed_start))
    return {layer: min(values) if values else "none" for layer, values in mapped.items()}


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
