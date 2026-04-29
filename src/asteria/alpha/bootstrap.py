from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2
from typing import Any

import duckdb

from asteria.alpha.audit_engine import build_alpha_audit_rows
from asteria.alpha.contracts import (
    ALPHA_RULE_VERSION,
    ALPHA_SCHEMA_VERSION,
    AlphaBuildSummary,
    AlphaFamilyRequest,
)
from asteria.alpha.rules import build_alpha_rows, wave_position_from_row
from asteria.alpha.schema import bootstrap_alpha_family_database

ALPHA_FAMILIES = ("BOF", "TST", "PB", "CPB", "BPB")
ALPHA_FAMILY_DATABASES = {
    "BOF": "alpha_bof.duckdb",
    "TST": "alpha_tst.duckdb",
    "PB": "alpha_pb.duckdb",
    "CPB": "alpha_cpb.duckdb",
    "BPB": "alpha_bpb.duckdb",
}


def run_alpha_family_build(request: AlphaFamilyRequest) -> AlphaBuildSummary:
    checkpoint = _load_completed_checkpoint(request, "build")
    if checkpoint:
        return checkpoint
    if request.mode == "audit-only":
        return run_alpha_family_audit(request)

    rows = _load_wave_positions(request)
    created_at = _utc_now()
    alpha_rows = build_alpha_rows(rows, request, created_at)
    bootstrap_alpha_family_database(request.target_alpha_db)
    source_run_id = rows[0].run_id if rows else None
    with duckdb.connect(str(request.target_alpha_db)) as con:
        con.execute("begin transaction")
        _delete_run(con, request.run_id)
        con.execute(
            "delete from alpha_schema_version where schema_version = ?", [request.schema_version]
        )
        con.execute(
            "delete from alpha_rule_version where alpha_family = ? and alpha_rule_version = ?",
            [request.alpha_family, request.alpha_rule_version],
        )
        con.execute(
            "insert into alpha_schema_version values (?, ?)", [request.schema_version, created_at]
        )
        con.execute(
            "insert into alpha_rule_version values (?, ?, ?, ?)",
            [request.alpha_family, request.alpha_rule_version, "waveposition_only", created_at],
        )
        con.executemany(
            "insert into alpha_event_ledger values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            alpha_rows.events,
        )
        con.executemany(
            "insert into alpha_score_ledger values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            alpha_rows.scores,
        )
        con.executemany(
            """
            insert into alpha_signal_candidate
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            alpha_rows.candidates,
        )
        con.execute(
            """
            insert into alpha_family_run
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                request.run_id,
                "alpha_family_build",
                request.mode,
                request.timeframe,
                request.alpha_family,
                "completed",
                str(request.source_malf_db),
                len(rows),
                len(alpha_rows.events),
                len(alpha_rows.scores),
                len(alpha_rows.candidates),
                request.schema_version,
                request.alpha_rule_version,
                request.source_malf_service_version,
                source_run_id,
                created_at,
            ],
        )
        con.execute("commit")

    audit = run_alpha_family_audit(request)
    summary = AlphaBuildSummary(
        run_id=request.run_id,
        alpha_family=request.alpha_family,
        stage="build",
        status="completed" if audit.hard_fail_count == 0 else "failed",
        event_count=len(alpha_rows.events),
        score_count=len(alpha_rows.scores),
        candidate_count=len(alpha_rows.candidates),
        hard_fail_count=audit.hard_fail_count,
        report_path=audit.report_path,
    )
    _save_checkpoint(request.checkpoint_path("build"), summary)
    return summary


def run_alpha_family_audit(request: AlphaFamilyRequest) -> AlphaBuildSummary:
    bootstrap_alpha_family_database(request.target_alpha_db)
    created_at = _utc_now()
    audit_rows, payload = build_alpha_audit_rows(request, created_at)
    with duckdb.connect(str(request.target_alpha_db)) as con:
        con.execute("begin transaction")
        con.execute(
            "delete from alpha_source_audit where run_id = ? and alpha_family = ?",
            [request.run_id, request.alpha_family],
        )
        con.executemany(
            "insert into alpha_source_audit values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            audit_rows,
        )
        con.execute("commit")

    report_path = _report_path(request.report_root, request.run_id, request.alpha_family)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = AlphaBuildSummary(
        run_id=request.run_id,
        alpha_family=request.alpha_family,
        stage="audit",
        status="completed" if payload["hard_fail_count"] == 0 else "failed",
        event_count=int(payload["event_count"]),
        score_count=int(payload["score_count"]),
        candidate_count=int(payload["candidate_count"]),
        hard_fail_count=int(payload["hard_fail_count"]),
        report_path=str(report_path),
    )
    _save_checkpoint(request.checkpoint_path("audit"), summary)
    return summary


