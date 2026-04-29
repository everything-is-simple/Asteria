from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


@dataclass(frozen=True)
class SyncFinding:
    path: Path
    message: str


@dataclass(frozen=True)
class SyncAction:
    path: Path
    message: str


@dataclass(frozen=True)
class ExecutionConclusion:
    module_id: str
    run_id: str
    status: str
    conclusion_path: Path
    card_path: Path
    record_path: Path
    evidence_path: Path
    allowed_next_action: str | None

    @property
    def expected_next_card(self) -> str | None:
        if self.allowed_next_action is None:
            return None
        return _slug(self.allowed_next_action)


@dataclass
class SyncReport:
    findings: list[SyncFinding] = field(default_factory=list)
    actions: list[SyncAction] = field(default_factory=list)


CONCLUSION_INDEX = Path("docs/04-execution/00-conclusion-index-v1.md")
EXECUTION_RECORDS = Path("docs/04-execution/records")
GATE_REGISTRY = Path("governance/module_gate_registry.toml")
GATE_LEDGER = Path("docs/03-refactor/00-module-gate-ledger-v1.md")
ROADMAP = Path("docs/03-refactor/04-asteria-full-system-roadmap-v1.md")
VALIDATED_ASSET_INVENTORY = Path("docs/01-architecture/02-validated-asset-inventory-v1.md")
MALF_AUTHORITY_BRIDGE = Path("docs/02-modules/02-malf-authoritative-design-bridge-v1.md")
LATEST_DOCS_CODE_SNAPSHOT = "Asteria-docs-code-20260428-214427.zip"
MALF_AUTHORITY_ROOT = Path(r"H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2")
MALF_AUTHORITY_ZIP = Path(r"H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2.zip")
LATEST_DOCS_CODE_ZIP = Path(rf"H:\Asteria-Validated\{LATEST_DOCS_CODE_SNAPSHOT}")
MALF_AUTHORITY_FILES = [
    "MALF_00_Three_Documents_Bridge_v1_2.md",
    "MALF_01_Core_Definitions_Theorems_v1_3.md",
    "MALF_02_Lifespan_Stats_Definitions_Theorems_v1_2.md",
    "MALF_03_System_Service_Interface_v1_2.md",
]
SAFE_ROADMAP_NEXT_CARD_ITEM = (
    "- [ ] 修正 `governance/module_gate_registry.toml`：把 MALF `next_card` "
    "从 `malf_day_bounded_proof` 改为 `alpha_freeze_review`。"
)
SAFE_ROADMAP_NEXT_CARD_DONE = SAFE_ROADMAP_NEXT_CARD_ITEM.replace("- [ ]", "- [x]", 1)


def run_docs_sync_checks(repo_root: Path) -> list[SyncFinding]:
    return plan_docs_sync(repo_root).findings


def plan_docs_sync(repo_root: Path) -> SyncReport:
    repo_root = repo_root.resolve()
    report = SyncReport()
    registry = _load_toml(repo_root / GATE_REGISTRY, report.findings)
    conclusions = _discover_conclusions(repo_root, report.findings)

    if registry is not None:
        _check_registry_next_cards(repo_root, registry, conclusions, report)
        _check_pre_gate_sources(repo_root, registry, report)
    _check_gate_ledger(repo_root, conclusions, report)
    _check_roadmap(repo_root, conclusions, report)
    _check_conclusion_index(repo_root, conclusions, report)
    _check_execution_record_sets(repo_root, conclusions, report)
    _check_validated_authority_assets(repo_root, report)
    _check_malf_authority_bridge(repo_root, report)
    _plan_safe_actions(repo_root, registry, conclusions, report)
    return report


def apply_safe_sync(repo_root: Path) -> SyncReport:
    repo_root = repo_root.resolve()
    report = plan_docs_sync(repo_root)
    applied_actions = list(report.actions)
    for action in report.actions:
        if action.message == "updated registry next_card":
            _apply_registry_next_card(repo_root, action.path)
        elif action.message == "registered missing execution conclusion":
            _apply_conclusion_index(repo_root)
        elif action.message == "marked completed roadmap sync item":
            _apply_roadmap_next_card_checkbox(repo_root)
    final_report = plan_docs_sync(repo_root)
    final_report.actions = applied_actions
    return final_report


