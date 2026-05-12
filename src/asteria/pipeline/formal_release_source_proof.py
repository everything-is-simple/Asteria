from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

FORMAL_RELEASE_SOURCE_PROOF_CARD = "formal-full-rebuild-and-daily-incremental-release-proof-card"
NEXT_ALLOWED_ACTION = "formal_full_rebuild_and_daily_incremental_release_proof_card"
REPORT_DATE = "2026-05-12"

SOURCE_SURFACES = {
    "formal_full_rebuild_proof": "formal-full-rebuild-proof",
    "daily_incremental_release_proof": "daily-incremental-release-proof",
    "resume_idempotence_proof": "resume-idempotence-proof",
}


@dataclass(frozen=True)
class FormalReleaseSourceProofRequest:
    repo_root: Path
    source_root: Path
    temp_root: Path
    report_root: Path
    run_id: str
    mode: str = "audit-only"

    def __post_init__(self) -> None:
        if self.mode not in {"audit-only", "source-proof", "resume"}:
            raise ValueError(f"Unsupported formal release source proof mode: {self.mode}")

    @property
    def run_root(self) -> Path:
        return self.temp_root / "formal-release-source-proof" / self.run_id

    @property
    def report_dir(self) -> Path:
        return self.report_root / "pipeline" / REPORT_DATE / self.run_id

    @property
    def source_surface_audit_path(self) -> Path:
        return self.run_root / "source-surface-audit.json"

    @property
    def source_proof_summary_path(self) -> Path:
        return self.run_root / "source-proof-summary.json"

    @property
    def formal_release_manifest_path(self) -> Path:
        return self.run_root / "formal-release-proof-manifest.json"

    @property
    def checkpoint_path(self) -> Path:
        return self.run_root / "source-proof-checkpoint.json"

    @property
    def summary_path(self) -> Path:
        return self.report_dir / "summary.json"

    @property
    def closeout_path(self) -> Path:
        return self.report_dir / "closeout.md"

    @property
    def gate_registry_path(self) -> Path:
        return self.repo_root / "governance" / "module_gate_registry.toml"


@dataclass(frozen=True)
class FormalReleaseSourceProofSummary:
    run_id: str
    status: str
    mode: str
    card_id: str
    next_allowed_action: str
    decisions: dict[str, str]
    boundaries: dict[str, bool]
    source_surface_audit_path: str
    source_proof_summary_path: str
    formal_release_manifest_path: str
    checkpoint_path: str
    summary_path: str
    closeout_path: str
    resume_reused: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_formal_release_source_proof(
    request: FormalReleaseSourceProofRequest,
) -> FormalReleaseSourceProofSummary:
    _validate_live_gate(request)
    request.run_root.mkdir(parents=True, exist_ok=True)
    request.report_dir.mkdir(parents=True, exist_ok=True)

    if request.mode == "resume":
        checkpoint = _load_completed_checkpoint(request)
        if checkpoint is not None:
            return checkpoint

    surface_audit = _build_source_surface_audit(request)
    decisions = {key: str(surface_audit["surfaces"][key]["decision"]) for key in SOURCE_SURFACES}
    status = (
        "passed / source surfaces ready"
        if all(decision == "passed" for decision in decisions.values())
        else "blocked / source surface gaps found"
    )
    manifest = _formal_release_manifest(request, decisions, surface_audit)
    summary = _summary(request, status, decisions)
    _write_outputs(request, summary, surface_audit, manifest)
    return summary


def _validate_live_gate(request: FormalReleaseSourceProofRequest) -> None:
    if not request.gate_registry_path.exists():
        raise ValueError(f"gate registry missing: {request.gate_registry_path}")
    with request.gate_registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    if registry.get("current_allowed_next_card") != NEXT_ALLOWED_ACTION:
        raise ValueError("formal release source proof is not currently authorized")


def _load_completed_checkpoint(
    request: FormalReleaseSourceProofRequest,
) -> FormalReleaseSourceProofSummary | None:
    if not request.checkpoint_path.exists():
        return None
    payload = _read_json(request.checkpoint_path)
    if payload.get("status") != "completed":
        return None
    return FormalReleaseSourceProofSummary(
        **{**payload["summary"], "mode": request.mode, "resume_reused": True}
    )


def _build_source_surface_audit(request: FormalReleaseSourceProofRequest) -> dict[str, Any]:
    surfaces = {
        key: _inspect_surface(request.source_root, proof_name)
        for key, proof_name in SOURCE_SURFACES.items()
    }
    return {
        "run_id": request.run_id,
        "card_id": FORMAL_RELEASE_SOURCE_PROOF_CARD,
        "source_root": str(request.source_root),
        "surfaces": surfaces,
        "formal_data_mutation": False,
    }


