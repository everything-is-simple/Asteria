from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2
from typing import Any

import duckdb

from asteria.signal.audit_engine import build_signal_audit_rows
from asteria.signal.bootstrap_constants import SIGNAL_FAMILIES, SIGNAL_FAMILY_DATABASES
from asteria.signal.contracts import (
    SIGNAL_RULE_VERSION,
    SIGNAL_SCHEMA_VERSION,
    SignalBuildRequest,
    SignalBuildSummary,
)
from asteria.signal.rules import AlphaCandidate, build_signal_rows, candidate_from_row
from asteria.signal.schema import bootstrap_signal_database


def run_signal_build(request: SignalBuildRequest) -> SignalBuildSummary:
    checkpoint = _load_completed_checkpoint(request, "build")
    if checkpoint:
        return checkpoint
    if request.mode == "audit-only":
        return run_signal_audit(request)

    candidates = _load_alpha_candidates(request)
    created_at = _utc_now()
    signal_rows = build_signal_rows(candidates, request, created_at)
    bootstrap_signal_database(request.target_signal_db)
    with duckdb.connect(str(request.target_signal_db)) as con:
        con.execute("begin transaction")
        _delete_run(con, request.run_id)
        con.execute(
            "delete from signal_schema_version where schema_version = ?",
            [request.schema_version],
        )
        con.execute(
            "delete from signal_rule_version where signal_rule_version = ?",
            [request.signal_rule_version],
        )
        con.execute(
            "insert into signal_schema_version values (?, ?)",
            [request.schema_version, created_at],
        )
        con.execute(
            "insert into signal_rule_version values (?, ?, ?)",
            [request.signal_rule_version, "alpha_candidate_aggregation", created_at],
        )
        con.executemany(
            """
            insert into signal_input_snapshot
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            signal_rows.snapshots,
        )
        con.executemany(
            """
            insert into formal_signal_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            signal_rows.signals,
        )
        con.executemany(
            "insert into signal_component_ledger values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            signal_rows.components,
        )
        con.execute(
            """
            insert into signal_run
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                request.run_id,
                "signal_build",
                request.mode,
                request.timeframe,
                "completed",
                str(request.source_alpha_root),
                len(signal_rows.snapshots),
                len(signal_rows.signals),
                len(signal_rows.components),
                0,
                request.schema_version,
                request.signal_rule_version,
                request.source_alpha_release_version,
                created_at,
            ],
        )
        con.execute("commit")

    audit = run_signal_audit(request)
    summary = SignalBuildSummary(
        run_id=request.run_id,
        stage="build",
        status="completed" if audit.hard_fail_count == 0 else "failed",
        input_candidate_count=len(signal_rows.snapshots),
        formal_signal_count=len(signal_rows.signals),
        component_count=len(signal_rows.components),
        hard_fail_count=audit.hard_fail_count,
        report_path=audit.report_path,
    )
    _save_checkpoint(request.checkpoint_path("build"), summary)
    return summary


def run_signal_audit(request: SignalBuildRequest) -> SignalBuildSummary:
    bootstrap_signal_database(request.target_signal_db)
    created_at = _utc_now()
    audit_rows, payload = build_signal_audit_rows(request, created_at)
    with duckdb.connect(str(request.target_signal_db)) as con:
        con.execute("begin transaction")
        con.execute("delete from signal_audit where run_id = ?", [request.run_id])
        con.executemany("insert into signal_audit values (?, ?, ?, ?, ?, ?, ?, ?)", audit_rows)
        con.execute("commit")

    report_path = _report_path(request.report_root, request.run_id)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = SignalBuildSummary(
        run_id=request.run_id,
        stage="audit",
        status="completed" if payload["hard_fail_count"] == 0 else "failed",
        input_candidate_count=int(payload["input_candidate_count"]),
        formal_signal_count=int(payload["formal_signal_count"]),
        component_count=int(payload["component_count"]),
        hard_fail_count=int(payload["hard_fail_count"]),
        report_path=str(report_path),
    )
    _save_checkpoint(request.checkpoint_path("audit"), summary)
    return summary


def run_signal_bounded_proof(
    source_alpha_root: Path,
    target_signal_db: Path,
    report_root: Path,
    validated_root: Path,
    temp_root: Path,
    run_id: str,
    source_alpha_release_version: str,
    start_dt: str | None,
    end_dt: str | None,
    symbol_limit: int | None,
    schema_version: str = SIGNAL_SCHEMA_VERSION,
    signal_rule_version: str = SIGNAL_RULE_VERSION,
    mode: str = "bounded",
) -> SignalBuildSummary:
    request = SignalBuildRequest(
        source_alpha_root=source_alpha_root,
        target_signal_db=target_signal_db,
        report_root=report_root,
        validated_root=validated_root,
        temp_root=temp_root,
        run_id=run_id,
        mode=mode,
        source_alpha_release_version=source_alpha_release_version,
        schema_version=schema_version,
        signal_rule_version=signal_rule_version,
        start_dt=start_dt,
        end_dt=end_dt,
        symbol_limit=symbol_limit,
    )
    summary = run_signal_build(request)
    evidence = _write_bounded_proof_evidence(request, summary)
    return SignalBuildSummary(**{**summary.as_dict(), **evidence})


def _load_alpha_candidates(request: SignalBuildRequest) -> list[AlphaCandidate]:
    candidates: list[AlphaCandidate] = []
    for family in SIGNAL_FAMILIES:
        db_path = request.source_alpha_root / SIGNAL_FAMILY_DATABASES[family]
        if not db_path.exists():
            raise FileNotFoundError(f"Missing Alpha family DB: {db_path}")
        clauses = ["timeframe = ?", "alpha_family = ?"]
        params: list[object] = [request.timeframe, family]
        if request.start_date:
            clauses.append("bar_dt >= ?")
            params.append(request.start_date)
        if request.end_date:
            clauses.append("bar_dt <= ?")
            params.append(request.end_date)
        symbol_limit = ""
        if request.symbol_limit is not None:
            symbol_limit = """
            and symbol in (
                select symbol
                from alpha_signal_candidate
                where timeframe = ? and alpha_family = ?
                group by symbol
                order by symbol
                limit ?
            )
            """
            params.extend([request.timeframe, family, request.symbol_limit])
        query = f"""
            select alpha_candidate_id, alpha_event_id, alpha_family, symbol, timeframe,
                   bar_dt, candidate_type, candidate_state, opportunity_bias,
                   confidence_bucket, reason_code, candidate_score,
                   source_malf_service_version, run_id, alpha_rule_version
            from alpha_signal_candidate
            where {" and ".join(clauses)}
            {symbol_limit}
            order by symbol, bar_dt, alpha_family, alpha_candidate_id
        """
        with duckdb.connect(str(db_path), read_only=True) as con:
            rows = con.execute(query, params).fetchall()
            candidates.extend(candidate_from_row(row) for row in rows)
    return sorted(
        candidates,
        key=lambda row: (row.symbol, row.timeframe, row.bar_dt, row.alpha_family),
    )


def _delete_run(con: duckdb.DuckDBPyConnection, run_id: str) -> None:
    for table in [
        "signal_run",
        "signal_input_snapshot",
        "formal_signal_ledger",
        "signal_component_ledger",
        "signal_audit",
    ]:
        column = "signal_run_id" if table == "signal_input_snapshot" else "run_id"
        if table == "signal_component_ledger":
            column = "signal_run_id"
        con.execute(f"delete from {table} where {column} = ?", [run_id])


def _write_bounded_proof_evidence(
    request: SignalBuildRequest,
    summary: SignalBuildSummary,
) -> dict[str, str]:
    report_dir = request.report_root / "signal" / _utc_now().date().isoformat() / request.run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": request.run_id,
        "module": "signal",
        "stage": "bounded_proof",
        "status": "passed" if summary.hard_fail_count == 0 else "failed",
        "hard_fail_count": summary.hard_fail_count,
        "input_candidate_count": summary.input_candidate_count,
        "formal_signal_count": summary.formal_signal_count,
        "component_count": summary.component_count,
        "source_alpha_release_version": request.source_alpha_release_version,
        "target_signal_db": str(request.target_signal_db),
        "generated_at": _utc_now().isoformat(),
    }
    manifest_path = report_dir / "manifest.json"
    closeout_path = report_dir / "closeout.md"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    closeout_path.write_text(_closeout_text(manifest), encoding="utf-8")
    zip_path = request.validated_root / f"Asteria-{request.run_id}.zip"
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(manifest_path, manifest_path.name)
        archive.write(closeout_path, closeout_path.name)
        if summary.report_path and Path(summary.report_path).exists():
            archive.write(Path(summary.report_path), f"audit/{Path(summary.report_path).name}")
    copy2(manifest_path, report_dir / f"{request.run_id}-summary.json")
    return {
        "manifest_path": str(manifest_path),
        "closeout_path": str(closeout_path),
        "validated_zip": str(zip_path),
    }


def _closeout_text(manifest: dict[str, Any]) -> str:
    lines = [
        f"# Signal bounded proof closeout: {manifest['run_id']}",
        "",
        f"- status: {manifest['status']}",
        f"- hard_fail_count: {manifest['hard_fail_count']}",
        f"- input_candidate_count: {manifest['input_candidate_count']}",
        f"- formal_signal_count: {manifest['formal_signal_count']}",
        f"- component_count: {manifest['component_count']}",
        "- forbidden downstream scope: Position / Portfolio / Trade / System / Pipeline",
    ]
    return "\n".join(lines) + "\n"


def _report_path(report_root: Path, run_id: str) -> Path:
    return report_root / "signal" / _utc_now().date().isoformat() / f"{run_id}-audit-summary.json"


def _load_completed_checkpoint(
    request: SignalBuildRequest,
    stage: str,
) -> SignalBuildSummary | None:
    if request.mode != "resume":
        return None
    checkpoint = _load_checkpoint(request.checkpoint_path(stage))
    if checkpoint and checkpoint.get("status") == "completed":
        summary = SignalBuildSummary(**checkpoint["summary"])
        return SignalBuildSummary(**{**summary.as_dict(), "resume_reused": True})
    return None


def _load_checkpoint(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _save_checkpoint(path: Path, summary: SignalBuildSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": summary.status,
        "summary": summary.as_dict(),
        "created_at": _utc_now().isoformat(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
