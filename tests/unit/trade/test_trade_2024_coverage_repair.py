from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb
import pytest
from tests.unit.trade.trade_2024_coverage_repair_support import (
    ALPHA_FAMILIES,
    PORTFOLIO_RUN_ID,
    SYSTEM_RUN_ID,
    TRADE_RUN_ID,
    build_request,
    seed_alpha_db,
    seed_data_foundation,
    seed_malf_db_with_stale_manifest_source,
    seed_portfolio_plan_db,
    seed_position_db,
    seed_repo_root,
    seed_signal_db,
    seed_system_db,
    seed_trade_from_late_portfolio_source,
    trading_dates,
)

from asteria.pipeline.year_replay_coverage_gap_contracts import SYSTEM_REPAIR_CARD
from asteria.trade.coverage_repair import run_trade_2024_coverage_repair
from asteria.trade.coverage_repair_contracts import Trade2024CoverageRepairRequest


def test_repair_rewrites_trade_focus_window_and_moves_break_to_system_readout(
    tmp_path: Path,
) -> None:
    repo_root = seed_repo_root(tmp_path)
    data_root = tmp_path / "data"
    full_dates = trading_dates()
    late_dates = trading_dates(start="2024-01-09")
    seed_data_foundation(data_root, full_dates)
    seed_malf_db_with_stale_manifest_source(
        data_root / "malf_service_day.duckdb",
        baseline_dates=late_dates,
        repaired_dates=full_dates,
    )
    for family in ALPHA_FAMILIES:
        seed_alpha_db(data_root / f"alpha_{family}.duckdb", full_dates)
    seed_signal_db(data_root / "signal.duckdb", full_dates)
    seed_position_db(data_root / "position.duckdb", full_dates)
    seed_portfolio_plan_db(data_root / "portfolio_plan.duckdb", full_dates)
    seed_trade_from_late_portfolio_source(tmp_path, late_dates)
    seed_system_db(data_root / "system.duckdb", data_root, late_dates)

    registry_before = (repo_root / "governance" / "module_gate_registry.toml").read_text(
        encoding="utf-8"
    )
    summary = run_trade_2024_coverage_repair(build_request(tmp_path, repo_root=repo_root))

    assert summary.status == "completed"
    assert summary.released_portfolio_plan_run_id == PORTFOLIO_RUN_ID
    assert summary.released_trade_run_id == TRADE_RUN_ID
    assert summary.followup_next_card == SYSTEM_REPAIR_CARD
    assert summary.followup_attribution == "released_surface_gap:system_readout"
    assert summary.hard_fail_count == 0
    with duckdb.connect(str(data_root / "trade.duckdb"), read_only=True) as con:
        intent_dates = con.execute(
            """
            select distinct intent_dt
            from order_intent_ledger
            where run_id = ?
            order by 1
            """,
            [TRADE_RUN_ID],
        ).fetchall()
        execution_dates = con.execute(
            """
            select distinct execution_valid_from
            from execution_plan_ledger
            where run_id = ?
            order by 1
            """,
            [TRADE_RUN_ID],
        ).fetchall()
        rejection_dates = con.execute(
            """
            select distinct rejection_dt
            from order_rejection_ledger
            where run_id = ?
            order by 1
            """,
            [TRADE_RUN_ID],
        ).fetchall()
        fill_count = con.execute(
            "select count(*) from fill_ledger where run_id = ?",
            [TRADE_RUN_ID],
        ).fetchone()[0]
        run_row = con.execute(
            """
            select input_portfolio_plan_count, order_intent_count, execution_plan_count,
                   fill_count, rejection_count, hard_fail_count, status
            from trade_run
            where run_id = ?
            """,
            [TRADE_RUN_ID],
        ).fetchone()

    assert intent_dates[:1] == [(date(2024, 1, 5),)]
    assert execution_dates[:1] == [(date(2024, 1, 5),)]
    assert (date(2024, 1, 9),) in intent_dates
    assert (date(2024, 1, 9),) in execution_dates
    assert (date(2024, 1, 2),) in rejection_dates
    assert (date(2024, 1, 3),) in rejection_dates
    assert (date(2024, 1, 4),) in rejection_dates
    assert fill_count == 0
    assert run_row[0] == run_row[1] + run_row[4]
    assert run_row[1] >= len(late_dates)
    assert run_row[2] == run_row[1]
    assert run_row[3] == 0
    assert run_row[4] == 3
    assert run_row[5] == 0
    assert run_row[6] == "completed"
    assert Path(summary.validated_zip).exists()
    assert (repo_root / "governance" / "module_gate_registry.toml").read_text(
        encoding="utf-8"
    ) == registry_before


def test_repair_rejects_duplicate_trade_manifest_rows(tmp_path: Path) -> None:
    repo_root = seed_repo_root(tmp_path)
    data_root = tmp_path / "data"
    full_dates = trading_dates()
    late_dates = trading_dates(start="2024-01-09")
    seed_data_foundation(data_root, full_dates)
    seed_malf_db_with_stale_manifest_source(
        data_root / "malf_service_day.duckdb",
        baseline_dates=late_dates,
        repaired_dates=full_dates,
    )
    for family in ALPHA_FAMILIES:
        seed_alpha_db(data_root / f"alpha_{family}.duckdb", full_dates)
    seed_signal_db(data_root / "signal.duckdb", full_dates)
    seed_position_db(data_root / "position.duckdb", full_dates)
    seed_portfolio_plan_db(data_root / "portfolio_plan.duckdb", full_dates)
    seed_trade_from_late_portfolio_source(tmp_path, late_dates)
    seed_system_db(data_root / "system.duckdb", data_root, late_dates)
    with duckdb.connect(str(data_root / "system.duckdb")) as con:
        con.execute(
            "insert into system_source_manifest values (?, 'trade', ?, ?, ?)",
            [SYSTEM_RUN_ID, str(data_root / "trade.duckdb"), TRADE_RUN_ID, TRADE_RUN_ID],
        )

    with pytest.raises(ValueError, match="expected exactly one trade manifest row"):
        run_trade_2024_coverage_repair(build_request(tmp_path, repo_root=repo_root))


def test_request_rejects_non_2024_or_changed_focus_window(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="locked to target_year=2024"):
        Trade2024CoverageRepairRequest(
            repo_root=tmp_path,
            source_system_db=tmp_path / "system.duckdb",
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id="trade-2024-coverage-repair-card-20260509-01",
            target_year=2025,
        )
    with pytest.raises(ValueError, match="focus window is fixed"):
        Trade2024CoverageRepairRequest(
            repo_root=tmp_path,
            source_system_db=tmp_path / "system.duckdb",
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id="trade-2024-coverage-repair-card-20260509-01",
            focus_start_dt="2024-01-03",
        )
