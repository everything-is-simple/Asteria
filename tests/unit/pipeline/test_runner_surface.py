from asteria.governance.pipeline_runner_surface import allowed_pipeline_runner_names


def test_alpha_signal_daily_incremental_runner_is_allowlisted() -> None:
    assert "run_alpha_signal_daily_incremental_ledger.py" in allowed_pipeline_runner_names()
