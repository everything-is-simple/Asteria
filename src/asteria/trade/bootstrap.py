from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2
from typing import Any

import duckdb

from asteria.trade.audit_engine import build_trade_audit_rows
from asteria.trade.contracts import (
    TRADE_RULE_VERSION,
    TRADE_SCHEMA_VERSION,
    TradeBuildRequest,
    TradeBuildSummary,
)
from asteria.trade.rules import (
    PortfolioPlanInput,
    build_trade_rows,
    portfolio_plan_input_from_row,
)
from asteria.trade.schema import bootstrap_trade_database


def run_trade_build(request: TradeBuildRequest) -> TradeBuildSummary:
    checkpoint = _load_completed_checkpoint(request, "build")
    if checkpoint:
        return checkpoint
    if request.mode == "audit-only":
        return run_trade_audit(request)

    inputs = _load_portfolio_plan_inputs(request)
    created_at = _utc_now()
    trade_rows = build_trade_rows(inputs, request, created_at)
    staging_db = request.staging_db_path
    if staging_db.exists():
        staging_db.unlink()
    bootstrap_trade_database(staging_db)
    with duckdb.connect(str(staging_db)) as con:
        con.execute("begin transaction")
        _delete_run(con, request)
        con.execute(
            "delete from trade_schema_version where schema_version = ?",
            [request.schema_version],
        )
        con.execute(
            "delete from trade_rule_version where trade_rule_version = ?",
            [request.trade_rule_version],
        )
        con.execute(
            "insert into trade_schema_version values (?, ?)",
            [request.schema_version, created_at],
        )
        con.execute(
            "insert into trade_rule_version values (?, ?, ?, ?)",
            [
                request.trade_rule_version,
                "portfolio_plan_to_trade_day",
                "retained_gap_without_fill_source",
                created_at,
            ],
        )
        _executemany(
            con,
            """
            insert into trade_portfolio_snapshot
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            trade_rows.snapshots,
        )
        _executemany(
            con,
            """
            insert into order_intent_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            trade_rows.intents,
        )
        _executemany(
            con,
            """
            insert into execution_plan_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            trade_rows.execution_plans,
        )
        _executemany(
            con,
            """
            insert into fill_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            trade_rows.fills,
        )
        _executemany(
            con,
            """
            insert into order_rejection_ledger
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            trade_rows.rejections,
        )
        con.execute(
            """
            insert into trade_run
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                request.run_id,
                "trade_build",
                request.mode,
                request.timeframe,
                "completed",
                str(request.source_portfolio_plan_db),
                len(trade_rows.snapshots),
                len(trade_rows.intents),
                len(trade_rows.execution_plans),
                len(trade_rows.fills),
                len(trade_rows.rejections),
                0,
                request.schema_version,
                request.trade_rule_version,
                request.source_portfolio_plan_release_version,
                request.source_portfolio_plan_run_id,
                created_at,
            ],
        )
        con.execute("commit")

    audit = run_trade_audit(request, target_db=staging_db)
    status = "completed" if audit.hard_fail_count == 0 else "failed"
    if audit.hard_fail_count == 0:
        _promote_staging_db(request, staging_db)
    summary = TradeBuildSummary(
        run_id=request.run_id,
        stage="build",
        status=status,
        timeframe=request.timeframe,
        input_portfolio_plan_count=len(trade_rows.snapshots),
        order_intent_count=len(trade_rows.intents),
        execution_plan_count=len(trade_rows.execution_plans),
        fill_count=len(trade_rows.fills),
        rejection_count=len(trade_rows.rejections),
        hard_fail_count=audit.hard_fail_count,
        report_path=audit.report_path,
    )
    _save_checkpoint(request.checkpoint_path("build"), summary)
    return summary