def run_alpha_bounded_proof(
    source_malf_db: Path,
    target_data_root: Path,
    report_root: Path,
    validated_root: Path,
    temp_root: Path,
    run_id: str,
    start_dt: str | None,
    end_dt: str | None,
    symbol_limit: int | None,
    source_malf_service_version: str = "service-v1",
    schema_version: str = ALPHA_SCHEMA_VERSION,
    alpha_rule_version: str = ALPHA_RULE_VERSION,
    mode: str = "bounded",
) -> list[AlphaBuildSummary]:
    summaries: list[AlphaBuildSummary] = []
    for family in ALPHA_FAMILIES:
        request = AlphaFamilyRequest(
            source_malf_db=source_malf_db,
            target_alpha_db=target_data_root / ALPHA_FAMILY_DATABASES[family],
            report_root=report_root,
            validated_root=validated_root,
            temp_root=temp_root,
            run_id=run_id,
            mode=mode,
            alpha_family=family,
            source_malf_service_version=source_malf_service_version,
            schema_version=schema_version,
            alpha_rule_version=alpha_rule_version,
            start_dt=start_dt,
            end_dt=end_dt,
            symbol_limit=symbol_limit,
        )
        summaries.append(run_alpha_family_build(request))
    _write_bounded_proof_evidence(report_root, validated_root, run_id, summaries)
    return summaries


def _load_wave_positions(request: AlphaFamilyRequest) -> list[Any]:
    if not request.source_malf_db.exists():
        raise FileNotFoundError(f"Missing MALF service DB: {request.source_malf_db}")
    clauses = ["timeframe = ?", "service_version = ?"]
    params: list[object] = [request.timeframe, request.source_malf_service_version]
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
            select symbol from malf_wave_position
            where timeframe = ? and service_version = ?
            group by symbol
            order by symbol
            limit ?
        )
        """
        params.extend(
            [request.timeframe, request.source_malf_service_version, request.symbol_limit]
        )
    query = f"""
        with scoped as (
            select symbol, timeframe, bar_dt, system_state, wave_core_state, direction,
                   new_count, no_new_span, transition_span, update_rank, stagnation_rank,
                   life_state, position_quadrant, service_version, run_id
            from malf_wave_position
            where {" and ".join(clauses)}
            {symbol_limit}
        ),
        canonical as (
            select *,
                   row_number() over (
                       partition by symbol, timeframe, bar_dt
                       order by
                           case when system_state = 'transition' then 1 else 0 end,
                           transition_span desc,
                           run_id
                   ) as row_rank
            from scoped
        )
        select symbol, timeframe, bar_dt, system_state, wave_core_state, direction,
               new_count, no_new_span, transition_span, update_rank, stagnation_rank,
               life_state, position_quadrant, service_version, run_id
        from canonical
        where row_rank = 1
        order by symbol, bar_dt
    """
    with duckdb.connect(str(request.source_malf_db), read_only=True) as con:
        return [wave_position_from_row(row) for row in con.execute(query, params).fetchall()]


def _delete_run(con: duckdb.DuckDBPyConnection, run_id: str) -> None:
    for table in [
        "alpha_family_run",
        "alpha_event_ledger",
        "alpha_score_ledger",
        "alpha_signal_candidate",
        "alpha_source_audit",
    ]:
        con.execute(f"delete from {table} where run_id = ?", [run_id])


def _write_bounded_proof_evidence(
    report_root: Path,
    validated_root: Path,
    run_id: str,
    summaries: list[AlphaBuildSummary],
) -> None:
    report_dir = report_root / "alpha" / _utc_now().date().isoformat() / run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": run_id,
        "module": "alpha",
        "stage": "bounded_proof",
        "hard_fail_count": sum(summary.hard_fail_count for summary in summaries),
        "families": [summary.as_dict() for summary in summaries],
        "generated_at": _utc_now().isoformat(),
    }
    manifest_path = report_dir / "manifest.json"
    closeout_path = report_dir / "closeout.md"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    closeout_path.write_text(_closeout_text(manifest), encoding="utf-8")
    zip_path = validated_root / f"Asteria-{run_id}.zip"
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(manifest_path, manifest_path.name)
        archive.write(closeout_path, closeout_path.name)
        for summary in summaries:
            if summary.report_path:
                report_path = Path(summary.report_path)
                if report_path.exists():
                    archive.write(report_path, f"family/{report_path.name}")
    copy2(
        manifest_path,
        report_root / "alpha" / _utc_now().date().isoformat() / f"{run_id}-summary.json",
    )


def _closeout_text(manifest: dict[str, Any]) -> str:
    lines = [
        f"# Alpha bounded proof closeout: {manifest['run_id']}",
        "",
        f"- status: {'passed' if manifest['hard_fail_count'] == 0 else 'failed'}",
        f"- hard_fail_count: {manifest['hard_fail_count']}",
        "- forbidden downstream scope: Signal / Position / Portfolio / Trade / System / Pipeline",
    ]
    return "\n".join(lines) + "\n"


def _report_path(report_root: Path, run_id: str, family: str) -> Path:
    return (
        report_root
        / "alpha"
        / _utc_now().date().isoformat()
        / f"{run_id}-{family.lower()}-audit-summary.json"
    )


def _load_completed_checkpoint(request: AlphaFamilyRequest, stage: str) -> AlphaBuildSummary | None:
    if request.mode != "resume":
        return None
    checkpoint = _load_checkpoint(request.checkpoint_path(stage))
    if checkpoint and checkpoint.get("status") == "completed":
        summary = AlphaBuildSummary(**checkpoint["summary"])
        return AlphaBuildSummary(**{**summary.as_dict(), "resume_reused": True})
    return None


def _load_checkpoint(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _save_checkpoint(path: Path, summary: AlphaBuildSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": summary.status,
        "summary": summary.as_dict(),
        "created_at": _utc_now().isoformat(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
