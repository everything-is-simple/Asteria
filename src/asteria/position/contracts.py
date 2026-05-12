from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

POSITION_SCHEMA_VERSION = "position-bounded-proof-v1"
POSITION_RULE_VERSION = "position-signal-plan-minimal-v1"
POSITION_DAILY_INCREMENTAL_SCHEMA_VERSION = "position-daily-incremental-ledger-v1"
VALID_POSITION_RUN_MODES = {"audit-only", "bounded", "daily_incremental", "resume"}
VALID_POSITION_TIMEFRAMES = {"day"}


@dataclass(frozen=True)
class PositionBuildRequest:
    source_signal_db: Path
    target_position_db: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    run_id: str
    mode: str
    source_signal_release_version: str
    source_signal_run_id: str | None = None
    schema_version: str = POSITION_SCHEMA_VERSION
    position_rule_version: str = POSITION_RULE_VERSION
    timeframe: str = "day"
    start_dt: str | None = None
    end_dt: str | None = None
    symbol_limit: int | None = None
    symbols: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        if self.mode not in VALID_POSITION_RUN_MODES:
            raise ValueError(f"Unsupported Position run mode: {self.mode}")
        if self.timeframe not in VALID_POSITION_TIMEFRAMES:
            raise ValueError(f"Unsupported Position timeframe: {self.timeframe}")
        if self.mode == "bounded" and not (
            self.start_dt or self.end_dt or self.symbol_limit is not None
        ):
            raise ValueError("bounded Position runs require start_dt, end_dt, or symbol_limit")
        if not self.source_signal_release_version:
            raise ValueError("source_signal_release_version is required")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_dt cannot be later than end_dt")

    @property
    def start_date(self) -> date | None:
        return date.fromisoformat(self.start_dt) if self.start_dt else None

    @property
    def end_date(self) -> date | None:
        return date.fromisoformat(self.end_dt) if self.end_dt else None

    def checkpoint_path(self, stage: str) -> Path:
        return self.temp_root / "position" / self.run_id / f"{self.timeframe}-{stage}.json"


@dataclass(frozen=True)
class PositionBuildSummary:
    run_id: str
    stage: str
    status: str
    timeframe: str = "day"
    input_signal_count: int = 0
    position_candidate_count: int = 0
    entry_plan_count: int = 0
    exit_plan_count: int = 0
    hard_fail_count: int = 0
    report_path: str | None = None
    manifest_path: str | None = None
    closeout_path: str | None = None
    validated_zip: str | None = None
    resume_reused: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PositionDailyIncrementalLedgerRequest:
    source_signal_db: Path
    target_position_db: Path
    temp_root: Path
    report_root: Path
    run_id: str
    mode: str
    signal_daily_impact_scope_path: Path
    signal_lineage_path: Path
    signal_checkpoint_path: Path
    batch_size: int = 1
    timeframe: str = "day"
    schema_version: str = POSITION_DAILY_INCREMENTAL_SCHEMA_VERSION
    position_rule_version: str = POSITION_RULE_VERSION
    source_signal_release_version: str = "signal-daily-incremental-sample"

    def __post_init__(self) -> None:
        if self.mode not in {"daily_incremental", "resume", "audit-only"}:
            raise ValueError(f"Unsupported Position daily incremental mode: {self.mode}")
        if self.timeframe != "day":
            raise ValueError("Position daily incremental sample is day-only")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")

    @property
    def run_root(self) -> Path:
        return self.temp_root / "position" / self.run_id

    @property
    def report_dir(self) -> Path:
        return self.report_root / "position" / "2026-05-12" / self.run_id

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
class PositionDailyIncrementalLedgerSummary:
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
