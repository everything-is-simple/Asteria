from __future__ import annotations

import json
from pathlib import Path

import duckdb
from scripts.pipeline.run_formal_release_proof import _request_from_args, build_parser

from asteria.pipeline.formal_release_proof import (
    FORMAL_RELEASE_PROOF_CARD,
    FormalReleaseProofRequest,
    run_formal_release_proof,
)

RUN_ID = "formal-full-rebuild-and-daily-incremental-release-proof-card"


def _write_db(path: Path, *, value: str = "one") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute("create table facts(id integer, value varchar)")
        con.execute("insert into facts values (1, ?)", [value])
        con.execute("create table schema_version(schema_version varchar)")
        con.execute("insert into schema_version values ('schema-v1')")
        con.execute("create table rule_version(rule_version varchar)")
        con.execute("insert into rule_version values ('rule-v1')")


def _request(
    tmp_path: Path,
    *,
    mode: str = "audit-only",
    allow_formal_data_write: bool = False,
) -> FormalReleaseProofRequest:
    return FormalReleaseProofRequest(
        source_root=tmp_path / "source",
        formal_data_root=tmp_path / "asteria-data",
        temp_root=tmp_path / "asteria-temp",
        report_root=tmp_path / "asteria-report",
        validated_root=tmp_path / "Asteria-Validated",
        run_id=RUN_ID,
        mode=mode,
        allow_formal_data_write=allow_formal_data_write,
    )


