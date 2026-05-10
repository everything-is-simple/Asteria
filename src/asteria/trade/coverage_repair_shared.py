from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from asteria.pipeline.year_replay_coverage_gap_contracts import SYSTEM_REPAIR_CARD


def trade_report_dir(report_root: Path, run_id: str) -> Path:
    return report_root / "trade" / utc_now().date().isoformat() / run_id


def summary_status(
    *,
    hard_fail_count: int,
    followup_next_card: str,
    followup_attribution: str,
) -> str:
    if hard_fail_count != 0:
        return "failed"
    if followup_next_card != SYSTEM_REPAIR_CARD:
        return "failed"
    if followup_attribution != "released_surface_gap:system_readout":
        return "failed"
    return "completed"


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
