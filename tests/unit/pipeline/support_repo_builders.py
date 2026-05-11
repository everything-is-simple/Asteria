from __future__ import annotations

from pathlib import Path
from shutil import copy2, copytree

from tests.unit.pipeline.constants import (
    CURRENT_ALLOWED_NEXT_CARD_ACTION,
    CURRENT_PIPELINE_ACTIVE_CARD,
    DATA_DAILY_HARDENING_ACTION,
    DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION,
    PIPELINE_BOUNDED_INPUT_BOUNDARY,
    PIPELINE_BOUNDED_PROOF_CARD_ACTION,
    PIPELINE_BOUNDED_PROOF_CARD_RUN_ID,
    PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID,
    PIPELINE_BOUNDED_PROOF_FORMAL_DB_PERMISSION,
    PIPELINE_BOUNDED_PROOF_GATE_STATE,
    PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_CONCLUSION,
    PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_EVIDENCE_INDEX,
    PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID,
    PIPELINE_CURRENT_DOC_STATUS,
    PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
    PIPELINE_CURRENT_GATE_STATE,
    PIPELINE_CURRENT_PROOF_RUN_ID,
    PIPELINE_DISPOSITION_DECISION_RUN_ID,
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
    PIPELINE_POSITION_REPAIR_ACTION,
    PIPELINE_PREPARED_DOC_STATUS,
    PIPELINE_PREPARED_FORMAL_DB_PERMISSION,
    PIPELINE_PREPARED_GATE_STATE,
    PIPELINE_RELEASE_CONCLUSION,
    PIPELINE_RELEASE_EVIDENCE_INDEX,
    PIPELINE_RUN_ID,
    PIPELINE_SCOPE_FREEZE_RUN_ID,
    PIPELINE_STAGE11_PROTOCOL_ACTION,
    PIPELINE_YEAR_REPLAY_CARD_ACTION,
    PIPELINE_YEAR_REPLAY_PREPARED_DOC_STATUS,
    PIPELINE_YEAR_REPLAY_RERUN_CARD_ACTION,
    PIPELINE_YEAR_REPLAY_RERUN_CARD_RUN_ID,
    PIPELINE_YEAR_REPLAY_SCOPE_FREEZE_RUN_ID,
)
from tests.unit.pipeline.support_state import (
    rewind_current_malf_repair_state,
    rewrite_registry_module_fields,
)


