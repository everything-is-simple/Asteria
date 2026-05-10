from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

from tests.unit.pipeline.support import (
    CURRENT_ACTIVE_MAINLINE_MODULE,
    CURRENT_ALLOWED_NEXT_CARD_ACTION,
    PIPELINE_BOUNDED_PROOF_CARD_RUN_ID,
    PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID,
    PIPELINE_CURRENT_DOC_STATUS,
    PIPELINE_DRY_RUN_CARD_RUN_ID,
    PIPELINE_FULL_CHAIN_PASSED_DOC_STATUS,
    PIPELINE_YEAR_REPLAY_CARD_RUN_ID,
)


def test_pipeline_full_chain_dry_run_passes_and_closes_current_next_card() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    modules = {module["module_id"]: module for module in registry["modules"]}
    conclusion_index = (
        repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    ).read_text(encoding="utf-8")
    dry_run_conclusion = (
        repo_root
        / "docs/04-execution/records/pipeline/"
        / f"{PIPELINE_DRY_RUN_CARD_RUN_ID}.conclusion.md"
    ).read_text(encoding="utf-8")

    assert registry["active_mainline_module"] == CURRENT_ACTIVE_MAINLINE_MODULE
    assert registry["current_allowed_next_card"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert modules["pipeline"]["status"] == "released"
    assert modules["pipeline"]["doc_status"] == PIPELINE_CURRENT_DOC_STATUS
    assert modules["pipeline"]["doc_status"] != PIPELINE_FULL_CHAIN_PASSED_DOC_STATUS
    assert modules["pipeline"]["next_card"] == CURRENT_ALLOWED_NEXT_CARD_ACTION
    assert modules["pipeline"]["proof_run_id"] == PIPELINE_BOUNDED_PROOF_CARD_RUN_ID
    assert PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID in conclusion_index
    assert f"| Pipeline | `{PIPELINE_DRY_RUN_CARD_RUN_ID}` | `passed` |" in conclusion_index
    assert f"| Pipeline | `{PIPELINE_BOUNDED_PROOF_CARD_RUN_ID}` | `passed` |" in conclusion_index
    assert f"| Pipeline | `{PIPELINE_YEAR_REPLAY_CARD_RUN_ID}` | `blocked` |" in conclusion_index
    assert (
        "当前唯一 prepared next card 已切到 `position-2024-coverage-repair-card-20260509-01`"
        in (conclusion_index)
    )
    assert "system-readout-2024-coverage-repair-card-20260509-01" in conclusion_index
    assert "状态：`passed`" in dry_run_conclusion
    assert "| allowed next action | `none` |" in dry_run_conclusion
