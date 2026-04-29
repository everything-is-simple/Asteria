from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

SIGNAL_SCHEMA_VERSION = "signal-bounded-proof-v1"
SIGNAL_RULE_VERSION = "signal-alpha-aggregation-minimal-v1"
VALID_SIGNAL_RUN_MODES = {"bounded", "resume", "audit-only"}
VALID_SIGNAL_TIMEFRAMES = {"day"}


@dataclass(frozen=True)
class SignalBuildRequest:
    source_alpha_root: Path
    target_signal_db: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    run_id: str
    mode: str
    source_alpha_release_version: str
    schema_version: str = SIGNAL_SCHEMA_VERSION
    signal_rule_version: str = SIGNAL_RULE_VERSION
    timeframe: str = "day"
    start_dt: str | None = None
    end_dt: str | None = None
    symbol_limit: int | None = None

    def __post_init__(self) -> None:
        if self.mode not in VALID_SIGNAL_RUN_MODES:
            raise ValueError(f"Unsupported Signal run mode: {self.mode}")
        if self.timeframe not in VALID_SIGNAL_TIMEFRAMES:
            raise ValueError(f"Unsupported Signal timeframe: {self.timeframe}")
        if self.mode == "bounded" and not (
            self.start_dt or self.end_dt or self.symbol_limit is not None
        ):
            raise ValueError("bounded Signal runs require start_dt, end_dt, or symbol_limit")
        if not self.source_alpha_release_version:
            raise ValueError("source_alpha_release_version is required")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_dt cannot be later than end_dt")

    @property
    def start_date(self) -> date | None:
        return date.fromisoformat(self.start_dt) if self.start_dt else None

    @property
    def end_date(self) -> date | None:
        return date.fromisoformat(self.end_dt) if self.end_dt else None

    def checkpoint_path(self, stage: str) -> Path:
        return self.temp_root / "signal" / self.run_id / f"{stage}.json"


@dataclass(frozen=True)
class SignalBuildSummary:
    run_id: str
    stage: str
    status: str
    input_candidate_count: int = 0
    formal_signal_count: int = 0
    component_count: int = 0
    hard_fail_count: int = 0
    report_path: str | None = None
    manifest_path: str | None = None
    closeout_path: str | None = None
    validated_zip: str | None = None
    resume_reused: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
