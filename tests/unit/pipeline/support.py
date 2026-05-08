from __future__ import annotations

from pathlib import Path
from shutil import copy2, copytree

from tests.unit.system_readout.support import build_request as build_system_request
from tests.unit.system_readout.support import seed_chain

from asteria.system_readout.bootstrap import run_system_readout_build

SYSTEM_SOURCE_RUN_ID = "system-readout-bounded-proof-unit-001"
PIPELINE_RUN_ID = "pipeline-single-module-orchestration-build-card-20260508-01"
PIPELINE_SCOPE_FREEZE_RUN_ID = "pipeline-build-runtime-authorization-scope-freeze-20260508-01"
PIPELINE_DRY_RUN_SCOPE_FREEZE_RUN_ID = (
    "pipeline-full-chain-dry-run-authorization-scope-freeze-20260508-01"
)
PIPELINE_DRY_RUN_CARD_RUN_ID = "pipeline-full-chain-dry-run-card-20260508-01"
PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID = (
    "pipeline-full-chain-bounded-proof-authorization-scope-freeze-20260508-01"
)
PIPELINE_BOUNDED_PROOF_CARD_RUN_ID = "pipeline-full-chain-bounded-proof-build-card-20260508-01"
PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID = "pipeline-full-chain-bounded-proof-closeout-20260508-01"
PIPELINE_YEAR_REPLAY_SCOPE_FREEZE_RUN_ID = (
    "pipeline-one-year-strategy-behavior-replay-authorization-scope-freeze-20260508-01"
)
PIPELINE_YEAR_REPLAY_CARD_RUN_ID = (
    "pipeline-one-year-strategy-behavior-replay-build-card-20260508-01"
)
PIPELINE_DRY_RUN_CARD_ACTION = "pipeline_full_chain_dry_run_card"
PIPELINE_BOUNDED_PROOF_CARD_ACTION = "pipeline_full_chain_bounded_proof_build_card"
PIPELINE_YEAR_REPLAY_CARD_ACTION = "pipeline_one_year_strategy_behavior_replay_build_card"
PIPELINE_DRY_RUN_PASSED_DOC_STATUS = (
    "frozen six-doc set / freeze review passed / single-module orchestration build passed / "
    "full-chain dry-run passed"
)
PIPELINE_YEAR_REPLAY_PREPARED_DOC_STATUS = (
    "frozen six-doc set / freeze review passed / single-module orchestration build passed / "
    "full-chain dry-run passed / full-chain day bounded proof passed / one-year strategy "
    "behavior replay authorization scope freeze passed / year replay prepared"
)
PIPELINE_CURRENT_DOC_STATUS = (
    "frozen six-doc set / freeze review passed / single-module orchestration build passed / "
    "full-chain dry-run passed / full-chain day bounded proof passed / one-year strategy "
    "behavior replay blocked"
)
PIPELINE_FULL_CHAIN_PREPARED_DOC_STATUS = (
    "frozen six-doc set / freeze review passed / single-module orchestration build passed / "
    "full-chain dry-run prepared"
)
PIPELINE_FULL_CHAIN_PASSED_DOC_STATUS = PIPELINE_DRY_RUN_PASSED_DOC_STATUS
PIPELINE_PREPARED_DOC_STATUS = (
    "frozen six-doc set / freeze review passed / single-module orchestration build prepared / "
    "build not executed"
)
PIPELINE_RELEASE_CONCLUSION = (
    f'release_conclusion = "docs/04-execution/records/pipeline/{PIPELINE_RUN_ID}.conclusion.md"'
)
PIPELINE_DRY_RUN_RELEASE_CONCLUSION = (
    "release_conclusion = "
    f'"docs/04-execution/records/pipeline/{PIPELINE_DRY_RUN_CARD_RUN_ID}.conclusion.md"'
)
PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_CONCLUSION = (
    "release_conclusion = "
    f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID}.conclusion.md"'
)
PIPELINE_SCOPE_FREEZE_CONCLUSION = (
    f"release_conclusion = "
    f'"docs/04-execution/records/pipeline/{PIPELINE_SCOPE_FREEZE_RUN_ID}.conclusion.md"'
)
PIPELINE_RELEASE_EVIDENCE_INDEX = (
    f'evidence_index = "docs/04-execution/records/pipeline/{PIPELINE_RUN_ID}.evidence-index.md"'
)
PIPELINE_DRY_RUN_RELEASE_EVIDENCE_INDEX = (
    "evidence_index = "
    f'"docs/04-execution/records/pipeline/{PIPELINE_DRY_RUN_CARD_RUN_ID}.evidence-index.md"'
)
PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_EVIDENCE_INDEX = (
    "evidence_index = "
    f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID}.evidence-index.md"'
)
PIPELINE_SCOPE_FREEZE_EVIDENCE_INDEX = (
    f"evidence_index = "
    f'"docs/04-execution/records/pipeline/{PIPELINE_SCOPE_FREEZE_RUN_ID}.evidence-index.md"'
)
PIPELINE_DRY_RUN_GATE_STATE = (
    "single_module_orchestration_build_passed; full_chain_dry_run_passed; "
    "full_chain_bounded_proof_not_opened"
)
PIPELINE_BOUNDED_PROOF_GATE_STATE = (
    "single_module_orchestration_build_passed; full_chain_dry_run_passed; "
    "full_chain_day_bounded_proof_passed; one_year_strategy_behavior_replay_not_opened"
)
PIPELINE_CURRENT_GATE_STATE = (
    "single_module_orchestration_build_passed; full_chain_dry_run_passed; "
    "full_chain_day_bounded_proof_passed; one_year_strategy_behavior_replay_blocked"
)
PIPELINE_PREPARED_GATE_STATE = (
    "single_module_orchestration_build_passed; full_chain_dry_run_prepared; full_chain_not_executed"
)
PIPELINE_DRY_RUN_FORMAL_DB_PERMISSION = (
    "released_full_chain_dry_run_ledger_only; bounded_proof_requires_new_card"
)
PIPELINE_BOUNDED_PROOF_FORMAL_DB_PERMISSION = (
    "released_full_chain_bounded_proof_ledger_only; "
    "one_year_strategy_behavior_replay_requires_new_card"
)
PIPELINE_CURRENT_FORMAL_DB_PERMISSION = (
    "released_full_chain_bounded_proof_ledger_only; "
    "one_year_strategy_behavior_replay_blocked_incomplete_natural_year_coverage; "
    "full_rebuild_requires_new_card"
)
PIPELINE_PREPARED_FORMAL_DB_PERMISSION = (
    "released_single_module_orchestration_ledger_only; "
    "full_chain_dry_run_prepared_not_executed; bounded_proof_requires_new_card"
)
PIPELINE_DRY_RUN_INPUT_BOUNDARY = (
    'input_boundary = "orchestration_metadata_only; '
    'released_full_chain_day_bounded_surfaces_dry_run_only"'
)
PIPELINE_BOUNDED_INPUT_BOUNDARY = (
    'input_boundary = "orchestration_metadata_only; released_full_chain_day_bounded_surfaces"'
)


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
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            'current_allowed_next_card = ""',
            f'current_allowed_next_card = "{PIPELINE_DRY_RUN_CARD_ACTION}"',
            1,
        )
        .replace(
            f'doc_status = "{PIPELINE_CURRENT_DOC_STATUS}"',
            f'doc_status = "{PIPELINE_FULL_CHAIN_PREPARED_DOC_STATUS}"',
            1,
        )
        .replace(
            'next_card = "none"',
            f'next_card = "{PIPELINE_DRY_RUN_CARD_ACTION}"',
            1,
        )
        .replace(
            _active_card_line(PIPELINE_YEAR_REPLAY_CARD_RUN_ID),
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
            PIPELINE_CURRENT_GATE_STATE,
            PIPELINE_PREPARED_GATE_STATE,
            1,
        )
        .replace(
            PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
            PIPELINE_PREPARED_FORMAL_DB_PERMISSION,
            1,
        )
        .replace(
            'next_allowed_action = "none"',
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
            'next_allowed_action = "none"',
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
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            'current_allowed_next_card = ""',
            f'current_allowed_next_card = "{PIPELINE_BOUNDED_PROOF_CARD_ACTION}"',
            1,
        )
        .replace(
            f'doc_status = "{PIPELINE_CURRENT_DOC_STATUS}"',
            (
                "doc_status = "
                '"frozen six-doc set / freeze review passed / single-module orchestration '
                "build passed / full-chain dry-run passed / full-chain bounded proof authorization "
                'scope freeze passed / bounded proof prepared"'
            ),
            1,
        )
        .replace(
            'next_card = "none"',
            f'next_card = "{PIPELINE_BOUNDED_PROOF_CARD_ACTION}"',
            1,
        )
        .replace(
            _active_card_line(PIPELINE_YEAR_REPLAY_CARD_RUN_ID),
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
            f'proof_status = "{PIPELINE_CURRENT_GATE_STATE}"',
            f'proof_status = "{PIPELINE_DRY_RUN_GATE_STATE}"',
            1,
        )
        .replace(
            f'proof_run_id = "{PIPELINE_BOUNDED_PROOF_CARD_RUN_ID}"',
            f'proof_run_id = "{PIPELINE_DRY_RUN_CARD_RUN_ID}"',
            1,
        )
        .replace(
            PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
            PIPELINE_DRY_RUN_FORMAL_DB_PERMISSION,
            1,
        )
        .replace(
            'next_allowed_action = "none"',
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
            'next_allowed_action = "none"',
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
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            'current_allowed_next_card = ""',
            f'current_allowed_next_card = "{PIPELINE_YEAR_REPLAY_CARD_ACTION}"',
            1,
        )
        .replace(
            f'doc_status = "{PIPELINE_CURRENT_DOC_STATUS}"',
            f'doc_status = "{PIPELINE_YEAR_REPLAY_PREPARED_DOC_STATUS}"',
            1,
        )
        .replace(
            'next_card = "none"',
            f'next_card = "{PIPELINE_YEAR_REPLAY_CARD_ACTION}"',
            1,
        )
        .replace(
            _active_card_line(PIPELINE_YEAR_REPLAY_CARD_RUN_ID),
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
            f'proof_status = "{PIPELINE_CURRENT_GATE_STATE}"',
            f'proof_status = "{PIPELINE_BOUNDED_PROOF_GATE_STATE}"',
            1,
        )
        .replace(
            PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
            PIPELINE_BOUNDED_PROOF_FORMAL_DB_PERMISSION,
            1,
        )
        .replace(
            'next_allowed_action = "none"',
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
            'next_allowed_action = "none"',
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


def seed_system_source(tmp_path: Path) -> Path:
    seed_chain(tmp_path)
    summary = run_system_readout_build(build_system_request(tmp_path))
    if summary.hard_fail_count != 0:
        raise AssertionError(f"seed system source failed: {summary.as_dict()}")
    return tmp_path / "data" / "system.duckdb"