def _load_toml(path: Path, findings: list[SyncFinding]) -> dict[str, Any] | None:
    if not path.exists():
        findings.append(SyncFinding(path, "required docs sync registry is missing"))
        return None
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _module_map(gate_registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {module["module_id"]: module for module in gate_registry.get("modules", [])}


def _discover_conclusions(
    repo_root: Path, findings: list[SyncFinding]
) -> list[ExecutionConclusion]:
    record_root = repo_root / EXECUTION_RECORDS
    if not record_root.exists():
        findings.append(SyncFinding(record_root, "execution records directory is missing"))
        return []

    conclusions: list[ExecutionConclusion] = []
    for conclusion_path in sorted(record_root.glob("*/*.conclusion.md")):
        module_id = conclusion_path.parent.name
        run_id = conclusion_path.name.removesuffix(".conclusion.md")
        text = conclusion_path.read_text(encoding="utf-8")
        conclusions.append(
            ExecutionConclusion(
                module_id=module_id,
                run_id=run_id,
                status=_parse_status(text),
                conclusion_path=conclusion_path,
                card_path=conclusion_path.with_name(f"{run_id}.card.md"),
                record_path=conclusion_path.with_name(f"{run_id}.record.md"),
                evidence_path=conclusion_path.with_name(f"{run_id}.evidence-index.md"),
                allowed_next_action=_parse_allowed_next_action(text),
            )
        )
    return conclusions


def _parse_status(text: str) -> str:
    match = re.search(r"状态：`([^`]+)`", text)
    return match.group(1) if match else "unknown"


def _parse_allowed_next_action(text: str) -> str | None:
    match = re.search(r"\|\s*allowed next action\s*\|\s*`([^`]+)`\s*\|", text)
    return match.group(1) if match else None


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _check_registry_next_cards(
    repo_root: Path,
    gate_registry: dict[str, Any],
    conclusions: list[ExecutionConclusion],
    report: SyncReport,
) -> None:
    modules = _module_map(gate_registry)
    for conclusion in conclusions:
        expected = conclusion.expected_next_card
        if conclusion.status != "passed" or expected is None or conclusion.module_id not in modules:
            continue
        actual = modules.get(conclusion.module_id, {}).get("next_card")
        if actual != expected:
            report.findings.append(
                SyncFinding(
                    repo_root / GATE_REGISTRY,
                    f"{conclusion.module_id.upper()} next_card must be {expected}",
                )
            )


def _check_gate_ledger(
    repo_root: Path, conclusions: list[ExecutionConclusion], report: SyncReport
) -> None:
    path = repo_root / GATE_LEDGER
    if not path.exists():
        report.findings.append(SyncFinding(path, "gate ledger is missing"))
        return
    text = path.read_text(encoding="utf-8")
    for conclusion in conclusions:
        if (
            conclusion.status == "passed"
            and conclusion.allowed_next_action
            and conclusion.allowed_next_action not in text
        ):
            report.findings.append(
                SyncFinding(
                    path,
                    "gate ledger missing allowed next action from execution conclusion",
                )
            )


def _check_roadmap(
    repo_root: Path, conclusions: list[ExecutionConclusion], report: SyncReport
) -> None:
    path = repo_root / ROADMAP
    if not path.exists():
        report.findings.append(SyncFinding(path, "full system roadmap is missing"))
        return
    text = path.read_text(encoding="utf-8")
    mainline = _extract_strategy_mainline(text)
    if "Data Foundation" in mainline:
        report.findings.append(
            SyncFinding(path, "Data Foundation must not appear in Strategy Mainline")
        )
    if "Pipeline" in mainline:
        report.findings.append(SyncFinding(path, "Pipeline must not appear in Strategy Mainline"))
    for conclusion in conclusions:
        if (
            conclusion.status == "passed"
            and conclusion.allowed_next_action
            and conclusion.allowed_next_action not in text
        ):
            report.findings.append(
                SyncFinding(path, "roadmap missing allowed next action from conclusion")
            )


def _extract_strategy_mainline(text: str) -> str:
    match = re.search(
        r"Strategy Mainline:\s*\n(?P<mainline>.+?)(?:\n\s*\n|Governance / Orchestration)",
        text,
        re.DOTALL,
    )
    return match.group("mainline") if match else ""


def _check_conclusion_index(
    repo_root: Path, conclusions: list[ExecutionConclusion], report: SyncReport
) -> None:
    path = repo_root / CONCLUSION_INDEX
    if not path.exists():
        report.findings.append(SyncFinding(path, "conclusion index is missing"))
        return
    text = path.read_text(encoding="utf-8")
    for conclusion in conclusions:
        if conclusion.run_id not in text:
            report.findings.append(
                SyncFinding(path, "execution conclusion is missing from conclusion index")
            )


def _check_execution_record_sets(
    repo_root: Path, conclusions: list[ExecutionConclusion], report: SyncReport
) -> None:
    for conclusion in conclusions:
        for path, message in [
            (conclusion.card_path, "execution conclusion is missing matching card"),
            (conclusion.record_path, "execution conclusion is missing matching record"),
            (
                conclusion.evidence_path,
                "execution conclusion is missing matching evidence-index",
            ),
        ]:
            if not path.exists():
                report.findings.append(SyncFinding(path, message))
        if conclusion.evidence_path.exists():
            _check_external_evidence_paths(conclusion.evidence_path, report)


def _check_validated_authority_assets(repo_root: Path, report: SyncReport) -> None:
    path = repo_root / VALIDATED_ASSET_INVENTORY
    text = _read_text(path)
    if not text:
        report.findings.append(SyncFinding(path, "validated asset inventory is missing"))
        return

    if LATEST_DOCS_CODE_SNAPSHOT not in text:
        report.findings.append(
            SyncFinding(path, "validated asset inventory must reference latest docs/code snapshot")
        )

    for asset_path, message in [
        (LATEST_DOCS_CODE_ZIP, "latest docs/code snapshot asset is missing"),
        (MALF_AUTHORITY_ZIP, "MALF authority zip asset is missing"),
        (MALF_AUTHORITY_ROOT, "MALF authority directory asset is missing"),
    ]:
        if not asset_path.exists():
            report.findings.append(SyncFinding(path, message))

    for file_name in MALF_AUTHORITY_FILES:
        authority_file = MALF_AUTHORITY_ROOT / file_name
        if not authority_file.exists():
            report.findings.append(
                SyncFinding(path, f"MALF authority source file is missing: {file_name}")
            )


def _check_malf_authority_bridge(repo_root: Path, report: SyncReport) -> None:
    path = repo_root / MALF_AUTHORITY_BRIDGE
    text = _read_text(path)
    if not text:
        report.findings.append(SyncFinding(path, "MALF authority bridge is missing"))
        return

    for file_name in MALF_AUTHORITY_FILES:
        if file_name not in text:
            report.findings.append(
                SyncFinding(
                    path,
                    f"MALF authority bridge missing authority file reference: {file_name}",
                )
            )


def _check_external_evidence_paths(evidence_path: Path, report: SyncReport) -> None:
    text = evidence_path.read_text(encoding="utf-8")
    for raw_path in re.findall(r"`(H:\\Asteria-(?:report|Validated)[^`]+)`", text):
        path = Path(raw_path)
        if not path.exists():
            report.findings.append(
                SyncFinding(evidence_path, f"evidence asset path does not exist: {raw_path}")
            )


def _check_pre_gate_sources(
    repo_root: Path, gate_registry: dict[str, Any], report: SyncReport
) -> None:
    for module_id, module in _module_map(gate_registry).items():
        if (
            bool(module.get("allow_build"))
            or module.get("exception") == "bounded_bootstrap_support"
        ):
            continue
        script_dir = repo_root / "scripts" / module_id
        if not script_dir.exists():
            continue
        for script_path in script_dir.glob("run_*.py"):
            report.findings.append(
                SyncFinding(script_path, "pre-gate module has forbidden formal runner")
            )
        db_scripts = set(script_dir.glob("create_*.py")) | set(script_dir.glob("*_schema.py"))
        for script_path in sorted(db_scripts):
            report.findings.append(
                SyncFinding(script_path, "pre-gate module has forbidden formal DB create script")
            )


def _plan_safe_actions(
    repo_root: Path,
    gate_registry: dict[str, Any] | None,
    conclusions: list[ExecutionConclusion],
    report: SyncReport,
) -> None:
    if gate_registry is not None:
        modules = _module_map(gate_registry)
        for conclusion in conclusions:
            expected = conclusion.expected_next_card
            if conclusion.module_id not in modules:
                continue
            actual = modules.get(conclusion.module_id, {}).get("next_card")
            if conclusion.status == "passed" and expected and actual != expected:
                report.actions.append(
                    SyncAction(repo_root / GATE_REGISTRY, "updated registry next_card")
                )

    index_text = _read_text(repo_root / CONCLUSION_INDEX)
    for conclusion in conclusions:
        if conclusion.run_id not in index_text:
            report.actions.append(
                SyncAction(repo_root / CONCLUSION_INDEX, "registered missing execution conclusion")
            )

    roadmap_text = _read_text(repo_root / ROADMAP)
    if SAFE_ROADMAP_NEXT_CARD_ITEM in roadmap_text:
        report.actions.append(SyncAction(repo_root / ROADMAP, "marked completed roadmap sync item"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _apply_registry_next_card(repo_root: Path, path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace('next_card = "malf_day_bounded_proof"', 'next_card = "alpha_freeze_review"')
    path.write_text(text, encoding="utf-8")


def _apply_conclusion_index(repo_root: Path) -> None:
    path = repo_root / CONCLUSION_INDEX
    text = path.read_text(encoding="utf-8")
    conclusions = _discover_conclusions(repo_root, [])
    rows = []
    for conclusion in conclusions:
        if conclusion.run_id in text:
            continue
        conclusion_rel = conclusion.conclusion_path.relative_to(path.parent).as_posix()
        evidence_rel = conclusion.evidence_path.relative_to(path.parent).as_posix()
        rows.append(
            f"| {conclusion.module_id.upper()} | `{conclusion.run_id}` | `{conclusion.status}` | "
            f"[conclusion]({conclusion_rel}) | [evidence-index]({evidence_rel}) |"
        )
    if not rows:
        return
    marker = "|---|---|---|---|---|\n"
    text = text.replace(marker, marker + "\n".join(rows) + "\n", 1)
    path.write_text(text, encoding="utf-8")


def _apply_roadmap_next_card_checkbox(repo_root: Path) -> None:
    path = repo_root / ROADMAP
    text = path.read_text(encoding="utf-8")
    text = text.replace(SAFE_ROADMAP_NEXT_CARD_ITEM, SAFE_ROADMAP_NEXT_CARD_DONE)
    path.write_text(text, encoding="utf-8")
