from __future__ import annotations

from tests.unit.pipeline.test_year_replay_coverage_gap_diagnosis import (
    _seed_scenario,
    _trading_dates,
)

from asteria.pipeline.year_replay_coverage_gap_diagnosis import (
    run_year_replay_coverage_gap_diagnosis,
)


def test_post_alpha_signal_repair_can_move_first_break_to_system_readout(tmp_path) -> None:
    full_dates = _trading_dates()
    request = _seed_scenario(
        tmp_path,
        data_dates=full_dates,
        malf_dates=full_dates,
        alpha_dates=full_dates,
        signal_dates=full_dates,
        position_dates=full_dates,
        portfolio_dates=full_dates,
        trade_dates=full_dates,
        system_dates=_trading_dates(start="2024-01-08"),
    )

    summary = run_year_replay_coverage_gap_diagnosis(request)

    assert summary.recommended_next_card == "system-readout-2024-coverage-repair-card-20260509-01"


def test_post_alpha_signal_repair_can_leave_pipeline_source_selection_as_truthful_next_card(
    tmp_path,
) -> None:
    full_dates = _trading_dates()
    request = _seed_scenario(
        tmp_path,
        data_dates=full_dates,
        malf_dates=full_dates,
        alpha_dates=full_dates,
        signal_dates=full_dates,
        position_dates=full_dates,
        portfolio_dates=full_dates,
        trade_dates=full_dates,
        system_dates=full_dates,
    )

    summary = run_year_replay_coverage_gap_diagnosis(request)

    assert (
        summary.recommended_next_card
        == "pipeline-year-replay-source-selection-repair-card-20260509-01"
    )
