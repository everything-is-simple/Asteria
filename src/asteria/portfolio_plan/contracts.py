from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

PORTFOLIO_PLAN_SCHEMA_VERSION = "portfolio-plan-bounded-proof-v1"
PORTFOLIO_PLAN_RULE_VERSION = "portfolio-position-capacity-minimal-v1"
PORTFOLIO_PLAN_MAX_ACTIVE_SYMBOLS = 3
VALID_PORTFOLIO_PLAN_RUN_MODES = {"audit-only", "bounded", "resume"}
VALID_PORTFOLIO_PLAN_TIMEFRAMES = {"day"}


@dataclass(frozen=True)
class PortfolioPlanBuildRequest:
    source_position_db: Path
    target_portfolio_plan_db: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    run_id: str
    mode: str
    source_position_release_version: str
    source_position_run_id: str | None = None
    schema_version: str = PORTFOLIO_PLAN_SCHEMA_VERSION
    portfolio_plan_rule_version: str = PORTFOLIO_PLAN_RULE_VERSION
    timeframe: str = "day"
    start_dt: str | None = None
    end_dt: str | None = None
    symbol_limit: int | None = None
    max_active_symbols: int = PORTFOLIO_PLAN_MAX_ACTIVE_SYMBOLS

    def __post_init__(self) -> None:
        if self.mode not in VALID_PORTFOLIO_PLAN_RUN_MODES:
            raise ValueError(f"Unsupported Portfolio Plan run mode: {self.mode}")
        if self.timeframe not in VALID_PORTFOLIO_PLAN_TIMEFRAMES:
            raise ValueError(f"Unsupported Portfolio Plan timeframe: {self.timeframe}")
        if self.mode == "bounded" and not (
            self.start_dt or self.end_dt or self.symbol_limit is not None
        ):
            raise ValueError(
                "bounded Portfolio Plan runs require start_dt, end_dt, or symbol_limit"
            )
        if not self.source_position_release_version:
            raise ValueError("source_position_release_version is required")
        if self.max_active_symbols <= 0:
            raise ValueError("max_active_symbols must be positive")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_dt cannot be later than end_dt")

    @property
    def start_date(self) -> date | None:
        return date.fromisoformat(self.start_dt) if self.start_dt else None

    @property
    def end_date(self) -> date | None:
        return date.fromisoformat(self.end_dt) if self.end_dt else None

    @property
    def staging_db_path(self) -> Path:
        return self.temp_root / "portfolio_plan" / self.run_id / "portfolio_plan-staging.duckdb"

    def checkpoint_path(self, stage: str) -> Path:
        return self.temp_root / "portfolio_plan" / self.run_id / f"{self.timeframe}-{stage}.json"


@dataclass(frozen=True)
class PortfolioPlanBuildSummary:
    run_id: str
    stage: str
    status: str
    timeframe: str = "day"
    input_position_count: int = 0
    admission_count: int = 0
    target_exposure_count: int = 0
    trim_count: int = 0
    hard_fail_count: int = 0
    report_path: str | None = None
    manifest_path: str | None = None
    closeout_path: str | None = None
    validated_zip: str | None = None
    resume_reused: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
