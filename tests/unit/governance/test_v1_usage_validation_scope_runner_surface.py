from __future__ import annotations

from pathlib import Path

from tests.unit.governance.test_project_docs_sync import _messages
from tests.unit.pipeline.support import build_governance_repo


def test_docs_sync_allows_v1_usage_validation_scope_runner(tmp_path: Path) -> None:
    repo_root = build_governance_repo(tmp_path)
    source_runner = (
        Path(__file__).resolve().parents[3]
        / "scripts"
        / "pipeline"
        / "run_v1_usage_validation_scope.py"
    )
    target_runner = repo_root / "scripts" / "pipeline" / "run_v1_usage_validation_scope.py"
    target_runner.parent.mkdir(parents=True, exist_ok=True)
    target_runner.write_text(source_runner.read_text(encoding="utf-8"), encoding="utf-8")

    assert not any(
        "pre-gate module has forbidden formal runner" in message for message in _messages(repo_root)
    )


def test_docs_sync_allows_v1_application_db_readiness_runner(tmp_path: Path) -> None:
    repo_root = build_governance_repo(tmp_path)
    source_runner = (
        Path(__file__).resolve().parents[3]
        / "scripts"
        / "pipeline"
        / "run_v1_application_db_readiness_audit.py"
    )
    target_runner = repo_root / "scripts" / "pipeline" / "run_v1_application_db_readiness_audit.py"
    target_runner.parent.mkdir(parents=True, exist_ok=True)
    target_runner.write_text(source_runner.read_text(encoding="utf-8"), encoding="utf-8")

    assert not any(
        "pre-gate module has forbidden formal runner" in message for message in _messages(repo_root)
    )


def test_docs_sync_allows_v1_usage_readout_report_runner(tmp_path: Path) -> None:
    repo_root = build_governance_repo(tmp_path)
    source_runner = (
        Path(__file__).resolve().parents[3]
        / "scripts"
        / "pipeline"
        / "run_v1_usage_readout_report.py"
    )
    target_runner = repo_root / "scripts" / "pipeline" / "run_v1_usage_readout_report.py"
    target_runner.parent.mkdir(parents=True, exist_ok=True)
    target_runner.write_text(source_runner.read_text(encoding="utf-8"), encoding="utf-8")

    assert not any(
        "pre-gate module has forbidden formal runner" in message for message in _messages(repo_root)
    )


def test_docs_sync_allows_v1_usage_value_decision_runner(tmp_path: Path) -> None:
    repo_root = build_governance_repo(tmp_path)
    source_runner = (
        Path(__file__).resolve().parents[3]
        / "scripts"
        / "pipeline"
        / "run_v1_usage_value_decision.py"
    )
    target_runner = repo_root / "scripts" / "pipeline" / "run_v1_usage_value_decision.py"
    target_runner.parent.mkdir(parents=True, exist_ok=True)
    target_runner.write_text(source_runner.read_text(encoding="utf-8"), encoding="utf-8")

    assert not any(
        "pre-gate module has forbidden formal runner" in message for message in _messages(repo_root)
    )
