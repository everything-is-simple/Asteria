from pathlib import Path
from shutil import copy2, copytree

from scripts.governance.check_project_governance import run_checks

from asteria.governance.release_gates import ReleaseGateRecord, _check_gate_ledger

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


def test_project_governance_passes_current_repo() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    findings = [
        finding
        for finding in run_checks(repo_root)
        if "evidence asset path does not exist" not in finding.message
        and "release gate evidence asset does not exist" not in finding.message
        and "latest docs/code snapshot asset is missing" not in finding.message
        and "MALF authority zip asset is missing" not in finding.message
    ]

    assert findings == []


def test_malf_module_contract_points_at_month_bounded_closeout() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    contract_path = repo_root / "governance" / "module_api_contracts" / "malf.toml"
    with contract_path.open("rb") as handle:
        contract = tomllib.load(handle)

    assert contract["release_conclusion"] == (
        "docs/04-execution/records/malf/malf-month-bounded-proof-build-20260506-01.conclusion.md"
    )
    assert contract["evidence_index"] == (
        "docs/04-execution/records/malf/malf-month-bounded-proof-build-20260506-01.evidence-index.md"
    )
    assert (
        contract["formal_db_permission"]
        == "released_day_week_month_core_lifespan_service_only; malf_full_build_requires_new_card"
    )


def test_project_governance_rejects_multiple_build_allowed_mainline_modules(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            'doc_status = "frozen six-doc set / bounded proof passed / '
            'production hardening passed"\n'
            "allow_build = false",
            'doc_status = "frozen six-doc set / bounded proof passed / '
            'production hardening passed"\n'
            "allow_build = true",
            1,
        ),
        encoding="utf-8",
    )

    assert any(
        "pipeline orchestration next card must not reopen any mainline build/review flag" in message
        for message in _messages(repo_root)
    )


def test_project_governance_rejects_pyproject_next_card_state(tmp_path: Path) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    pyproject_path = repo_root / "pyproject.toml"
    pyproject_text = pyproject_path.read_text(encoding="utf-8")
    if "current_allowed_next_card" not in pyproject_text:
        pyproject_path.write_text(
            pyproject_text.replace(
                "max_python_file_lines = 500",
                'current_allowed_next_card = "signal_freeze_review"\nmax_python_file_lines = 500',
            ),
            encoding="utf-8",
        )

    assert any(
        "pyproject governance must not define current_allowed_next_card" in message
        for message in _messages(repo_root)
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
    pipeline_script = repo_root / "scripts" / "pipeline" / "run_pipeline_build.py"
    pipeline_script.parent.mkdir(parents=True)
    pipeline_script.write_text("raise SystemExit(0)\n", encoding="utf-8")

    assert any(
        "pre-gate module has forbidden formal runner" in message for message in _messages(repo_root)
    )


def test_project_governance_rejects_pre_gate_db_create_script(tmp_path: Path) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    pipeline_script = repo_root / "scripts" / "pipeline" / "create_pipeline_schema.py"
    pipeline_script.parent.mkdir(parents=True)
    pipeline_script.write_text("raise SystemExit(0)\n", encoding="utf-8")

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


def test_project_governance_rejects_repo_root_codex_tmp(tmp_path: Path) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    codex_tmp = repo_root / ".codex-tmp"
    codex_tmp.mkdir()
    (codex_tmp / "scratch.txt").write_text("temporary\n", encoding="utf-8")

    assert any(
        "generated cache/report artifact is inside repo root" in message
        for message in _messages(repo_root)
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
            r"H:\Asteria-Validated\2.backups\Asteria-malf-day-bounded-proof-20260428-01.zip",
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


def test_project_governance_allows_blocked_gap_conclusion_without_release_assets(
    tmp_path: Path,
) -> None:
    repo_root = _copy_governance_repo(tmp_path)
    run_id = "malf-lifespan-dense-bar-snapshot-gap-20260429-01"
    record_dir = repo_root / "docs" / "04-execution" / "records" / "malf"
    for suffix in ["card", "record", "evidence-index", "conclusion"]:
        (record_dir / f"{run_id}.{suffix}.md").write_text(
            "# MALF Lifespan Dense Bar Snapshot Gap\n\n状态：`blocked`\n",
            encoding="utf-8",
        )
    index_path = repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    index_text = index_path.read_text(encoding="utf-8")
    conclusion_link = (
        "[conclusion](records/malf/malf-lifespan-dense-bar-snapshot-gap-20260429-01.conclusion.md)"
    )
    evidence_link = (
        "[evidence-index]"
        "(records/malf/malf-lifespan-dense-bar-snapshot-gap-20260429-01.evidence-index.md)"
    )
    index_path.write_text(
        index_text + "\n| MALF | `malf-lifespan-dense-bar-snapshot-gap-20260429-01` | `blocked` | "
        f"{conclusion_link} | {evidence_link} |\n",
        encoding="utf-8",
    )

    messages = _messages(repo_root)

    assert not any(
        "release gate evidence-index missing required asset" in message for message in messages
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
        / "signal"
        / "signal-production-builder-hardening-20260506-01.conclusion.md"
    )
    conclusion_text = conclusion_path.read_text(encoding="utf-8")
    conclusion_path.write_text(
        conclusion_text.replace(
            "`upstream_pre_position_release_decision`",
            "`malf_dense_resolution`",
            1,
        ),
        encoding="utf-8",
    )

    assert any(
        "release gate allowed next action must match registry next_card" in message
        for message in _messages(repo_root)
    )


def test_release_gate_ledger_check_does_not_depend_on_alpha_freeze_review_phrase() -> None:
    record = ReleaseGateRecord(
        module_id="signal",
        run_id="signal-bounded-proof-20260429-01",
        status="passed",
        conclusion_path=Path("docs/04-execution/records/signal/signal.conclusion.md"),
        evidence_path=Path("docs/04-execution/records/signal/signal.evidence-index.md"),
    )
    ledger_text = """
    ## Signal Bounded Proof 放行记录
    | run_id | `signal-bounded-proof-20260429-01` |
    | module | `signal` |
    | allowed next action | `Position freeze review` |
    """

    assert _check_gate_ledger(record, ledger_text, "Position freeze review") == []
