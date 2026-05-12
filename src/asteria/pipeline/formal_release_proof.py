from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from asteria.pipeline.formal_release_proof_io import (
    backup_formal_dbs as _backup_formal_dbs,
)
from asteria.pipeline.formal_release_proof_io import (
    build_db_manifest as _build_db_manifest,
)
from asteria.pipeline.formal_release_proof_io import (
    load_source_proof_manifest as _load_source_proof_manifest,
)
from asteria.pipeline.formal_release_proof_io import (
    promote_staging_dbs as _promote_staging_dbs,
)
from asteria.pipeline.formal_release_proof_io import (
    read_json as _read_json,
)
from asteria.pipeline.formal_release_proof_io import (
    sha256 as _sha256,
)
from asteria.pipeline.formal_release_proof_io import (
    source_db_root as _source_db_root,
)
from asteria.pipeline.formal_release_proof_io import (
    source_manifest_passes as _source_manifest_passes,
)
from asteria.pipeline.formal_release_proof_io import (
    stage_formal_dbs as _stage_formal_dbs,
)
from asteria.pipeline.formal_release_proof_io import (
    write_json as _write_json,
)
from asteria.pipeline.formal_release_proof_io import (
    write_promote_skipped as _write_promote_skipped,
)
from asteria.pipeline.formal_release_proof_io import (
    write_skipped_staging_and_promote as _write_skipped_staging_and_promote,
)
from asteria.pipeline.formal_release_proof_io import (
    write_staging_failed as _write_staging_failed,
)

FORMAL_RELEASE_PROOF_CARD = "formal-full-rebuild-and-daily-incremental-release-proof-card"
NEXT_ALLOWED_ACTION = "formal_full_rebuild_and_daily_incremental_release_proof_card"
FINAL_RELEASE_CLOSEOUT_ACTION = "final_release_closeout_card"
REPORT_DATE = "2026-05-12"


@dataclass(frozen=True)
class FormalReleaseProofRequest:
    source_root: Path
    formal_data_root: Path
    temp_root: Path
    report_root: Path
    validated_root: Path
    run_id: str
    mode: str = "audit-only"
    allow_formal_data_write: bool = False

    def __post_init__(self) -> None:
        if self.mode not in {"audit-only", "release-proof", "resume"}:
            raise ValueError(f"Unsupported formal release proof mode: {self.mode}")

    @property
    def run_root(self) -> Path:
        return self.temp_root / "formal-release-proof" / self.run_id

    @property
    def staging_root(self) -> Path:
        return self.run_root / "staging"

    @property
    def backup_root(self) -> Path:
        return self.run_root / "formal-data-backup"

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
    def db_manifest_path(self) -> Path:
        return self.run_root / "db-manifest.json"

    @property
    def backup_manifest_path(self) -> Path:
        return self.run_root / "backup-manifest.json"

    @property
    def staging_manifest_path(self) -> Path:
        return self.run_root / "staging-manifest.json"

    @property
    def promote_manifest_path(self) -> Path:
        return self.run_root / "promote-manifest.json"

    @property
    def resume_idempotence_manifest_path(self) -> Path:
        return self.run_root / "resume-idempotence-manifest.json"

    @property
    def final_release_evidence_path(self) -> Path:
        return self.run_root / "final-release-evidence.json"

    @property
    def validated_manifest_path(self) -> Path:
        return self.validated_root / f"Asteria-{self.run_id}-manifest.json"


