from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb
import pytest
from tests.unit.position.position_2024_coverage_repair_source_fixtures import (
    seed_alpha_family_dbs,
    seed_data_foundation,
    seed_malf_db,
    seed_signal_db,
)
from tests.unit.position.position_2024_coverage_repair_support import (
    POSITION_RUN_ID,
    SIGNAL_RUN_ID,
    request,
    seed_repo_root,
    trading_dates,
)
from tests.unit.position.position_2024_coverage_repair_system_fixtures import (
    seed_system_db,
)
from tests.unit.position.position_2024_coverage_repair_target_fixtures import (
    seed_portfolio_plan_db,
    seed_position_release_db,
    seed_trade_db,
)

from asteria.pipeline.year_replay_coverage_gap_contracts import (
    PORTFOLIO_PLAN_REPAIR_CARD,
    POSITION_REPAIR_CARD,
)
from asteria.position.coverage_repair import run_position_2024_coverage_repair


def test_repair_rewrites_only_focus_window_for_released_position_run(tmp_path: Path) -> None:
    repo_root = seed_repo_root(tmp_path)
    data_root = tmp_path / "data"
    dates = trading_dates()
    seed_data_foundation(data_root, dates)
    seed_malf_db(data_root / "malf_service_day.duckdb", dates)
    seed_alpha_family_dbs(data_root, dates)
    seed_signal_db(data_root / "signal.duckdb", dates)
    seed_position_release_db(
        data_root / "position.duckdb",
        released_dates=[date(2024, 1, 9), date(2024, 1, 10)],
        released_run_id=POSITION_RUN_ID,
        signal_run_id=SIGNAL_RUN_ID,
        include_week_row=True,
    )
    late_dates = trading_dates(start="2024-01-09")
    seed_portfolio_plan_db(data_root / "portfolio_plan.duckdb", late_dates)
    seed_trade_db(data_root / "trade.duckdb", late_dates)
    seed_system_db(data_root / "system.duckdb", data_root)

    registry_before = (repo_root / "governance" / "module_gate_registry.toml").read_text(
        encoding="utf-8"
    )
    summary = run_position_2024_coverage_repair(request(tmp_path, repo_root=repo_root))

    assert summary.status == "completed"
    assert summary.released_position_run_id == POSITION_RUN_ID
    assert summary.released_signal_run_id == SIGNAL_RUN_ID
    with duckdb.connect(str(data_root / "position.duckdb"), read_only=True) as con:
        day_dates = con.execute(
            """
            select distinct candidate_dt
            from position_candidate_ledger
            where run_id = ? and timeframe = 'day'
            order by 1
            """,
            [POSITION_RUN_ID],
        ).fetchall()
        week_rows = con.execute(
            """
            select count(*)
            from position_candidate_ledger
            where run_id = ? and timeframe = 'week'
            """,
            [POSITION_RUN_ID],
        ).fetchone()[0]
        run_row = con.execute(
            """
            select input_signal_count, position_candidate_count, entry_plan_count, exit_plan_count
            from position_run
            where run_id = ?
            """,
            [POSITION_RUN_ID],
        ).fetchone()

    assert day_dates == [
        (date(2024, 1, 2),),
        (date(2024, 1, 3),),
        (date(2024, 1, 4),),
        (date(2024, 1, 5),),
        (date(2024, 1, 9),),
        (date(2024, 1, 10),),
    ]
    assert week_rows == 1
    assert run_row == (7, 7, 7, 7)
    assert (repo_root / "governance" / "module_gate_registry.toml").read_text(
        encoding="utf-8"
    ) == registry_before


def test_repair_followup_truthfully_moves_next_break_to_portfolio_plan(tmp_path: Path) -> None:
    repo_root = seed_repo_root(tmp_path)
    data_root = tmp_path / "data"
    dates = trading_dates()
    seed_data_foundation(data_root, dates)
    seed_malf_db(data_root / "malf_service_day.duckdb", dates)
    seed_alpha_family_dbs(data_root, dates)
    seed_signal_db(data_root / "signal.duckdb", dates)
    seed_position_release_db(
        data_root / "position.duckdb",
        released_dates=trading_dates(start="2024-01-09"),
        released_run_id=POSITION_RUN_ID,
        signal_run_id=SIGNAL_RUN_ID,
        include_week_row=False,
    )
    late_dates = trading_dates(start="2024-01-09")
    seed_portfolio_plan_db(data_root / "portfolio_plan.duckdb", late_dates)
    seed_trade_db(data_root / "trade.duckdb", late_dates)
    seed_system_db(data_root / "system.duckdb", data_root)

    summary = run_position_2024_coverage_repair(request(tmp_path, repo_root=repo_root))

    assert summary.status == "completed"
    assert summary.followup_next_card == PORTFOLIO_PLAN_REPAIR_CARD
    assert summary.followup_attribution == "downstream_surface_gap:portfolio_plan"


