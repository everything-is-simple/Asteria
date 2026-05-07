from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2
from typing import Any

import duckdb

from asteria.position.audit_engine import build_position_audit_rows
from asteria.position.contracts import (
    POSITION_RULE_VERSION,
    POSITION_SCHEMA_VERSION,
    PositionBuildRequest,
    PositionBuildSummary,
)
from asteria.position.rules import SignalInput, build_position_rows, signal_from_row
from asteria.position.schema import bootstrap_position_database


def run_position_build(request: PositionBuildRequest) -> PositionBuildSummary:
    checkpoint = _load_completed_checkpoint(request, "build")
    if checkpoint:
        return checkpoint
    if request.mode == "audit-only":
        return run_position_audit(request)

    signals = _load_signals(request)
    created_at = _utc_now()
    position_rows = build_position_rows(signals, request, created_at)
    bootstrap_position_database(request.target_position_db)
    with duckdb.connect(str(request.target_position_db)) as con:
        con.execute("begin transaction")
        _delete_run(con, request)
        con.execute(
            "delete from position_schema_version where schema_version = ?",
            [request.schema_version],
        )
        con.execute(
            "delete from position_rule_version where position_rule_version = ?",
            [request.position_rule_version],
        )
        con.execute(
            "insert into position_schema_version values (?, ?)",
            [request.schema_version, created_at],
        )
        con.execute(
            "insert into position_rule_version values (?, ?, ?)",
            [request.position_rule_version, "signal_to_position_plan", created_at],
        )
        con.executemany(
            """
            insert into position_signal_snapshot
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            position_rows.snapshots,
        )
        con.executemany(
            """
            insert into position_candidate_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            position_rows.candidates,
        )
        con.executemany(
            "insert into position_entry_plan values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            position_rows.entries,
        )
        con.executemany(
            "insert into position_exit_plan values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            position_rows.exits,
        )
        con.execute(
            "insert into position_run values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                request.run_id,
                "position_build",
                request.mode,
                request.timeframe,
                "completed",
                str(request.source_signal_db),
                len(position_rows.snapshots),
                len(position_rows.candidates),
                len(position_rows.entries),
                len(position_rows.exits),
                0,
                request.schema_version,
                request.position_rule_version,
                request.source_signal_release_version,
                request.source_signal_run_id,
                created_at,
            ],
        )
        con.execute("commit")

    audit = run_position_audit(request)
    summary = PositionBuildSummary(
        run_id=request.run_id,
        stage="build",
        status="completed" if audit.hard_fail_count == 0 else "failed",
        timeframe=request.timeframe,
        input_signal_count=len(position_rows.snapshots),
        position_candidate_count=len(position_rows.candidates),
        entry_plan_count=len(position_rows.entries),
        exit_plan_count=len(position_rows.exits),
        hard_fail_count=audit.hard_fail_count,
        report_path=audit.report_path,
    )
    _save_checkpoint(request.checkpoint_path("build"), summary)
    return summary


def run_position_audit(request: PositionBuildRequest) -> PositionBuildSummary:
    bootstrap_position_database(request.target_position_db)
    created_at = _utc_now()
    audit_rows, payload = build_position_audit_rows(request, created_at)
    with duckdb.connect(str(request.target_position_db)) as con:
        con.execute("begin transaction")
        con.execute(
            "delete from position_audit where audit_id like ?",
            [f"{request.run_id}|{request.timeframe}|%"],
        )
        con.executemany("insert into position_audit values (?, ?, ?, ?, ?, ?, ?, ?)", audit_rows)
        con.execute("commit")

    report_path = _report_path(request.report_root, request.run_id, request.timeframe)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = PositionBuildSummary(
        run_id=request.run_id,
        stage="audit",
        status="completed" if payload["hard_fail_count"] == 0 else "failed",
        timeframe=request.timeframe,
        input_signal_count=int(payload["input_signal_count"]),
        position_candidate_count=int(payload["position_candidate_count"]),
        entry_plan_count=int(payload["entry_plan_count"]),
        exit_plan_count=int(payload["exit_plan_count"]),
        hard_fail_count=int(payload["hard_fail_count"]),
        report_path=str(report_path),
    )
    _save_checkpoint(request.checkpoint_path("audit"), summary)
    return summary


def run_position_bounded_proof(
    source_signal_db: Path,
    target_position_db: Path,
    report_root: Path,
    validated_root: Path,
    temp_root: Path,
    run_id: str,
    source_signal_release_version: str,
    source_signal_run_id: str | None,
    start_dt: str | None,
    end_dt: str | None,
    symbol_limit: int | None,
    schema_version: str = POSITION_SCHEMA_VERSION,
    position_rule_version: str = POSITION_RULE_VERSION,
    mode: str = "bounded",
) -> PositionBuildSummary:
    request = PositionBuildRequest(
        source_signal_db=source_signal_db,
        target_position_db=target_position_db,
        report_root=report_root,
        validated_root=validated_root,
        temp_root=temp_root,
        run_id=run_id,
        mode=mode,
        source_signal_release_version=source_signal_release_version,
        source_signal_run_id=source_signal_run_id,
        schema_version=schema_version,
        position_rule_version=position_rule_version,
        start_dt=start_dt,
        end_dt=end_dt,
        symbol_limit=symbol_limit,
    )
    summary = run_position_build(request)
    evidence = _write_bounded_proof_evidence(request, summary)
    return PositionBuildSummary(**{**summary.as_dict(), **evidence})


