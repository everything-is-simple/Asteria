from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

ALPHA_SCHEMA_VERSION = "alpha-family-schema-v1"
ALPHA_RULE_VERSION = "alpha-waveposition-production-v1"
ALPHA_DAILY_INCREMENTAL_SCHEMA_VERSION = "alpha-daily-incremental-ledger-v1"
VALID_ALPHA_FAMILIES = {"BOF", "TST", "PB", "CPB", "BPB"}
VALID_ALPHA_RUN_MODES = {
    "audit-only",
    "bounded",
    "daily_incremental",
    "full",
    "resume",
    "segmented",
}
VALID_ALPHA_TIMEFRAMES = {"day", "month", "week"}


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
    source_malf_run_id: str | None = None
    source_malf_sample_version: str | None = None
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
        if self.mode in {"bounded", "daily_incremental", "segmented"} and not (
            self.start_dt or self.end_dt or self.symbol_limit is not None
        ):
            raise ValueError(f"{self.mode} Alpha runs require start_dt, end_dt, or symbol_limit")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_dt cannot be later than end_dt")

    @property
    def start_date(self) -> date | None:
        return date.fromisoformat(self.start_dt) if self.start_dt else None

    @property
    def end_date(self) -> date | None:
        return date.fromisoformat(self.end_dt) if self.end_dt else None

    def checkpoint_path(self, stage: str) -> Path:
        name = f"{self.alpha_family}-{self.timeframe}-{stage}.json"
        return self.temp_root / "alpha" / self.run_id / name


@dataclass(frozen=True)
class AlphaBuildSummary:
    run_id: str
    alpha_family: str
    stage: str
    status: str
    timeframe: str = "day"
    event_count: int = 0
    score_count: int = 0
    candidate_count: int = 0
    hard_fail_count: int = 0
    report_path: str | None = None
    resume_reused: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AlphaDailyIncrementalLedgerRequest:
    source_malf_root: Path
    target_root: Path
    temp_root: Path
    report_root: Path
    run_id: str
    mode: str
    malf_daily_impact_scope_path: Path
    malf_lineage_path: Path
    malf_checkpoint_path: Path
    batch_size: int = 1
    timeframe: str = "day"
    schema_version: str = ALPHA_DAILY_INCREMENTAL_SCHEMA_VERSION
    alpha_rule_version: str = ALPHA_RULE_VERSION
    source_malf_service_version: str = "service-v1"

    def __post_init__(self) -> None:
        if self.mode not in {"daily_incremental", "resume", "audit-only"}:
            raise ValueError(f"Unsupported Alpha daily incremental mode: {self.mode}")
        if self.timeframe != "day":
            raise ValueError("Alpha daily incremental sample is day-only")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")

    @property
    def run_root(self) -> Path:
        return self.temp_root / "alpha" / self.run_id

    @property
    def report_dir(self) -> Path:
        return self.report_root / "alpha" / "2026-05-11" / self.run_id

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
class AlphaDailyIncrementalLedgerSummary:
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
