from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Finding:
    path: Path
    message: str


REQUIRED_MODULE_DOCS = [
    "00-authority-design-v1.md",
    "01-semantic-contract-v1.md",
    "02-database-schema-spec-v1.md",
    "03-runner-contract-v1.md",
    "04-audit-spec-v1.md",
    "05-build-card-v1.md",
]
MAINLINE_MODULES = {
    "malf",
    "alpha",
    "signal",
    "position",
    "portfolio_plan",
    "trade",
    "system_readout",
}


def check_gate_registry(repo_root: Path, gate_registry: dict[str, Any]) -> list[Finding]:
    path = repo_root / "governance" / "module_gate_registry.toml"
    findings: list[Finding] = []
    modules = {module["module_id"]: module for module in gate_registry.get("modules", [])}
    active = gate_registry.get("active_mainline_module")
    current_next = gate_registry.get("current_allowed_next_card")
    action_allowed = [
        module_id
        for module_id, module in modules.items()
        if module_id in MAINLINE_MODULES
        and (bool(module.get("allow_build")) or bool(module.get("allow_review")))
    ]

    if len(action_allowed) != 1:
        findings.append(Finding(path, "only one mainline module may allow build or review"))
    if active not in action_allowed:
        findings.append(
            Finding(path, "active_mainline_module must be the action-allowed mainline module")
        )
    if current_next:
        _check_current_next_card(
            repo_root, path, findings, gate_registry, modules, str(active), str(current_next)
        )
    if "system" in modules or "system_readout" not in modules:
        findings.append(
            Finding(path, "module_id must be system_readout; system is only a DB display shorthand")
        )

    for module_id, module in modules.items():
        _check_module_docs(repo_root, path, findings, module_id, module)
    return findings


def _check_current_next_card(
    repo_root: Path,
    path: Path,
    findings: list[Finding],
    gate_registry: dict[str, Any],
    modules: dict[str, dict[str, Any]],
    active: str,
    current_next: str,
) -> None:
    next_card_module = active
    if modules.get(active, {}).get("next_card") != current_next:
        foundation_module = _foundation_next_card_module(gate_registry, modules, current_next)
        if foundation_module is None:
            findings.append(
                Finding(path, "current_allowed_next_card must match active module next_card")
            )
        else:
            next_card_module = foundation_module
    if not _current_next_card_file_exists(repo_root, next_card_module, current_next):
        findings.append(
            Finding(path, "current allowed next card is missing matching execution card")
        )
    if _current_next_card_has_blocked_conclusion(repo_root, next_card_module, current_next):
        findings.append(
            Finding(
                path,
                "current allowed next card must not point to a blocked execution conclusion",
            )
        )


def _foundation_next_card_module(
    gate_registry: dict[str, Any],
    modules: dict[str, dict[str, Any]],
    current_next: str,
) -> str | None:
    active_foundation_card = str(gate_registry.get("active_foundation_card", "none"))
    data_module = modules.get("data", {})
    if (
        active_foundation_card == "none"
        or data_module.get("exception") != "data_foundation_maintenance_card_only"
    ):
        return None
    card_prefix = current_next.replace("_", "-")
    if active_foundation_card == card_prefix or active_foundation_card.startswith(
        f"{card_prefix}-"
    ):
        return "data"
    return None


def _check_module_docs(
    repo_root: Path,
    path: Path,
    findings: list[Finding],
    module_id: str,
    module: dict[str, Any],
) -> None:
    for field in ["display_name", "status", "doc_path", "allow_build"]:
        if field not in module:
            findings.append(
                Finding(path, f"module {module_id} missing required gate field: {field}")
            )
    doc_path = repo_root / str(module.get("doc_path", ""))
    if not doc_path.exists():
        findings.append(Finding(path, f"module {module_id} doc_path does not exist"))
        return
    for doc_name in REQUIRED_MODULE_DOCS:
        if not (doc_path / doc_name).exists():
            findings.append(
                Finding(path, f"module {module_id} missing required six-doc file: {doc_name}")
            )


def _current_next_card_file_exists(repo_root: Path, module_id: str, next_card: str) -> bool:
    record_dir = _next_card_record_dir(repo_root, module_id, next_card)
    if not record_dir.exists():
        return False
    card_prefix = next_card.replace("_", "-")
    for card_path in record_dir.glob("*.card.md"):
        run_id = card_path.name.removesuffix(".card.md")
        if run_id == card_prefix or run_id.startswith(f"{card_prefix}-"):
            return True
    return False


def _current_next_card_has_blocked_conclusion(
    repo_root: Path, module_id: str, next_card: str
) -> bool:
    record_dir = _next_card_record_dir(repo_root, module_id, next_card)
    if not record_dir.exists():
        return False
    card_prefix = next_card.replace("_", "-")
    for conclusion_path in record_dir.glob("*.conclusion.md"):
        run_id = conclusion_path.name.removesuffix(".conclusion.md")
        if run_id != card_prefix and not run_id.startswith(f"{card_prefix}-"):
            continue
        text = conclusion_path.read_text(encoding="utf-8")
        if re.search(r"状态：`blocked`", text):
            return True
    return False


def _next_card_record_dir(repo_root: Path, module_id: str, next_card: str) -> Path:
    record_module = "pipeline" if next_card.startswith("pipeline_") else module_id
    return repo_root / "docs" / "04-execution" / "records" / record_module
