from __future__ import annotations

from pathlib import Path

RUN_ID = "v1-signal-export-contract-card-20260513-01"


def test_v1_signal_export_contract_is_recorded_without_reopening_live_next() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    registry_text = (repo_root / "governance" / "module_gate_registry.toml").read_text(
        encoding="utf-8"
    )
    ledger_text = (repo_root / "docs" / "03-refactor" / "00-module-gate-ledger-v1.md").read_text(
        encoding="utf-8"
    )
    roadmap_text = (
        repo_root / "docs" / "03-refactor" / "05-asteria-v1-usage-validation-roadmap-v1.md"
    ).read_text(encoding="utf-8")
    conclusion_index = (
        repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    ).read_text(encoding="utf-8")
    pipeline_records = repo_root / "docs" / "04-execution" / "records" / "pipeline"

    assert 'current_allowed_next_card = ""' in registry_text
    assert "none / terminal" in ledger_text
    assert (
        "| 2 | `v1-signal-export-contract-card` | passed / signal export contract frozen |"
    ) in roadmap_text
    assert (
        "| 3 | `v1-t-plus-one-open-backtesting-py-proof-card` | "
        "passed / t+1 open backtesting.py proof completed |"
    ) in roadmap_text
    assert (
        "| 4 | `v1-vectorbt-portfolio-analytics-proof-card` | "
        "passed / vectorbt portfolio analytics proof completed |"
    ) in roadmap_text
    assert "| 5 | `v1-broker-adapter-feasibility-card` | prepared next route card |" in roadmap_text
    assert (
        "v1-signal-export-contract-card-20260513-01 = passed / signal export contract frozen"
    ) in ledger_text
    assert (
        "v1-t-plus-one-open-backtesting-py-proof-card-20260514-01 = "
        "passed / t+1 open backtesting.py proof completed"
    ) in ledger_text
    assert (
        "v1-vectorbt-portfolio-analytics-proof-card-20260514-01 = "
        "passed / vectorbt portfolio analytics proof completed"
    ) in ledger_text
    assert "next route card = v1-broker-adapter-feasibility-card" in ledger_text
    for required_text in (
        "`symbol`",
        "`signal_date`",
        "`signal_strength`",
        "`signal_family`",
        "`source_run_id`",
        "`lineage`",
        "`T_PLUS_1_OPEN`",
        "`next_trading_day_after_signal_date`",
        "`open`",
        "T+0 signal -> T+1 open execution",
    ):
        assert required_text in roadmap_text
    assert "当前 Asteria 仍不能宣称正式收益回测" in roadmap_text
    expected_row = f"| Pipeline | `{RUN_ID}` | `passed / signal export contract frozen` |"
    assert expected_row in conclusion_index
    for suffix in ("card", "record", "evidence-index", "conclusion"):
        assert (pipeline_records / f"{RUN_ID}.{suffix}.md").exists()
