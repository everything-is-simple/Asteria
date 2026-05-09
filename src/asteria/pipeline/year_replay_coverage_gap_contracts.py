from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

ALPHA_FAMILY_MODULES = ("alpha_bof", "alpha_tst", "alpha_pb", "alpha_cpb", "alpha_bpb")
DATA_REPAIR_CARD = "data-2024-natural-year-coverage-maintenance-card-20260509-01"
MALF_REPAIR_CARD = "malf-2024-natural-year-coverage-repair-card-20260509-01"
ALPHA_SIGNAL_REPAIR_CARD = "alpha-signal-2024-coverage-repair-card-20260509-01"
SYSTEM_REPAIR_CARD = "system-readout-2024-coverage-repair-card-20260509-01"
PIPELINE_REPAIR_CARD = "pipeline-year-replay-source-selection-repair-card-20260509-01"
EVIDENCE_INCOMPLETE_CARD = "coverage-gap-evidence-incomplete-closeout-card-20260509-01"


@dataclass(frozen=True)
class YearReplayCoverageGapDiagnosisRequest:
    repo_root: Path
    source_system_db: Path
    report_root: Path
    validated_root: Path
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


@dataclass(frozen=True)
class CoverageMatrixRow:
    layer: str
    surface_name: str
    db_path: str
    table_name: str
    run_selector: str
    date_column: str
    observed_start: str | None
    observed_end: str | None
    row_count_2024: int
    missing_focus_dates: tuple[str, ...]
    notes: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class YearReplayCoverageGapDiagnosisSummary:
    run_id: str
    target_year: int
    released_system_run_id: str
    recommended_next_card: str
    attribution: str
    manifest_path: str
    coverage_matrix_path: str
    coverage_attribution_path: str
    closeout_path: str
    validated_zip: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)
