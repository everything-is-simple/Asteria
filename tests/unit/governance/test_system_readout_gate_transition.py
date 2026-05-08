from pathlib import Path
from shutil import copy2, copytree

from scripts.governance.check_project_governance import run_checks

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


def _copy_governance_repo(tmp_path: Path) -> Path:
    source_root = Path(__file__).resolve().parents[3]
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    for file_name in ["README.md", "AGENTS.md", "pyproject.toml"]:
        copy2(source_root / file_name, repo_root / file_name)
    for directory_name in ["docs", "governance"]:
        copytree(source_root / directory_name, repo_root / directory_name)
    scripts_governance = repo_root / "scripts" / "governance"
    scripts_governance.mkdir(parents=True)
    copy2(
        source_root / "scripts" / "governance" / "check_project_governance.py",
        scripts_governance / "check_project_governance.py",
    )
    return repo_root


def _messages(repo_root: Path) -> list[str]:
    return [finding.message for finding in run_checks(repo_root)]


def test_current_gate_advances_to_pipeline_freeze_review_after_system_readout_proof() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    modules = {module["module_id"]: module for module in registry["modules"]}
    conclusion_index = (
        repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    ).read_text(encoding="utf-8")
    position_conclusion = (
        repo_root
        / "docs/04-execution/records/position/"
        / "position-bounded-proof-build-card-20260506-01.conclusion.md"
    ).read_text(encoding="utf-8")
    portfolio_freeze_conclusion = (
        repo_root
        / "docs/04-execution/records/portfolio_plan/"
        / "portfolio-plan-freeze-review-20260507-01.conclusion.md"
    ).read_text(encoding="utf-8")
    portfolio_proof_conclusion = (
        repo_root
        / "docs/04-execution/records/portfolio_plan/"
        / "portfolio-plan-bounded-proof-build-card-20260507-01.conclusion.md"
    ).read_text(encoding="utf-8")
    trade_freeze_conclusion = (
        repo_root
        / "docs/04-execution/records/trade/"
        / "trade-freeze-review-20260507-01.conclusion.md"
    ).read_text(encoding="utf-8")
    trade_proof_conclusion = (
        repo_root
        / "docs/04-execution/records/trade/"
        / "trade-bounded-proof-build-card-20260507-01.conclusion.md"
    ).read_text(encoding="utf-8")
    system_freeze_conclusion = (
        repo_root
        / "docs/04-execution/records/system_readout/"
        / "system-readout-freeze-review-20260507-01.conclusion.md"
    ).read_text(encoding="utf-8")
    system_freeze_evidence = (
        repo_root
        / "docs/04-execution/records/system_readout/"
        / "system-readout-freeze-review-20260507-01.evidence-index.md"
    ).read_text(encoding="utf-8")
    system_proof_conclusion = (
        repo_root
        / "docs/04-execution/records/system_readout/"
        / "system-readout-bounded-proof-build-card-20260508-01.conclusion.md"
    ).read_text(encoding="utf-8")

    assert registry["active_mainline_module"] == "system_readout"
    assert registry["active_foundation_card"] == "none"
    assert registry["current_allowed_next_card"] == "pipeline_freeze_review"
    assert registry["latest_mainline_release_run_id"] == (
        "system-readout-bounded-proof-build-card-20260508-01"
    )
    assert modules["malf"]["allow_build"] is False
    assert modules["malf"]["next_card"] == "alpha_production_builder_hardening"
    assert modules["alpha"]["allow_build"] is False
    assert modules["alpha"]["next_card"] == "signal_production_builder_hardening"
    assert modules["signal"]["allow_build"] is False
    assert modules["signal"]["next_card"] == "upstream_pre_position_release_decision"
    assert modules["data"]["latest_completed_card"] == "data_reference_target_maintenance_closeout"
    assert modules["position"]["allow_review"] is False
    assert modules["position"]["allow_build"] is False
    assert modules["position"]["next_card"] == "portfolio_plan_freeze_review"
    assert modules["portfolio_plan"]["allow_review"] is False
    assert modules["portfolio_plan"]["allow_build"] is False
    assert modules["portfolio_plan"]["next_card"] == "trade_freeze_review"
    assert modules["portfolio_plan"]["freeze_review_status"] == "passed"
    assert modules["trade"]["allow_review"] is False
    assert modules["trade"]["allow_build"] is False
    assert modules["trade"]["status"] == "released"
    assert modules["trade"]["next_card"] == "system_readout_freeze_review"
    assert modules["trade"]["freeze_review_status"] == "passed"
    assert modules["trade"]["proof_status"] == "bounded_proof_passed; full_build_not_executed"
    assert modules["system_readout"]["status"] == "released"
    assert modules["system_readout"]["allow_review"] is False
    assert modules["system_readout"]["allow_build"] is True
    assert modules["system_readout"]["proof_status"] == (
        "bounded_proof_passed; full_build_not_executed"
    )
    assert modules["system_readout"]["next_card"] == "pipeline_freeze_review"
    assert modules["system_readout"]["active_card"] == (
        "docs/04-execution/records/pipeline/pipeline-freeze-review-20260508-01.card.md"
    )
    assert "data-reference-target-maintenance-scope-20260506-01" in conclusion_index
    assert "data-reference-target-maintenance-closeout-20260506-01" in conclusion_index
    assert "malf-week-bounded-proof-build-20260506-01" in conclusion_index
    assert "malf-month-bounded-proof-build-20260506-01" in conclusion_index
    assert "alpha-production-builder-hardening-20260506-01" in conclusion_index
    assert "signal-production-builder-hardening-20260506-01" in conclusion_index
    assert "portfolio-plan-bounded-proof-build-card-20260507-01" in conclusion_index
    assert "trade-freeze-review-20260507-01" in conclusion_index
    assert "trade-bounded-proof-build-card-20260507-01" in conclusion_index
    assert "upstream-pre-position-release-decision-20260506-01" in conclusion_index
    assert "position-bounded-proof-build-card-20260506-01" in conclusion_index
    assert "portfolio-plan-freeze-review-20260507-01" in conclusion_index
    assert "malf-v1-3-formal-rebuild-closeout-20260502-01" in conclusion_index
    assert "system-readout-freeze-review-20260507-01" in conclusion_index
    assert "system-readout-bounded-proof-build-card-20260508-01" in conclusion_index
    assert "状态：`passed`" in position_conclusion
    assert "| allowed next action | `portfolio_plan_freeze_review` |" in position_conclusion
    assert "状态：`passed`" in portfolio_freeze_conclusion
    assert "`portfolio_plan_bounded_proof_build_card`" in portfolio_freeze_conclusion
    assert "状态：`passed`" in portfolio_proof_conclusion
    assert "| allowed next action | `trade_freeze_review` |" in portfolio_proof_conclusion
    assert "状态：`passed`" in trade_freeze_conclusion
    assert "| allowed next action | `trade_bounded_proof_build_card` |" in trade_freeze_conclusion
    assert "| status | `passed` |" in trade_proof_conclusion
    assert "| allowed next action | `system_readout_freeze_review` |" in trade_proof_conclusion
    assert "状态：`passed`" in system_freeze_conclusion
    assert (
        "| allowed next action | `system_readout_bounded_proof_build_card` |"
        in system_freeze_conclusion
    )
    assert "[next prepared card](system-readout-bounded-proof-build-card-20260508-01.card.md)" in (
        system_freeze_evidence
    )
    assert "状态：`passed`" in system_proof_conclusion
    assert "| allowed next action | `Pipeline freeze review` |" in system_proof_conclusion


