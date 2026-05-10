from __future__ import annotations

from pathlib import Path

from asteria.portfolio_plan.coverage_repair_contracts import (
    PortfolioPlan2024CoverageRepairRequest,
)


def request(tmp_path: Path, *, repo_root: Path) -> PortfolioPlan2024CoverageRepairRequest:
    return PortfolioPlan2024CoverageRepairRequest(
        repo_root=repo_root,
        source_system_db=tmp_path / "data" / "system.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="portfolio-plan-2024-coverage-repair-card-20260509-01",
    )


def seed_repo_root(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    governance_root = repo_root / "governance"
    governance_root.mkdir(parents=True, exist_ok=True)
    (governance_root / "module_gate_registry.toml").write_text(
        'current_allowed_next_card = "portfolio_plan_2024_coverage_repair_card"\n',
        encoding="utf-8",
    )
    return repo_root
