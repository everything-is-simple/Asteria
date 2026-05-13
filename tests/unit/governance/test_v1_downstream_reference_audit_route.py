from __future__ import annotations

from pathlib import Path

RUN_ID = "v1-downstream-reference-audit-20260513-01"


def test_v1_downstream_reference_audit_is_recorded_as_supplemental_input() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    registry_text = (repo_root / "governance" / "module_gate_registry.toml").read_text(
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
    assert "`v1-downstream-reference-audit-20260513-01`" in roadmap_text
    assert "| 4 | `v1-usage-value-decision-card` | prepared next route card |" in roadmap_text
    expected_row = (
        f"| Pipeline | `{RUN_ID}` | `passed / downstream semantics benchmark input generated` |"
    )
    assert expected_row in conclusion_index
    for suffix in ("card", "record", "evidence-index", "conclusion"):
        assert (pipeline_records / f"{RUN_ID}.{suffix}.md").exists()