def run_trade_audit(request: TradeBuildRequest, target_db: Path | None = None) -> TradeBuildSummary:
    audit_db = request.target_trade_db if target_db is None else target_db
    bootstrap_trade_database(audit_db)
    created_at = _utc_now()
    audit_rows, payload = build_trade_audit_rows(request, created_at, str(audit_db))
    with duckdb.connect(str(audit_db)) as con:
        con.execute("begin transaction")
        con.execute(
            "delete from trade_audit where audit_id like ?",
            [f"{request.run_id}|{request.timeframe}|%"],
        )
        con.executemany("insert into trade_audit values (?, ?, ?, ?, ?, ?, ?, ?)", audit_rows)
        con.execute(
            """
            update trade_run
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
    summary = TradeBuildSummary(
        run_id=request.run_id,
        stage="audit",
        status="completed" if payload["hard_fail_count"] == 0 else "failed",
        timeframe=request.timeframe,
        input_portfolio_plan_count=int(payload["input_portfolio_plan_count"]),
        order_intent_count=int(payload["order_intent_count"]),
        execution_plan_count=int(payload["execution_plan_count"]),
        fill_count=int(payload["fill_count"]),
        rejection_count=int(payload["rejection_count"]),
        hard_fail_count=int(payload["hard_fail_count"]),
        report_path=str(report_path),
    )
    _save_checkpoint(request.checkpoint_path("audit"), summary)
    return summary


def run_trade_bounded_proof(
    source_portfolio_plan_db: Path,
    target_trade_db: Path,
    report_root: Path,
    validated_root: Path,
    temp_root: Path,
    run_id: str,
    source_portfolio_plan_release_version: str,
    source_portfolio_plan_run_id: str | None,
    start_dt: str | None,
    end_dt: str | None,
    symbol_limit: int | None,
    schema_version: str = TRADE_SCHEMA_VERSION,
    trade_rule_version: str = TRADE_RULE_VERSION,
    mode: str = "bounded",
) -> TradeBuildSummary:
    request = TradeBuildRequest(
        source_portfolio_plan_db=source_portfolio_plan_db,
        target_trade_db=target_trade_db,
        report_root=report_root,
        validated_root=validated_root,
        temp_root=temp_root,
        run_id=run_id,
        mode=mode,
        source_portfolio_plan_release_version=source_portfolio_plan_release_version,
        source_portfolio_plan_run_id=source_portfolio_plan_run_id,
        schema_version=schema_version,
        trade_rule_version=trade_rule_version,
        start_dt=start_dt,
        end_dt=end_dt,
        symbol_limit=symbol_limit,
    )
    summary = run_trade_build(request)
    evidence = _write_bounded_proof_evidence(request, summary)
    return TradeBuildSummary(**{**summary.as_dict(), **evidence})


def _load_portfolio_plan_inputs(request: TradeBuildRequest) -> list[PortfolioPlanInput]:
    if not request.source_portfolio_plan_db.exists():
        raise FileNotFoundError(f"Missing Portfolio Plan DB: {request.source_portfolio_plan_db}")
    clauses = ["a.timeframe = ?"]
    params: list[object] = [request.timeframe]
    source_run_id = (
        request.source_portfolio_plan_run_id or request.source_portfolio_plan_release_version
    )
    if source_run_id:
        clauses.append("a.run_id = ?")
        params.append(source_run_id)
    if request.start_dt:
        clauses.append("a.plan_dt >= ?")
        params.append(request.start_dt)
    if request.end_dt:
        clauses.append("a.plan_dt <= ?")
        params.append(request.end_dt)
    if request.symbols:
        placeholders = ", ".join("?" for _ in request.symbols)
        clauses.append(f"a.symbol in ({placeholders})")
        params.extend(request.symbols)
    symbol_limit = ""
    if request.symbol_limit is not None and not request.symbols:
        source_run_clause = ""
        source_run_params: list[object] = []
        if source_run_id:
            source_run_clause = " and run_id = ?"
            source_run_params.append(source_run_id)
        symbol_limit = f"""
        and a.symbol in (
            select symbol
            from portfolio_admission_ledger
            where timeframe = ?
            {source_run_clause}
            group by symbol
            order by symbol
            limit ?
        )
        """
        params.extend([request.timeframe, *source_run_params, request.symbol_limit])
    query = f"""
        select a.portfolio_admission_id, a.position_candidate_id, a.symbol, a.timeframe,
               a.plan_dt, a.admission_state, a.admission_reason,
               te.target_exposure_id, te.exposure_type, te.target_weight,
               te.target_notional, te.target_quantity_hint,
               a.source_position_release_version, a.portfolio_plan_rule_version,
               r.run_id, a.run_id,
               t.trim_reason
        from portfolio_admission_ledger a
        left join portfolio_target_exposure te
          on a.portfolio_admission_id = te.portfolio_admission_id
         and (te.exposure_type = 'target_weight' or te.exposure_type is null)
        left join portfolio_trim_ledger t
          on a.portfolio_admission_id = t.portfolio_admission_id
        left join portfolio_plan_run r
          on a.run_id = r.run_id
        where {" and ".join(clauses)}
        {symbol_limit}
        order by a.symbol, a.plan_dt, a.portfolio_admission_id
    """
    with duckdb.connect(str(request.source_portfolio_plan_db), read_only=True) as con:
        rows = con.execute(query, params).fetchall()
    return [portfolio_plan_input_from_row(row) for row in rows]


def _delete_run(con: duckdb.DuckDBPyConnection, request: TradeBuildRequest) -> None:
    con.execute("delete from order_rejection_ledger where run_id = ?", [request.run_id])
    con.execute("delete from fill_ledger where run_id = ?", [request.run_id])
    con.execute("delete from execution_plan_ledger where run_id = ?", [request.run_id])
    con.execute("delete from order_intent_ledger where run_id = ?", [request.run_id])
    con.execute("delete from trade_portfolio_snapshot where trade_run_id = ?", [request.run_id])
    con.execute("delete from trade_run where run_id = ?", [request.run_id])
    con.execute(
        "delete from trade_audit where audit_id like ?", [f"{request.run_id}|{request.timeframe}|%"]
    )


def _promote_staging_db(request: TradeBuildRequest, staging_db: Path) -> None:
    if _target_contains_run(request):
        raise ValueError(f"target trade.duckdb already contains run_id: {request.run_id}")
    request.target_trade_db.parent.mkdir(parents=True, exist_ok=True)
    copy2(staging_db, request.target_trade_db)


def _target_contains_run(request: TradeBuildRequest) -> bool:
    if not request.target_trade_db.exists():
        return False
    with duckdb.connect(str(request.target_trade_db), read_only=True) as con:
        tables = {
            str(row[0])
            for row in con.execute(
                "select table_name from information_schema.tables where table_schema = 'main'"
            ).fetchall()
        }
        if "trade_run" not in tables:
            return False
        row = con.execute(
            "select count(*) from trade_run where run_id = ?", [request.run_id]
        ).fetchone()
    return False if row is None else int(row[0]) > 0


def _write_bounded_proof_evidence(
    request: TradeBuildRequest,
    summary: TradeBuildSummary,
) -> dict[str, str]:
    report_dir = request.report_root / "trade" / _utc_now().date().isoformat() / request.run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": request.run_id,
        "module": "trade",
        "stage": "bounded_proof",
        "status": "passed" if summary.hard_fail_count == 0 else "failed",
        "hard_fail_count": summary.hard_fail_count,
        "input_portfolio_plan_count": summary.input_portfolio_plan_count,
        "order_intent_count": summary.order_intent_count,
        "execution_plan_count": summary.execution_plan_count,
        "fill_count": summary.fill_count,
        "rejection_count": summary.rejection_count,
        "source_portfolio_plan_release_version": request.source_portfolio_plan_release_version,
        "source_portfolio_plan_run_id": request.source_portfolio_plan_run_id,
        "target_trade_db": str(request.target_trade_db),
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
        f"# Trade bounded proof closeout: {manifest['run_id']}",
        "",
        f"- status: {manifest['status']}",
        f"- hard_fail_count: {manifest['hard_fail_count']}",
        f"- input_portfolio_plan_count: {manifest['input_portfolio_plan_count']}",
        f"- order_intent_count: {manifest['order_intent_count']}",
        f"- execution_plan_count: {manifest['execution_plan_count']}",
        f"- fill_count: {manifest['fill_count']}",
        f"- rejection_count: {manifest['rejection_count']}",
        "- fill ledger retained gap: no evidence-backed execution / fill source was available",
        "- forbidden downstream scope: System Readout / Pipeline",
    ]
    return "\n".join(lines) + "\n"


def _report_path(report_root: Path, run_id: str, timeframe: str) -> Path:
    return (
        report_root
        / "trade"
        / _utc_now().date().isoformat()
        / f"{run_id}-{timeframe}-audit-summary.json"
    )


def _load_completed_checkpoint(
    request: TradeBuildRequest,
    stage: str,
) -> TradeBuildSummary | None:
    if request.mode != "resume":
        return None
    checkpoint = _load_checkpoint(request.checkpoint_path(stage))
    if checkpoint and checkpoint.get("status") == "completed":
        summary = TradeBuildSummary(**checkpoint["summary"])
        return TradeBuildSummary(**{**summary.as_dict(), "resume_reused": True})
    return None


def _load_checkpoint(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _save_checkpoint(path: Path, summary: TradeBuildSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": summary.status,
        "summary": summary.as_dict(),
        "created_at": _utc_now().isoformat(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _executemany(
    con: duckdb.DuckDBPyConnection,
    sql: str,
    rows: list[tuple[object, ...]],
) -> None:
    if rows:
        con.executemany(sql, rows)
