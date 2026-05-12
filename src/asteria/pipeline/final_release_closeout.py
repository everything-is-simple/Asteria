from __future__ import annotations

import shutil
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from asteria.pipeline.formal_release_proof_io import (
    build_db_manifest,
    read_json,
    sha256,
    source_manifest_passes,
    write_json,
)

FINAL_RELEASE_CLOSEOUT_CARD = "final-release-closeout-card"
FINAL_RELEASE_CLOSEOUT_ACTION = "final_release_closeout_card"
FINAL_RELEASE_PROOF_CARD = "formal-full-rebuild-and-daily-incremental-release-proof-card"
REPORT_DATE = "2026-05-12"
EXPECTED_DB_COUNT = 25


@dataclass(frozen=True)
class FinalReleaseCloseoutRequest:
    formal_data_root: Path
    source_proof_root: Path
    proof_run_root: Path
    proof_report_dir: Path
    report_root: Path
    validated_root: Path
    run_id: str
    mode: str = "audit-only"

    def __post_init__(self) -> None:
        if self.mode not in {"audit-only", "closeout"}:
            raise ValueError(f"Unsupported final release closeout mode: {self.mode}")

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
    def final_closeout_manifest_path(self) -> Path:
        return self.report_dir / "final-closeout-manifest.json"

    @property
    def validated_manifest_path(self) -> Path:
        return self.validated_root / f"Asteria-{self.run_id}-manifest.json"

    @property
    def validated_zip_path(self) -> Path:
        return self.validated_root / f"Asteria-{self.run_id}-20260512-01.zip"


@dataclass(frozen=True)
class FinalReleaseCloseoutSummary:
    run_id: str
    status: str
    mode: str
    card_id: str
    next_allowed_action: str
    decisions: dict[str, str]
    boundaries: dict[str, bool]
    db_count: int
    known_limits: list[str]
    evidence_issues: list[str]
    summary_path: str
    closeout_path: str
    final_closeout_manifest_path: str
    validated_manifest_path: str
    validated_zip_path: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_final_release_closeout(
    request: FinalReleaseCloseoutRequest,
) -> FinalReleaseCloseoutSummary:
    request.report_dir.mkdir(parents=True, exist_ok=True)
    request.validated_root.mkdir(parents=True, exist_ok=True)

    evidence = _read_evidence(request)
    current_db_manifest = (
        build_db_manifest(request.formal_data_root)
        if request.formal_data_root.exists()
        else {"root": str(request.formal_data_root), "databases": {}}
    )
    decisions, issues = _decide(request, evidence, current_db_manifest)
    if request.mode == "audit-only" and not issues:
        decisions["final_closeout_execution"] = "not executed"
        issues = ["final closeout mode was audit-only"]

    passed = not issues
    status = "passed / v1 complete" if passed else "blocked / final release evidence inconsistent"
    known_limits = _known_limits(evidence)
    summary = FinalReleaseCloseoutSummary(
        run_id=request.run_id,
        status=status,
        mode=request.mode,
        card_id=FINAL_RELEASE_CLOSEOUT_CARD,
        next_allowed_action="" if passed else FINAL_RELEASE_CLOSEOUT_ACTION,
        decisions=decisions,
        boundaries={
            "formal_data_mutation": False,
            "pipeline_semantic_repair": False,
            "system_full_build_claim": False,
            "v1_complete_claim": passed,
        },
        db_count=len(current_db_manifest["databases"]),
        known_limits=known_limits,
        evidence_issues=issues,
        summary_path=str(request.summary_path),
        closeout_path=str(request.closeout_path),
        final_closeout_manifest_path=str(request.final_closeout_manifest_path),
        validated_manifest_path=str(request.validated_manifest_path),
        validated_zip_path=str(request.validated_zip_path),
    )
    _write_outputs(request, summary, evidence, current_db_manifest)
    if passed:
        _write_validated_archive(request, summary)
    return summary


def _read_evidence(request: FinalReleaseCloseoutRequest) -> dict[str, Any]:
    paths = {
        "source_manifest": request.source_proof_root / "formal-release-proof-manifest.json",
        "proof_summary": request.proof_report_dir / "summary.json",
        "db_manifest": request.proof_run_root / "db-manifest.json",
        "backup_manifest": request.proof_run_root / "backup-manifest.json",
        "staging_manifest": request.proof_run_root / "staging-manifest.json",
        "promote_manifest": request.proof_run_root / "promote-manifest.json",
        "resume_manifest": request.proof_run_root / "resume-idempotence-manifest.json",
        "final_release_evidence": request.proof_run_root / "final-release-evidence.json",
        "previous_validated_manifest": (
            request.validated_root / f"Asteria-{FINAL_RELEASE_PROOF_CARD}-manifest.json"
        ),
        "previous_validated_zip": (
            request.validated_root / f"Asteria-{FINAL_RELEASE_PROOF_CARD}-20260512-01.zip"
        ),
    }
    loaded: dict[str, Any] = {"paths": {name: str(path) for name, path in paths.items()}}
    for name, path in paths.items():
        if path.suffix == ".zip":
            loaded[name] = {"exists": path.exists(), "sha256": sha256(path)}
        elif path.exists():
            loaded[name] = read_json(path)
        else:
            loaded[name] = None
    return loaded


