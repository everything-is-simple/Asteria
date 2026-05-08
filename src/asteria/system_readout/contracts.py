from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

SYSTEM_READOUT_SCHEMA_VERSION = "system-readout-bounded-proof-v1"
SYSTEM_READOUT_VERSION = "system-readout-chain-day-v1"
ALPHA_FAMILIES = ("bof", "tst", "pb", "cpb", "bpb")
VALID_SYSTEM_READOUT_RUN_MODES = {"audit-only", "bounded", "resume"}
VALID_SYSTEM_READOUT_TIMEFRAMES = {"day"}


@dataclass(frozen=True)
class SystemReadoutBuildRequest:
    source_malf_service_db: Path
    source_alpha_root: Path
    source_signal_db: Path
    source_position_db: Path
    source_portfolio_plan_db: Path
    source_trade_db: Path
    target_system_db: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    run_id: str
    mode: str
    source_chain_release_version: str
    schema_version: str = SYSTEM_READOUT_SCHEMA_VERSION
    system_readout_version: str = SYSTEM_READOUT_VERSION
    timeframe: str = "day"
    start_dt: str | None = None
    end_dt: str | None = None
    symbol_limit: int | None = None

    def __post_init__(self) -> None:
        if self.mode not in VALID_SYSTEM_READOUT_RUN_MODES:
            raise ValueError(f"Unsupported System Readout run mode: {self.mode}")
        if self.timeframe not in VALID_SYSTEM_READOUT_TIMEFRAMES:
            raise ValueError(f"Unsupported System Readout timeframe: {self.timeframe}")
        if self.mode == "bounded" and not (
            self.start_dt or self.end_dt or self.symbol_limit is not None
        ):
            raise ValueError(
                "bounded System Readout runs require start_dt, end_dt, or symbol_limit"
            )
        if not self.source_chain_release_version:
            raise ValueError("source_chain_release_version is required")
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
        return self.temp_root / "system_readout" / self.run_id / "system-staging.duckdb"

    @property
    def alpha_db_paths(self) -> dict[str, Path]:
        return {
            family.upper(): self.source_alpha_root / f"alpha_{family}.duckdb"
            for family in ALPHA_FAMILIES
        }

    def checkpoint_path(self, stage: str) -> Path:
        return self.temp_root / "system_readout" / self.run_id / f"{self.timeframe}-{stage}.json"


@dataclass(frozen=True)
class SystemReadoutBuildSummary:
    run_id: str
    stage: str
    status: str
    timeframe: str = "day"
    source_manifest_count: int = 0
    module_status_count: int = 0
    readout_count: int = 0
    summary_count: int = 0
    audit_snapshot_count: int = 0
    hard_fail_count: int = 0
    report_path: str | None = None
    manifest_path: str | None = None
    closeout_path: str | None = None
    validated_zip: str | None = None
    resume_reused: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