def _pipeline_record_line(field: str, run_id: str, suffix: str) -> str:
    return f'{field} = "docs/04-execution/records/pipeline/{run_id}.{suffix}.md"'


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
    registry_path.write_text(
        registry_path.read_text(encoding="utf-8").replace(
            f'current_allowed_next_card = "{PIPELINE_DRY_RUN_CARD_ACTION}"',
            'current_allowed_next_card = "pipeline_single_module_orchestration_build_card"',
            1,
        ),
        encoding="utf-8",
    )
    registry_path.write_text(
        rewrite_registry_module_fields(
            registry_path.read_text(encoding="utf-8"),
            module_id="system_readout",
            field_updates={
                "next_card": '"pipeline_single_module_orchestration_build_card"',
                "next_allowed_action": '"pipeline_single_module_orchestration_build_card"',
            },
        ),
        encoding="utf-8",
    )
    registry_path.write_text(
        rewrite_registry_module_fields(
            registry_path.read_text(encoding="utf-8"),
            module_id="pipeline",
            field_updates={
                "status": '"freeze_review_passed"',
                "doc_status": f'"{PIPELINE_PREPARED_DOC_STATUS}"',
                "next_card": '"pipeline_single_module_orchestration_build_card"',
                "active_card": (
                    f'"docs/04-execution/records/pipeline/{PIPELINE_SCOPE_FREEZE_RUN_ID}.card.md"'
                ),
                "release_conclusion": (
                    f'"docs/04-execution/records/pipeline/{PIPELINE_SCOPE_FREEZE_RUN_ID}.conclusion.md"'
                ),
                "evidence_index": (
                    f'"docs/04-execution/records/pipeline/{PIPELINE_SCOPE_FREEZE_RUN_ID}.evidence-index.md"'
                ),
                "next_allowed_action": '"pipeline_single_module_orchestration_build_card"',
            },
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
            _pipeline_record_line("active_card", PIPELINE_DRY_RUN_SCOPE_FREEZE_RUN_ID, "card"),
            1,
        )
        .replace(
            "release_conclusion = "
            f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.conclusion.md"',
            PIPELINE_RELEASE_CONCLUSION,
            1,
        )
        .replace(
            "evidence_index = "
            f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.evidence-index.md"',
            PIPELINE_RELEASE_EVIDENCE_INDEX,
            1,
        )
        .replace(
            f'proof_run_id = "{PIPELINE_BOUNDED_PROOF_CARD_RUN_ID}"',
            f'proof_run_id = "{PIPELINE_RUN_ID}"',
            1,
        )
        .replace(PIPELINE_MALF_REPAIR_PREPARED_GATE_STATE, PIPELINE_PREPARED_GATE_STATE, 1)
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
    _rewrite_pipeline_next_card(
        registry_path,
        current_action=PIPELINE_DRY_RUN_CARD_ACTION,
        active_card_run_id=PIPELINE_DRY_RUN_SCOPE_FREEZE_RUN_ID,
        proof_run_id=PIPELINE_RUN_ID,
    )
    contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    contract_text = contract_path.read_text(encoding="utf-8")
    contract_path.write_text(
        contract_text.replace(
            "release_conclusion = "
            f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.conclusion.md"',
            PIPELINE_RELEASE_CONCLUSION,
            1,
        )
        .replace(
            "evidence_index = "
            f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.evidence-index.md"',
            PIPELINE_RELEASE_EVIDENCE_INDEX,
            1,
        )
        .replace(
            f'next_allowed_action = "{PIPELINE_POSITION_REPAIR_ACTION}"',
            f'next_allowed_action = "{PIPELINE_DRY_RUN_CARD_ACTION}"',
            1,
        )
        .replace(PIPELINE_CURRENT_GATE_STATE, PIPELINE_PREPARED_GATE_STATE, 1)
        .replace(PIPELINE_CURRENT_FORMAL_DB_PERMISSION, PIPELINE_PREPARED_FORMAL_DB_PERMISSION, 1),
        encoding="utf-8",
    )
    return repo_root


def build_bounded_proof_authorized_repo(tmp_path: Path) -> Path:
    repo_root = build_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = rewind_current_malf_repair_state(registry_path.read_text(encoding="utf-8"))
    freeze_run_id = PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID
    closeout_run_id = PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID
    registry_path.write_text(
        registry_text.replace(
            f'current_allowed_next_card = "{PIPELINE_MALF_REPAIR_ACTION}"',
            f'current_allowed_next_card = "{PIPELINE_BOUNDED_PROOF_CARD_ACTION}"',
            1,
        )
        .replace(
            f'doc_status = "{PIPELINE_MALF_REPAIR_PREPARED_DOC_STATUS}"',
            'doc_status = "frozen six-doc set / freeze review passed / single-module orchestration '
            "build passed / full-chain dry-run passed / full-chain bounded proof authorization "
            'scope freeze passed / bounded proof prepared"',
            1,
        )
        .replace(
            f'next_card = "{PIPELINE_MALF_REPAIR_ACTION}"',
            f'next_card = "{PIPELINE_BOUNDED_PROOF_CARD_ACTION}"',
            1,
        )
        .replace(
            PIPELINE_MALF_REPAIR_ACTIVE_CARD,
            _pipeline_record_line("active_card", freeze_run_id, "card"),
            1,
        )
        .replace(
            "release_conclusion = "
            f'"docs/04-execution/records/pipeline/{closeout_run_id}.conclusion.md"',
            _pipeline_record_line("release_conclusion", freeze_run_id, "conclusion"),
            1,
        )
        .replace(
            "evidence_index = "
            f'"docs/04-execution/records/pipeline/{closeout_run_id}.evidence-index.md"',
            _pipeline_record_line("evidence_index", freeze_run_id, "evidence-index"),
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
    _rewrite_pipeline_next_card(
        registry_path,
        current_action=PIPELINE_BOUNDED_PROOF_CARD_ACTION,
        active_card_run_id=PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID,
        proof_run_id=PIPELINE_DRY_RUN_CARD_RUN_ID,
    )
    contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    contract_text = contract_path.read_text(encoding="utf-8")
    contract_path.write_text(
        contract_text.replace(
            "release_conclusion = "
            f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.conclusion.md"',
            _pipeline_record_line(
                "release_conclusion", PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID, "conclusion"
            ),
            1,
        )
        .replace(
            "evidence_index = "
            f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.evidence-index.md"',
            _pipeline_record_line(
                "evidence_index", PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID, "evidence-index"
            ),
            1,
        )
        .replace(
            f'next_allowed_action = "{PIPELINE_POSITION_REPAIR_ACTION}"',
            f'next_allowed_action = "{PIPELINE_BOUNDED_PROOF_CARD_ACTION}"',
            1,
        )
        .replace(PIPELINE_CURRENT_GATE_STATE, PIPELINE_DRY_RUN_GATE_STATE, 1)
        .replace(PIPELINE_CURRENT_FORMAL_DB_PERMISSION, PIPELINE_DRY_RUN_FORMAL_DB_PERMISSION, 1),
        encoding="utf-8",
    )
    return repo_root


def build_year_replay_authorized_repo(tmp_path: Path) -> Path:
    repo_root = build_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = rewind_current_malf_repair_state(registry_path.read_text(encoding="utf-8"))
    freeze_run_id = PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_RUN_ID
    closeout_run_id = PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID
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
            _pipeline_record_line("active_card", PIPELINE_YEAR_REPLAY_SCOPE_FREEZE_RUN_ID, "card"),
            1,
        )
        .replace(
            _pipeline_record_line("release_conclusion", freeze_run_id, "conclusion"),
            _pipeline_record_line("release_conclusion", closeout_run_id, "conclusion"),
            1,
        )
        .replace(
            _pipeline_record_line("evidence_index", freeze_run_id, "evidence-index"),
            _pipeline_record_line("evidence_index", closeout_run_id, "evidence-index"),
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
    _rewrite_pipeline_next_card(
        registry_path,
        current_action=PIPELINE_YEAR_REPLAY_CARD_ACTION,
        active_card_run_id=PIPELINE_YEAR_REPLAY_SCOPE_FREEZE_RUN_ID,
        proof_run_id=PIPELINE_BOUNDED_PROOF_CARD_RUN_ID,
    )
    contract_path = repo_root / "governance" / "module_api_contracts" / "pipeline.toml"
    contract_text = contract_path.read_text(encoding="utf-8")
    contract_path.write_text(
        contract_text.replace(
            PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_CONCLUSION,
            "release_conclusion = "
            f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.conclusion.md"',
            1,
        )
        .replace(
            PIPELINE_BOUNDED_PROOF_SCOPE_FREEZE_EVIDENCE_INDEX,
            "evidence_index = "
            f'"docs/04-execution/records/pipeline/{PIPELINE_BOUNDED_PROOF_CLOSEOUT_RUN_ID}.evidence-index.md"',
            1,
        )
        .replace(
            f'next_allowed_action = "{PIPELINE_POSITION_REPAIR_ACTION}"',
            f'next_allowed_action = "{PIPELINE_YEAR_REPLAY_CARD_ACTION}"',
            1,
        )
        .replace(PIPELINE_CURRENT_GATE_STATE, PIPELINE_BOUNDED_PROOF_GATE_STATE, 1)
        .replace(
            PIPELINE_CURRENT_FORMAL_DB_PERMISSION,
            PIPELINE_BOUNDED_PROOF_FORMAL_DB_PERMISSION,
            1,
        )
        .replace(PIPELINE_DRY_RUN_INPUT_BOUNDARY, PIPELINE_BOUNDED_INPUT_BOUNDARY, 1),
        encoding="utf-8",
    )
    return repo_root


def build_year_replay_rerun_authorized_repo(tmp_path: Path) -> Path:
    repo_root = build_governance_repo(tmp_path)
    registry_path = repo_root / "governance" / "module_gate_registry.toml"
    registry_text = registry_path.read_text(encoding="utf-8")
    if f'current_allowed_next_card = "{PIPELINE_YEAR_REPLAY_RERUN_CARD_ACTION}"' in registry_text:
        return repo_root
    updated_text = registry_text
    for field_name in ("current_allowed_next_card", "next_allowed_action"):
        for old_action in (
            CURRENT_ALLOWED_NEXT_CARD_ACTION,
            DATA_DAILY_HARDENING_ACTION,
            DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION,
            PIPELINE_POSITION_REPAIR_ACTION,
            "system_readout_2024_coverage_repair_card",
            "pipeline_year_replay_source_selection_repair_card",
            "pipeline_year_replay_disposition_decision_card",
            PIPELINE_STAGE11_PROTOCOL_ACTION,
        ):
            updated_text = updated_text.replace(
                f'{field_name} = "{old_action}"',
                f'{field_name} = "{PIPELINE_YEAR_REPLAY_RERUN_CARD_ACTION}"',
            )
    for old_card in (
        CURRENT_ALLOWED_NEXT_CARD_ACTION,
        DOWNSTREAM_DAILY_IMPACT_LEDGER_SCHEMA_ACTION,
        "pipeline_year_replay_source_selection_repair_card",
        "pipeline_year_replay_disposition_decision_card",
        PIPELINE_STAGE11_PROTOCOL_ACTION,
    ):
        updated_text = updated_text.replace(
            f'next_card = "{old_card}"',
            f'next_card = "{PIPELINE_YEAR_REPLAY_RERUN_CARD_ACTION}"',
        )
    registry_path.write_text(
        updated_text.replace(
            f'doc_status = "{PIPELINE_CURRENT_DOC_STATUS}"',
            'doc_status = "frozen six-doc set / freeze review passed / single-module orchestration '
            "build passed / full-chain dry-run passed / full-chain day bounded proof passed / "
            "one-year strategy behavior replay blocked / coverage gap diagnosis executed / MALF "
            'natural-year coverage repair passed / year replay rerun prepared"',
            1,
        )
        .replace(
            f'proof_run_id = "{PIPELINE_CURRENT_PROOF_RUN_ID}"',
            f'proof_run_id = "{PIPELINE_BOUNDED_PROOF_CARD_RUN_ID}"',
            1,
        )
        .replace(
            'proof_run_id = "pipeline-system-readout-2024-coverage-repair-handoff-20260510-01"',
            f'proof_run_id = "{PIPELINE_BOUNDED_PROOF_CARD_RUN_ID}"',
            1,
        )
        .replace(
            f'proof_run_id = "{PIPELINE_DISPOSITION_DECISION_RUN_ID}"',
            f'proof_run_id = "{PIPELINE_BOUNDED_PROOF_CARD_RUN_ID}"',
            1,
        )
        .replace(
            CURRENT_PIPELINE_ACTIVE_CARD,
            _pipeline_record_line("active_card", PIPELINE_YEAR_REPLAY_RERUN_CARD_RUN_ID, "card"),
            1,
        ),
        encoding="utf-8",
    )
    _rewrite_pipeline_next_card(
        registry_path,
        current_action=PIPELINE_YEAR_REPLAY_RERUN_CARD_ACTION,
        active_card_run_id=PIPELINE_YEAR_REPLAY_RERUN_CARD_RUN_ID,
        proof_run_id=PIPELINE_BOUNDED_PROOF_CARD_RUN_ID,
    )
    return repo_root


def _rewrite_pipeline_next_card(
    registry_path: Path,
    *,
    current_action: str,
    active_card_run_id: str,
    proof_run_id: str | None = None,
) -> None:
    text = registry_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    in_pipeline = False
    for idx, line in enumerate(lines):
        if line == 'module_id = "pipeline"':
            in_pipeline = True
            continue
        if in_pipeline and line == "[[modules]]":
            break
        if not in_pipeline:
            continue
        if line.startswith('next_card = "'):
            lines[idx] = f'next_card = "{current_action}"'
        elif line.startswith('active_card = "docs/04-execution/records/pipeline/'):
            lines[idx] = _pipeline_record_line("active_card", active_card_run_id, "card")
        elif line.startswith('next_allowed_action = "'):
            lines[idx] = f'next_allowed_action = "{current_action}"'
        elif proof_run_id is not None and line.startswith('proof_run_id = "'):
            lines[idx] = f'proof_run_id = "{proof_run_id}"'
    registry_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
