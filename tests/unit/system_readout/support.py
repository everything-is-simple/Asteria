from __future__ import annotations

from pathlib import Path

from tests.unit.system_readout.support_downstream import (
    seed_portfolio_plan_db,
    seed_position_db,
    seed_trade_db,
)
from tests.unit.system_readout.support_upstream import (
    ALPHA_FAMILIES,
    TRADE_RUN_ID,
    seed_alpha_db,
    seed_malf_db,
    seed_signal_db,
)

from asteria.system_readout.contracts import SystemReadoutBuildRequest

SOURCE_CHAIN_RELEASE_VERSION = TRADE_RUN_ID


def build_request(tmp_path: Path, mode: str = "bounded") -> SystemReadoutBuildRequest:
    return SystemReadoutBuildRequest(
        source_malf_service_db=tmp_path / "data" / "malf_service_day.duckdb",
        source_alpha_root=tmp_path / "data",
        source_signal_db=tmp_path / "data" / "signal.duckdb",
        source_position_db=tmp_path / "data" / "position.duckdb",
        source_portfolio_plan_db=tmp_path / "data" / "portfolio_plan.duckdb",
        source_trade_db=tmp_path / "data" / "trade.duckdb",
        target_system_db=tmp_path / "data" / "system.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="system-readout-bounded-proof-unit-001",
        mode=mode,
        source_chain_release_version=SOURCE_CHAIN_RELEASE_VERSION,
        start_dt="2024-01-01",
        end_dt="2024-01-31",
        symbol_limit=10,
    )


def seed_chain(tmp_path: Path, *, trade_hard_fail_count: int = 0) -> None:
    data_dir = tmp_path / "data"
    seed_malf_db(data_dir / "malf_service_day.duckdb")
    for family in ALPHA_FAMILIES:
        seed_alpha_db(data_dir / f"alpha_{family}.duckdb", family.upper())
    seed_signal_db(data_dir / "signal.duckdb")
    seed_position_db(data_dir / "position.duckdb")
    seed_portfolio_plan_db(data_dir / "portfolio_plan.duckdb")
    seed_trade_db(data_dir / "trade.duckdb", hard_fail_count=trade_hard_fail_count)
