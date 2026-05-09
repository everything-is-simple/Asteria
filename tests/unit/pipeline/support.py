from __future__ import annotations

from pathlib import Path
from shutil import copy2, copytree

from tests.unit.pipeline import constants as pipeline_constants
from tests.unit.pipeline.constants import (
    CURRENT_PIPELINE_ACTIVE_CARD,
    PIPELINE_BOUNDED_INPUT_BOUNDARY,
    PIPELINE_BOUNDED_PROOF_CARD_ACTION,
    PIPELINE_BOUNDED_PROOF_CARD_RUN_ID,
    PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID,
    PIPELINE_BOUNDED_PROOF_FORMAL_DB_PERMISSION,
    PIPELINE_BOUNDED_PROOF_GATE_STATE,
    PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_CONCLUSION,
    PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_EVIDENCE_INDEX,
    PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID,
    PIPELINE_COVERAGE_GAP_EVIDENCE_INCOMPLETE_CLOSEOUT_ACTION,
    PIPELINE_CURRENT_DOC_STATUS,
    PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
    PIPELINE_CURRENT_GATE_STATE,
    PIPELINE_DRY_RUN_CARD_ACTION,
    PIPELINE_DRY_RUN_CARD_RUN_ID,
    PIPELINE_DRY_RUN_FORMAL_DB_PERMISSION,
    PIPELINE_DRY_RUN_GATE_STATE,
    PIPELINE_DRY_RUN_INPUT_BOUNDARY,
    PIPELINE_DRY_RUN_SCOPE_FREEZE_RUN_ID,
    PIPELINE_FULL_CHAIN_PREPARED_DOC_STATUS,
    PIPELINE_MALF_REPAIR_ACTION,
    PIPELINE_MALF_REPAIR_ACTIVE_CARD,
    PIPELINE_MALF_REPAIR_PREPARED_DOC_STATUS,
    PIPELINE_MALF_REPAIR_PREPARED_FORMAL_DB_PERMISSION,
    PIPELINE_MALF_REPAIR_PREPARED_GATE_STATE,
    PIPELINE_PREPARED_DOC_STATUS,
    PIPELINE_PREPARED_FORMAL_DB_PERMISSION,
    PIPELINE_PREPARED_GATE_STATE,
    PIPELINE_RELEASE_CONCLUSION,
    PIPELINE_RELEASE_EVIDENCE_INDEX,
    PIPELINE_RUN_ID,
    PIPELINE_SCOPE_FREEZE_CONCLUSION,
    PIPELINE_SCOPE_FREEZE_EVIDENCE_INDEX,
    PIPELINE_SCOPE_FREEZE_RUN_ID,
    PIPELINE_YEAR_REPLAY_CARD_ACTION,
    PIPELINE_YEAR_REPLAY_PREPARED_DOC_STATUS,
    PIPELINE_YEAR_REPLAY_RERUN_CARD_ACTION,
    PIPELINE_YEAR_REPLAY_RERUN_CARD_RUN_ID,
    PIPELINE_YEAR_REPLAY_SCOPE_FREEZE_RUN_ID,
)
from tests.unit.pipeline.support_state import rewind_current_malf_repair_state
from tests.unit.system_readout.support import build_request as build_system_request
from tests.unit.system_readout.support import seed_chain

from asteria.system_readout.bootstrap import run_system_readout_build

CURRENT_ACTIVE_MAINLINE_MODULE = pipeline_constants.CURRENT_ACTIVE_MAINLINE_MODULE
PIPELINE_FULL_CHAIN_PASSED_DOC_STATUS = pipeline_constants.PIPELINE_FULL_CHAIN_PASSED_DOC_STATUS
PIPELINE_ALPHA_SIGNAL_REPAIR_RUN_ID = pipeline_constants.PIPELINE_ALPHA_SIGNAL_REPAIR_RUN_ID
PIPELINE_COVERAGE_GAP_EVIDENCE_INCOMPLETE_CLOSEOUT_RUN_ID = (
    pipeline_constants.PIPELINE_COVERAGE_GAP_EVIDENCE_INCOMPLETE_CLOSEOUT_RUN_ID
)
PIPELINE_YEAR_REPLAY_CARD_RUN_ID = pipeline_constants.PIPELINE_YEAR_REPLAY_CARD_RUN_ID
PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID = (
    pipeline_constants.PIPELINE_YEAR_REPLAY_RERUN_REQUIRED_MALF_RUN_ID
)
SYSTEM_SOURCE_RUN_ID = pipeline_constants.SYSTEM_SOURCE_RUN_ID


