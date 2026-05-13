from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

V1_USAGE_READOUT_REPORT_CARD = "v1-usage-readout-report-card"
V1_USAGE_READOUT_REPORT_RUN_ID = "v1-usage-readout-report-card-20260513-01"
V1_USAGE_VALUE_DECISION_CARD = "v1-usage-value-decision-card"
V1_APPLICATION_DB_READINESS_AUDIT_CARD = "v1-application-db-readiness-audit-card"
V1_USAGE_SCOPE_RUN_ID = "v1-usage-validation-scope-card-20260512-01"
DEFAULT_SCOPE_MANIFEST_PATH = (
    "H:/Asteria-report/pipeline/2026-05-12/"
    "v1-usage-validation-scope-card-20260512-01/scope-manifest.json"
)


@dataclass(frozen=True)
class UsageReadoutTableSpec:
    section: str
    db_name: str
    table_name: str
    date_column: str | None
    group_columns: tuple[str, ...]


USAGE_READOUT_TABLE_SPECS: tuple[UsageReadoutTableSpec, ...] = (
    UsageReadoutTableSpec(
        "market_structure",
        "malf_service_day.duckdb",
        "malf_wave_position",
        "bar_dt",
        ("system_state", "wave_core_state", "life_state", "position_quadrant", "direction"),
    ),
    UsageReadoutTableSpec(
        "market_structure",
        "malf_lifespan_day.duckdb",
        "malf_lifespan_snapshot",
        "bar_dt",
        ("life_state", "position_quadrant", "wave_core_state"),
    ),
    UsageReadoutTableSpec(
        "opportunity",
        "alpha_bof.duckdb",
        "alpha_signal_candidate",
        "bar_dt",
        ("alpha_family", "candidate_state", "opportunity_bias", "confidence_bucket"),
    ),
    UsageReadoutTableSpec(
        "opportunity",
        "alpha_tst.duckdb",
        "alpha_signal_candidate",
        "bar_dt",
        ("alpha_family", "candidate_state", "opportunity_bias", "confidence_bucket"),
    ),
    UsageReadoutTableSpec(
        "opportunity",
        "alpha_pb.duckdb",
        "alpha_signal_candidate",
        "bar_dt",
        ("alpha_family", "candidate_state", "opportunity_bias", "confidence_bucket"),
    ),
    UsageReadoutTableSpec(
        "opportunity",
        "alpha_cpb.duckdb",
        "alpha_signal_candidate",
        "bar_dt",
        ("alpha_family", "candidate_state", "opportunity_bias", "confidence_bucket"),
    ),
    UsageReadoutTableSpec(
        "opportunity",
        "alpha_bpb.duckdb",
        "alpha_signal_candidate",
        "bar_dt",
        ("alpha_family", "candidate_state", "opportunity_bias", "confidence_bucket"),
    ),
    UsageReadoutTableSpec(
        "opportunity",
        "signal.duckdb",
        "formal_signal_ledger",
        "signal_dt",
        ("signal_state", "signal_bias", "confidence_bucket", "reason_code"),
    ),
    UsageReadoutTableSpec(
        "position_portfolio",
        "position.duckdb",
        "position_candidate_ledger",
        "candidate_dt",
        ("candidate_state", "position_bias", "reason_code"),
    ),
    UsageReadoutTableSpec(
        "position_portfolio",
        "portfolio_plan.duckdb",
        "portfolio_admission_ledger",
        "plan_dt",
        ("admission_state", "admission_reason"),
    ),
    UsageReadoutTableSpec(
        "trade_intent",
        "trade.duckdb",
        "order_intent_ledger",
        "intent_dt",
        ("order_side", "order_intent_state"),
    ),
    UsageReadoutTableSpec(
        "trade_intent",
        "trade.duckdb",
        "order_rejection_ledger",
        "rejection_dt",
        ("rejection_stage", "rejection_reason"),
    ),
    UsageReadoutTableSpec(
        "system_pipeline",
        "system.duckdb",
        "system_chain_readout",
        "readout_dt",
        ("readout_status", "wave_core_state", "system_state"),
    ),
    UsageReadoutTableSpec(
        "system_pipeline",
        "pipeline.duckdb",
        "build_manifest",
        None,
        ("artifact_role", "source_type"),
    ),
)


@dataclass(frozen=True)
class UsageReadoutReportRequest:
    repo_root: Path
    formal_data_root: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    scope_manifest_path: Path = Path(DEFAULT_SCOPE_MANIFEST_PATH)
    run_id: str = V1_USAGE_READOUT_REPORT_RUN_ID

    @property
    def report_dir(self) -> Path:
        return self.report_root / "pipeline" / "2026-05-13" / self.run_id

    @property
    def temp_dir(self) -> Path:
        return self.temp_root / "pipeline" / self.run_id


@dataclass(frozen=True)
class UsageReadoutReportSummary:
    run_id: str
    status: str
    live_next_card: str
    live_next_card_preserved: bool
    selected_symbol_count: int
    date_window: str
    issue_count: int
    issues: list[str]
    caveats: list[str]
    next_route_card: str
    manifest_path: str
    report_path: str
    closeout_path: str
    temp_manifest_path: str
    validated_zip: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