def _load_signals(request: PositionBuildRequest) -> list[SignalInput]:
    if not request.source_signal_db.exists():
        raise FileNotFoundError(f"Missing Signal DB: {request.source_signal_db}")
    clauses = ["timeframe = ?"]
    params: list[object] = [request.timeframe]
    if request.source_signal_run_id:
        clauses.append("run_id = ?")
        params.append(request.source_signal_run_id)
    if request.start_date:
        clauses.append("signal_dt >= ?")
        params.append(request.start_date)
    if request.end_date:
        clauses.append("signal_dt <= ?")
        params.append(request.end_date)
    symbol_limit = ""
    if request.symbol_limit is not None:
        source_run_clause = ""
        source_run_params: list[object] = []
        if request.source_signal_run_id:
            source_run_clause = " and run_id = ?"
            source_run_params.append(request.source_signal_run_id)
        symbol_limit = f"""
        and symbol in (
            select symbol
            from formal_signal_ledger
            where timeframe = ?
            {source_run_clause}
            group by symbol
            order by symbol
            limit ?
        )
        """
        params.extend([request.timeframe, *source_run_params, request.symbol_limit])
    query = f"""
        select signal_id, symbol, timeframe, signal_dt, signal_type, signal_state,
               signal_bias, signal_strength, confidence_bucket, reason_code,
               source_alpha_release_version, run_id, schema_version, signal_rule_version
        from formal_signal_ledger
        where {" and ".join(clauses)}
        {symbol_limit}
        order by symbol, signal_dt, signal_id
    """
    with duckdb.connect(str(request.source_signal_db), read_only=True) as con:
        rows = con.execute(query, params).fetchall()
    return [signal_from_row(row) for row in rows]


def _delete_run(con: duckdb.DuckDBPyConnection, request: PositionBuildRequest) -> None:
    con.execute("delete from position_exit_plan where run_id = ?", [request.run_id])
    con.execute("delete from position_entry_plan where run_id = ?", [request.run_id])
    con.execute("delete from position_candidate_ledger where run_id = ?", [request.run_id])
    con.execute(
        "delete from position_signal_snapshot where position_run_id = ?",
        [request.run_id],
    )
    con.execute("delete from position_run where run_id = ?", [request.run_id])
    con.execute(
        "delete from position_audit where audit_id like ?",
        [f"{request.run_id}|{request.timeframe}|%"],
    )


def _write_bounded_proof_evidence(
    request: PositionBuildRequest,
    summary: PositionBuildSummary,
) -> dict[str, str]:
    report_dir = request.report_root / "position" / _utc_now().date().isoformat() / request.run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": request.run_id,
        "module": "position",
        "stage": "bounded_proof",
        "status": "passed" if summary.hard_fail_count == 0 else "failed",
        "hard_fail_count": summary.hard_fail_count,
        "input_signal_count": summary.input_signal_count,
        "position_candidate_count": summary.position_candidate_count,
        "entry_plan_count": summary.entry_plan_count,
        "exit_plan_count": summary.exit_plan_count,
        "source_signal_release_version": request.source_signal_release_version,
        "source_signal_run_id": request.source_signal_run_id,
        "target_position_db": str(request.target_position_db),
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
        f"# Position bounded proof closeout: {manifest['run_id']}",
        "",
        f"- status: {manifest['status']}",
        f"- hard_fail_count: {manifest['hard_fail_count']}",
        f"- input_signal_count: {manifest['input_signal_count']}",
        f"- position_candidate_count: {manifest['position_candidate_count']}",
        f"- entry_plan_count: {manifest['entry_plan_count']}",
        f"- exit_plan_count: {manifest['exit_plan_count']}",
        "- forbidden downstream scope: Portfolio Plan / Trade / System / Pipeline",
    ]
    return "\n".join(lines) + "\n"


def _report_path(report_root: Path, run_id: str, timeframe: str) -> Path:
    return (
        report_root
        / "position"
        / _utc_now().date().isoformat()
        / f"{run_id}-{timeframe}-audit-summary.json"
    )


def _load_completed_checkpoint(
    request: PositionBuildRequest,
    stage: str,
) -> PositionBuildSummary | None:
    if request.mode != "resume":
        return None
    checkpoint = _load_checkpoint(request.checkpoint_path(stage))
    if checkpoint and checkpoint.get("status") == "completed":
        summary = PositionBuildSummary(**checkpoint["summary"])
        return PositionBuildSummary(**{**summary.as_dict(), "resume_reused": True})
    return None


def _load_checkpoint(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _save_checkpoint(path: Path, summary: PositionBuildSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": summary.status,
        "summary": summary.as_dict(),
        "created_at": _utc_now().isoformat(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
