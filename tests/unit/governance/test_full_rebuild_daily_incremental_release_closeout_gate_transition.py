from pathlib import Path

from tests.unit.pipeline.constants import (
    FULL_REBUILD_AND_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_ACTION,
    FULL_REBUILD_AND_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_RUN_ID,
)

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


def test_release_closeout_blocked_state_is_registered() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    pipeline_contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    records_root = repo_root / "docs" / "04-execution" / "records" / "pipeline"

    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    with pipeline_contract_path.open("rb") as handle:
        pipeline_contract = tomllib.load(handle)

    modules = {module["module_id"]: module for module in registry["modules"]}
    card = (
        records_root / f"{FULL_REBUILD_AND_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_RUN_ID}.card.md"
    ).read_text(encoding="utf-8")
    record = (
        records_root / f"{FULL_REBUILD_AND_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_RUN_ID}.record.md"
    ).read_text(encoding="utf-8")
    conclusion = (
        records_root / f"{FULL_REBUILD_AND_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_RUN_ID}.conclusion.md"
    ).read_text(encoding="utf-8")
    evidence = (
        records_root
        / f"{FULL_REBUILD_AND_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_RUN_ID}.evidence-index.md"
    ).read_text(encoding="utf-8")
    conclusion_index = (
        repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    ).read_text(encoding="utf-8")

    assert registry["current_allowed_next_card"] == (
        FULL_REBUILD_AND_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_ACTION
    )
    assert modules["pipeline"]["active_card"] == (
        "docs/04-execution/records/pipeline/"
        f"{FULL_REBUILD_AND_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_RUN_ID}.card.md"
    )
    assert modules["pipeline"]["release_conclusion"] == (
        "docs/04-execution/records/pipeline/"
        f"{FULL_REBUILD_AND_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_RUN_ID}.conclusion.md"
    )
    assert modules["pipeline"]["evidence_index"] == (
        "docs/04-execution/records/pipeline/"
        f"{FULL_REBUILD_AND_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_RUN_ID}.evidence-index.md"
    )
    assert (
        "full_rebuild_daily_incremental_release_closeout_blocked"
        in modules["pipeline"]["proof_status"]
    )
    assert "formal_release_evidence_incomplete" in modules["pipeline"]["proof_status"]
    assert "full_rebuild_proof_missing" in modules["pipeline"]["formal_db_permission"]
    assert pipeline_contract["next_allowed_action"] == (
        FULL_REBUILD_AND_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_ACTION
    )
    assert pipeline_contract["release_conclusion"] == modules["pipeline"]["release_conclusion"]
    assert pipeline_contract["evidence_index"] == modules["pipeline"]["evidence_index"]
    assert "状态：`blocked / formal release evidence incomplete`" in card
    assert "result | `blocked / formal release evidence incomplete`" in record
    assert "formal full rebuild proof | `blocked`" in conclusion
    assert "daily incremental release proof | `blocked`" in conclusion
    assert "formal full rebuild not executed" in evidence
    assert (
        f"| Pipeline | `{FULL_REBUILD_AND_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_RUN_ID}` | "
        "`blocked / formal release evidence incomplete` |"
    ) in conclusion_index
