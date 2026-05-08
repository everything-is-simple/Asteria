from __future__ import annotations

from pathlib import Path
from shutil import copy2, copytree

from tests.unit.system_readout.support import (
    build_request as build_system_request,
)
from tests.unit.system_readout.support import (
    seed_chain,
)

from asteria.system_readout.bootstrap import run_system_readout_build

SYSTEM_SOURCE_RUN_ID = "system-readout-bounded-proof-unit-001"
PIPELINE_RUN_ID = "pipeline-single-module-orchestration-build-card-20260508-01"
PIPELINE_SCOPE_FREEZE_RUN_ID = "pipeline-build-runtime-authorization-scope-freeze-20260508-01"
PIPELINE_RELEASE_DOC_STATUS = (
    "frozen six-doc set / freeze review passed / single-module orchestration build passed / "
    "full-chain not executed"
)
PIPELINE_PREPARED_DOC_STATUS = (
    "frozen six-doc set / freeze review passed / single-module orchestration build prepared / "
    "build not executed"
)
PIPELINE_RELEASE_CONCLUSION = (
    f'release_conclusion = "docs/04-execution/records/pipeline/{PIPELINE_RUN_ID}.conclusion.md"'
)
PIPELINE_SCOPE_FREEZE_CONCLUSION = (
    f"release_conclusion = "
    f'"docs/04-execution/records/pipeline/{PIPELINE_SCOPE_FREEZE_RUN_ID}.conclusion.md"'
)
PIPELINE_RELEASE_EVIDENCE_INDEX = (
    f'evidence_index = "docs/04-execution/records/pipeline/{PIPELINE_RUN_ID}.evidence-index.md"'
)
PIPELINE_SCOPE_FREEZE_EVIDENCE_INDEX = (
    f"evidence_index = "
    f'"docs/04-execution/records/pipeline/{PIPELINE_SCOPE_FREEZE_RUN_ID}.evidence-index.md"'
)


def build_governance_repo(tmp_path: Path) -> Path:
    source_root = Path(__file__).resolve().parents[3]
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    for file_name in ["README.md", "AGENTS.md", "pyproject.toml"]:
        copy2(source_root / file_name, repo_root / file_name)
    for directory_name in ["docs", "governance"]:
        copytree(source_root / directory_name, repo_root / directory_name)
    return repo_root


def build_prepared_pipeline_repo(tmp_path: Path) -> Path:
    repo_root = build_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            'current_allowed_next_card = ""',
            'current_allowed_next_card = "pipeline_single_module_orchestration_build_card"',
        )
        .replace(
            f'status = "released"\ndoc_status = "{PIPELINE_RELEASE_DOC_STATUS}"',
            f'status = "freeze_review_passed"\ndoc_status = "{PIPELINE_PREPARED_DOC_STATUS}"',
            1,
        )
        .replace(
            'next_card = "none"',
            'next_card = "pipeline_single_module_orchestration_build_card"',
            1,
        )
        .replace(
            PIPELINE_RELEASE_CONCLUSION,
            PIPELINE_SCOPE_FREEZE_CONCLUSION,
            1,
        )
        .replace(
            PIPELINE_RELEASE_EVIDENCE_INDEX,
            PIPELINE_SCOPE_FREEZE_EVIDENCE_INDEX,
            1,
        ),
        encoding="utf-8",
    )
    return repo_root


def seed_system_source(tmp_path: Path) -> Path:
    seed_chain(tmp_path)
    summary = run_system_readout_build(build_system_request(tmp_path))
    if summary.hard_fail_count != 0:
        raise AssertionError(f"seed system source failed: {summary.as_dict()}")
    return tmp_path / "data" / "system.duckdb"
