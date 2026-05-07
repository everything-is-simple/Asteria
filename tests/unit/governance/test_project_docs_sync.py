from pathlib import Path
from shutil import copy2, copytree

from asteria.governance.docs_sync import apply_safe_sync, run_docs_sync_checks


def _copy_docs_sync_repo(tmp_path: Path) -> Path:
    source_root = Path(__file__).resolve().parents[3]
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    for file_name in ["README.md", "AGENTS.md", "pyproject.toml"]:
        copy2(source_root / file_name, repo_root / file_name)
    for directory_name in ["docs", "governance"]:
        copytree(source_root / directory_name, repo_root / directory_name)

    return repo_root


def _messages(repo_root: Path) -> list[str]:
    return [finding.message for finding in run_docs_sync_checks(repo_root)]


def test_docs_sync_rejects_missing_latest_malf_review_index_row(
    tmp_path: Path,
) -> None:
    repo_root = _copy_docs_sync_repo(tmp_path)
    index_path = repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    index_path.write_text(
        "\n".join(
            line
            for line in index_path.read_text(encoding="utf-8").splitlines()
            if "malf-authority-runtime-completeness-review-20260506-01" not in line
        ),
        encoding="utf-8",
    )
    assert any(
        "execution conclusion is missing from conclusion index" in message
        for message in _messages(repo_root)
    )


def test_docs_sync_rejects_conclusion_without_evidence_index(tmp_path: Path) -> None:
    repo_root = _copy_docs_sync_repo(tmp_path)
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
        "execution conclusion is missing matching evidence-index" in message
        for message in _messages(repo_root)
    )


def test_docs_sync_safe_apply_registers_missing_conclusion_index_row(
    tmp_path: Path,
) -> None:
    repo_root = _copy_docs_sync_repo(tmp_path)
    index_path = repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    index_text = index_path.read_text(encoding="utf-8")
    malf_row = (
        "| MALF | `malf-day-bounded-proof-20260428-01` | `passed` | "
        "[conclusion](records/malf/malf-day-bounded-proof-20260428-01.conclusion.md) | "
        "[evidence-index]"
        "(records/malf/malf-day-bounded-proof-20260428-01.evidence-index.md) |\n"
    )
    index_path.write_text(
        index_text.replace(malf_row, ""),
        encoding="utf-8",
    )

    report = apply_safe_sync(repo_root)

    updated_text = index_path.read_text(encoding="utf-8")
    assert "malf-day-bounded-proof-20260428-01" in updated_text
    assert any(
        action.path == index_path and action.message == "registered missing execution conclusion"
        for action in report.actions
    )


def test_docs_sync_rejects_data_foundation_inside_strategy_mainline(
    tmp_path: Path,
) -> None:
    repo_root = _copy_docs_sync_repo(tmp_path)
    roadmap_path = repo_root / "docs" / "03-refactor" / "04-asteria-full-system-roadmap-v1.md"
    roadmap_text = roadmap_path.read_text(encoding="utf-8")
    roadmap_path.write_text(
        roadmap_text.replace(
            "策略主线：\nMALF -> Alpha -> Signal",
            "策略主线：\nData Foundation -> MALF -> Alpha -> Signal",
        ),
        encoding="utf-8",
    )

    assert any(
        "Data Foundation must not appear in Strategy Mainline" in message
        for message in _messages(repo_root)
    )


def test_docs_sync_rejects_pre_gate_system_readout_formal_runner(tmp_path: Path) -> None:
    repo_root = _copy_docs_sync_repo(tmp_path)
    system_runner = repo_root / "scripts" / "system_readout" / "run_system_readout_build.py"
    system_runner.parent.mkdir(parents=True)
    system_runner.write_text("raise SystemExit(0)\n", encoding="utf-8")

    assert any(
        "pre-gate module has forbidden formal runner" in message for message in _messages(repo_root)
    )


def test_docs_sync_rejects_stale_validated_docs_code_snapshot(tmp_path: Path) -> None:
    repo_root = _copy_docs_sync_repo(tmp_path)
    inventory_path = repo_root / "docs" / "01-architecture" / "02-validated-asset-inventory-v1.md"
    inventory_path.write_text(
        inventory_path.read_text(encoding="utf-8").replace(
            "Asteria-docs-code-20260502-104932.zip",
            "Asteria-docs-code-20260428-123534.zip",
        ),
        encoding="utf-8",
    )

    assert any(
        "validated asset inventory must reference latest docs/code snapshot" in message
        for message in _messages(repo_root)
    )


def test_docs_sync_rejects_missing_malf_authority_bridge_file_reference(tmp_path: Path) -> None:
    repo_root = _copy_docs_sync_repo(tmp_path)
    bridge_path = repo_root / "docs" / "02-modules" / "02-malf-authoritative-design-bridge-v1.md"
    bridge_path.write_text(
        bridge_path.read_text(encoding="utf-8").replace(
            "`MALF_03_System_Service_Interface_v1_3.md`",
            "`MALF_03_System_Service_Interface_REMOVED.md`",
        ),
        encoding="utf-8",
    )

    assert any(
        "MALF authority bridge missing authority file reference" in message
        for message in _messages(repo_root)
    )
