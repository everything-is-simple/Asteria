from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

FULL_REBUILD_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_CARD = (
    "full-rebuild-and-daily-incremental-release-closeout-card"
)
PREREQUISITE_CHAIN_CARD = "pipeline-full-daily-incremental-chain-build-card"
PREREQUISITE_ALLOWED_ACTION = "full_rebuild_and_daily_incremental_release_closeout_card"
NEXT_ALLOWED_ACTION = "formal_full_rebuild_and_daily_incremental_release_proof_card"
REPORT_DATE = "2026-05-12"
RELEASE_EVIDENCE_MARKERS = {
    "manifest": ("manifest",),
    "row_counts": ("row count", "row counts", "row_counts"),
    "schema_rule_versions": (
        "schema/rule versions",
        "schema version",
        "rule version",
    ),
    "audit_summaries": ("audit summary", "audit summaries"),
    "known_limits": ("known limit", "known limits"),
}


@dataclass(frozen=True)
class FullRebuildDailyIncrementalReleaseCloseoutRequest:
    repo_root: Path
    temp_root: Path
    report_root: Path
    validated_root: Path
    run_id: str
    mode: str = "audit-only"

    def __post_init__(self) -> None:
        if self.mode not in {"audit-only", "closeout"}:
            raise ValueError(f"Unsupported release closeout mode: {self.mode}")

    @property
    def run_root(self) -> Path:
        return self.temp_root / "pipeline-release-closeout" / self.run_id

    @property
    def report_dir(self) -> Path:
        return self.report_root / "pipeline" / REPORT_DATE / self.run_id

    @property
    def summary_path(self) -> Path:
        return self.report_dir / "summary.json"

    @property
    def closeout_path(self) -> Path:
        return self.report_dir / "closeout.md"

    @property
    def readiness_manifest_path(self) -> Path:
        return self.run_root / "release-readiness-summary.json"

    @property
    def validated_manifest_path(self) -> Path:
        return self.validated_root / f"Asteria-{self.run_id}-manifest.json"


@dataclass(frozen=True)
class FullRebuildDailyIncrementalReleaseCloseoutSummary:
    run_id: str
    status: str
    mode: str
    card_id: str
    next_allowed_action: str
    decisions: dict[str, str]
    boundaries: dict[str, bool]
    evidence_paths: dict[str, str]
    summary_path: str
    closeout_path: str
    readiness_manifest_path: str
    validated_manifest_path: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_full_rebuild_daily_incremental_release_closeout(
    request: FullRebuildDailyIncrementalReleaseCloseoutRequest,
) -> FullRebuildDailyIncrementalReleaseCloseoutSummary:
    request.run_root.mkdir(parents=True, exist_ok=True)
    request.report_dir.mkdir(parents=True, exist_ok=True)
    request.validated_root.mkdir(parents=True, exist_ok=True)

    evidence = _read_prerequisite_evidence(request.repo_root)
    decisions = _decisions(evidence)
    summary = _summary(request, decisions, evidence)
    _write_outputs(request, summary)
    return summary


def _read_prerequisite_evidence(repo_root: Path) -> dict[str, str]:
    records_root = repo_root / "docs" / "04-execution" / "records" / "pipeline"
    paths = {
        "prerequisite_record": (records_root / f"{PREREQUISITE_CHAIN_CARD}.record.md"),
        "prerequisite_conclusion": (records_root / f"{PREREQUISITE_CHAIN_CARD}.conclusion.md"),
        "prerequisite_evidence_index": (
            records_root / f"{PREREQUISITE_CHAIN_CARD}.evidence-index.md"
        ),
        "release_closeout_card": (
            records_root / f"{FULL_REBUILD_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_CARD}.card.md"
        ),
    }
    return {
        key: path.read_text(encoding="utf-8") if path.exists() else ""
        for key, path in paths.items()
    }


def _decisions(evidence: dict[str, str]) -> dict[str, str]:
    conclusion = evidence["prerequisite_conclusion"]
    evidence_index = evidence["prerequisite_evidence_index"]
    prerequisite_passed = (
        "passed / pipeline full daily incremental chain proof passed" in conclusion
        and PREREQUISITE_ALLOWED_ACTION in conclusion
    )
    if not prerequisite_passed:
        return {
            "pipeline_chain_proof": "blocked",
            "daily_incremental_resume_audit_modes": "not evaluated",
            "formal_full_rebuild_proof": "not evaluated",
            "daily_incremental_release_proof": "not evaluated",
            "resume_idempotence_proof": "not evaluated",
            "final_release_evidence": "not evaluated",
            "v1_complete_claim": "forbidden / not claimed",
        }

    combined_evidence = "\n".join(evidence.values()).lower()
    mode_evidence_complete = all(
        marker in combined_evidence for marker in ("daily incremental", "resume", "audit-only")
    )
    release_evidence_complete = _release_evidence_complete(combined_evidence)
    full_rebuild_missing = (
        "formal full rebuild not executed" in conclusion
        or "formal full rebuild not executed" in evidence_index
    )
    daily_release_missing = "daily incremental release closeout not executed" in conclusion
    return {
        "pipeline_chain_proof": "passed",
        "daily_incremental_resume_audit_modes": (
            "passed" if mode_evidence_complete else "retained gap"
        ),
        "formal_full_rebuild_proof": "blocked" if full_rebuild_missing else "passed",
        "daily_incremental_release_proof": "blocked" if daily_release_missing else "passed",
        "resume_idempotence_proof": "passed" if mode_evidence_complete else "retained gap",
        "final_release_evidence": "passed" if release_evidence_complete else "retained gap",
        "v1_complete_claim": "forbidden / not claimed",
    }


