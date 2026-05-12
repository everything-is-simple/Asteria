from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

TRADE_SCHEMA_VERSION = "trade-bounded-proof-v1"
TRADE_RULE_VERSION = "trade-portfolio-plan-minimal-v1"
TRADE_DAILY_INCREMENTAL_SCHEMA_VERSION = "trade-daily-incremental-ledger-v1"
VALID_TRADE_RUN_MODES = {"audit-only", "bounded", "daily_incremental", "resume"}
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
    symbols: tuple[str, ...] | None = None

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


@dataclass(frozen=True)
class TradeDailyIncrementalLedgerRequest:
    source_portfolio_plan_db: Path
    target_trade_db: Path
    temp_root: Path
    report_root: Path
    run_id: str
    mode: str
    portfolio_plan_daily_impact_scope_path: Path
    portfolio_plan_lineage_path: Path
    portfolio_plan_checkpoint_path: Path
    batch_size: int = 1
    timeframe: str = "day"
    schema_version: str = TRADE_DAILY_INCREMENTAL_SCHEMA_VERSION
    trade_rule_version: str = TRADE_RULE_VERSION
    source_portfolio_plan_release_version: str = "portfolio-plan-daily-incremental-sample"

    def __post_init__(self) -> None:
        if self.mode not in {"daily_incremental", "resume", "audit-only"}:
            raise ValueError(f"Unsupported Trade daily incremental mode: {self.mode}")
        if self.timeframe != "day":
            raise ValueError("Trade daily incremental sample is day-only")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")

    @property
    def run_root(self) -> Path:
        return self.temp_root / "trade" / self.run_id

    @property
    def report_dir(self) -> Path:
        return self.report_root / "trade" / "2026-05-12" / self.run_id

    @property
    def source_manifest_path(self) -> Path:
        return self.run_root / "source-manifest.json"

    @property
    def derived_replay_scope_path(self) -> Path:
        return self.run_root / "derived-replay-scope.json"

    @property
    def daily_impact_scope_path(self) -> Path:
        return self.run_root / "daily-impact-scope.json"

    @property
    def lineage_path(self) -> Path:
        return self.run_root / "lineage.json"

    @property
    def batch_ledger_path(self) -> Path:
        return self.run_root / "batch-ledger.jsonl"

    @property
    def checkpoint_path(self) -> Path:
        return self.run_root / "checkpoint.json"

    @property
    def audit_summary_path(self) -> Path:
        return self.report_dir / "audit-summary.json"


@dataclass(frozen=True)
class TradeDailyIncrementalLedgerSummary:
    run_id: str
    status: str
    mode: str
    timeframe: str
    schema_version: str
    batch_count: int
    replay_scope_count: int
    impact_scope_count: int
    source_manifest_path: str
    derived_replay_scope_path: str
    daily_impact_scope_path: str
    lineage_path: str
    batch_ledger_path: str
    checkpoint_path: str
    audit_summary_path: str
    resume_reused: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
