from __future__ import annotations

from pathlib import Path

RUN_ID = "v1-application-db-readiness-audit-card-20260513-01"


def test_v1_application_db_readiness_audit_route_is_recorded_without_reopening_live_next() -> None:
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
    assert (
        "| 2 | `v1-application-db-readiness-audit-card` | "
        "passed / application DB readiness audited |"
    ) in roadmap_text
    assert ("| 3 | `v1-usage-readout-report-card` | prepared next route card |") in roadmap_text
    assert f"| Pipeline | `{RUN_ID}` | `passed / application DB readiness audited` |" in (
        conclusion_index
    )
    for suffix in ("card", "record", "evidence-index", "conclusion"):
        assert (pipeline_records / f"{RUN_ID}.{suffix}.md").exists()
