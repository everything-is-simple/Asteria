from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2
from typing import Any

import duckdb

from asteria.portfolio_plan.audit_engine import build_portfolio_plan_audit_rows
from asteria.portfolio_plan.contracts import (
    PORTFOLIO_PLAN_RULE_VERSION,
    PORTFOLIO_PLAN_SCHEMA_VERSION,
    PortfolioPlanBuildRequest,
    PortfolioPlanBuildSummary,
)
from asteria.portfolio_plan.rules import (
    PositionPlanInput,
    build_portfolio_plan_rows,
    position_input_from_row,
)
from asteria.portfolio_plan.schema import bootstrap_portfolio_plan_database


def run_portfolio_plan_build(
    request: PortfolioPlanBuildRequest,
) -> PortfolioPlanBuildSummary:
    checkpoint = _load_completed_checkpoint(request, "build")
    if checkpoint:
        return checkpoint
    if request.mode == "audit-only":
        return run_portfolio_plan_audit(request)
    if _target_contains_run(request):
        raise ValueError(f"target portfolio_plan.duckdb already contains run_id: {request.run_id}")

    positions = _load_position_inputs(request)
    created_at = _utc_now()
    portfolio_rows = build_portfolio_plan_rows(positions, request, created_at)
    staging_db = request.staging_db_path
    if staging_db.exists():
        staging_db.unlink()
    bootstrap_portfolio_plan_database(staging_db)
    with duckdb.connect(str(staging_db)) as con:
        con.execute("begin transaction")
        _delete_run(con, request)
        con.execute(
            "delete from portfolio_plan_schema_version where schema_version = ?",
            [request.schema_version],
        )
        con.execute(
            """
            delete from portfolio_plan_rule_version
            where portfolio_plan_rule_version = ?
            """,
            [request.portfolio_plan_rule_version],
        )
        con.execute(
            "insert into portfolio_plan_schema_version values (?, ?)",
            [request.schema_version, created_at],
        )
        con.execute(
            "insert into portfolio_plan_rule_version values (?, ?, ?, ?)",
            [
                request.portfolio_plan_rule_version,
                "position_capacity_admission",
                request.max_active_symbols,
                created_at,
            ],
        )
        con.executemany(
            """
            insert into portfolio_position_snapshot
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            portfolio_rows.snapshots,
        )
        con.executemany(
            """
            insert into portfolio_constraint_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            portfolio_rows.constraints,
        )
        con.executemany(
            """
            insert into portfolio_admission_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            portfolio_rows.admissions,
        )
        con.executemany(
            """
            insert into portfolio_target_exposure
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            portfolio_rows.exposures,
        )
        con.executemany(
            """
            insert into portfolio_trim_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            portfolio_rows.trims,
        )
        con.execute(
            """
            insert into portfolio_plan_run
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                request.run_id,
                "portfolio_plan_build",
                request.mode,
                request.timeframe,
                "staged",
                str(request.source_position_db),
                len(portfolio_rows.snapshots),
                len(portfolio_rows.admissions),
                len(portfolio_rows.exposures),
                len(portfolio_rows.trims),
                0,
                request.schema_version,
                request.portfolio_plan_rule_version,
                request.source_position_release_version,
                request.source_position_run_id,
                created_at,
            ],
        )
        con.execute("commit")

    audit = _run_portfolio_plan_audit_on_db(request, staging_db)
    status = "completed" if audit.hard_fail_count == 0 else "failed"
    if audit.hard_fail_count == 0:
        _promote_staging_db(request, staging_db)
    summary = PortfolioPlanBuildSummary(
        run_id=request.run_id,
        stage="build",
        status=status,
        timeframe=request.timeframe,
        input_position_count=len(portfolio_rows.snapshots),
        admission_count=len(portfolio_rows.admissions),
        target_exposure_count=len(portfolio_rows.exposures),
        trim_count=len(portfolio_rows.trims),
        hard_fail_count=audit.hard_fail_count,
        report_path=audit.report_path,
    )
    _save_checkpoint(request.checkpoint_path("build"), summary)
    return summary


def run_portfolio_plan_audit(
    request: PortfolioPlanBuildRequest,
) -> PortfolioPlanBuildSummary:
    return _run_portfolio_plan_audit_on_db(request, request.target_portfolio_plan_db)