def test_repair_keeps_live_next_card_at_position_when_focus_window_still_lacks_entry_exit(
    tmp_path: Path,
) -> None:
    repo_root = seed_repo_root(tmp_path)
    data_root = tmp_path / "data"
    dates = trading_dates()
    seed_data_foundation(data_root, dates)
    seed_malf_db(data_root / "malf_service_day.duckdb", dates)
    seed_alpha_family_dbs(data_root, dates)
    seed_signal_db(data_root / "signal.duckdb", dates)
    with duckdb.connect(str(data_root / "signal.duckdb")) as con:
        con.execute(
            """
            update formal_signal_ledger
            set signal_state = 'rejected',
                signal_type = 'conflict_or_weak_signal',
                signal_bias = 'neutral',
                reason_code = 'no_active_alpha_candidate'
            where run_id = ?
              and signal_dt in ('2024-01-02', '2024-01-03')
            """,
            [SIGNAL_RUN_ID],
        )
    seed_position_release_db(
        data_root / "position.duckdb",
        released_dates=[date(2024, 1, 9), date(2024, 1, 10)],
        released_run_id=POSITION_RUN_ID,
        signal_run_id=SIGNAL_RUN_ID,
        include_week_row=False,
    )
    late_dates = trading_dates(start="2024-01-09")
    seed_portfolio_plan_db(data_root / "portfolio_plan.duckdb", late_dates)
    seed_trade_db(data_root / "trade.duckdb", late_dates)
    seed_system_db(data_root / "system.duckdb", data_root)

    registry_before = (repo_root / "governance" / "module_gate_registry.toml").read_text(
        encoding="utf-8"
    )
    summary = run_position_2024_coverage_repair(request(tmp_path, repo_root=repo_root))

    assert summary.status == "failed"
    assert summary.followup_next_card == POSITION_REPAIR_CARD
    assert summary.followup_attribution == "downstream_surface_gap:position"
    with duckdb.connect(str(data_root / "position.duckdb"), read_only=True) as con:
        candidate_earliest = con.execute(
            """
            select min(candidate_dt)
            from position_candidate_ledger
            where run_id = ? and timeframe = 'day'
            """,
            [POSITION_RUN_ID],
        ).fetchone()[0]
        entry_earliest = con.execute(
            """
            select min(entry_reference_dt)
            from position_entry_plan
            where run_id = ?
            """,
            [POSITION_RUN_ID],
        ).fetchone()[0]
        exit_earliest = con.execute(
            """
            select min(exit_reference_dt)
            from position_exit_plan
            where run_id = ?
            """,
            [POSITION_RUN_ID],
        ).fetchone()[0]

    assert candidate_earliest == date(2024, 1, 2)
    assert entry_earliest == date(2024, 1, 4)
    assert exit_earliest == date(2024, 1, 4)
    assert (repo_root / "governance" / "module_gate_registry.toml").read_text(
        encoding="utf-8"
    ) == registry_before


def test_repair_rejects_missing_position_manifest_entry(tmp_path: Path) -> None:
    repo_root = seed_repo_root(tmp_path)
    data_root = tmp_path / "data"
    dates = trading_dates()
    seed_data_foundation(data_root, dates)
    seed_malf_db(data_root / "malf_service_day.duckdb", dates)
    seed_alpha_family_dbs(data_root, dates)
    seed_signal_db(data_root / "signal.duckdb", dates)
    seed_position_release_db(
        data_root / "position.duckdb",
        released_dates=[date(2024, 1, 9)],
        released_run_id=POSITION_RUN_ID,
        signal_run_id=SIGNAL_RUN_ID,
        include_week_row=False,
    )
    late_dates = trading_dates(start="2024-01-09")
    seed_portfolio_plan_db(data_root / "portfolio_plan.duckdb", late_dates)
    seed_trade_db(data_root / "trade.duckdb", late_dates)
    seed_system_db(data_root / "system.duckdb", data_root)
    with duckdb.connect(str(data_root / "system.duckdb")) as con:
        con.execute("delete from system_source_manifest where module_name = 'position'")

    with pytest.raises(ValueError, match="expected exactly one position manifest row"):
        run_position_2024_coverage_repair(request(tmp_path, repo_root=repo_root))


def test_repair_rejects_duplicate_position_manifest_rows(tmp_path: Path) -> None:
    repo_root = seed_repo_root(tmp_path)
    data_root = tmp_path / "data"
    dates = trading_dates()
    seed_data_foundation(data_root, dates)
    seed_malf_db(data_root / "malf_service_day.duckdb", dates)
    seed_alpha_family_dbs(data_root, dates)
    seed_signal_db(data_root / "signal.duckdb", dates)
    seed_position_release_db(
        data_root / "position.duckdb",
        released_dates=[date(2024, 1, 9)],
        released_run_id=POSITION_RUN_ID,
        signal_run_id=SIGNAL_RUN_ID,
        include_week_row=False,
    )
    late_dates = trading_dates(start="2024-01-09")
    seed_portfolio_plan_db(data_root / "portfolio_plan.duckdb", late_dates)
    seed_trade_db(data_root / "trade.duckdb", late_dates)
    seed_system_db(data_root / "system.duckdb", data_root)
    with duckdb.connect(str(data_root / "system.duckdb")) as con:
        con.execute(
            """
            insert into system_source_manifest
            values (?, 'position', ?, ?, ?)
            """,
            [
                "system-readout-bounded-proof-build-card-20260508-01",
                str(data_root / "position.duckdb"),
                POSITION_RUN_ID,
                POSITION_RUN_ID,
            ],
        )

    with pytest.raises(ValueError, match="expected exactly one position manifest row"):
        run_position_2024_coverage_repair(request(tmp_path, repo_root=repo_root))
