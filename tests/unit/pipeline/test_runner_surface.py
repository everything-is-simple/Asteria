from asteria.governance.pipeline_runner_surface import allowed_pipeline_runner_names


def test_alpha_signal_daily_incremental_runner_is_allowlisted() -> None:
    assert "run_alpha_signal_daily_incremental_ledger.py" in allowed_pipeline_runner_names()


def test_pipeline_full_daily_incremental_chain_runner_is_allowlisted() -> None:
    assert "run_pipeline_full_daily_incremental_chain.py" in allowed_pipeline_runner_names()