def run_portfolio_plan_bounded_proof(
    source_position_db: Path,
    target_portfolio_plan_db: Path,
    report_root: Path,
    validated_root: Path,
    temp_root: Path,
    run_id: str,
    source_position_release_version: str,
    source_position_run_id: str | None,
    start_dt: str | None,
    end_dt: str | None,
    symbol_limit: int | None,
    schema_version: str = PORTFOLIO_PLAN_SCHEMA_VERSION,
    portfolio_plan_rule_version: str = PORTFOLIO_PLAN_RULE_VERSION,
    mode: str = "bounded",
) -> PortfolioPlanBuildSummary:
    request = PortfolioPlanBuildRequest(
        source_position_db=source_position_db,
        target_portfolio_plan_db=target_portfolio_plan_db,
        report_root=report_root,
        validated_root=validated_root,
        temp_root=temp_root,
        run_id=run_id,
        mode=mode,
        source_position_release_version=source_position_release_version,
        source_position_run_id=source_position_run_id,
        schema_version=schema_version,
        portfolio_plan_rule_version=portfolio_plan_rule_version,
        start_dt=start_dt,
        end_dt=end_dt,
        symbol_limit=symbol_limit,
    )
    summary = run_portfolio_plan_build(request)
    evidence = _write_bounded_proof_evidence(request, summary)
    return PortfolioPlanBuildSummary(**{**summary.as_dict(), **evidence})


def _run_portfolio_plan_audit_on_db(
    request: PortfolioPlanBuildRequest,
    audit_db_path: Path,
) -> PortfolioPlanBuildSummary:
    created_at = _utc_now()
    audit_rows, payload = build_portfolio_plan_audit_rows(request, created_at, audit_db_path)
    if audit_db_path.exists():
        with duckdb.connect(str(audit_db_path)) as con:
            con.execute("begin transaction")
            con.execute(
                "delete from portfolio_plan_audit where audit_id like ?",
                [f"{request.run_id}|{request.timeframe}|%"],
            )
            con.executemany(
                "insert into portfolio_plan_audit values (?, ?, ?, ?, ?, ?, ?, ?)",
                audit_rows,
            )
            con.execute(
                """
                update portfolio_plan_run
                set hard_fail_count = ?, status = ?
                where run_id = ?
                """,
                [
                    payload["hard_fail_count"],
                    "completed" if payload["hard_fail_count"] == 0 else "failed",
                    request.run_id,
                ],
            )
            con.execute("commit")

    report_path = _report_path(request.report_root, request.run_id, request.timeframe)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = PortfolioPlanBuildSummary(
        run_id=request.run_id,
        stage="audit",
        status="completed" if payload["hard_fail_count"] == 0 else "failed",
        timeframe=request.timeframe,
        input_position_count=int(payload["input_position_count"]),
        admission_count=int(payload["admission_count"]),
        target_exposure_count=int(payload["target_exposure_count"]),
        trim_count=int(payload["trim_count"]),
        hard_fail_count=int(payload["hard_fail_count"]),
        report_path=str(report_path),
    )
    _save_checkpoint(request.checkpoint_path("audit"), summary)
    return summary


def _load_position_inputs(request: PortfolioPlanBuildRequest) -> list[PositionPlanInput]:
    if not request.source_position_db.exists():
        raise FileNotFoundError(f"Missing Position DB: {request.source_position_db}")
    clauses = ["c.timeframe = ?"]
    params: list[object] = [request.timeframe]
    if request.source_position_run_id:
        clauses.append("c.run_id = ?")
        params.append(request.source_position_run_id)
    if request.start_date:
        clauses.append("c.candidate_dt >= ?")
        params.append(request.start_date)
    if request.end_date:
        clauses.append("c.candidate_dt <= ?")
        params.append(request.end_date)
    symbol_limit = ""
    if request.symbol_limit is not None:
        source_run_clause = ""
        source_run_params: list[object] = []
        if request.source_position_run_id:
            source_run_clause = " and run_id = ?"
            source_run_params.append(request.source_position_run_id)
        symbol_limit = f"""
        and c.symbol in (
            select symbol
            from position_candidate_ledger
            where timeframe = ?
            {source_run_clause}
            group by symbol
            order by symbol
            limit ?
        )
        """
        params.extend([request.timeframe, *source_run_params, request.symbol_limit])
    query = f"""
        select c.position_candidate_id, c.signal_id, c.symbol, c.timeframe,
               c.candidate_dt, c.candidate_type, c.candidate_state,
               c.position_bias, c.reason_code, c.run_id, c.position_rule_version,
               e.entry_plan_id, x.exit_plan_id
        from position_candidate_ledger c
        left join position_entry_plan e
          on c.position_candidate_id = e.position_candidate_id
        left join position_exit_plan x
          on c.position_candidate_id = x.position_candidate_id
        where {" and ".join(clauses)}
        {symbol_limit}
        order by c.symbol, c.candidate_dt, c.position_candidate_id
    """
    with duckdb.connect(str(request.source_position_db), read_only=True) as con:
        rows = con.execute(query, params).fetchall()
    return [position_input_from_row(row) for row in rows]


