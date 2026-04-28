from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

DATA_SCHEMA_VERSION = "data-bootstrap-v1"
SOURCE_VENDOR = "tdx_offline_txt"

VALID_ADJ_MODES = {"backward", "forward", "none", "all"}
VALID_ASSET_TYPES = {"stock", "index", "block"}
VALID_RUN_MODES = {"bounded", "segmented", "full", "resume", "audit-only"}


@dataclass(frozen=True)
class TdxSourceFile:
    asset_type: str
    adj_mode: str
    symbol: str
    source_path: Path
    source_size_bytes: int
    source_mtime: datetime
    source_content_hash: str

    @property
    def source_file_key(self) -> str:
        return "|".join(
            (
                SOURCE_VENDOR,
                self.asset_type,
                self.adj_mode,
                self.symbol,
                self.source_content_hash[:16],
            )
        )


@dataclass(frozen=True)
class RawMarketBar:
    symbol: str
    asset_type: str
    timeframe: str
    bar_dt: date
    trade_date: date
    adj_mode: str
    open_px: float | None
    high_px: float | None
    low_px: float | None
    close_px: float | None
    volume: float | None
    amount: float | None


@dataclass(frozen=True)
class ParsedTdxFile:
    source: TdxSourceFile
    name: str
    header: str
    bars: tuple[RawMarketBar, ...]


@dataclass(frozen=True)
class DataBootstrapRequest:
    source_root: Path
    target_root: Path
    temp_root: Path
    asset_type: str
    adj_mode: str
    mode: str
    run_id: str
    start_dt: str | None = None
    end_dt: str | None = None
    symbol_limit: int | None = None

    def __post_init__(self) -> None:
        if self.asset_type not in VALID_ASSET_TYPES:
            raise ValueError(f"Unsupported asset type: {self.asset_type}")
        if self.adj_mode not in VALID_ADJ_MODES:
            raise ValueError(f"Unsupported adjustment mode: {self.adj_mode}")
        if self.mode not in VALID_RUN_MODES:
            raise ValueError(f"Unsupported run mode: {self.mode}")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_dt cannot be later than end_dt")

    @property
    def start_date(self) -> date | None:
        return date.fromisoformat(self.start_dt) if self.start_dt else None

    @property
    def end_date(self) -> date | None:
        return date.fromisoformat(self.end_dt) if self.end_dt else None

    @property
    def raw_db_path(self) -> Path:
        return self.target_root / "raw_market.duckdb"

    @property
    def base_db_path(self) -> Path:
        return self.target_root / "market_base_day.duckdb"

    @property
    def checkpoint_path(self) -> Path:
        return self.temp_root / "data" / self.run_id / "checkpoint.json"


@dataclass(frozen=True)
class DataBootstrapSummary:
    run_id: str
    status: str
    raw_db_path: str
    base_db_path: str
    source_file_count: int
    raw_rows_written: int
    base_rows_written: int
    dirty_scope_count: int
    resume_reused: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LegacyCoverageSummary:
    legacy_raw_path: str
    legacy_base_path: str
    asset_type: str
    adj_mode: str
    raw_symbol_count: int
    base_symbol_count: int
    raw_row_count: int
    base_row_count: int
    raw_only_symbols: tuple[str, ...]
    base_only_symbols: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
