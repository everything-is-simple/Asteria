from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

ALPHA_SCHEMA_VERSION = "alpha-bounded-proof-v1"
ALPHA_RULE_VERSION = "alpha-waveposition-minimal-v1"
VALID_ALPHA_FAMILIES = {"BOF", "TST", "PB", "CPB", "BPB"}
VALID_ALPHA_RUN_MODES = {"bounded", "resume", "audit-only"}
VALID_ALPHA_TIMEFRAMES = {"day"}


@dataclass(frozen=True)
class AlphaFamilyRequest:
    source_malf_db: Path
    target_alpha_db: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    run_id: str
    mode: str
    alpha_family: str
    source_malf_service_version: str
    schema_version: str = ALPHA_SCHEMA_VERSION
    alpha_rule_version: str = ALPHA_RULE_VERSION
    timeframe: str = "day"
    start_dt: str | None = None
    end_dt: str | None = None
    symbol_limit: int | None = None

    def __post_init__(self) -> None:
        family = self.alpha_family.upper()
        object.__setattr__(self, "alpha_family", family)
        if family not in VALID_ALPHA_FAMILIES:
            raise ValueError(f"Unsupported Alpha family: {self.alpha_family}")
        if self.mode not in VALID_ALPHA_RUN_MODES:
            raise ValueError(f"Unsupported Alpha run mode: {self.mode}")
        if self.timeframe not in VALID_ALPHA_TIMEFRAMES:
            raise ValueError(f"Unsupported Alpha timeframe: {self.timeframe}")
        if self.mode == "bounded" and not (
            self.start_dt or self.end_dt or self.symbol_limit is not None
        ):
            raise ValueError("bounded Alpha runs require start_dt, end_dt, or symbol_limit")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_dt cannot be later than end_dt")

    @property
    def start_date(self) -> date | None:
        return date.fromisoformat(self.start_dt) if self.start_dt else None

    @property
    def end_date(self) -> date | None:
        return date.fromisoformat(self.end_dt) if self.end_dt else None

    def checkpoint_path(self, stage: str) -> Path:
        return self.temp_root / "alpha" / self.run_id / f"{self.alpha_family}-{stage}.json"


@dataclass(frozen=True)
class AlphaBuildSummary:
    run_id: str
    alpha_family: str
    stage: str
    status: str
    event_count: int = 0
    score_count: int = 0
    candidate_count: int = 0
    hard_fail_count: int = 0
    report_path: str | None = None
    resume_reused: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
