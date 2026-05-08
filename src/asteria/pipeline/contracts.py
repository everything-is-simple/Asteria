from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PIPELINE_SCHEMA_VERSION = "pipeline-single-module-orchestration-v1"
PIPELINE_VERSION = "pipeline-system-readout-single-module-v1"
PIPELINE_FULL_CHAIN_SCHEMA_VERSION = "pipeline-full-chain-dry-run-v1"
PIPELINE_FULL_CHAIN_VERSION = "pipeline-full-chain-day-dry-run-v1"
VALID_PIPELINE_RUN_MODES = {"audit-only", "bounded", "dry-run", "resume"}
VALID_PIPELINE_MODULE_SCOPES = {"system_readout", "full_chain_day"}
FULL_CHAIN_DAY_MODULES = (
    "malf",
    "alpha",
    "signal",
    "position",
    "portfolio_plan",
    "trade",
    "system_readout",
)


@dataclass(frozen=True)
class PipelineBuildRequest:
    repo_root: Path
    source_system_db: Path
    target_pipeline_db: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    run_id: str
    mode: str
    source_chain_release_version: str
    module_scope: str = "system_readout"
    schema_version: str = PIPELINE_SCHEMA_VERSION
    pipeline_version: str = PIPELINE_VERSION

    def __post_init__(self) -> None:
        if self.mode not in VALID_PIPELINE_RUN_MODES:
            raise ValueError(f"Unsupported Pipeline run mode: {self.mode}")
        if self.module_scope not in VALID_PIPELINE_MODULE_SCOPES:
            raise ValueError(f"Unsupported Pipeline module_scope: {self.module_scope}")
        if not self.source_chain_release_version:
            raise ValueError("source_chain_release_version is required")
        if self.module_scope == "system_readout" and self.mode == "dry-run":
            raise ValueError("system_readout single-module pipeline does not support dry-run mode")
        if self.module_scope == "full_chain_day" and self.mode == "bounded":
            raise ValueError("full-chain day pipeline requires dry-run/resume/audit-only mode")
        if self.module_scope == "full_chain_day" and self.schema_version == PIPELINE_SCHEMA_VERSION:
            object.__setattr__(self, "schema_version", PIPELINE_FULL_CHAIN_SCHEMA_VERSION)
        if self.module_scope == "full_chain_day" and self.pipeline_version == PIPELINE_VERSION:
            object.__setattr__(self, "pipeline_version", PIPELINE_FULL_CHAIN_VERSION)

    @property
    def gate_registry_path(self) -> Path:
        return self.repo_root / "governance" / "module_gate_registry.toml"

    @property
    def staging_db_path(self) -> Path:
        return self.temp_root / "pipeline" / self.run_id / "pipeline-staging.duckdb"

    @property
    def run_root(self) -> Path:
        return self.temp_root / "pipeline" / self.run_id

    @property
    def runtime_manifest_path(self) -> Path:
        return self.run_root / "runtime-manifest.json"

    @property
    def batch_ledger_path(self) -> Path:
        return self.run_root / "batch-ledger.jsonl"

    def checkpoint_path(self, stage: str) -> Path:
        return self.run_root / f"{stage}.json"

    def step_checkpoint_path(self, step_seq: int) -> Path:
        return self.run_root / f"step-{step_seq}.json"


@dataclass(frozen=True)
class PipelineBuildSummary:
    run_id: str
    stage: str
    status: str
    module_scope: str
    step_count: int = 0
    gate_snapshot_count: int = 0
    manifest_count: int = 0
    audit_count: int = 0
    hard_fail_count: int = 0
    report_path: str | None = None
    manifest_path: str | None = None
    closeout_path: str | None = None
    validated_zip: str | None = None
    resume_reused: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