def _release_evidence_complete(combined_evidence: str) -> bool:
    return all(
        any(marker in combined_evidence for marker in accepted_markers)
        for accepted_markers in RELEASE_EVIDENCE_MARKERS.values()
    )


def _summary(
    request: FullRebuildDailyIncrementalReleaseCloseoutRequest,
    decisions: dict[str, str],
    evidence: dict[str, str],
) -> FullRebuildDailyIncrementalReleaseCloseoutSummary:
    if decisions["pipeline_chain_proof"] != "passed":
        status = "blocked / prerequisite chain proof missing"
    elif any(decision == "blocked" for decision in decisions.values()):
        status = "blocked / formal release evidence incomplete"
    elif any(decision == "retained gap" for decision in decisions.values()):
        status = "blocked / release evidence retained gap"
    else:
        status = "passed / release evidence complete"
    return FullRebuildDailyIncrementalReleaseCloseoutSummary(
        run_id=request.run_id,
        status=status,
        mode=request.mode,
        card_id=FULL_REBUILD_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_CARD,
        next_allowed_action=NEXT_ALLOWED_ACTION,
        decisions=decisions,
        boundaries={
            "formal_data_mutation": False,
            "pipeline_semantic_repair": False,
            "system_full_build_claim": False,
            "v1_complete_claim": False,
        },
        evidence_paths=_evidence_paths(request.repo_root, evidence),
        summary_path=str(request.summary_path),
        closeout_path=str(request.closeout_path),
        readiness_manifest_path=str(request.readiness_manifest_path),
        validated_manifest_path=str(request.validated_manifest_path),
    )


def _evidence_paths(repo_root: Path, evidence: dict[str, str]) -> dict[str, str]:
    records_root = repo_root / "docs" / "04-execution" / "records" / "pipeline"
    mapping = {
        "prerequisite_record": records_root / f"{PREREQUISITE_CHAIN_CARD}.record.md",
        "prerequisite_conclusion": records_root / f"{PREREQUISITE_CHAIN_CARD}.conclusion.md",
        "prerequisite_evidence_index": (
            records_root / f"{PREREQUISITE_CHAIN_CARD}.evidence-index.md"
        ),
        "release_closeout_card": (
            records_root / f"{FULL_REBUILD_DAILY_INCREMENTAL_RELEASE_CLOSEOUT_CARD}.card.md"
        ),
    }
    return {key: str(path) for key, path in mapping.items() if evidence.get(key)}


def _write_outputs(
    request: FullRebuildDailyIncrementalReleaseCloseoutRequest,
    summary: FullRebuildDailyIncrementalReleaseCloseoutSummary,
) -> None:
    payload = summary.as_dict()
    _write_json(request.summary_path, payload)
    _write_json(request.readiness_manifest_path, payload)
    _write_json(request.validated_manifest_path, _validated_manifest(summary))
    request.closeout_path.write_text(_closeout_text(summary), encoding="utf-8")


def _validated_manifest(
    summary: FullRebuildDailyIncrementalReleaseCloseoutSummary,
) -> dict[str, Any]:
    return {
        "run_id": summary.run_id,
        "card_id": summary.card_id,
        "status": summary.status,
        "summary_path": summary.summary_path,
        "closeout_path": summary.closeout_path,
        "formal_data_mutation": summary.boundaries["formal_data_mutation"],
    }


def _closeout_text(summary: FullRebuildDailyIncrementalReleaseCloseoutSummary) -> str:
    full_rebuild_passed = summary.decisions["formal_full_rebuild_proof"] == "passed"
    daily_release_passed = summary.decisions["daily_incremental_release_proof"] == "passed"
    lines = [
        f"# Full rebuild and daily incremental release closeout: {summary.run_id}",
        "",
        f"- status: {summary.status}",
        f"- pipeline chain proof: {summary.decisions['pipeline_chain_proof']}",
        "- daily/resume/audit-only modes: "
        f"{summary.decisions['daily_incremental_resume_audit_modes']}",
        f"- full rebuild passed: {'yes' if full_rebuild_passed else 'no'}",
        f"- daily incremental release passed: {'yes' if daily_release_passed else 'no'}",
        f"- final release evidence: {summary.decisions['final_release_evidence']}",
        "- formal H:/Asteria-data mutation: no",
        "- System full build: no",
        "- v1 complete: no",
        f"- next allowed action: {summary.next_allowed_action}",
    ]
    return "\n".join(lines) + "\n"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
