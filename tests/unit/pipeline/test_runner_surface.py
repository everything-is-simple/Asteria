from asteria.governance.pipeline_runner_surface import allowed_pipeline_runner_names


def test_alpha_signal_daily_incremental_runner_is_allowlisted() -> None:
    assert "run_alpha_signal_daily_incremental_ledger.py" in allowed_pipeline_runner_names()


def test_pipeline_full_daily_incremental_chain_runner_is_allowlisted() -> None:
    assert "run_pipeline_full_daily_incremental_chain.py" in allowed_pipeline_runner_names()


def test_formal_release_proof_runner_is_allowlisted() -> None:
    assert "run_formal_release_proof.py" in allowed_pipeline_runner_names()
    assert "run_final_release_closeout.py" in allowed_pipeline_runner_names()


def test_formal_release_source_proof_runner_is_allowlisted() -> None:
    assert "run_formal_release_source_proof.py" in allowed_pipeline_runner_names()


def test_v1_vectorbt_portfolio_analytics_runner_is_allowlisted() -> None:
    assert "run_v1_vectorbt_portfolio_analytics_proof.py" in allowed_pipeline_runner_names()
