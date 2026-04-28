from pathlib import Path
from shutil import copy2, copytree

from scripts.governance.check_project_governance import run_checks


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


def test_project_governance_passes_current_repo() -> None:
    repo_root = Path(__file__).resolve().parents[3]

    assert run_checks(repo_root) == []


def test_project_governance_rejects_multiple_build_allowed_mainline_modules(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            'allow_build = false\ndoc_path = "docs/02-modules/alpha"',
            'allow_build = true\ndoc_path = "docs/02-modules/alpha"',
        ),
        encoding="utf-8",
    )

    assert any(
        "only one mainline module may allow build" in message for message in _messages(repo_root)
    )


def test_project_governance_rejects_unregistered_topology_database(tmp_path: Path) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    topology_doc = repo_root / "docs" / "01-architecture" / "01-database-topology-v1.md"
    topology_doc.write_text(
        topology_doc.read_text(encoding="utf-8") + "\n`rogue.duckdb`\n",
        encoding="utf-8",
    )

    assert any(
        "database topology doc mentions unregistered DB" in message
        for message in _messages(repo_root)
    )


def test_project_governance_rejects_mock_or_legacy_official_input(tmp_path: Path) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    contract_path = repo_root / "governance" / "module_api_contracts" / "malf.toml"
    contract_path.write_text(
        contract_path.read_text(encoding="utf-8").replace(
            'source_role = "official"',
            'source_role = "mock"',
            1,
        ),
        encoding="utf-8",
    )

    assert any(
        "official input cannot use mock or legacy downstream source" in message
        for message in _messages(repo_root)
    )


def test_project_governance_rejects_pre_gate_runner_script(tmp_path: Path) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    alpha_script = repo_root / "scripts" / "alpha" / "run_alpha_bounded_proof.py"
    alpha_script.parent.mkdir(parents=True)
    alpha_script.write_text("raise SystemExit(0)\n", encoding="utf-8")

    assert any(
        "pre-gate module has forbidden formal runner" in message for message in _messages(repo_root)
    )


def test_project_governance_rejects_pre_gate_db_create_script(tmp_path: Path) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    alpha_script = repo_root / "scripts" / "alpha" / "create_alpha_schema.py"
    alpha_script.parent.mkdir(parents=True)
    alpha_script.write_text("raise SystemExit(0)\n", encoding="utf-8")

    assert any(
        "pre-gate module has forbidden formal DB create script" in message
        for message in _messages(repo_root)
    )


def test_project_governance_rejects_repo_root_duckdb(tmp_path: Path) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    (repo_root / "rogue.duckdb").write_bytes(b"")

    assert any(
        "generated database artifact is inside repo" in message for message in _messages(repo_root)
    )


def test_project_governance_rejects_docs_sync_next_card_mismatch(tmp_path: Path) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            'next_card = "alpha_freeze_review"',
            'next_card = "malf_day_bounded_proof"',
        ),
        encoding="utf-8",
    )

    assert any(
        "MALF next_card must be alpha_freeze_review" in message for message in _messages(repo_root)
    )


def test_project_governance_rejects_missing_release_gate_conclusion(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    conclusion_path = (
        repo_root
        / "docs"
        / "04-execution"
        / "records"
        / "malf"
        / "malf-day-bounded-proof-20260428-01.conclusion.md"
    )
    conclusion_path.unlink()

    assert any(
        "release gate missing required artifact: conclusion" in message
        for message in _messages(repo_root)
    )


def test_project_governance_rejects_missing_release_gate_evidence_index(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    evidence_path = (
        repo_root
        / "docs"
        / "04-execution"
        / "records"
        / "malf"
        / "malf-day-bounded-proof-20260428-01.evidence-index.md"
    )
    evidence_path.unlink()

    assert any(
        "release gate missing required artifact: evidence-index" in message
        for message in _messages(repo_root)
    )


def test_project_governance_rejects_missing_release_gate_external_asset(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    evidence_path = (
        repo_root
        / "docs"
        / "04-execution"
        / "records"
        / "malf"
        / "malf-day-bounded-proof-20260428-01.evidence-index.md"
    )
    evidence_text = evidence_path.read_text(encoding="utf-8")
    evidence_path.write_text(
        evidence_text.replace(
            r"H:\Asteria-Validated\Asteria-malf-day-bounded-proof-20260428-01.zip",
            r"H:\Asteria-Validated\missing-release-gate-evidence.zip",
        ),
        encoding="utf-8",
    )

    assert any(
        "release gate evidence asset does not exist: validated_zip" in message
        for message in _messages(repo_root)
    )


def test_project_governance_rejects_missing_release_gate_manifest(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    evidence_path = (
        repo_root
        / "docs"
        / "04-execution"
        / "records"
        / "malf"
        / "malf-day-bounded-proof-20260428-01.evidence-index.md"
    )
    evidence_text = evidence_path.read_text(encoding="utf-8")
    evidence_path.write_text(
        evidence_text.replace(
            r"H:\Asteria-report\malf\2026-04-28"
            r"\malf-day-bounded-proof-20260428-01\manifest.json",
            r"H:\Asteria-report\malf\2026-04-28"
            r"\malf-day-bounded-proof-20260428-01\missing-manifest.json",
        ),
        encoding="utf-8",
    )

    assert any(
        "release gate evidence asset does not exist: manifest" in message
        for message in _messages(repo_root)
    )


def test_project_governance_rejects_release_gate_next_card_mismatch(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    conclusion_path = (
        repo_root
        / "docs"
        / "04-execution"
        / "records"
        / "malf"
        / "malf-day-bounded-proof-20260428-01.conclusion.md"
    )
    conclusion_text = conclusion_path.read_text(encoding="utf-8")
    conclusion_path.write_text(
        conclusion_text.replace("`Alpha freeze review`", "`Signal freeze review`", 1),
        encoding="utf-8",
    )

    assert any(
        "release gate allowed next action must match registry next_card" in message
        for message in _messages(repo_root)
    )
