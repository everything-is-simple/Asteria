from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

V1_USAGE_VALUE_DECISION_CARD = "v1-usage-value-decision-card"
V1_USAGE_VALUE_DECISION_RUN_ID = "v1-usage-value-decision-card-20260513-01"
V1_USAGE_READOUT_REPORT_RUN_ID = "v1-usage-readout-report-card-20260513-01"
V1_DOWNSTREAM_REFERENCE_AUDIT_RUN_ID = "v1-downstream-reference-audit-20260513-01"
V1_DAILY_INCREMENTAL_PRODUCTION_SCOPE_CARD = "daily-incremental-production-scope-card"
VALUE_DECISION_RESEARCH_USABLE = "research_usable_with_caveats"
VALUE_DECISION_INSUFFICIENT = "insufficient_evidence"

DEFAULT_USAGE_READOUT_MANIFEST_PATH = (
    "H:/Asteria-report/pipeline/2026-05-13/"
    "v1-usage-readout-report-card-20260513-01/usage-readout-manifest.json"
)
DEFAULT_DOWNSTREAM_REFERENCE_MANIFEST_PATH = (
    "H:/Asteria-report/pipeline/2026-05-13/"
    "v1-downstream-reference-audit-20260513-01/downstream-reference-audit-manifest.json"
)


@dataclass(frozen=True)
class UsageValueDecisionRequest:
    repo_root: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    usage_readout_manifest_path: Path = Path(DEFAULT_USAGE_READOUT_MANIFEST_PATH)
    downstream_reference_manifest_path: Path = Path(DEFAULT_DOWNSTREAM_REFERENCE_MANIFEST_PATH)
    run_id: str = V1_USAGE_VALUE_DECISION_RUN_ID

    @property
    def report_dir(self) -> Path:
        return self.report_root / "pipeline" / "2026-05-13" / self.run_id

    @property
    def temp_dir(self) -> Path:
        return self.temp_root / "pipeline" / self.run_id


@dataclass(frozen=True)
class UsageValueDecisionSummary:
    run_id: str
    status: str
    live_next_card: str
    live_next_card_preserved: bool
    value_decision: str
    human_conclusion: str
    issue_count: int
    issues: list[str]
    category_counts: dict[str, int]
    next_route_card: str
    manifest_path: str
    report_path: str
    closeout_path: str
    temp_manifest_path: str
    validated_zip: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
