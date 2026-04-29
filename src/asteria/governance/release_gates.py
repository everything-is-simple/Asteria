from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ReleaseGateFinding:
    path: Path
    message: str


@dataclass(frozen=True)
class ReleaseGateRecord:
    module_id: str
    run_id: str
    status: str
    conclusion_path: Path
    evidence_path: Path


REQUIRED_RECORD_KINDS = {
    "card": "card",
    "record": "record",
    "evidence-index": "evidence-index",
    "conclusion": "conclusion",
}
REQUIRED_EVIDENCE_ASSETS = {
    "closeout": "closeout",
    "manifest": "manifest",
    "validated_zip": "validated_zip",
}


def run_release_gate_checks(
    repo_root: Path, gate_registry: dict[str, Any]
) -> list[ReleaseGateFinding]:
    findings: list[ReleaseGateFinding] = []
    conclusion_index = repo_root / "docs" / "04-execution" / "00-conclusion-index-v1.md"
    gate_ledger = repo_root / "docs" / "03-refactor" / "00-module-gate-ledger-v1.md"
    if not conclusion_index.exists():
        return [
            ReleaseGateFinding(conclusion_index, "release conclusion index is missing"),
        ]
    if not gate_ledger.exists():
        return [ReleaseGateFinding(gate_ledger, "module gate ledger is missing")]

    records = _parse_conclusion_index(conclusion_index)
    latest_by_module = _latest_passed_by_module(records)
    ledger_text = gate_ledger.read_text(encoding="utf-8")
    modules = {module["module_id"]: module for module in gate_registry.get("modules", [])}
    for record in records:
        if record.status != "passed":
            continue
        findings.extend(_check_required_record_files(record))
        if not record.conclusion_path.exists() or not record.evidence_path.exists():
            continue
        conclusion_text = record.conclusion_path.read_text(encoding="utf-8")
        evidence_text = record.evidence_path.read_text(encoding="utf-8")
        if record.module_id in modules:
            findings.extend(
                _check_conclusion(
                    record,
                    conclusion_text,
                    modules,
                    latest_by_module.get(record.module_id) == record.run_id,
                )
            )
        findings.extend(_check_evidence_assets(repo_root, record.evidence_path, evidence_text))
        if record.module_id in modules:
            findings.extend(_check_gate_ledger(record, ledger_text))
    return findings


def _parse_conclusion_index(path: Path) -> list[ReleaseGateRecord]:
    records: list[ReleaseGateRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 5 or cells[0] == "模块":
            continue
        run_id_match = re.search(r"`([^`]+)`", cells[1])
        status_match = re.search(r"`([^`]+)`", cells[2])
        conclusion_match = re.search(r"\]\(([^)]+)\)", cells[3])
        evidence_match = re.search(r"\]\(([^)]+)\)", cells[4])
        if not (run_id_match and status_match and conclusion_match and evidence_match):
            continue
        conclusion_path = (path.parent / conclusion_match.group(1)).resolve()
        evidence_path = (path.parent / evidence_match.group(1)).resolve()
        module_id = conclusion_path.parent.name
        records.append(
            ReleaseGateRecord(
                module_id=module_id,
                run_id=run_id_match.group(1),
                status=status_match.group(1),
                conclusion_path=conclusion_path,
                evidence_path=evidence_path,
            )
        )
    return records


def _latest_passed_by_module(records: list[ReleaseGateRecord]) -> dict[str, str]:
    latest: dict[str, str] = {}
    for record in records:
        if record.status == "passed":
            latest[record.module_id] = record.run_id
    return latest


def _check_required_record_files(record: ReleaseGateRecord) -> list[ReleaseGateFinding]:
    findings: list[ReleaseGateFinding] = []
    record_dir = record.conclusion_path.parent
    for kind, suffix in REQUIRED_RECORD_KINDS.items():
        path = record_dir / f"{record.run_id}.{suffix}.md"
        if not path.exists():
            findings.append(
                ReleaseGateFinding(path, f"release gate missing required artifact: {kind}")
            )
    return findings


def _check_conclusion(
    record: ReleaseGateRecord,
    conclusion_text: str,
    modules: dict[str, dict[str, Any]],
    is_latest_for_module: bool,
) -> list[ReleaseGateFinding]:
    findings: list[ReleaseGateFinding] = []
    if not _contains_backticked_value(conclusion_text, "passed"):
        findings.append(
            ReleaseGateFinding(
                record.conclusion_path,
                "passed release gate conclusion status missing",
            )
        )
    allowed_next_action = _extract_table_value(conclusion_text, "allowed next action")
    if allowed_next_action is None:
        findings.append(
            ReleaseGateFinding(
                record.conclusion_path,
                "release gate conclusion missing allowed next action",
            )
        )
        return findings

    next_card = modules.get(record.module_id, {}).get("next_card")
    if is_latest_for_module and next_card != _normalize_action(allowed_next_action):
        findings.append(
            ReleaseGateFinding(
                record.conclusion_path,
                "release gate allowed next action must match registry next_card",
            )
        )
    return findings


def _check_evidence_assets(
    repo_root: Path, evidence_path: Path, evidence_text: str
) -> list[ReleaseGateFinding]:
    findings: list[ReleaseGateFinding] = []
    for asset_name, table_key in REQUIRED_EVIDENCE_ASSETS.items():
        asset_path = _extract_table_value(evidence_text, table_key)
        if asset_path is None:
            findings.append(
                ReleaseGateFinding(
                    evidence_path,
                    f"release gate evidence-index missing required asset: {asset_name}",
                )
            )
            continue
        path = Path(asset_path)
        if _is_inside_repo(repo_root, path):
            findings.append(
                ReleaseGateFinding(
                    evidence_path,
                    f"release gate evidence asset must not be inside repo: {asset_name}",
                )
            )
        if not path.exists():
            findings.append(
                ReleaseGateFinding(
                    evidence_path,
                    f"release gate evidence asset does not exist: {asset_name}",
                )
            )
    return findings


def _check_gate_ledger(record: ReleaseGateRecord, ledger_text: str) -> list[ReleaseGateFinding]:
    if record.run_id in ledger_text and "Alpha freeze review" in ledger_text:
        return []
    return [
        ReleaseGateFinding(
            record.conclusion_path,
            "release gate ledger does not reflect conclusion state and next action",
        )
    ]


def _extract_table_value(text: str, key: str) -> str | None:
    pattern = rf"\|\s*{re.escape(key)}\s*\|\s*`([^`]+)`\s*\|"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1) if match else None


def _contains_backticked_value(text: str, value: str) -> bool:
    return re.search(rf"`{re.escape(value)}`", text, flags=re.IGNORECASE) is not None


def _normalize_action(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    if normalized.endswith("_design_freeze_review"):
        return normalized.replace("_design_freeze_review", "_freeze_review")
    return normalized


def _is_inside_repo(repo_root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True