def _write_formal_release_manifest(tmp_path: Path, *, source_db_root: Path | None = None) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir(parents=True, exist_ok=True)
    payload = {
        "proof_scope": "formal_release",
        "sample_proof": False,
        "full_rebuild_proof": "passed",
        "daily_incremental_release_proof": "passed",
        "resume_idempotence_proof": "passed",
        "source_db_root": str(source_db_root or source_root / "formal-dbs"),
        "known_limits": ["fill_ledger remains source-bound"],
    }
    (source_root / "formal-release-proof-manifest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def test_audit_only_reads_formal_dbs_without_writing_formal_data(tmp_path: Path) -> None:
    _write_db(tmp_path / "asteria-data" / "pipeline.duckdb")

    summary = run_formal_release_proof(_request(tmp_path))

    assert summary.card_id == FORMAL_RELEASE_PROOF_CARD
    assert summary.status == "blocked / formal release proof not executed"
    assert summary.mode == "audit-only"
    assert summary.boundaries["formal_data_mutation"] is False
    assert summary.db_count == 1
    assert "pipeline.duckdb" in summary.db_manifest["databases"]
    assert Path(summary.db_manifest_path).exists()
    assert Path(summary.summary_path).exists()
    assert (tmp_path / "asteria-data" / "formal-data-backup").exists() is False


def test_release_proof_blocks_without_explicit_formal_write_flag(tmp_path: Path) -> None:
    _write_db(tmp_path / "asteria-data" / "pipeline.duckdb")

    summary = run_formal_release_proof(_request(tmp_path, mode="release-proof"))

    assert summary.status == "blocked / formal data write not authorized"
    assert summary.decisions["formal_data_write_authorized"] == "blocked"
    assert summary.boundaries["formal_data_mutation"] is False
    assert Path(summary.backup_manifest_path).exists() is False
    assert Path(summary.promote_manifest_path).exists() is False


def test_release_proof_staging_failure_does_not_promote(tmp_path: Path) -> None:
    formal_db = tmp_path / "asteria-data" / "pipeline.duckdb"
    _write_db(formal_db, value="original")
    missing_source_root = tmp_path / "source" / "missing-formal-dbs"
    _write_formal_release_manifest(tmp_path, source_db_root=missing_source_root)

    summary = run_formal_release_proof(
        _request(tmp_path, mode="release-proof", allow_formal_data_write=True)
    )

    assert summary.status == "blocked / staging rebuild failed"
    assert summary.decisions["staging_rebuild"] == "blocked"
    assert summary.decisions["formal_promote"] == "skipped"
    assert Path(summary.backup_manifest_path).exists()
    assert Path(summary.promote_manifest_path).exists()
    promote = json.loads(Path(summary.promote_manifest_path).read_text(encoding="utf-8"))
    assert promote["status"] == "skipped"
    with duckdb.connect(str(formal_db), read_only=True) as con:
        assert con.execute("select value from facts").fetchone() == ("original",)


def test_release_proof_promotes_staged_formal_dbs_and_writes_final_evidence(
    tmp_path: Path,
) -> None:
    _write_db(tmp_path / "asteria-data" / "pipeline.duckdb", value="old")
    source_db_root = tmp_path / "source" / "formal-dbs"
    _write_db(source_db_root / "pipeline.duckdb", value="new")
    _write_formal_release_manifest(tmp_path, source_db_root=source_db_root)

    summary = run_formal_release_proof(
        _request(tmp_path, mode="release-proof", allow_formal_data_write=True)
    )

    assert summary.status == "passed / formal release evidence complete"
    assert summary.boundaries["formal_data_mutation"] is True
    assert summary.decisions["formal_full_rebuild_proof"] == "passed"
    assert summary.decisions["daily_incremental_release_proof"] == "passed"
    assert summary.decisions["resume_idempotence_proof"] == "passed"
    assert Path(summary.final_release_evidence_path).exists()
    final_evidence = json.loads(
        Path(summary.final_release_evidence_path).read_text(encoding="utf-8")
    )
    assert "pipeline.duckdb" in final_evidence["db_manifest"]["databases"]
    assert final_evidence["schema_versions"]["pipeline.duckdb"]["schema_version"]
    assert final_evidence["rule_versions"]["pipeline.duckdb"]["rule_version"]
    assert final_evidence["row_counts"]["pipeline.duckdb"]["facts"] == 1
    assert final_evidence["audit_summaries"]["status"] == "passed"
    assert final_evidence["known_limits"] == ["fill_ledger remains source-bound"]
    with duckdb.connect(str(tmp_path / "asteria-data" / "pipeline.duckdb"), read_only=True) as con:
        assert con.execute("select value from facts").fetchone() == ("new",)


def test_resume_reuses_promoted_manifest_without_duplicate_promote(tmp_path: Path) -> None:
    _write_db(tmp_path / "asteria-data" / "pipeline.duckdb", value="old")
    source_db_root = tmp_path / "source" / "formal-dbs"
    _write_db(source_db_root / "pipeline.duckdb", value="new")
    _write_formal_release_manifest(tmp_path, source_db_root=source_db_root)
    request = _request(tmp_path, mode="release-proof", allow_formal_data_write=True)
    first = run_formal_release_proof(request)

    resumed = run_formal_release_proof(
        _request(tmp_path, mode="resume", allow_formal_data_write=True)
    )

    assert first.status == "passed / formal release evidence complete"
    assert resumed.status == "passed / formal release evidence complete"
    assert resumed.resume_reused is True
    resume_manifest = json.loads(
        Path(resumed.resume_idempotence_manifest_path).read_text(encoding="utf-8")
    )
    assert resume_manifest["promote_reused"] is True
    assert resume_manifest["promote_attempt_count"] == 1
    assert resumed.manifest_hashes == first.manifest_hashes


def test_formal_release_proof_cli_defaults_to_external_roots() -> None:
    args = build_parser().parse_args([])
    request = _request_from_args(args)

    assert request.source_root == Path("H:/tdx_offline_Data")
    assert request.formal_data_root == Path("H:/Asteria-data")
    assert request.temp_root == Path("H:/Asteria-temp")
    assert request.report_root == Path("H:/Asteria-report")
    assert request.validated_root == Path("H:/Asteria-Validated")
    assert request.mode == "audit-only"
    assert request.run_id == RUN_ID
    assert request.allow_formal_data_write is False
