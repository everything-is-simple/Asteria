from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

MALF_SCHEMA_VERSION = "malf-v1-4-runtime-sync-v1"
VALID_TIMEFRAMES = {"day", "week", "month"}
VALID_RUN_MODES = {"bounded", "segmented", "full", "resume", "audit-only", "daily_incremental"}
DEFAULT_PIVOT_DETECTION_RULE_VERSION = "pivot-fractal-1bar-v1"
DEFAULT_CORE_EVENT_ORDERING_VERSION = "core-event-order-v1"
DEFAULT_PRICE_COMPARE_POLICY = "strict"
DEFAULT_EPSILON_POLICY = "none_after_price_normalization"


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
    schema_version: str = MALF_SCHEMA_VERSION
    timeframe: str = "day"
    core_rule_version: str | None = None
    lifespan_rule_version: str | None = None
    sample_version: str | None = None
    service_version: str | None = None
    pivot_detection_rule_version: str = DEFAULT_PIVOT_DETECTION_RULE_VERSION
    core_event_ordering_version: str = DEFAULT_CORE_EVENT_ORDERING_VERSION
    price_compare_policy: str = DEFAULT_PRICE_COMPARE_POLICY
    epsilon_policy: str = DEFAULT_EPSILON_POLICY
    source_market_base_run_id: str | None = None
    start_dt: str | None = None
    end_dt: str | None = None
    symbol_limit: int | None = None
    symbols: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.mode not in VALID_RUN_MODES:
            raise ValueError(f"Unsupported MALF run mode: {self.mode}")
        if self.timeframe not in VALID_TIMEFRAMES:
            raise ValueError(f"Unsupported MALF timeframe: {self.timeframe}")
        if self.mode == "bounded" and not (
            self.start_dt or self.end_dt or self.symbol_limit is not None or self.symbols
        ):
            raise ValueError("bounded MALF runs require date or symbol scope")
        if self.mode == "segmented" and not (
            self.start_dt or self.end_dt or self.symbol_limit is not None or self.symbols
        ):
            raise ValueError("segmented MALF runs require segmented scope")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_dt cannot be later than end_dt")
        if self.symbol_limit is not None and self.symbols:
            raise ValueError("Use either symbol_limit or explicit symbols, not both")

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
