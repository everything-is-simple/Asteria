from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

V1_USAGE_VALIDATION_SCOPE_ACTION = "v1_usage_validation_scope_card"
V1_USAGE_VALIDATION_SCOPE_CARD = "v1-usage-validation-scope-card"
V1_APPLICATION_DB_READINESS_AUDIT_CARD = "v1-application-db-readiness-audit-card"
V1_USAGE_VALIDATION_SCOPE_INDUSTRY_SCHEMA = "sw2021_level3_snapshot"
V1_USAGE_VALIDATION_SCOPE_SOURCE_REFERENCE = (
    "H:/Asteria-Validated/MALF-reference/申万行业分类/最新个股申万行业分类(完整版-截至7月末).xlsx"
)
V1_USAGE_VALIDATION_SCOPE_DB_PERMISSION = "read_only"


@dataclass(frozen=True)
class UsageValidationScopeManualOverride:
    level1_industry: str
    symbol: str
    reason: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class UsageValidationScopeSelectionEntry:
    level1_industry: str
    industry_code: str
    symbol: str
    first_seen_date: str
    latest_seen_date: str
    coverage_days_2024: int
    total_trading_days: int
    coverage_complete: bool
    amount_rank_metric: float
    total_amount_2024: float
    observed_start_2024: str
    observed_end_2024: str
    manual_override_reason: str | None = None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class UsageValidationScopeRequest:
    repo_root: Path
    market_meta_db: Path
    market_base_day_db: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    run_id: str
    start_date: date
    end_date: date
    research_question: str
    report_shape: str
    selection_rule: str = (
        "coverage completeness first, average execution-line amount second, "
        "manual override allowed with recorded reason"
    )
    industry_schema: str = V1_USAGE_VALIDATION_SCOPE_INDUSTRY_SCHEMA
    expected_industry_count: int = 31
    db_permission: str = V1_USAGE_VALIDATION_SCOPE_DB_PERMISSION
    industry_source_reference: str = V1_USAGE_VALIDATION_SCOPE_SOURCE_REFERENCE
    appendix_policy: str = (
        "summary report plus up to five symbol appendices chosen from the frozen 31-symbol pool"
    )
    manual_override_path: Path | None = None

    @property
    def run_root(self) -> Path:
        return self.temp_root / "pipeline" / self.run_id


@dataclass(frozen=True)
class UsageValidationScopeSummary:
    run_id: str
    status: str
    live_next_card: str
    live_next_card_preserved: bool
    next_route_card: str
    level1_industry_count: int
    selected_symbol_count: int
    total_trading_days: int
    manifest_path: str
    closeout_path: str
    validated_zip: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)
