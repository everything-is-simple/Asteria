from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

V1_APPLICATION_DB_READINESS_AUDIT_CARD = "v1-application-db-readiness-audit-card"
V1_APPLICATION_DB_READINESS_AUDIT_RUN_ID = "v1-application-db-readiness-audit-card-20260513-01"
V1_USAGE_READOUT_REPORT_CARD = "v1-usage-readout-report-card"
EXPECTED_FORMAL_DB_COUNT = 25

FORMAL_DB_GROUPS: dict[str, list[str]] = {
    "data": [
        "raw_market.duckdb",
        "market_meta.duckdb",
        "market_base_day.duckdb",
        "market_base_week.duckdb",
        "market_base_month.duckdb",
    ],
    "malf": [
        "malf_core_day.duckdb",
        "malf_lifespan_day.duckdb",
        "malf_service_day.duckdb",
        "malf_core_week.duckdb",
        "malf_lifespan_week.duckdb",
        "malf_service_week.duckdb",
        "malf_core_month.duckdb",
        "malf_lifespan_month.duckdb",
        "malf_service_month.duckdb",
    ],
    "alpha_signal": [
        "alpha_bof.duckdb",
        "alpha_tst.duckdb",
        "alpha_pb.duckdb",
        "alpha_cpb.duckdb",
        "alpha_bpb.duckdb",
        "signal.duckdb",
    ],
    "downstream_pipeline": [
        "position.duckdb",
        "portfolio_plan.duckdb",
        "trade.duckdb",
        "system.duckdb",
        "pipeline.duckdb",
    ],
}

APPLICATION_INPUT_GROUPS = {"data", "malf", "alpha_signal"}

REQUIRED_DB_TABLES: dict[str, tuple[str, ...]] = {
    "raw_market.duckdb": ("raw_market_bar", "raw_market_source_file", "raw_market_sync_run"),
    "market_meta.duckdb": (
        "instrument_master",
        "trade_calendar",
        "industry_classification",
        "meta_source_manifest",
    ),
    "market_base_day.duckdb": ("market_base_bar", "market_base_run", "market_base_latest"),
    "market_base_week.duckdb": ("market_base_bar", "market_base_run", "market_base_latest"),
    "market_base_month.duckdb": ("market_base_bar", "market_base_run", "market_base_latest"),
    "malf_core_day.duckdb": ("malf_core_run", "malf_wave_ledger", "malf_core_state_snapshot"),
    "malf_core_week.duckdb": ("malf_core_run", "malf_wave_ledger", "malf_core_state_snapshot"),
    "malf_core_month.duckdb": ("malf_core_run", "malf_wave_ledger", "malf_core_state_snapshot"),
    "malf_lifespan_day.duckdb": ("malf_lifespan_run", "malf_lifespan_snapshot"),
    "malf_lifespan_week.duckdb": ("malf_lifespan_run", "malf_lifespan_snapshot"),
    "malf_lifespan_month.duckdb": ("malf_lifespan_run", "malf_lifespan_snapshot"),
    "malf_service_day.duckdb": ("malf_service_run", "malf_wave_position"),
    "malf_service_week.duckdb": ("malf_service_run", "malf_wave_position"),
    "malf_service_month.duckdb": ("malf_service_run", "malf_wave_position"),
    "alpha_bof.duckdb": ("alpha_family_run", "alpha_signal_candidate"),
    "alpha_tst.duckdb": ("alpha_family_run", "alpha_signal_candidate"),
    "alpha_pb.duckdb": ("alpha_family_run", "alpha_signal_candidate"),
    "alpha_cpb.duckdb": ("alpha_family_run", "alpha_signal_candidate"),
    "alpha_bpb.duckdb": ("alpha_family_run", "alpha_signal_candidate"),
    "signal.duckdb": ("signal_run", "formal_signal_ledger"),
    "position.duckdb": ("position_run", "position_candidate_ledger"),
    "portfolio_plan.duckdb": ("portfolio_plan_run", "portfolio_admission_ledger"),
    "trade.duckdb": ("trade_run", "order_intent_ledger", "order_rejection_ledger"),
    "system.duckdb": ("system_readout_run", "system_chain_readout"),
    "pipeline.duckdb": ("pipeline_run", "pipeline_step_run", "build_manifest"),
}


@dataclass(frozen=True)
class ApplicationDbReadinessAuditRequest:
    repo_root: Path
    formal_data_root: Path
    report_root: Path
    validated_root: Path
    run_id: str = V1_APPLICATION_DB_READINESS_AUDIT_RUN_ID

    @property
    def report_dir(self) -> Path:
        return self.report_root / "pipeline" / "2026-05-13" / self.run_id


@dataclass(frozen=True)
class DbReadinessEntry:
    db_name: str
    group: str
    path: str
    exists: bool
    read_only_opened: bool
    table_count: int
    row_counts: dict[str, int]
    required_tables: list[str]
    missing_required_tables: list[str]
    zero_required_tables: list[str]
    schema_versions: dict[str, list[str]]
    rule_versions: dict[str, list[str]]
    error: str | None = None

    @property
    def ready(self) -> bool:
        return (
            self.exists
            and self.read_only_opened
            and not self.missing_required_tables
            and not self.zero_required_tables
        )

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["ready"] = self.ready
        return payload


@dataclass(frozen=True)
class ApplicationDbReadinessAuditSummary:
    run_id: str
    status: str
    live_next_card: str
    live_next_card_preserved: bool
    db_count: int
    read_only_open_count: int
    application_input_db_count: int
    application_input_ready_count: int
    downstream_pipeline_readable_count: int
    issue_count: int
    issues: list[str]
    caveats: list[str]
    next_route_card: str
    manifest_path: str
    closeout_path: str
    validated_zip: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