def test_project_governance_rejects_missing_current_next_card_file(tmp_path: Path) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    card_path = repo_root / (
        "docs/04-execution/records/pipeline/pipeline-freeze-review-20260508-01.card.md"
    )
    if card_path.exists():
        card_path.unlink()

    assert any(
        "current allowed next card is missing matching execution card" in message
        for message in _messages(repo_root)
    )


def test_project_governance_rejects_current_next_card_that_is_already_blocked(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    conclusion_path = repo_root / (
        "docs/04-execution/records/pipeline/pipeline-freeze-review-20260508-01.conclusion.md"
    )
    conclusion_path.parent.mkdir(parents=True, exist_ok=True)
    conclusion_path.write_text(
        "# Pipeline Freeze Review Conclusion\n\n状态：`blocked`\n",
        encoding="utf-8",
    )

    assert any(
        "current allowed next card must not point to a blocked execution conclusion" in message
        for message in _messages(repo_root)
    )


def test_project_governance_rejects_docs_sync_next_card_mismatch(tmp_path: Path) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            'current_allowed_next_card = "pipeline_freeze_review"',
            'current_allowed_next_card = "malf_day_bounded_proof"',
        ),
        encoding="utf-8",
    )

    assert any(
        "current_allowed_next_card must match active module next_card" in message
        for message in _messages(repo_root)
    )