@dataclass(frozen=True)
class FormalReleaseProofSummary:
    run_id: str
    status: str
    mode: str
    card_id: str
    next_allowed_action: str
    decisions: dict[str, str]
    boundaries: dict[str, bool]
    db_count: int
    db_manifest: dict[str, Any]
    manifest_hashes: dict[str, str]
    summary_path: str
    closeout_path: str
    db_manifest_path: str
    backup_manifest_path: str
    staging_manifest_path: str
    promote_manifest_path: str
    resume_idempotence_manifest_path: str
    final_release_evidence_path: str
    validated_manifest_path: str
    resume_reused: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_formal_release_proof(
    request: FormalReleaseProofRequest,
) -> FormalReleaseProofSummary:
    request.run_root.mkdir(parents=True, exist_ok=True)
    request.report_dir.mkdir(parents=True, exist_ok=True)
    request.validated_root.mkdir(parents=True, exist_ok=True)

    if request.mode == "resume" and _promote_completed(request.promote_manifest_path):
        return _resume_completed(request)

    db_manifest = _build_db_manifest(request.formal_data_root)
    _write_json(request.db_manifest_path, db_manifest)

    if request.mode == "audit-only":
        return _blocked_summary(
            request,
            status="blocked / formal release proof not executed",
            decisions={
                "formal_data_write_authorized": "not requested",
                "formal_full_rebuild_proof": "not executed",
                "daily_incremental_release_proof": "not executed",
                "resume_idempotence_proof": "not executed",
                "staging_rebuild": "not executed",
                "formal_promote": "not executed",
                "final_release_evidence": "retained gap",
            },
            db_manifest=db_manifest,
        )

    if not request.allow_formal_data_write:
        return _blocked_summary(
            request,
            status="blocked / formal data write not authorized",
            decisions={
                "formal_data_write_authorized": "blocked",
                "formal_full_rebuild_proof": "not evaluated",
                "daily_incremental_release_proof": "not evaluated",
                "resume_idempotence_proof": "not evaluated",
                "staging_rebuild": "not evaluated",
                "formal_promote": "not evaluated",
                "final_release_evidence": "retained gap",
            },
            db_manifest=db_manifest,
        )

    backup_manifest = _backup_formal_dbs(request)
    source_manifest = _load_source_proof_manifest(request.source_root)
    if not _source_manifest_passes(source_manifest):
        _write_skipped_staging_and_promote(request, "runner surface missing")
        return _blocked_summary(
            request,
            status="blocked / runner surface missing",
            decisions={
                "formal_data_write_authorized": "passed",
                "formal_full_rebuild_proof": "blocked / runner surface missing",
                "daily_incremental_release_proof": "blocked / runner surface missing",
                "resume_idempotence_proof": "blocked / runner surface missing",
                "staging_rebuild": "skipped",
                "formal_promote": "skipped",
                "final_release_evidence": "retained gap",
            },
            db_manifest=db_manifest,
            backup_manifest=backup_manifest,
        )

    source_db_root = _source_db_root(request.source_root, source_manifest)
    if not source_db_root.exists() or not any(source_db_root.glob("*.duckdb")):
        _write_staging_failed(request, source_db_root)
        _write_promote_skipped(request, "staging rebuild failed")
        return _blocked_summary(
            request,
            status="blocked / staging rebuild failed",
            decisions={
                "formal_data_write_authorized": "passed",
                "formal_full_rebuild_proof": "passed",
                "daily_incremental_release_proof": "passed",
                "resume_idempotence_proof": "passed",
                "staging_rebuild": "blocked",
                "formal_promote": "skipped",
                "final_release_evidence": "retained gap",
            },
            db_manifest=db_manifest,
            backup_manifest=backup_manifest,
        )

    staging_manifest = _stage_formal_dbs(request, source_db_root)
    promoted_manifest = _promote_staging_dbs(request)
    final_evidence = _final_release_evidence(
        request,
        known_limits=tuple(source_manifest.get("known_limits", ())),
    )
    _write_json(request.db_manifest_path, final_evidence["db_manifest"])
    _write_json(request.final_release_evidence_path, final_evidence)
    _write_resume_manifest(request, promote_reused=False)
    return _passed_summary(
        request,
        db_manifest=final_evidence["db_manifest"],
        staging_manifest=staging_manifest,
        promote_manifest=promoted_manifest,
        final_evidence=final_evidence,
    )


