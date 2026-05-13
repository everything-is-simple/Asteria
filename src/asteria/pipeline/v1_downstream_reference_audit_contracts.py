from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

V1_DOWNSTREAM_REFERENCE_AUDIT_RUN_ID = "v1-downstream-reference-audit-20260513-01"
V1_USAGE_READOUT_REPORT_RUN_ID = "v1-usage-readout-report-card-20260513-01"
V1_USAGE_VALUE_DECISION_CARD = "v1-usage-value-decision-card"
DEFAULT_USAGE_READOUT_MANIFEST_PATH = (
    "H:/Asteria-report/pipeline/2026-05-13/"
    "v1-usage-readout-report-card-20260513-01/usage-readout-manifest.json"
)


@dataclass(frozen=True)
class ReferenceBenchmarkRow:
    dimension: str
    category: str
    decision_bucket: str
    asteria_surface: str
    reference_signal: str
    audit_judgment: str


BENCHMARK_ROWS: tuple[ReferenceBenchmarkRow, ...] = (
    ReferenceBenchmarkRow(
        "signal_to_position",
        "covered",
        "future_enhancement",
        "Position consumes formal_signal_ledger into candidate / entry / exit plan.",
        "Hikyuu SYS uses signal indicators as one explicit strategy component.",
        "Asteria's split is acceptable for research readout and preserves upstream lineage.",
    ),
    ReferenceBenchmarkRow(
        "money_position_sizing",
        "covered",
        "future_enhancement",
        "Portfolio Plan owns admission and target exposure instead of Position.",
        "Hikyuu MM owns buy/sell size and risk-based capital control.",
        "Sizing is present, but richer risk models can stay future enhancement.",
    ),
    ReferenceBenchmarkRow(
        "portfolio_constraints",
        "covered",
        "future_enhancement",
        "Portfolio Plan owns portfolio admission, constraints, target exposure and trim.",
        "Hikyuu PF / AF separates multi-target selection and fund allocation.",
        "The module split matches the common portfolio layer boundary.",
    ),
    ReferenceBenchmarkRow(
        "system_readout",
        "covered",
        "future_enhancement",
        "System Readout is read-only chain summary and audit snapshot.",
        "FinHack-style end-to-end workflows expose research / backtest / live-read surfaces.",
        "Asteria intentionally keeps readout separate from business mutation.",
    ),
    ReferenceBenchmarkRow(
        "order_intent_vs_rejection_scope",
        "expression_risk",
        "strategy_quality_issue",
        "Usage readout shows sample-filtered order intent beside full-window rejection rows.",
        (
            "Trading systems usually present order requests and rejection/error facts "
            "with scope clarity."
        ),
        "This is not a proof failure, but it must be carried into the value decision.",
    ),
    ReferenceBenchmarkRow(
        "rejection_reason_attribution",
        "expression_risk",
        "strategy_quality_issue",
        "Trade rejection ledger lacks symbol, so sample filtering cannot be applied.",
        "easytrader / miniqmt surfaces order errors through explicit callbacks and order status.",
        "Asteria should keep the current scope note visible before any decision on usefulness.",
    ),
    ReferenceBenchmarkRow(
        "fill_fact",
        "real_gap",
        "source_caveat",
        "fill_ledger is retained as source-bound gap and cannot prove real fills.",
        "easytrader exposes entrusted orders and today_trades from broker-facing interfaces.",
        "This is a real execution evidence gap, not a reason to rewrite upstream strategy layers.",
    ),
    ReferenceBenchmarkRow(
        "broker_adapter",
        "not_applicable_reference",
        "future_enhancement",
        "Asteria v1 usage validation is read-only research infrastructure.",
        "easytrader provides broker / client adapters for live order operations.",
        "Broker integration is outside this route and must not be used to judge v1 release truth.",
    ),
)


@dataclass(frozen=True)
class DownstreamReferenceAuditRequest:
    repo_root: Path
    formal_data_root: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    usage_readout_manifest_path: Path = Path(DEFAULT_USAGE_READOUT_MANIFEST_PATH)
    run_id: str = V1_DOWNSTREAM_REFERENCE_AUDIT_RUN_ID

    @property
    def report_dir(self) -> Path:
        return self.report_root / "pipeline" / "2026-05-13" / self.run_id

    @property
    def temp_dir(self) -> Path:
        return self.temp_root / "pipeline" / self.run_id


@dataclass(frozen=True)
class DownstreamReferenceAuditSummary:
    run_id: str
    status: str
    live_next_card: str
    live_next_card_preserved: bool
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
