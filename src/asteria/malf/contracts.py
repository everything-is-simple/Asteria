from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

MALF_SCHEMA_VERSION = "malf-v1-4-runtime-sync-v1"
VALID_TIMEFRAMES = {"day"}
VALID_RUN_MODES = {"bounded", "segmented", "full", "resume", "audit-only"}
VALID_PRICE_COMPARE_POLICIES = {"strict"}
VALID_EPSILON_POLICIES = {"none_after_price_normalization"}


@dataclass(frozen=True)
class MalfDayRequest:
    source_db: Path
    core_db: Path
    lifespan_db: Path
    service_db: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    run_id: str
    mode: str
    pivot_detection_rule_version: str
    core_event_ordering_version: str
    price_compare_policy: str
    epsilon_policy: str
    schema_version: str = MALF_SCHEMA_VERSION
    timeframe: str = "day"
    core_rule_version: str | None = None
    lifespan_rule_version: str | None = None
    sample_version: str | None = None
    service_version: str | None = None
    start_dt: str | None = None
    end_dt: str | None = None
    symbol_limit: int | None = None

    def __post_init__(self) -> None:
        if self.mode not in VALID_RUN_MODES:
            raise ValueError(f"Unsupported MALF run mode: {self.mode}")
        if self.timeframe not in VALID_TIMEFRAMES:
            raise ValueError(f"Unsupported MALF timeframe: {self.timeframe}")
        if self.price_compare_policy not in VALID_PRICE_COMPARE_POLICIES:
            raise ValueError(f"Unsupported MALF price compare policy: {self.price_compare_policy}")
        if self.epsilon_policy not in VALID_EPSILON_POLICIES:
            raise ValueError(f"Unsupported MALF epsilon policy: {self.epsilon_policy}")
        if self.mode == "bounded" and not (
            self.start_dt or self.end_dt or self.symbol_limit is not None
        ):
            raise ValueError("bounded MALF runs require start_dt, end_dt, or symbol_limit")
        if self.mode == "segmented" and not (
            self.start_dt or self.end_dt or self.symbol_limit is not None
        ):
            raise ValueError("segmented MALF runs require segmented scope")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_dt cannot be later than end_dt")

    @property
    def start_date(self) -> date | None:
        return date.fromisoformat(self.start_dt) if self.start_dt else None

    @property
    def end_date(self) -> date | None:
        return date.fromisoformat(self.end_dt) if self.end_dt else None

    def checkpoint_path(self, stage: str) -> Path:
        return self.temp_root / "malf" / self.run_id / f"{stage}-checkpoint.json"


@dataclass(frozen=True)
class MalfBuildSummary:
    run_id: str
    stage: str
    status: str
    input_row_count: int = 0
    input_wave_count: int = 0
    published_row_count: int = 0
    report_path: str | None = None
    resume_reused: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
