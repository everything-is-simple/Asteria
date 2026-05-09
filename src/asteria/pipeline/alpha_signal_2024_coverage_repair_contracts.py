from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

DEFAULT_BASELINE_MALF_RUN_ID = "malf-v1-4-core-runtime-sync-implementation-20260505-01"
DEFAULT_REPAIRED_MALF_RUN_ID = "malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001"
DEFAULT_ALPHA_RELEASED_RUN_ID = "alpha-production-builder-hardening-20260506-01"
DEFAULT_SIGNAL_RELEASED_RUN_ID = "signal-production-builder-hardening-20260506-01"
DEFAULT_SYSTEM_RELEASED_RUN_ID = "system-readout-bounded-proof-build-card-20260508-01"
DEFAULT_MALF_SERVICE_VERSION = "malf-wave-position-dense-v1"


@dataclass(frozen=True)
class AlphaSignalCoverageRepairRequest:
    repo_root: Path
    source_system_db: Path
    baseline_malf_service_db: Path
    repaired_malf_service_db: Path
    target_data_root: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    run_id: str
    baseline_malf_run_id: str = DEFAULT_BASELINE_MALF_RUN_ID
    repaired_malf_run_id: str = DEFAULT_REPAIRED_MALF_RUN_ID
    released_alpha_run_id: str = DEFAULT_ALPHA_RELEASED_RUN_ID
    released_signal_run_id: str = DEFAULT_SIGNAL_RELEASED_RUN_ID
    source_chain_release_version: str = DEFAULT_SYSTEM_RELEASED_RUN_ID
    malf_service_version: str = DEFAULT_MALF_SERVICE_VERSION
    target_year: int = 2024
    run_followup_checks: bool = True

    @property
    def run_root(self) -> Path:
        return self.temp_root / "pipeline" / self.run_id

    @property
    def merged_malf_service_db(self) -> Path:
        return self.run_root / "merged-malf-service-day.duckdb"

    @property
    def followup_pipeline_db(self) -> Path:
        return self.run_root / "followup-pipeline.duckdb"

    @property
    def followup_repo_root(self) -> Path:
        return self.run_root / "followup-repo"

    @property
    def followup_rerun_run_id(self) -> str:
        return f"{self.run_id}-rerun-check"

    @property
    def followup_diagnosis_run_id(self) -> str:
        return f"{self.run_id}-post-repair-diagnosis"


@dataclass(frozen=True)
class AlphaSignalCoverageRepairSummary:
    run_id: str
    status: str
    merged_malf_service_db: str
    alpha_repair_count: int = 0
    signal_hard_fail_count: int = 0
    followup_rerun_status: str | None = None
    followup_rerun_hard_fail_count: int | None = None
    followup_next_card: str | None = None
    followup_diagnosis_run_id: str | None = None
    manifest_path: str | None = None
    closeout_path: str | None = None
    validated_zip: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
