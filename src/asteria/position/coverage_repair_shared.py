from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from asteria.pipeline.year_replay_coverage_gap_contracts import (
    EVIDENCE_INCOMPLETE_CARD,
    POSITION_REPAIR_CARD,
)


def build_earliest_day_map(rows: list[dict[str, object]]) -> dict[str, str]:
    mapped: dict[str, list[str]] = {
        "signal": [],
        "position": [],
        "portfolio_plan": [],
        "trade": [],
    }
    for row in rows:
        layer = str(row["layer"])
        observed_start = row["observed_start"]
        if observed_start is None or layer not in mapped:
            continue
        mapped[layer].append(str(observed_start))
    return {layer: min(values) if values else "none" for layer, values in mapped.items()}


def position_report_dir(report_root: Path, run_id: str) -> Path:
    return report_root / "position" / utc_now().date().isoformat() / run_id


def summary_status(
    *,
    hard_fail_count: int,
    followup_next_card: str,
    followup_attribution: str,
) -> str:
    if hard_fail_count != 0:
        return "failed"
    if followup_attribution == "evidence_incomplete":
        return "failed"
    if followup_next_card == POSITION_REPAIR_CARD:
        return "failed"
    if (
        followup_next_card == EVIDENCE_INCOMPLETE_CARD
        and followup_attribution != "downstream_surface_gap:trade"
    ):
        return "failed"
    return "completed"


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
