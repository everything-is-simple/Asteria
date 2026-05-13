from __future__ import annotations

from pathlib import Path
from typing import Any


def allowed_pipeline_runner_names() -> set[str]:
    return {
        "run_pipeline_record.py",
        "run_pipeline_audit.py",
        "run_pipeline_bounded_proof.py",
        "run_pipeline_full_chain_dry_run.py",
        "run_year_replay_coverage_gap_diagnosis.py",
        "run_pipeline_year_replay_source_selection_repair.py",
        "run_pipeline_year_replay_disposition_decision.py",
        "run_v1_usage_validation_scope.py",
        "run_alpha_signal_2024_coverage_repair.py",
        "run_alpha_signal_daily_incremental_ledger.py",
        "run_downstream_daily_incremental_ledger.py",
        "run_pipeline_full_daily_incremental_chain.py",
        "run_full_rebuild_daily_incremental_release_closeout.py",
        "run_formal_release_source_proof.py",
        "run_formal_release_proof.py",
        "run_final_release_closeout.py",
        "run_downstream_coverage_gap_closeout.py",
    }


def pipeline_runtime_surface_allowed(
    gate_registry: dict[str, Any],
    module: dict[str, Any],
) -> bool:
    return (
        module.get("module_id") == "pipeline"
        and module.get("orchestration") is True
        and module.get("status") == "freeze_review_passed"
        and gate_registry.get("active_mainline_module") == "system_readout"
        and gate_registry.get("current_allowed_next_card")
        == "pipeline_single_module_orchestration_build_card"
        and module.get("next_card") == "pipeline_single_module_orchestration_build_card"
    )


def pipeline_scripts_dir(repo_root: Path) -> Path:
    return repo_root / "scripts" / "pipeline"