def _decide(
    request: FinalReleaseCloseoutRequest,
    evidence: dict[str, Any],
    current_db_manifest: dict[str, Any],
) -> tuple[dict[str, str], list[str]]:
    issues: list[str] = []
    decisions = {
        "source_release_proof": _source_manifest_decision(evidence, issues),
        "proof_summary": _proof_summary_decision(evidence, issues),
        "formal_release_evidence": _final_evidence_decision(evidence, issues),
        "backup_manifest": _status_decision(evidence, issues, "backup_manifest", "completed"),
        "staging_manifest": _status_decision(evidence, issues, "staging_manifest", "passed"),
        "promote_manifest": _status_decision(evidence, issues, "promote_manifest", "promoted"),
        "resume_idempotence_manifest": _resume_decision(evidence, issues),
        "validated_manifest": _validated_manifest_decision(evidence, issues),
        "validated_archive": _validated_zip_decision(evidence, issues),
        "current_formal_data_matches_evidence": _db_manifest_decision(
            evidence, current_db_manifest, issues
        ),
    }
    if not request.formal_data_root.exists():
        issues.append(f"formal data root missing: {request.formal_data_root}")
    return decisions, issues


def _source_manifest_decision(evidence: dict[str, Any], issues: list[str]) -> str:
    manifest = evidence.get("source_manifest")
    if manifest is None:
        issues.append("source proof manifest missing")
        return "missing"
    if not source_manifest_passes(manifest):
        issues.append("source proof manifest is not passed formal release proof")
        return "blocked"
    return "passed"


def _proof_summary_decision(evidence: dict[str, Any], issues: list[str]) -> str:
    summary = evidence.get("proof_summary")
    if summary is None:
        issues.append("formal release proof summary missing")
        return "missing"
    if summary.get("status") != "passed / formal release evidence complete":
        issues.append("formal release proof summary status is not passed")
        return "blocked"
    if summary.get("next_allowed_action") != FINAL_RELEASE_CLOSEOUT_ACTION:
        issues.append("formal release proof summary next action is not final closeout")
        return "blocked"
    if summary.get("db_count") != EXPECTED_DB_COUNT:
        issues.append("formal release proof summary DB count is not 25")
        return "blocked"
    return "passed"


def _final_evidence_decision(evidence: dict[str, Any], issues: list[str]) -> str:
    final_evidence = evidence.get("final_release_evidence")
    if final_evidence is None:
        issues.append("final release evidence missing")
        return "missing"
    audit = final_evidence.get("audit_summaries", {})
    databases = final_evidence.get("db_manifest", {}).get("databases", {})
    if final_evidence.get("status") != "passed" or audit.get("status") != "passed":
        issues.append("final release evidence status is not passed")
        return "blocked"
    if audit.get("db_count") != EXPECTED_DB_COUNT or len(databases) != EXPECTED_DB_COUNT:
        issues.append("final release evidence DB count is not 25")
        return "blocked"
    return "passed"


def _status_decision(
    evidence: dict[str, Any],
    issues: list[str],
    key: str,
    expected_status: str,
) -> str:
    manifest = evidence.get(key)
    if manifest is None:
        issues.append(f"{key.replace('_', ' ')} missing")
        return "missing"
    if manifest.get("status") != expected_status:
        issues.append(f"{key.replace('_', ' ')} status is not {expected_status}")
        return "blocked"
    return "passed"


def _resume_decision(evidence: dict[str, Any], issues: list[str]) -> str:
    manifest = evidence.get("resume_manifest")
    if manifest is None:
        issues.append("resume idempotence manifest missing")
        return "missing"
    if manifest.get("status") != "passed" or manifest.get("promote_reused") is not True:
        issues.append("resume idempotence manifest did not reuse promoted evidence")
        return "blocked"
    return "passed"


def _validated_manifest_decision(evidence: dict[str, Any], issues: list[str]) -> str:
    manifest = evidence.get("previous_validated_manifest")
    if manifest is None:
        issues.append("previous validated manifest missing")
        return "missing"
    if manifest.get("status") != "passed / formal release evidence complete":
        issues.append("previous validated manifest is not passed")
        return "blocked"
    return "passed"


