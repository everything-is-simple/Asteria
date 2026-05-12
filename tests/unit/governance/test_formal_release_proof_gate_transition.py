from pathlib import Path

from tests.unit.pipeline.constants import (
    FINAL_RELEASE_CLOSEOUT_ACTION,
    FORMAL_RELEASE_PROOF_RUN_ID,
    FULL_REBUILD_AND_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_RUN_ID,
)

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


def test_formal_release_proof_card_transitioned_to_final_closeout() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    pipeline_contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    records_root = repo_root / "docs" / "04-execution" / "records" / "pipeline"

    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    with pipeline_contract_path.open("rb") as handle:
        pipeline_contract = tomllib.load(handle)

    modules = {module["module_id"]: module for module in registry["modules"]}
    card = (records_root / f"{FORMAL_RELEASE_PROOF_RUN_ID}.card.md").read_text(encoding="utf-8")
    conclusion = (records_root / f"{FORMAL_RELEASE_PROOF_RUN_ID}.conclusion.md").read_text(
        encoding="utf-8"
    )
    evidence = (records_root / f"{FORMAL_RELEASE_PROOF_RUN_ID}.evidence-index.md").read_text(
        encoding="utf-8"
    )
    old_closeout = (
        records_root / f"{FULL_REBUILD_AND_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_RUN_ID}.conclusion.md"
    ).read_text(encoding="utf-8")
    conclusion_index = (
        repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    ).read_text(encoding="utf-8")

    next_card = (records_root / "final-release-closeout-card.card.md").read_text(encoding="utf-8")

    assert registry["current_allowed_next_card"] == FINAL_RELEASE_CLOSEOUT_ACTION
    assert modules["pipeline"]["active_card"] == (
        f"docs/04-execution/records/pipeline/{FORMAL_RELEASE_PROOF_RUN_ID}.card.md"
    )
    assert modules["pipeline"]["release_conclusion"] == (
        f"docs/04-execution/records/pipeline/{FORMAL_RELEASE_PROOF_RUN_ID}.conclusion.md"
    )
    assert modules["pipeline"]["evidence_index"] == (
        f"docs/04-execution/records/pipeline/{FORMAL_RELEASE_PROOF_RUN_ID}.evidence-index.md"
    )
    assert (
        "formal_full_rebuild_and_daily_incremental_release_proof_passed"
        in modules["pipeline"]["proof_status"]
    )
    assert "final_release_closeout_pending" in modules["pipeline"]["proof_status"]
    assert (
        "guarded_promote_completed_with_explicit_allow"
        in modules["pipeline"]["formal_db_permission"]
    )
    assert pipeline_contract["next_allowed_action"] == FINAL_RELEASE_CLOSEOUT_ACTION
    assert pipeline_contract["release_conclusion"] == modules["pipeline"]["release_conclusion"]
    assert pipeline_contract["evidence_index"] == modules["pipeline"]["evidence_index"]
    assert "状态：`passed / formal release evidence complete`" in card
    assert "状态：`passed / formal release evidence complete`" in conclusion
    assert "formal-release-proof-manifest.json" in conclusion
    assert "run_formal_release_source_proof.py" in evidence
    assert "formal full rebuild proof | `passed`" in conclusion
    assert "daily incremental release proof | `passed`" in conclusion
    assert "backup manifest" in evidence
    assert "staging manifest" in evidence
    assert "promote manifest" in evidence
    assert "final release evidence" in evidence
    assert "状态：`blocked / formal release evidence incomplete`" in old_closeout
    assert "状态：`prepared / pending final release closeout`" in next_card
    passed_row = (
        f"| Pipeline | `{FORMAL_RELEASE_PROOF_RUN_ID}` | "
        "`passed / formal release evidence complete` |"
    )
    prepared_row = (
        "| Pipeline | `final-release-closeout-card` | `prepared / pending final release closeout` |"
    )
    assert passed_row in conclusion_index
    assert prepared_row in conclusion_index
