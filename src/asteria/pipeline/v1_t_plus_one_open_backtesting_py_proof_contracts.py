from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

V1_T_PLUS_ONE_OPEN_BACKTESTING_PY_PROOF_CARD = "v1-t-plus-one-open-backtesting-py-proof-card"
V1_T_PLUS_ONE_OPEN_BACKTESTING_PY_PROOF_RUN_ID = (
    "v1-t-plus-one-open-backtesting-py-proof-card-20260514-01"
)
V1_SIGNAL_EXPORT_CONTRACT_RUN_ID = "v1-signal-export-contract-card-20260513-01"
V1_SIGNAL_EXPORT_CONTRACT_CARD = "v1-signal-export-contract-card"
V1_VECTORBT_PORTFOLIO_ANALYTICS_PROOF_CARD = "v1-vectorbt-portfolio-analytics-proof-card"
V1_USAGE_SCOPE_RUN_ID = "v1-usage-validation-scope-card-20260512-01"
DEFAULT_SCOPE_MANIFEST_PATH = (
    "H:/Asteria-report/pipeline/2026-05-12/"
    "v1-usage-validation-scope-card-20260512-01/scope-manifest.json"
)


@dataclass(frozen=True)
class TPlusOneOpenBacktestingPyProofRequest:
    repo_root: Path
    formal_data_root: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    scope_manifest_path: Path = Path(DEFAULT_SCOPE_MANIFEST_PATH)
    run_id: str = V1_T_PLUS_ONE_OPEN_BACKTESTING_PY_PROOF_RUN_ID
    initial_cash: float = 100_000.0
    commission: float = 0.001
    position_fraction: float = 0.95

    @property
    def report_dir(self) -> Path:
        return self.report_root / "pipeline" / "2026-05-14" / self.run_id

    @property
    def temp_dir(self) -> Path:
        return self.temp_root / "pipeline" / self.run_id


@dataclass(frozen=True)
class TPlusOneOpenBacktestingPyProofSummary:
    run_id: str
    status: str
    live_next_card: str
    live_next_card_preserved: bool
    selected_symbol_count: int
    signal_symbol_count: int
    completed_backtest_count: int
    skipped_symbol_count: int
    total_trade_count: int
    date_window: str
    issue_count: int
    issues: list[str]
    next_route_card: str
    manifest_path: str
    report_path: str
    closeout_path: str
    temp_manifest_path: str
    validated_zip: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