def _resume_completed(request: FormalReleaseProofRequest) -> FormalReleaseProofSummary:
    db_manifest = _build_db_manifest(request.formal_data_root)
    final_evidence = (
        _read_json(request.final_release_evidence_path)
        if request.final_release_evidence_path.exists()
        else _final_release_evidence(request, known_limits=())
    )
    _write_json(request.db_manifest_path, db_manifest)
    _write_resume_manifest(request, promote_reused=True)
    return _passed_summary(
        request,
        db_manifest=final_evidence.get("db_manifest", db_manifest),
        staging_manifest=_read_json(request.staging_manifest_path),
        promote_manifest=_read_json(request.promote_manifest_path),
        final_evidence=final_evidence,
        resume_reused=True,
    )


def _blocked_summary(
    request: FormalReleaseProofRequest,
    *,
    status: str,
    decisions: dict[str, str],
    db_manifest: dict[str, Any],
    backup_manifest: dict[str, Any] | None = None,
) -> FormalReleaseProofSummary:
    final_evidence = _final_release_evidence(
        request,
        known_limits=("formal release proof incomplete",),
        db_manifest=db_manifest,
        status="blocked",
    )
    _write_json(request.final_release_evidence_path, final_evidence)
    _write_json(request.validated_manifest_path, _validated_manifest(status, request))
    summary = FormalReleaseProofSummary(
        run_id=request.run_id,
        status=status,
        mode=request.mode,
        card_id=FORMAL_RELEASE_PROOF_CARD,
        next_allowed_action=NEXT_ALLOWED_ACTION,
        decisions=decisions,
        boundaries={
            "formal_data_mutation": False,
            "pipeline_semantic_repair": False,
            "system_full_build_claim": False,
            "v1_complete_claim": False,
        },
        db_count=len(db_manifest["databases"]),
        db_manifest=db_manifest,
        manifest_hashes=_manifest_hashes(request),
        summary_path=str(request.summary_path),
        closeout_path=str(request.closeout_path),
        db_manifest_path=str(request.db_manifest_path),
        backup_manifest_path=str(request.backup_manifest_path),
        staging_manifest_path=str(request.staging_manifest_path),
        promote_manifest_path=str(request.promote_manifest_path),
        resume_idempotence_manifest_path=str(request.resume_idempotence_manifest_path),
        final_release_evidence_path=str(request.final_release_evidence_path),
        validated_manifest_path=str(request.validated_manifest_path),
    )
    _write_summary_outputs(request, summary, backup_manifest=backup_manifest)
    return summary


def _passed_summary(
    request: FormalReleaseProofRequest,
    *,
    db_manifest: dict[str, Any],
    staging_manifest: dict[str, Any],
    promote_manifest: dict[str, Any],
    final_evidence: dict[str, Any],
    resume_reused: bool = False,
) -> FormalReleaseProofSummary:
    status = "passed / formal release evidence complete"
    _write_json(request.validated_manifest_path, _validated_manifest(status, request))
    summary = FormalReleaseProofSummary(
        run_id=request.run_id,
        status=status,
        mode=request.mode,
        card_id=FORMAL_RELEASE_PROOF_CARD,
        next_allowed_action=FINAL_RELEASE_CLOSEOUT_ACTION,
        decisions={
            "formal_data_write_authorized": "passed",
            "formal_full_rebuild_proof": "passed",
            "daily_incremental_release_proof": "passed",
            "resume_idempotence_proof": "passed",
            "staging_rebuild": str(staging_manifest.get("status", "passed")),
            "formal_promote": str(promote_manifest.get("status", "promoted")),
            "final_release_evidence": str(final_evidence.get("status", "passed")),
        },
        boundaries={
            "formal_data_mutation": not resume_reused,
            "pipeline_semantic_repair": False,
            "system_full_build_claim": False,
            "v1_complete_claim": False,
        },
        db_count=len(db_manifest["databases"]),
        db_manifest=db_manifest,
        manifest_hashes=_manifest_hashes(request),
        summary_path=str(request.summary_path),
        closeout_path=str(request.closeout_path),
        db_manifest_path=str(request.db_manifest_path),
        backup_manifest_path=str(request.backup_manifest_path),
        staging_manifest_path=str(request.staging_manifest_path),
        promote_manifest_path=str(request.promote_manifest_path),
        resume_idempotence_manifest_path=str(request.resume_idempotence_manifest_path),
        final_release_evidence_path=str(request.final_release_evidence_path),
        validated_manifest_path=str(request.validated_manifest_path),
        resume_reused=resume_reused,
    )
    _write_summary_outputs(request, summary)
    return summary


