from pathlib import Path

from scripts.governance.check_project_governance import run_checks


def test_project_governance_passes_current_repo() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    assert run_checks(repo_root) == []
