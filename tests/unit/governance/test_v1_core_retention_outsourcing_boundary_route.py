from __future__ import annotations

from pathlib import Path

RUN_ID = "v1-core-retention-and-outsourcing-boundary-card-20260513-01"


def test_v1_core_retention_outsourcing_boundary_is_recorded_without_reopening_live_next() -> None:
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
    assert "Phase 2：Core Retention And Outsourcing Boundary" in roadmap_text
    assert (
        "| 1 | `v1-core-retention-and-outsourcing-boundary-card` | "
        "passed / core retention and outsourcing boundary frozen |"
    ) in roadmap_text
    assert "`Data source fact + MALF + Alpha + Signal`" in roadmap_text
    assert "`Position / Portfolio Plan / Trade / System Readout`" in roadmap_text
    assert "`T+0 signal -> T+1 open execution`" in roadmap_text
    assert "`v1-signal-export-contract-card`" in ledger_text
    expected_row = (
        f"| Pipeline | `{RUN_ID}` | `passed / core retention and outsourcing boundary frozen` |"
    )
    assert expected_row in conclusion_index
    for suffix in ("card", "record", "evidence-index", "conclusion"):
        assert (pipeline_records / f"{RUN_ID}.{suffix}.md").exists()