def _active_card_line(run_id: str) -> str:
    return f'active_card = "docs/04-execution/records/pipeline/{run_id}.card.md"'


def _release_conclusion_line(run_id: str) -> str:
    return f'release_conclusion = "docs/04-execution/records/pipeline/{run_id}.conclusion.md"'


def _evidence_index_line(run_id: str) -> str:
    return f'evidence_index = "docs/04-execution/records/pipeline/{run_id}.evidence-index.md"'


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
    repo_root = build_full_chain_dry_run_prepared_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            f'status = "released"\ndoc_status = "{PIPELINE_FULL_CHAIN_PREPARED_DOC_STATUS}"',
            f'status = "freeze_review_passed"\ndoc_status = "{PIPELINE_PREPARED_DOC_STATUS}"',
            1,
        )
        .replace(
            f'current_allowed_next_card = "{PIPELINE_DRY_RUN_CARD_ACTION}"',
            'current_allowed_next_card = "pipeline_single_module_orchestration_build_card"',
            1,
        )
        .replace(
            f'next_card = "{PIPELINE_DRY_RUN_CARD_ACTION}"',
            'next_card = "pipeline_single_module_orchestration_build_card"',
            1,
        )
        .replace(
            _active_card_line(PIPELINE_DRY_RUN_SCOPE_FREEZE_RUN_ID),
            _active_card_line(PIPELINE_SCOPE_FREEZE_RUN_ID),
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


def build_full_chain_dry_run_prepared_repo(tmp_path: Path) -> Path:
    repo_root = build_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = rewind_current_malf_repair_state(registry_path.read_text(encoding="utf-8"))
    registry_path.write_text(
        registry_text.replace(
            f'current_allowed_next_card = "{PIPELINE_MALF_REPAIR_ACTION}"',
            f'current_allowed_next_card = "{PIPELINE_DRY_RUN_CARD_ACTION}"',
            1,
        )
        .replace(
            f'doc_status = "{PIPELINE_MALF_REPAIR_PREPARED_DOC_STATUS}"',
            f'doc_status = "{PIPELINE_FULL_CHAIN_PREPARED_DOC_STATUS}"',
            1,
        )
        .replace(
            f'next_card = "{PIPELINE_MALF_REPAIR_ACTION}"',
            f'next_card = "{PIPELINE_DRY_RUN_CARD_ACTION}"',
            1,
        )
        .replace(
            PIPELINE_MALF_REPAIR_ACTIVE_CARD,
            _active_card_line(PIPELINE_DRY_RUN_SCOPE_FREEZE_RUN_ID),
            1,
        )
        .replace(
            (
                "release_conclusion = "
                f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.conclusion.md"'
            ),
            PIPELINE_RELEASE_CONCLUSION,
            1,
        )
        .replace(
            (
                "evidence_index = "
                f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.evidence-index.md"'
            ),
            PIPELINE_RELEASE_EVIDENCE_INDEX,
            1,
        )
        .replace(
            f'proof_run_id = "{PIPELINE_BOUNDED_PROOF_CARD_RUN_ID}"',
            f'proof_run_id = "{PIPELINE_RUN_ID}"',
            1,
        )
        .replace(
            PIPELINE_MALF_REPAIR_PREPARED_GATE_STATE,
            PIPELINE_PREPARED_GATE_STATE,
            1,
        )
        .replace(
            PIPELINE_MALF_REPAIR_PREPARED_FORMAL_DB_PERMISSION,
            PIPELINE_PREPARED_FORMAL_DB_PERMISSION,
            1,
        )
        .replace(
            f'next_allowed_action = "{PIPELINE_MALF_REPAIR_ACTION}"',
            f'next_allowed_action = "{PIPELINE_DRY_RUN_CARD_ACTION}"',
            1,
        ),
        encoding="utf-8",
    )
    contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    contract_text = contract_path.read_text(encoding="utf-8")
    contract_path.write_text(
        contract_text.replace(
            (
                "release_conclusion = "
                f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.conclusion.md"'
            ),
            PIPELINE_RELEASE_CONCLUSION,
            1,
        )
        .replace(
            (
                "evidence_index = "
                f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.evidence-index.md"'
            ),
            PIPELINE_RELEASE_EVIDENCE_INDEX,
            1,
        )
        .replace(
            f'next_allowed_action = "{PIPELINE_MALF_REPAIR_ACTION}"',
            f'next_allowed_action = "{PIPELINE_DRY_RUN_CARD_ACTION}"',
            1,
        )
        .replace(
            PIPELINE_CURRENT_GATE_STATE,
            PIPELINE_PREPARED_GATE_STATE,
            1,
        )
        .replace(
            PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
            PIPELINE_PREPARED_FORMAL_DB_PERMISSION,
            1,
        ),
        encoding="utf-8",
    )

    return repo_root


def build_bounded_proof_authorized_repo(tmp_path: Path) -> Path:
    repo_root = build_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = rewind_current_malf_repair_state(registry_path.read_text(encoding="utf-8"))
    registry_path.write_text(
        registry_text.replace(
            f'current_allowed_next_card = "{PIPELINE_MALF_REPAIR_ACTION}"',
            f'current_allowed_next_card = "{PIPELINE_BOUNDED_PROOF_CARD_ACTION}"',
            1,
        )
        .replace(
            f'doc_status = "{PIPELINE_MALF_REPAIR_PREPARED_DOC_STATUS}"',
            (
                "doc_status = "
                '"frozen six-doc set / freeze review passed / single-module orchestration '
                "build passed / full-chain dry-run passed / full-chain bounded proof authorization "
                'scope freeze passed / bounded proof prepared"'
            ),
            1,
        )
        .replace(
            f'next_card = "{PIPELINE_MALF_REPAIR_ACTION}"',
            f'next_card = "{PIPELINE_BOUNDED_PROOF_CARD_ACTION}"',
            1,
        )
        .replace(
            PIPELINE_MALF_REPAIR_ACTIVE_CARD,
            _active_card_line(PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID),
            1,
        )
        .replace(
            (
                "release_conclusion = "
                f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.conclusion.md"'
            ),
            _release_conclusion_line(PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID),
            1,
        )
        .replace(
            (
                "evidence_index = "
                f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.evidence-index.md"'
            ),
            _evidence_index_line(PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID),
            1,
        )
        .replace(
            f'proof_status = "{PIPELINE_MALF_REPAIR_PREPARED_GATE_STATE}"',
            f'proof_status = "{PIPELINE_DRY_RUN_GATE_STATE}"',
            1,
        )
        .replace(
            f'proof_run_id = "{PIPELINE_BOUNDED_PROOF_CARD_RUN_ID}"',
            f'proof_run_id = "{PIPELINE_DRY_RUN_CARD_RUN_ID}"',
            1,
        )
        .replace(
            PIPELINE_MALF_REPAIR_PREPARED_FORMAL_DB_PERMISSION,
            PIPELINE_DRY_RUN_FORMAL_DB_PERMISSION,
            1,
        )
        .replace(
            f'next_allowed_action = "{PIPELINE_MALF_REPAIR_ACTION}"',
            f'next_allowed_action = "{PIPELINE_BOUNDED_PROOF_CARD_ACTION}"',
            1,
        ),
        encoding="utf-8",
    )
    contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    contract_text = contract_path.read_text(encoding="utf-8")
    contract_path.write_text(
        contract_text.replace(
            (
                "release_conclusion = "
                f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.conclusion.md"'
            ),
            _release_conclusion_line(PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID),
            1,
        )
        .replace(
            (
                "evidence_index = "
                f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.evidence-index.md"'
            ),
            _evidence_index_line(PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID),
            1,
        )
        .replace(
            f'next_allowed_action = "{PIPELINE_MALF_REPAIR_ACTION}"',
            f'next_allowed_action = "{PIPELINE_BOUNDED_PROOF_CARD_ACTION}"',
            1,
        )
        .replace(
            PIPELINE_CURRENT_GATE_STATE,
            PIPELINE_DRY_RUN_GATE_STATE,
            1,
        )
        .replace(
            PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
            PIPELINE_DRY_RUN_FORMAL_DB_PERMISSION,
            1,
        ),
        encoding="utf-8",
    )

    return repo_root


def build_year_replay_authorized_repo(tmp_path: Path) -> Path:
    repo_root = build_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = rewind_current_malf_repair_state(registry_path.read_text(encoding="utf-8"))
    registry_path.write_text(
        registry_text.replace(
            f'current_allowed_next_card = "{PIPELINE_MALF_REPAIR_ACTION}"',
            f'current_allowed_next_card = "{PIPELINE_YEAR_REPLAY_CARD_ACTION}"',
            1,
        )
        .replace(
            f'doc_status = "{PIPELINE_MALF_REPAIR_PREPARED_DOC_STATUS}"',
            f'doc_status = "{PIPELINE_YEAR_REPLAY_PREPARED_DOC_STATUS}"',
            1,
        )
        .replace(
            f'next_card = "{PIPELINE_MALF_REPAIR_ACTION}"',
            f'next_card = "{PIPELINE_YEAR_REPLAY_CARD_ACTION}"',
            1,
        )
        .replace(
            PIPELINE_MALF_REPAIR_ACTIVE_CARD,
            _active_card_line(PIPELINE_YEAR_REPLAY_SCOPE_FREEZE_RUN_ID),
            1,
        )
        .replace(
            _release_conclusion_line(PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID),
            _release_conclusion_line(PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID),
            1,
        )
        .replace(
            _evidence_index_line(PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID),
            _evidence_index_line(PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID),
            1,
        )
        .replace(
            f'proof_status = "{PIPELINE_MALF_REPAIR_PREPARED_GATE_STATE}"',
            f'proof_status = "{PIPELINE_BOUNDED_PROOF_GATE_STATE}"',
            1,
        )
        .replace(
            PIPELINE_MALF_REPAIR_PREPARED_FORMAL_DB_PERMISSION,
            PIPELINE_BOUNDED_PROOF_FORMAL_DB_PERMISSION,
            1,
        )
        .replace(
            f'next_allowed_action = "{PIPELINE_MALF_REPAIR_ACTION}"',
            f'next_allowed_action = "{PIPELINE_YEAR_REPLAY_CARD_ACTION}"',
            1,
        ),
        encoding="utf-8",
    )
    contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    contract_text = contract_path.read_text(encoding="utf-8")
    contract_path.write_text(
        contract_text.replace(
            PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_CONCLUSION,
            (
                "release_conclusion = "
                f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.conclusion.md"'
            ),
            1,
        )
        .replace(
            PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_EVIDENCE_INDEX,
            (
                "evidence_index = "
                f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.evidence-index.md"'
            ),
            1,
        )
        .replace(
            f'next_allowed_action = "{PIPELINE_MALF_REPAIR_ACTION}"',
            f'next_allowed_action = "{PIPELINE_YEAR_REPLAY_CARD_ACTION}"',
            1,
        )
        .replace(
            PIPELINE_CURRENT_GATE_STATE,
            PIPELINE_BOUNDED_PROOF_GATE_STATE,
            1,
        )
        .replace(
            PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
            PIPELINE_BOUNDED_PROOF_FORMAL_DB_PERMISSION,
            1,
        )
        .replace(
            PIPELINE_DRY_RUN_INPUT_BOUNDARY,
            PIPELINE_BOUNDED_INPUT_BOUNDARY,
            1,
        ),
        encoding="utf-8",
    )

    return repo_root


def build_year_replay_rerun_authorized_repo(tmp_path: Path) -> Path:
    repo_root = build_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = registry_path.read_text(encoding="utf-8")
    if f'current_allowed_next_card = "{PIPELINE_YEAR_REPLAY_RERUN_CARD_ACTION}"' in registry_text:
        return repo_root
    registry_path.write_text(
        registry_text.replace(
            (
                "current_allowed_next_card = "
                f'"{PIPELINE_COVERAGE_GAP_EVIDENCE_INCOMPLETE_CLOSEOUT_ACTION}"'
            ),
            f'current_allowed_next_card = "{PIPELINE_YEAR_REPLAY_RERUN_CARD_ACTION}"',
            1,
        )
        .replace(
            f'next_card = "{PIPELINE_COVERAGE_GAP_EVIDENCE_INCOMPLETE_CLOSEOUT_ACTION}"',
            f'next_card = "{PIPELINE_YEAR_REPLAY_RERUN_CARD_ACTION}"',
            1,
        )
        .replace(
            f'doc_status = "{PIPELINE_CURRENT_DOC_STATUS}"',
            (
                'doc_status = "frozen six-doc set / freeze review passed / single-module '
                "orchestration build passed / full-chain dry-run passed / full-chain day "
                "bounded proof passed / one-year strategy behavior replay blocked / coverage "
                "gap diagnosis executed / MALF natural-year coverage repair passed / year replay "
                'rerun prepared"'
            ),
            1,
        )
        .replace(
            CURRENT_PIPELINE_ACTIVE_CARD,
            _active_card_line(PIPELINE_YEAR_REPLAY_RERUN_CARD_RUN_ID),
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
