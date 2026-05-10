from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

FOCUS_START = "2024-01-02"
FOCUS_END = "2024-01-05"
FOCUS_DATES = (FOCUS_START, "2024-01-03", "2024-01-04", FOCUS_END)


@dataclass(frozen=True)
class Position2024CoverageRepairRequest:
    repo_root: Path
    source_system_db: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    run_id: str
    target_year: int = 2024
    focus_start_dt: str = FOCUS_START
    focus_end_dt: str = FOCUS_END

    def __post_init__(self) -> None:
        if not self.run_id:
            raise ValueError("run_id is required")
        if self.target_year != 2024:
            raise ValueError("Position 2024 repair is locked to target_year=2024")
        if self.focus_start_dt != FOCUS_START or self.focus_end_dt != FOCUS_END:
            raise ValueError("Position 2024 repair focus window is fixed to 2024-01-02..2024-01-05")

    @property
    def data_root(self) -> Path:
        return self.source_system_db.parent

    @property
    def run_root(self) -> Path:
        return self.temp_root / "position" / self.run_id


@dataclass(frozen=True)
class Position2024CoverageRepairSummary:
    run_id: str
    status: str
    released_system_run_id: str
    released_position_run_id: str
    released_signal_run_id: str
    repaired_focus_dates: tuple[str, ...]
    input_signal_count: int
    position_candidate_count: int
    entry_plan_count: int
    exit_plan_count: int
    hard_fail_count: int
    followup_next_card: str
    followup_attribution: str
    audit_report_path: str
    manifest_path: str
    closeout_path: str
    validated_zip: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
