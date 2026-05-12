from __future__ import annotations

from pathlib import Path

import duckdb
from scripts.pipeline.run_final_release_closeout import _request_from_args, build_parser

from asteria.pipeline.final_release_closeout import (
    FINAL_RELEASE_CLOSEOUT_CARD,
    FINAL_RELEASE_PROOF_CARD,
    FinalReleaseCloseoutRequest,
    run_final_release_closeout,
)
from asteria.pipeline.formal_release_proof_io import build_db_manifest, write_json

RUN_ID = "final-release-closeout-card"
FORMAL_PROOF_RUN_ID = "formal-full-rebuild-and-daily-incremental-release-proof-card"


def _write_db(path: Path, *, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    with duckdb.connect(str(path)) as con:
        con.execute("create table facts(id integer, value varchar)")
        con.execute("insert into facts values (1, ?)", [value])
        con.execute("create table schema_version(schema_version varchar)")
        con.execute("insert into schema_version values ('schema-v1')")
        con.execute("create table rule_version(rule_version varchar)")
        con.execute("insert into rule_version values ('rule-v1')")


def _write_release_evidence(tmp_path: Path, *, db_count: int = 25) -> FinalReleaseCloseoutRequest:
    formal_data_root = tmp_path / "Asteria-data"
    source_proof_root = (
        tmp_path / "Asteria-temp" / "formal-release-source-proof" / "formal-release-source-proof"
    )
    proof_run_root = tmp_path / "Asteria-temp" / "formal-release-proof" / FORMAL_PROOF_RUN_ID
    report_dir = tmp_path / "Asteria-report" / "pipeline" / "2026-05-12" / FORMAL_PROOF_RUN_ID
    validated_root = tmp_path / "Asteria-Validated"

    for idx in range(db_count):
        _write_db(formal_data_root / f"db_{idx:02d}.duckdb", value=f"value-{idx}")

    db_manifest = build_db_manifest(formal_data_root)
    source_proof_root.mkdir(parents=True)
    write_json(
        source_proof_root / "formal-release-proof-manifest.json",
        {
            "proof_scope": "formal_release",
            "sample_proof": False,
            "full_rebuild_proof": "passed",
            "daily_incremental_release_proof": "passed",
            "resume_idempotence_proof": "passed",
            "source_db_root": str(formal_data_root),
        },
    )
    write_json(
        report_dir / "summary.json",
        {
            "run_id": FORMAL_PROOF_RUN_ID,
            "status": "passed / formal release evidence complete",
            "next_allowed_action": "final_release_closeout_card",
            "decisions": {
                "formal_full_rebuild_proof": "passed",
                "daily_incremental_release_proof": "passed",
                "resume_idempotence_proof": "passed",
                "final_release_evidence": "passed",
                "formal_promote": "promoted",
            },
            "boundaries": {
                "formal_data_mutation": False,
                "pipeline_semantic_repair": False,
                "system_full_build_claim": False,
                "v1_complete_claim": False,
            },
            "db_count": db_count,
        },
    )
    write_json(proof_run_root / "db-manifest.json", db_manifest)
    write_json(proof_run_root / "backup-manifest.json", {"status": "completed"})
    write_json(proof_run_root / "staging-manifest.json", {"status": "passed"})
    write_json(
        proof_run_root / "promote-manifest.json",
        {
            "status": "promoted",
            "databases": [{"db_name": name} for name in db_manifest["databases"]],
            "promote_attempt_count": 1,
        },
    )
    write_json(
        proof_run_root / "resume-idempotence-manifest.json",
        {"status": "passed", "promote_reused": True, "promote_attempt_count": 1},
    )
    write_json(
        proof_run_root / "final-release-evidence.json",
        {
            "run_id": FORMAL_PROOF_RUN_ID,
            "card_id": FINAL_RELEASE_PROOF_CARD,
            "status": "passed",
            "db_manifest": db_manifest,
            "schema_versions": {
                db_name: db["schema_versions"] for db_name, db in db_manifest["databases"].items()
            },
            "rule_versions": {
                db_name: db["rule_versions"] for db_name, db in db_manifest["databases"].items()
            },
            "row_counts": {
                db_name: db["row_counts"] for db_name, db in db_manifest["databases"].items()
            },
            "audit_summaries": {"status": "passed", "db_count": db_count},
            "known_limits": ["fill_ledger remains source-bound until execution source evidence"],
        },
    )
    write_json(
        validated_root / f"Asteria-{FORMAL_PROOF_RUN_ID}-manifest.json",
        {
            "run_id": FORMAL_PROOF_RUN_ID,
            "card_id": FINAL_RELEASE_PROOF_CARD,
            "status": "passed / formal release evidence complete",
        },
    )
    (validated_root / f"Asteria-{FORMAL_PROOF_RUN_ID}-20260512-01.zip").write_bytes(b"zip")

    return FinalReleaseCloseoutRequest(
        formal_data_root=formal_data_root,
        source_proof_root=source_proof_root,
        proof_run_root=proof_run_root,
        proof_report_dir=report_dir,
        report_root=tmp_path / "Asteria-report",
        validated_root=validated_root,
        run_id=RUN_ID,
        mode="closeout",
    )


def test_final_closeout_passes_when_release_evidence_matches_formal_data(
    tmp_path: Path,
) -> None:
    request = _write_release_evidence(tmp_path)

    summary = run_final_release_closeout(request)

    assert summary.card_id == FINAL_RELEASE_CLOSEOUT_CARD
    assert summary.status == "passed / v1 complete"
    assert summary.next_allowed_action == ""
    assert summary.decisions["formal_release_evidence"] == "passed"
    assert summary.decisions["current_formal_data_matches_evidence"] == "passed"
    assert summary.boundaries["formal_data_mutation"] is False
    assert summary.boundaries["pipeline_semantic_repair"] is False
    assert summary.boundaries["system_full_build_claim"] is False
    assert summary.boundaries["v1_complete_claim"] is True
    assert "fill_ledger remains source-bound" in summary.known_limits[0]
    assert Path(summary.closeout_path).exists()
    assert Path(summary.final_closeout_manifest_path).exists()
    assert Path(summary.validated_manifest_path).exists()
    assert Path(summary.validated_zip_path).exists()


def test_final_closeout_blocks_when_required_evidence_is_missing(tmp_path: Path) -> None:
    request = _write_release_evidence(tmp_path)
    Path(request.proof_run_root / "final-release-evidence.json").unlink()

    summary = run_final_release_closeout(request)

    assert summary.status == "blocked / final release evidence inconsistent"
    assert summary.next_allowed_action == "final_release_closeout_card"
    assert summary.decisions["formal_release_evidence"] == "missing"
    assert summary.boundaries["v1_complete_claim"] is False
    assert Path(summary.validated_zip_path).exists() is False


def test_final_closeout_blocks_when_current_formal_data_differs_from_evidence(
    tmp_path: Path,
) -> None:
    request = _write_release_evidence(tmp_path)
    _write_db(request.formal_data_root / "db_00.duckdb", value="changed")

    summary = run_final_release_closeout(request)

    assert summary.status == "blocked / final release evidence inconsistent"
    assert summary.next_allowed_action == "final_release_closeout_card"
    assert summary.decisions["current_formal_data_matches_evidence"] == "blocked"
    assert "db_00.duckdb" in summary.evidence_issues[0]


def test_final_closeout_cli_defaults_to_external_roots() -> None:
    args = build_parser().parse_args([])
    request = _request_from_args(args)

    assert request.formal_data_root == Path("H:/Asteria-data")
    assert request.source_proof_root == Path(
        "H:/Asteria-temp/formal-release-source-proof/formal-release-source-proof-20260512-01"
    )
    assert request.proof_run_root == Path(
        "H:/Asteria-temp/formal-release-proof/"
        "formal-full-rebuild-and-daily-incremental-release-proof-card"
    )
    assert request.report_root == Path("H:/Asteria-report")
    assert request.validated_root == Path("H:/Asteria-Validated")
    assert request.mode == "audit-only"
    assert request.run_id == RUN_ID
