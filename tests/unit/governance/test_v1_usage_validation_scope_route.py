from __future__ import annotations

from pathlib import Path

RUN_ID = "v1-usage-validation-scope-card-20260512-01"


def test_v1_usage_validation_scope_route_is_recorded_without_changing_terminal_live_next() -> None:
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
    assert f"| Pipeline | `{RUN_ID}` | `passed / scope frozen / roadmap-only route` |" in (
        conclusion_index
    )
    expected_row = (
        "| 1 | `v1-usage-validation-scope-card` | "
        "passed / scope frozen / 31-industry sample locked |"
    )
    assert expected_row in roadmap_text
    assert "申万一级行业各取" in roadmap_text
    assert "`31`" in roadmap_text
    assert "下一张只允许进入 `v1-application-db-readiness-audit-card`" in roadmap_text
    for suffix in ("card", "record", "evidence-index", "conclusion"):
        assert (pipeline_records / f"{RUN_ID}.{suffix}.md").exists()
