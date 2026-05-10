from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

import duckdb

from asteria.pipeline.year_replay_coverage_gap_diagnosis import (
    YearReplayCoverageGapDiagnosisRequest,
    run_year_replay_coverage_gap_diagnosis,
)
from asteria.trade.coverage_repair_contracts import (
    FOCUS_DATES,
    Trade2024CoverageRepairRequest,
)
from asteria.trade.coverage_repair_shared import summary_status, trade_report_dir, utc_now


def run_followup_diagnosis(
    *,
    request: Trade2024CoverageRepairRequest,
    released_chain: dict[str, Any],
) -> tuple[str, str, dict[str, str]]:
    probe_system_db = build_probe_system_db(request, released_chain)
    diagnosis_run_id = f"{request.run_id}-followup-diagnosis"
    diagnosis_summary = run_year_replay_coverage_gap_diagnosis(
        YearReplayCoverageGapDiagnosisRequest(
            repo_root=request.repo_root,
            source_system_db=probe_system_db,
            report_root=request.report_root,
            validated_root=request.validated_root,
            run_id=diagnosis_run_id,
            target_year=request.target_year,
            data_root=request.data_root,
        )
    )
    return (
        diagnosis_summary.recommended_next_card,
        diagnosis_summary.attribution,
        {
            "probe_system_db": str(probe_system_db),
            "coverage_matrix_path": diagnosis_summary.coverage_matrix_path,
            "coverage_attribution_path": diagnosis_summary.coverage_attribution_path,
            "diagnosis_closeout_path": diagnosis_summary.closeout_path,
            "diagnosis_manifest_path": diagnosis_summary.manifest_path,
        },
    )


def build_probe_system_db(
    request: Trade2024CoverageRepairRequest,
    released_chain: dict[str, Any],
) -> Path:
    probe_root = request.run_root / "followup-system-probe"
    probe_root.mkdir(parents=True, exist_ok=True)
    probe_system_db = probe_root / "system-probe.duckdb"
    if probe_system_db.exists():
        probe_system_db.unlink()
    probe_run_id = f"{request.run_id}-system-probe"
    with duckdb.connect(str(request.source_system_db), read_only=True) as source:
        readout_dates = source.execute(
            """
            select readout_dt
            from system_chain_readout
            where system_readout_run_id = ?
            order by readout_dt
            """,
            [released_chain["released_system_run_id"]],
        ).fetchall()
    with duckdb.connect(str(probe_system_db)) as con:
        con.execute(
            "create table system_readout_run (run_id varchar, status varchar, created_at timestamp)"
        )
        con.execute(
            """
            create table system_source_manifest (
                system_readout_run_id varchar,
                module_name varchar,
                source_db varchar,
                source_run_id varchar,
                source_release_version varchar
            )
            """
        )
        con.execute(
            "create table system_chain_readout (system_readout_run_id varchar, readout_dt date)"
        )
        con.execute(
            "insert into system_readout_run values (?, 'completed', ?)",
            [probe_run_id, utc_now()],
        )
        probe_manifest_rows = _resolve_probe_manifest_rows(released_chain["manifest_rows"])
        con.executemany(
            "insert into system_source_manifest values (?, ?, ?, ?, ?)",
            [
                [
                    probe_run_id,
                    row["module_name"],
                    row["source_db"],
                    row["source_run_id"],
                    row["source_release_version"],
                ]
                for row in probe_manifest_rows
            ],
        )
        con.executemany(
            "insert into system_chain_readout values (?, ?)",
            [[probe_run_id, row[0]] for row in readout_dates],
        )
    return probe_system_db


