from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

TRADE_SCHEMA_VERSION = "trade-bounded-proof-v1"
TRADE_RULE_VERSION = "trade-portfolio-plan-minimal-v1"
VALID_TRADE_RUN_MODES = {"audit-only", "bounded", "resume"}
VALID_TRADE_TIMEFRAMES = {"day"}


@dataclass(frozen=True)
class TradeBuildRequest:
    source_portfolio_plan_db: Path
    target_trade_db: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    run_id: str
    mode: str
    source_portfolio_plan_release_version: str
    source_portfolio_plan_run_id: str | None = None
    schema_version: str = TRADE_SCHEMA_VERSION
    trade_rule_version: str = TRADE_RULE_VERSION
    timeframe: str = "day"
    start_dt: str | None = None
    end_dt: str | None = None
    symbol_limit: int | None = None

    def __post_init__(self) -> None:
        if self.mode not in VALID_TRADE_RUN_MODES:
            raise ValueError(f"Unsupported Trade run mode: {self.mode}")
        if self.timeframe not in VALID_TRADE_TIMEFRAMES:
            raise ValueError(f"Unsupported Trade timeframe: {self.timeframe}")
        if self.mode == "bounded" and not self.source_portfolio_plan_release_version:
            raise ValueError("bounded Trade runs require source_portfolio_plan_release_version")

    @property
    def staging_db_path(self) -> Path:
        return self.temp_root / "trade" / self.run_id / f"{self.timeframe}-staging.duckdb"

    def checkpoint_path(self, stage: str) -> Path:
        return self.temp_root / "trade" / self.run_id / f"{self.timeframe}-{stage}.json"


@dataclass(frozen=True)
class TradeBuildSummary:
    run_id: str
    stage: str
    status: str
    timeframe: str = "day"
    input_portfolio_plan_count: int = 0
    order_intent_count: int = 0
    execution_plan_count: int = 0
    fill_count: int = 0
    rejection_count: int = 0
    hard_fail_count: int = 0
    report_path: str | None = None
    manifest_path: str | None = None
    closeout_path: str | None = None
    validated_zip: str | None = None
    resume_reused: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