def _inspect_surface(source_root: Path, proof_name: str) -> dict[str, Any]:
    path = source_root / f"{proof_name}.json"
    if not path.exists():
        return {
            "proof_name": proof_name,
            "path": str(path),
            "status": "missing",
            "decision": "blocked / source proof missing",
            "source_db_root": "",
        }
    try:
        payload = _read_json(path)
    except json.JSONDecodeError:
        return {
            "proof_name": proof_name,
            "path": str(path),
            "status": "unreadable",
            "decision": "blocked / source proof unreadable",
            "source_db_root": "",
        }
    source_db_root = str(payload.get("source_db_root", ""))
    if payload.get("proof_scope") != proof_name or payload.get("status") != "passed":
        decision = "blocked / source proof not passed"
    elif not source_db_root:
        decision = "blocked / source DB root missing"
    else:
        decision = "passed"
    return {
        "proof_name": proof_name,
        "path": str(path),
        "status": str(payload.get("status", "unknown")),
        "decision": decision,
        "source_db_root": source_db_root,
        "known_limits": list(payload.get("known_limits", ())),
    }


def _formal_release_manifest(
    request: FormalReleaseSourceProofRequest,
    decisions: dict[str, str],
    surface_audit: dict[str, Any],
) -> dict[str, Any]:
    source_db_root = _common_source_db_root(surface_audit) if _all_passed(decisions) else ""
    known_limits = _known_limits(surface_audit)
    if not _all_passed(decisions):
        known_limits.append("formal release source proof incomplete")
    return {
        "proof_scope": "formal_release",
        "sample_proof": False,
        "formal_full_rebuild_proof": decisions["formal_full_rebuild_proof"],
        "full_rebuild_proof": decisions["formal_full_rebuild_proof"],
        "daily_incremental_release_proof": decisions["daily_incremental_release_proof"],
        "resume_idempotence_proof": decisions["resume_idempotence_proof"],
        "source_db_root": source_db_root,
        "known_limits": known_limits,
        "source_surface_audit_path": str(request.source_surface_audit_path),
        "source_proof_summary_path": str(request.source_proof_summary_path),
    }


def _summary(
    request: FormalReleaseSourceProofRequest,
    status: str,
    decisions: dict[str, str],
) -> FormalReleaseSourceProofSummary:
    return FormalReleaseSourceProofSummary(
        run_id=request.run_id,
        status=status,
        mode=request.mode,
        card_id=FORMAL_RELEASE_SOURCE_PROOF_CARD,
        next_allowed_action=NEXT_ALLOWED_ACTION,
        decisions=decisions,
        boundaries={
            "formal_data_mutation": False,
            "pipeline_semantic_repair": False,
            "system_full_build_claim": False,
            "v1_complete_claim": False,
        },
        source_surface_audit_path=str(request.source_surface_audit_path),
        source_proof_summary_path=str(request.source_proof_summary_path),
        formal_release_manifest_path=str(request.formal_release_manifest_path),
        checkpoint_path=str(request.checkpoint_path),
        summary_path=str(request.summary_path),
        closeout_path=str(request.closeout_path),
    )


def _write_outputs(
    request: FormalReleaseSourceProofRequest,
    summary: FormalReleaseSourceProofSummary,
    surface_audit: dict[str, Any],
    manifest: dict[str, Any],
) -> None:
    _write_json(request.source_surface_audit_path, surface_audit)
    _write_json(request.formal_release_manifest_path, manifest)
    _write_json(request.source_proof_summary_path, summary.as_dict())
    _write_json(request.summary_path, summary.as_dict())
    _write_json(request.checkpoint_path, {"status": "completed", "summary": summary.as_dict()})
    request.closeout_path.write_text(_closeout_text(summary), encoding="utf-8")


def _closeout_text(summary: FormalReleaseSourceProofSummary) -> str:
    return (
        "\n".join(
            [
                f"# Formal release source proof: {summary.run_id}",
                "",
                f"- status: {summary.status}",
                f"- formal full rebuild proof: {summary.decisions['formal_full_rebuild_proof']}",
                "- daily incremental release proof: "
                f"{summary.decisions['daily_incremental_release_proof']}",
                f"- resume/idempotence proof: {summary.decisions['resume_idempotence_proof']}",
                "- formal H:/Asteria-data mutation: no",
                "- Pipeline semantic repair: no",
                "- System full build: no",
                "- v1 complete: no",
                f"- next allowed action: {summary.next_allowed_action}",
            ]
        )
        + "\n"
    )


def _all_passed(decisions: dict[str, str]) -> bool:
    return all(decision == "passed" for decision in decisions.values())


def _common_source_db_root(surface_audit: dict[str, Any]) -> str:
    roots = {
        str(surface.get("source_db_root", ""))
        for surface in surface_audit["surfaces"].values()
        if surface.get("decision") == "passed"
    }
    return roots.pop() if len(roots) == 1 else ""


def _known_limits(surface_audit: dict[str, Any]) -> list[str]:
    limits: list[str] = []
    for surface in surface_audit["surfaces"].values():
        for limit in surface.get("known_limits", ()):
            if str(limit) not in limits:
                limits.append(str(limit))
    return limits


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