def _resolve_probe_manifest_rows(
    manifest_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    return [_resolve_probe_manifest_row(row) for row in manifest_rows]


def _resolve_probe_manifest_row(row: dict[str, str]) -> dict[str, str]:
    latest_run_id = _load_latest_completed_day_run_id(
        Path(row["source_db"]),
        _run_table_name(row["module_name"]),
    )
    if latest_run_id is None:
        return dict(row)
    updated = dict(row)
    updated["source_run_id"] = latest_run_id
    updated["source_release_version"] = latest_run_id
    return updated


def _run_table_name(module_name: str) -> str | None:
    if module_name == "malf":
        return "malf_service_run"
    if module_name.startswith("alpha_"):
        return "alpha_family_run"
    if module_name == "signal":
        return "signal_run"
    if module_name == "position":
        return "position_run"
    if module_name == "portfolio_plan":
        return "portfolio_plan_run"
    if module_name == "trade":
        return "trade_run"
    return None


def _load_latest_completed_day_run_id(
    db_path: Path,
    run_table: str | None,
) -> str | None:
    if run_table is None or not db_path.exists():
        return None
    with duckdb.connect(str(db_path), read_only=True) as con:
        if not _table_exists(con, run_table):
            return None
        columns = {str(item[0]) for item in con.execute(f"describe {run_table}").fetchall()}
        if "run_id" not in columns or "status" not in columns or "created_at" not in columns:
            return None
        where_clauses = ["status = 'completed'"]
        if "timeframe" in columns:
            where_clauses.append("timeframe = 'day'")
        row = con.execute(
            f"""
            select run_id
            from {run_table}
            where {" and ".join(where_clauses)}
            order by created_at desc
            limit 1
            """
        ).fetchone()
    if row is None or row[0] is None:
        return None
    return str(row[0])


def _table_exists(con: duckdb.DuckDBPyConnection, table_name: str) -> bool:
    row = con.execute(
        """
        select count(*)
        from information_schema.tables
        where table_schema = 'main' and table_name = ?
        """,
        [table_name],
    ).fetchone()
    return row is not None and int(row[0]) > 0


def write_repair_evidence(
    *,
    request: Trade2024CoverageRepairRequest,
    released_system_run_id: str,
    released_portfolio_plan_run_id: str,
    released_trade_run_id: str,
    followup_next_card: str,
    followup_attribution: str,
    audit_report_path: Path,
    audit_payload: dict[str, Any],
    followup_artifacts: dict[str, str],
) -> tuple[Path, Path, Path]:
    report_dir = trade_report_dir(request.report_root, request.run_id)
    report_dir.mkdir(parents=True, exist_ok=True)
    matrix_payload = json.loads(
        Path(followup_artifacts["coverage_matrix_path"]).read_text(encoding="utf-8")
    )
    earliest_days = build_earliest_day_map(matrix_payload["rows"])
    manifest = {
        "run_id": request.run_id,
        "module": "trade",
        "stage": "trade_2024_coverage_repair",
        "status": summary_status(
            hard_fail_count=int(audit_payload["hard_fail_count"]),
            followup_next_card=followup_next_card,
            followup_attribution=followup_attribution,
        ),
        "released_system_run_id": released_system_run_id,
        "released_portfolio_plan_run_id": released_portfolio_plan_run_id,
        "released_trade_run_id": released_trade_run_id,
        "focus_dates": list(FOCUS_DATES),
        "hard_fail_count": audit_payload["hard_fail_count"],
        "input_portfolio_plan_count": audit_payload["input_portfolio_plan_count"],
        "order_intent_count": audit_payload["order_intent_count"],
        "execution_plan_count": audit_payload["execution_plan_count"],
        "fill_count": audit_payload["fill_count"],
        "rejection_count": audit_payload["rejection_count"],
        "followup_next_card": followup_next_card,
        "followup_attribution": followup_attribution,
        "followup_probe_system_db": followup_artifacts["probe_system_db"],
    }
    manifest_path = report_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    closeout_lines = [
        "# Trade 2024 Released Day Surface Repair",
        "",
        f"- run_id: `{request.run_id}`",
        f"- released_system_run_id: `{released_system_run_id}`",
        f"- released_portfolio_plan_run_id: `{released_portfolio_plan_run_id}`",
        f"- released_trade_run_id: `{released_trade_run_id}`",
        f"- focus_trading_dates: `{', '.join(FOCUS_DATES)}`",
        f"- hard_fail_count: `{audit_payload['hard_fail_count']}`",
        f"- followup_next_card: `{followup_next_card}`",
        f"- followup_attribution: `{followup_attribution}`",
        "",
        "## Earliest Days",
        "",
        f"- released Portfolio Plan earliest day: `{earliest_days.get('portfolio_plan', 'none')}`",
        f"- released Trade earliest day: `{earliest_days.get('trade', 'none')}`",
        f"- released System earliest day: `{earliest_days.get('system_readout', 'none')}`",
    ]
    closeout_path = report_dir / "closeout.md"
    closeout_path.write_text("\n".join(closeout_lines) + "\n", encoding="utf-8")
    validated_zip = request.validated_root / f"Asteria-{request.run_id}.zip"
    validated_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(validated_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(manifest_path, arcname="manifest.json")
        archive.write(closeout_path, arcname="closeout.md")
        archive.write(audit_report_path, arcname="trade-day-audit-summary.json")
        archive.write(followup_artifacts["coverage_matrix_path"], arcname="coverage-matrix.json")
        archive.write(
            followup_artifacts["coverage_attribution_path"],
            arcname="coverage-attribution.md",
        )
    return manifest_path, closeout_path, validated_zip


def build_earliest_day_map(rows: list[dict[str, object]]) -> dict[str, str]:
    mapped: dict[str, list[str]] = {
        "portfolio_plan": [],
        "trade": [],
        "system_readout": [],
    }
    for row in rows:
        layer = str(row["layer"])
        observed_start = row["observed_start"]
        if observed_start is None or layer not in mapped:
            continue
        mapped[layer].append(str(observed_start))
    return {layer: min(values) if values else "none" for layer, values in mapped.items()}
