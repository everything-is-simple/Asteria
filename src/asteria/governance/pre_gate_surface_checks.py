from __future__ import annotations

from pathlib import Path
from typing import Any

from asteria.governance.pipeline_runner_surface import (
    allowed_pipeline_runner_names,
    pipeline_runtime_surface_allowed,
    pipeline_scripts_dir,
)

PRE_GATE_RUNNER_MESSAGE = "pre-gate module has forbidden formal runner"
PRE_GATE_DB_CREATE_MESSAGE = "pre-gate module has forbidden formal DB create script"


def collect_pre_gate_surface_violations(
    repo_root: Path,
    gate_registry: dict[str, Any],
) -> list[tuple[Path, str]]:
    violations: list[tuple[Path, str]] = []
    for module in gate_registry.get("modules", []):
        module_id = module["module_id"]
        if module_id == "pipeline":
            violations.extend(
                _collect_pipeline_surface_violations(repo_root, gate_registry, module)
            )
            continue
        if (
            bool(module.get("allow_build"))
            or module.get("status") in {"released", "integrated"}
            or module.get("exception") == "bounded_bootstrap_support"
        ):
            continue
        script_dir = repo_root / "scripts" / module_id
        if not script_dir.exists():
            continue
        violations.extend(_collect_script_dir_violations(script_dir))
    return violations


def _collect_pipeline_surface_violations(
    repo_root: Path,
    gate_registry: dict[str, Any],
    module: dict[str, Any],
) -> list[tuple[Path, str]]:
    script_dir = pipeline_scripts_dir(repo_root)
    if not script_dir.exists():
        return []

    violations: list[tuple[Path, str]] = []
    allowed_runners = allowed_pipeline_runner_names()
    special_allowed = pipeline_runtime_surface_allowed(gate_registry, module)
    released = module.get("status") in {"released", "integrated"}
    for script_path in script_dir.glob("run_*.py"):
        if (special_allowed or released) and script_path.name in allowed_runners:
            continue
        violations.append((script_path, PRE_GATE_RUNNER_MESSAGE))
    violations.extend(_collect_db_create_violations(script_dir))
    return violations


def _collect_script_dir_violations(script_dir: Path) -> list[tuple[Path, str]]:
    violations = [
        (script_path, PRE_GATE_RUNNER_MESSAGE) for script_path in script_dir.glob("run_*.py")
    ]
    violations.extend(_collect_db_create_violations(script_dir))
    return violations


def _collect_db_create_violations(script_dir: Path) -> list[tuple[Path, str]]:
    db_create_scripts = set(script_dir.glob("create_*.py")) | set(script_dir.glob("*_schema.py"))
    return [(script_path, PRE_GATE_DB_CREATE_MESSAGE) for script_path in sorted(db_create_scripts)]
