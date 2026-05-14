from __future__ import annotations

from pathlib import Path

RUN_ID = "v1-t-plus-one-open-backtesting-py-proof-card-20260514-01"


def test_v1_t_plus_one_open_backtesting_py_proof_route_is_recorded() -> None:
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
        "| 3 | `v1-t-plus-one-open-backtesting-py-proof-card` | "
        "passed / t+1 open backtesting.py proof completed |"
    ) in roadmap_text
    assert (
        "| 4 | `v1-vectorbt-portfolio-analytics-proof-card` | "
        "passed / vectorbt portfolio analytics proof completed |"
    ) in roadmap_text
    assert "| 5 | `v1-broker-adapter-feasibility-card` | prepared next route card |" in roadmap_text
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
        "T+0 signal -> T+1 open execution",
        "`backtesting.py`",
        "`T_PLUS_1_OPEN`",
        "`formal_db_mutation = no`",
        "不得宣称实盘能力",
    ):
        assert required_text in roadmap_text
    expected_row = f"| Pipeline | `{RUN_ID}` | `passed / t+1 open backtesting.py proof completed` |"
    assert expected_row in conclusion_index
    for suffix in ("card", "record", "evidence-index", "conclusion"):
        assert (pipeline_records / f"{RUN_ID}.{suffix}.md").exists()