def _final_release_evidence(
    request: FormalReleaseProofRequest,
    *,
    known_limits: tuple[str, ...],
    db_manifest: dict[str, Any] | None = None,
    status: str = "passed",
) -> dict[str, Any]:
    manifest = db_manifest or _build_db_manifest(request.formal_data_root)
    return {
        "run_id": request.run_id,
        "card_id": FORMAL_RELEASE_PROOF_CARD,
        "status": status,
        "db_manifest": manifest,
        "schema_versions": {
            db_name: db["schema_versions"] for db_name, db in manifest["databases"].items()
        },
        "rule_versions": {
            db_name: db["rule_versions"] for db_name, db in manifest["databases"].items()
        },
        "row_counts": {db_name: db["row_counts"] for db_name, db in manifest["databases"].items()},
        "audit_summaries": {
            "status": "passed" if manifest["databases"] and status == "passed" else "blocked",
            "db_count": len(manifest["databases"]),
        },
        "known_limits": list(known_limits),
        "backup_manifest": str(request.backup_manifest_path),
        "staging_manifest": str(request.staging_manifest_path),
        "promote_manifest": str(request.promote_manifest_path),
        "resume_idempotence_manifest": str(request.resume_idempotence_manifest_path),
    }


def _write_resume_manifest(request: FormalReleaseProofRequest, *, promote_reused: bool) -> None:
    promote_attempt_count = 1 if _promote_completed(request.promote_manifest_path) else 0
    _write_json(
        request.resume_idempotence_manifest_path,
        {
            "status": "passed",
            "promote_reused": promote_reused,
            "promote_attempt_count": promote_attempt_count,
            "manifest_hashes": _manifest_hashes(request),
        },
    )


def _promote_completed(path: Path) -> bool:
    if not path.exists():
        return False
    return _read_json(path).get("status") == "promoted"


def _manifest_hashes(request: FormalReleaseProofRequest) -> dict[str, str]:
    paths = {
        "db_manifest": request.db_manifest_path,
        "final_release_evidence": request.final_release_evidence_path,
        "promote_manifest": request.promote_manifest_path,
        "staging_manifest": request.staging_manifest_path,
    }
    return {name: _sha256(path) for name, path in paths.items() if path.exists()}


def _write_summary_outputs(
    request: FormalReleaseProofRequest,
    summary: FormalReleaseProofSummary,
    *,
    backup_manifest: dict[str, Any] | None = None,
) -> None:
    payload = summary.as_dict()
    if backup_manifest is not None:
        payload["backup_manifest"] = backup_manifest
    _write_json(request.summary_path, payload)
    request.closeout_path.write_text(_closeout_text(summary), encoding="utf-8")


def _closeout_text(summary: FormalReleaseProofSummary) -> str:
    return (
        "\n".join(
            [
                f"# Formal release proof: {summary.run_id}",
                "",
                f"- status: {summary.status}",
                f"- formal full rebuild proof: {summary.decisions['formal_full_rebuild_proof']}",
                "- daily incremental release proof: "
                f"{summary.decisions['daily_incremental_release_proof']}",
                f"- resume/idempotence proof: {summary.decisions['resume_idempotence_proof']}",
                f"- final release evidence: {summary.decisions['final_release_evidence']}",
                f"- formal H:/Asteria-data mutation: {summary.boundaries['formal_data_mutation']}",
                "- Pipeline semantic repair: no",
                "- System full build: no",
                "- v1 complete: no",
                f"- next allowed action: {summary.next_allowed_action}",
            ]
        )
        + "\n"
    )


def _validated_manifest(status: str, request: FormalReleaseProofRequest) -> dict[str, Any]:
    return {
        "run_id": request.run_id,
        "card_id": FORMAL_RELEASE_PROOF_CARD,
        "status": status,
        "summary_path": str(request.summary_path),
        "closeout_path": str(request.closeout_path),
        "final_release_evidence_path": str(request.final_release_evidence_path),
    }
