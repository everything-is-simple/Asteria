from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

PIPELINE_DISPOSITION_DECISION_CARD = "pipeline-year-replay-disposition-decision-card-20260510-01"
PIPELINE_DISPOSITION_DECISION_ACTION = "pipeline_year_replay_disposition_decision_card"


@dataclass(frozen=True)
class PipelineYearReplaySourceSelectionRepairRequest:
    repo_root: Path
    source_system_db: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    run_id: str
    target_year: int

    @property
    def run_root(self) -> Path:
        return self.temp_root / "pipeline" / self.run_id


@dataclass(frozen=True)
class PipelineYearReplaySourceSelectionRepairSummary:
    run_id: str
    status: str
    released_system_run_id: str
    observed_start: str | None
    observed_end: str | None
    source_lock_clean: bool
    followup_attribution: str
    diagnosis_next_card: str
    next_card: str
    manifest_path: str
    closeout_path: str
    validated_zip: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)
