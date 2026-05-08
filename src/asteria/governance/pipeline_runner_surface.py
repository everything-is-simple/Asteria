from __future__ import annotations

from pathlib import Path
from typing import Any


def allowed_pipeline_runner_names() -> set[str]:
    return {
        "run_pipeline_record.py",
        "run_pipeline_audit.py",
        "run_pipeline_bounded_proof.py",
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