def _validated_zip_decision(evidence: dict[str, Any], issues: list[str]) -> str:
    archive = evidence.get("previous_validated_zip", {})
    if not archive.get("exists"):
        issues.append("previous validated archive missing")
        return "missing"
    return "passed"


def _db_manifest_decision(
    evidence: dict[str, Any],
    current_db_manifest: dict[str, Any],
    issues: list[str],
) -> str:
    final_evidence = evidence.get("final_release_evidence")
    if final_evidence is None:
        return "not evaluated"
    expected = final_evidence.get("db_manifest", {}).get("databases", {})
    current = current_db_manifest.get("databases", {})
    if set(expected) != set(current):
        issues.append("current formal DB names do not match final release evidence")
        return "blocked"
    for db_name in sorted(expected):
        for field in ["sha256", "row_counts", "schema_versions", "rule_versions"]:
            if expected[db_name].get(field) != current[db_name].get(field):
                issues.append(f"{db_name} {field} differs from final release evidence")
                return "blocked"
    return "passed"


def _known_limits(evidence: dict[str, Any]) -> list[str]:
    final_evidence = evidence.get("final_release_evidence") or {}
    known_limits = final_evidence.get("known_limits", [])
    normalized: list[str] = []
    for item in known_limits:
        text = str(item)
        if text == "does not claim v1 complete":
            text = "formal release proof did not claim v1 complete before final closeout"
        normalized.append(text)
    return normalized


def _write_outputs(
    request: FinalReleaseCloseoutRequest,
    summary: FinalReleaseCloseoutSummary,
    evidence: dict[str, Any],
    current_db_manifest: dict[str, Any],
) -> None:
    payload = summary.as_dict()
    payload["evidence_paths"] = evidence["paths"]
    payload["current_db_manifest"] = current_db_manifest
    write_json(request.summary_path, payload)
    write_json(request.final_closeout_manifest_path, _final_closeout_manifest(summary, evidence))
    request.closeout_path.write_text(_closeout_text(summary), encoding="utf-8")
    if summary.status.startswith("passed"):
        write_json(request.validated_manifest_path, _validated_manifest(summary))


def _final_closeout_manifest(
    summary: FinalReleaseCloseoutSummary,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "run_id": summary.run_id,
        "card_id": summary.card_id,
        "status": summary.status,
        "next_allowed_action": summary.next_allowed_action,
        "decisions": summary.decisions,
        "known_limits": summary.known_limits,
        "evidence_issues": summary.evidence_issues,
        "source_evidence_paths": evidence["paths"],
    }


def _validated_manifest(summary: FinalReleaseCloseoutSummary) -> dict[str, Any]:
    return {
        "run_id": summary.run_id,
        "card_id": summary.card_id,
        "status": summary.status,
        "summary_path": summary.summary_path,
        "closeout_path": summary.closeout_path,
        "final_closeout_manifest_path": summary.final_closeout_manifest_path,
        "validated_zip_path": summary.validated_zip_path,
    }


def _write_validated_archive(
    request: FinalReleaseCloseoutRequest,
    summary: FinalReleaseCloseoutSummary,
) -> None:
    staging_root = request.report_dir / "validated-archive"
    if staging_root.exists():
        shutil.rmtree(staging_root)
    staging_root.mkdir(parents=True)
    for source in [
        request.summary_path,
        request.closeout_path,
        request.final_closeout_manifest_path,
        request.validated_manifest_path,
    ]:
        shutil.copy2(source, staging_root / source.name)
    with zipfile.ZipFile(request.validated_zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(staging_root.iterdir()):
            archive.write(path, arcname=path.name)


def _closeout_text(summary: FinalReleaseCloseoutSummary) -> str:
    known_limits = "; ".join(summary.known_limits) if summary.known_limits else "none"
    issues = "; ".join(summary.evidence_issues) if summary.evidence_issues else "none"
    return (
        "\n".join(
            [
                f"# Final release closeout: {summary.run_id}",
                "",
                f"- status: {summary.status}",
                f"- formal release evidence: {summary.decisions['formal_release_evidence']}",
                "- current formal data matches evidence: "
                f"{summary.decisions['current_formal_data_matches_evidence']}",
                f"- v1 complete: {'yes' if summary.boundaries['v1_complete_claim'] else 'no'}",
                "- formal H:/Asteria-data mutation: no",
                "- Pipeline semantic repair: no",
                "- System full build: no",
                f"- known limits: {known_limits}",
                f"- evidence issues: {issues}",
                f"- next allowed action: {summary.next_allowed_action}",
            ]
        )
        + "\n"
    )
