from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

from asteria.position.coverage_repair import Position2024CoverageRepairRequest

POSITION_RUN_ID = "position-bounded-proof-build-card-20260506-01"
SIGNAL_RUN_ID = "signal-production-builder-hardening-20260506-01"
PORTFOLIO_RUN_ID = "portfolio-plan-bounded-proof-build-card-20260507-01"
TRADE_RUN_ID = "trade-bounded-proof-build-card-20260507-01"
SYSTEM_RUN_ID = "system-readout-bounded-proof-build-card-20260508-01"
ALPHA_RUN_ID = "alpha-production-builder-hardening-20260506-01"
MALF_RUN_ID = "malf-v1-4-core-runtime-sync-implementation-20260505-01"
ALPHA_FAMILIES = ("bof", "tst", "pb", "cpb", "bpb")
FOCUS_DATES = [date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 4), date(2024, 1, 5)]


def created_at() -> datetime:
    return datetime(2026, 5, 9, 12, 0, 0)


def request(tmp_path: Path, *, repo_root: Path) -> Position2024CoverageRepairRequest:
    return Position2024CoverageRepairRequest(
        repo_root=repo_root,
        source_system_db=tmp_path / "data" / "system.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="position-2024-coverage-repair-card-20260509-01",
    )


def seed_repo_root(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    governance_root = repo_root / "governance"
    governance_root.mkdir(parents=True, exist_ok=True)
    (governance_root / "module_gate_registry.toml").write_text(
        'current_allowed_next_card = "position_2024_coverage_repair_card"\n',
        encoding="utf-8",
    )
    return repo_root


def trading_dates(*, start: str = "2024-01-02") -> list[date]:
    start_dt = date.fromisoformat(start)
    end_dt = date(2024, 12, 31)
    current = start_dt
    dates: list[date] = []
    while current <= end_dt:
        if current.weekday() < 5 and current.isoformat() != "2024-01-01":
            dates.append(current)
        current += timedelta(days=1)
    return dates