def _delete_run(con: duckdb.DuckDBPyConnection, request: PortfolioPlanBuildRequest) -> None:
    con.execute("delete from portfolio_trim_ledger where run_id = ?", [request.run_id])
    con.execute("delete from portfolio_target_exposure where run_id = ?", [request.run_id])
    con.execute("delete from portfolio_admission_ledger where run_id = ?", [request.run_id])
    con.execute("delete from portfolio_constraint_ledger where run_id = ?", [request.run_id])
    con.execute(
        "delete from portfolio_position_snapshot where portfolio_run_id = ?",
        [request.run_id],
    )
    con.execute("delete from portfolio_plan_run where run_id = ?", [request.run_id])
    con.execute(
        "delete from portfolio_plan_audit where audit_id like ?",
        [f"{request.run_id}|{request.timeframe}|%"],
    )


def _promote_staging_db(request: PortfolioPlanBuildRequest, staging_db: Path) -> None:
    if _target_contains_run(request):
        raise ValueError(f"target portfolio_plan.duckdb already contains run_id: {request.run_id}")
    request.target_portfolio_plan_db.parent.mkdir(parents=True, exist_ok=True)
    copy2(staging_db, request.target_portfolio_plan_db)


def _target_contains_run(request: PortfolioPlanBuildRequest) -> bool:
    if not request.target_portfolio_plan_db.exists():
        return False
    with duckdb.connect(str(request.target_portfolio_plan_db), read_only=True) as con:
        tables = {
            str(row[0])
            for row in con.execute(
                "select table_name from information_schema.tables where table_schema = 'main'"
            ).fetchall()
        }
        if "portfolio_plan_run" not in tables:
            return False
        row = con.execute(
            "select count(*) from portfolio_plan_run where run_id = ?",
            [request.run_id],
        ).fetchone()
    return False if row is None else int(row[0]) > 0


def _write_bounded_proof_evidence(
    request: PortfolioPlanBuildRequest,
    summary: PortfolioPlanBuildSummary,
) -> dict[str, str]:
    report_dir = (
        request.report_root / "portfolio_plan" / _utc_now().date().isoformat() / request.run_id
    )
    report_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": request.run_id,
        "module": "portfolio_plan",
        "stage": "bounded_proof",
        "status": "passed" if summary.hard_fail_count == 0 else "failed",
        "hard_fail_count": summary.hard_fail_count,
        "input_position_count": summary.input_position_count,
        "admission_count": summary.admission_count,
        "target_exposure_count": summary.target_exposure_count,
        "trim_count": summary.trim_count,
        "source_position_release_version": request.source_position_release_version,
        "source_position_run_id": request.source_position_run_id,
        "target_portfolio_plan_db": str(request.target_portfolio_plan_db),
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
        f"# Portfolio Plan bounded proof closeout: {manifest['run_id']}",
        "",
        f"- status: {manifest['status']}",
        f"- hard_fail_count: {manifest['hard_fail_count']}",
        f"- input_position_count: {manifest['input_position_count']}",
        f"- admission_count: {manifest['admission_count']}",
        f"- target_exposure_count: {manifest['target_exposure_count']}",
        f"- trim_count: {manifest['trim_count']}",
        "- forbidden downstream scope: Trade / System / Pipeline",
    ]
    return "\n".join(lines) + "\n"


def _report_path(report_root: Path, run_id: str, timeframe: str) -> Path:
    return (
        report_root
        / "portfolio_plan"
        / _utc_now().date().isoformat()
        / f"{run_id}-{timeframe}-audit-summary.json"
    )


def _load_completed_checkpoint(
    request: PortfolioPlanBuildRequest,
    stage: str,
) -> PortfolioPlanBuildSummary | None:
    if request.mode != "resume":
        return None
    checkpoint = _load_checkpoint(request.checkpoint_path(stage))
    if checkpoint and checkpoint.get("status") == "completed":
        summary = PortfolioPlanBuildSummary(**checkpoint["summary"])
        return PortfolioPlanBuildSummary(**{**summary.as_dict(), "resume_reused": True})
    return None


def _load_checkpoint(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _save_checkpoint(path: Path, summary: PortfolioPlanBuildSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": summary.status,
        "summary": summary.as_dict(),
        "created_at": _utc_now().isoformat(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
