from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class DownstreamCoverageGapCloseoutRequest:
    repo_root: Path
    source_system_db: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    run_id: str
    target_year: int
    data_root: Path | None = None

    def __post_init__(self) -> None:
        if not self.run_id:
            raise ValueError("run_id is required")
        if self.target_year < 2000:
            raise ValueError("target_year must be a natural year")
        if self.data_root is None:
            object.__setattr__(self, "data_root", self.source_system_db.parent)

    @property
    def run_root(self) -> Path:
        return self.temp_root / "pipeline" / self.run_id


@dataclass(frozen=True)
class DownstreamCoverageGapCloseoutDecision:
    next_card: str
    attribution: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class DownstreamCoverageGapCloseoutSummary:
    run_id: str
    target_year: int
    probe_system_db: str
    probe_diagnosis_run_id: str
    next_card: str
    attribution: str
    manifest_path: str
    closeout_path: str
    validated_zip: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)
