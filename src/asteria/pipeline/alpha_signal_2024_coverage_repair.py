from __future__ import annotations

import json
import shutil
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

import duckdb

from asteria.alpha.bootstrap import ALPHA_FAMILIES, run_alpha_family_build
from asteria.alpha.contracts import (
    ALPHA_RULE_VERSION,
    ALPHA_SCHEMA_VERSION,
    AlphaBuildSummary,
    AlphaFamilyRequest,
)
from asteria.pipeline.alpha_signal_2024_coverage_repair_contracts import (
    AlphaSignalCoverageRepairRequest,
    AlphaSignalCoverageRepairSummary,
)
from asteria.pipeline.bootstrap import run_pipeline_bounded_proof
from asteria.pipeline.contracts import PipelineBuildSummary
from asteria.pipeline.system_probe_diagnosis import run_system_probe_diagnosis
from asteria.pipeline.year_replay_coverage_gap_diagnosis import (
    YearReplayCoverageGapDiagnosisRequest,
    run_year_replay_coverage_gap_diagnosis,
)
from asteria.signal.bootstrap import run_signal_build
from asteria.signal.contracts import (
    SIGNAL_RULE_VERSION,
    SIGNAL_SCHEMA_VERSION,
    SignalBuildRequest,
    SignalBuildSummary,
)

FOLLOWUP_YEAR_REPLAY_RERUN_ACTION = "pipeline_one_year_strategy_behavior_replay_rerun_build_card"
FOLLOWUP_YEAR_REPLAY_RERUN_CARD_RUN_ID = (
    "pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01"
)
FOLLOWUP_YEAR_REPLAY_REQUIRED_PROOF_RUN_ID = (
    "pipeline-full-chain-bounded-proof-build-card-20260508-01"
)


def run_alpha_signal_2024_coverage_repair(
    request: AlphaSignalCoverageRepairRequest,
) -> AlphaSignalCoverageRepairSummary:
    request.run_root.mkdir(parents=True, exist_ok=True)
    merged_db = build_merged_malf_service_day(request)
    alpha_summaries = _rewrite_alpha_day_surfaces(request, merged_db)
    signal_summary = _rewrite_signal_day_surface(request)
    status = "completed"
    if (
        any(summary.hard_fail_count > 0 for summary in alpha_summaries)
        or signal_summary.hard_fail_count > 0
    ):
        status = "failed"
    followup_next_card: str | None = None
    followup_rerun_status: str | None = None
    followup_rerun_hard_fail_count: int | None = None
    followup_diagnosis_run_id: str | None = None
    if status == "completed" and request.run_followup_checks:
        rerun_summary, diagnosis_next_card, diagnosis_run_id = _run_followup_checks(request)
        followup_rerun_status = rerun_summary.status
        followup_rerun_hard_fail_count = rerun_summary.hard_fail_count
        followup_next_card = diagnosis_next_card
        followup_diagnosis_run_id = diagnosis_run_id
    manifest_path, closeout_path, validated_zip = _write_card_evidence(
        request,
        merged_db,
        alpha_summaries,
        signal_summary,
        followup_rerun_status,
        followup_rerun_hard_fail_count,
        followup_next_card,
        followup_diagnosis_run_id,
    )
    return AlphaSignalCoverageRepairSummary(
        run_id=request.run_id,
        status=status,
        merged_malf_service_db=str(merged_db),
        alpha_repair_count=len(alpha_summaries),
        signal_hard_fail_count=signal_summary.hard_fail_count,
        followup_rerun_status=followup_rerun_status,
        followup_rerun_hard_fail_count=followup_rerun_hard_fail_count,
        followup_next_card=followup_next_card,
        followup_diagnosis_run_id=followup_diagnosis_run_id,
        manifest_path=str(manifest_path),
        closeout_path=str(closeout_path),
        validated_zip=str(validated_zip),
    )


def build_merged_malf_service_day(request: AlphaSignalCoverageRepairRequest) -> Path:
    merged_db = request.merged_malf_service_db
    merged_db.parent.mkdir(parents=True, exist_ok=True)
    if merged_db.exists():
        merged_db.unlink()
    shutil.copy2(request.baseline_malf_service_db, merged_db)
    with duckdb.connect(str(merged_db)) as con:
        overlap_keys = _fetch_overlap_keys(
            request.repaired_malf_service_db,
            request.repaired_malf_run_id,
        )
        for table_name in ("malf_wave_position", "malf_wave_position_latest"):
            if _table_exists(con, table_name):
                con.execute(
                    f"delete from {table_name} where timeframe = 'day' and run_id not in (?, ?)",
                    [request.baseline_malf_run_id, request.repaired_malf_run_id],
                )
                con.execute(
                    f"delete from {table_name} where timeframe = 'day' and run_id = ?",
                    [request.repaired_malf_run_id],
                )
                if overlap_keys:
                    overlap_params = [
                        (symbol, bar_dt, request.repaired_malf_run_id)
                        for symbol, bar_dt in overlap_keys
                    ]
                    con.executemany(
                        (
                            f"delete from {table_name} where timeframe = 'day' and symbol = ? and "
                            "bar_dt = ? and run_id <> ?"
                        ),
                        overlap_params,
                    )
                _insert_rows(
                    con,
                    table_name,
                    _load_rows_for_run(
                        request.repaired_malf_service_db,
                        table_name,
                        request.repaired_malf_run_id,
                        timeframe="day",
                    ),
                )
        for table_name in ("malf_service_run", "malf_interface_audit"):
            if _table_exists(con, table_name):
                con.execute(
                    f"delete from {table_name} where run_id not in (?, ?)",
                    [request.baseline_malf_run_id, request.repaired_malf_run_id],
                )
                con.execute(
                    f"delete from {table_name} where run_id = ?",
                    [request.repaired_malf_run_id],
                )
                _insert_rows(
                    con,
                    table_name,
                    _load_rows_for_run(
                        request.repaired_malf_service_db,
                        table_name,
                        request.repaired_malf_run_id,
                    ),
                )
    return merged_db


def _rewrite_alpha_day_surfaces(
    request: AlphaSignalCoverageRepairRequest,
    merged_db: Path,
) -> list[AlphaBuildSummary]:
    summaries: list[AlphaBuildSummary] = []
    for family in ALPHA_FAMILIES:
        summaries.append(
            run_alpha_family_build(
                AlphaFamilyRequest(
                    source_malf_db=merged_db,
                    target_alpha_db=request.target_data_root / f"alpha_{family.lower()}.duckdb",
                    report_root=request.report_root,
                    validated_root=request.validated_root,
                    temp_root=request.temp_root,
                    run_id=request.released_alpha_run_id,
                    mode="full",
                    alpha_family=family,
                    source_malf_service_version=request.malf_service_version,
                    schema_version=ALPHA_SCHEMA_VERSION,
                    alpha_rule_version=ALPHA_RULE_VERSION,
                    timeframe="day",
                )
            )
        )
    return summaries


def _rewrite_signal_day_surface(
    request: AlphaSignalCoverageRepairRequest,
) -> SignalBuildSummary:
    return run_signal_build(
        SignalBuildRequest(
            source_alpha_root=request.target_data_root,
            target_signal_db=request.target_data_root / "signal.duckdb",
            report_root=request.report_root,
            validated_root=request.validated_root,
            temp_root=request.temp_root,
            run_id=request.released_signal_run_id,
            mode="full",
            source_alpha_release_version=request.released_alpha_run_id,
            source_alpha_run_id=request.released_alpha_run_id,
            schema_version=SIGNAL_SCHEMA_VERSION,
            signal_rule_version=SIGNAL_RULE_VERSION,
            timeframe="day",
        )
    )


def _run_followup_checks(
    request: AlphaSignalCoverageRepairRequest,
) -> tuple[PipelineBuildSummary, str | None, str | None]:
    followup_repo_root = _build_followup_repo_root(request)
    rerun_summary = run_pipeline_bounded_proof(
        repo_root=followup_repo_root,
        source_system_db=request.source_system_db,
        target_pipeline_db=request.followup_pipeline_db,
        report_root=request.report_root,
        validated_root=request.validated_root,
        temp_root=request.temp_root,
        run_id=request.followup_rerun_run_id,
        source_chain_release_version=request.source_chain_release_version,
        module_scope="year_replay_rerun",
        target_year=request.target_year,
    )
    if rerun_summary.hard_fail_count == 0:
        return rerun_summary, None, None
    diagnosis_summary = run_year_replay_coverage_gap_diagnosis(
        YearReplayCoverageGapDiagnosisRequest(
            repo_root=request.repo_root,
            source_system_db=request.source_system_db,
            report_root=request.report_root,
            validated_root=request.validated_root,
            run_id=request.followup_diagnosis_run_id,
            target_year=request.target_year,
        )
    )
    if (
        diagnosis_summary.recommended_next_card
        == "malf-2024-natural-year-coverage-repair-card-20260509-01"
        and _alpha_signal_focus_window_repaired(request)
    ):
        probe_diagnosis = _run_system_probe_diagnosis(request)
        return rerun_summary, probe_diagnosis.recommended_next_card, probe_diagnosis.run_id
    return (
        rerun_summary,
        diagnosis_summary.recommended_next_card,
        diagnosis_summary.run_id,
    )


def _build_followup_repo_root(request: AlphaSignalCoverageRepairRequest) -> Path:
    registry_source = request.repo_root / "governance" / "module_gate_registry.toml"
    target_root = request.followup_repo_root
    governance_root = target_root / "governance"
    governance_root.mkdir(parents=True, exist_ok=True)
    registry_text = registry_source.read_text(encoding="utf-8")
    for old_action in (
        "data_ledger_daily_incremental_hardening_card",
        "system_wide_daily_dirty_scope_protocol_card",
        "pipeline_year_replay_disposition_decision_card",
        "pipeline_year_replay_source_selection_repair_card",
        "coverage_gap_evidence_incomplete_closeout_card",
        "alpha_signal_2024_coverage_repair_card",
    ):
        rewritten = registry_text.replace(
            f'current_allowed_next_card = "{old_action}"',
            (f'current_allowed_next_card = "{FOLLOWUP_YEAR_REPLAY_RERUN_ACTION}"'),
            1,
        )
        if rewritten != registry_text:
            registry_text = rewritten
            break
    registry_text = _rewrite_followup_pipeline_registry(registry_text)
    (governance_root / "module_gate_registry.toml").write_text(registry_text, encoding="utf-8")
    return target_root


def _rewrite_followup_pipeline_registry(registry_text: str) -> str:
    lines = registry_text.splitlines()
    in_pipeline = False
    for idx, line in enumerate(lines):
        if line == 'module_id = "pipeline"':
            in_pipeline = True
            continue
        if in_pipeline and line == "[[modules]]":
            break
        if not in_pipeline:
            continue
        if line.startswith('next_card = "'):
            lines[idx] = f'next_card = "{FOLLOWUP_YEAR_REPLAY_RERUN_ACTION}"'
        elif line.startswith('active_card = "docs/04-execution/records/pipeline/'):
            lines[idx] = (
                'active_card = "docs/04-execution/records/pipeline/'
                f'{FOLLOWUP_YEAR_REPLAY_RERUN_CARD_RUN_ID}.card.md"'
            )
        elif line.startswith('next_allowed_action = "'):
            lines[idx] = f'next_allowed_action = "{FOLLOWUP_YEAR_REPLAY_RERUN_ACTION}"'
        elif line.startswith('proof_run_id = "'):
            lines[idx] = f'proof_run_id = "{FOLLOWUP_YEAR_REPLAY_REQUIRED_PROOF_RUN_ID}"'
    return "\n".join(lines) + "\n"


def _write_card_evidence(
    request: AlphaSignalCoverageRepairRequest,
    merged_db: Path,
    alpha_summaries: list[AlphaBuildSummary],
    signal_summary: SignalBuildSummary,
    followup_rerun_status: str | None,
    followup_rerun_hard_fail_count: int | None,
    followup_next_card: str | None,
    followup_diagnosis_run_id: str | None,
) -> tuple[Path, Path, Path]:
    report_dir = request.report_root / "pipeline" / _utc_now().date().isoformat() / request.run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": request.run_id,
        "module": "pipeline",
        "stage": "alpha_signal_2024_coverage_repair",
        "status": "completed",
        "merged_malf_service_db": str(merged_db),
        "baseline_malf_run_id": request.baseline_malf_run_id,
        "repaired_malf_run_id": request.repaired_malf_run_id,
        "released_alpha_run_id": request.released_alpha_run_id,
        "released_signal_run_id": request.released_signal_run_id,
        "followup_rerun_status": followup_rerun_status,
        "followup_rerun_hard_fail_count": followup_rerun_hard_fail_count,
        "followup_next_card": followup_next_card,
        "followup_diagnosis_run_id": followup_diagnosis_run_id,
        "generated_at": _utc_now().isoformat(),
        "alpha_summaries": [summary.as_dict() for summary in alpha_summaries],
        "signal_summary": signal_summary.as_dict(),
    }
    manifest_path = report_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    closeout_lines = [
        f"# Alpha/Signal 2024 coverage repair closeout: {request.run_id}",
        "",
        f"- merged_malf_service_db: `{merged_db}`",
        f"- released_alpha_run_id: `{request.released_alpha_run_id}`",
        f"- released_signal_run_id: `{request.released_signal_run_id}`",
    ]
    if followup_rerun_status is not None:
        closeout_lines.append(f"- followup_rerun_status: `{followup_rerun_status}`")
    if followup_next_card is not None:
        closeout_lines.append(f"- truthful_next_card: `{followup_next_card}`")
    closeout_path = report_dir / "closeout.md"
    closeout_path.write_text("\n".join(closeout_lines) + "\n", encoding="utf-8")
    validated_zip = request.validated_root / f"Asteria-{request.run_id}.zip"
    validated_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(validated_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(manifest_path, arcname="manifest.json")
        archive.write(closeout_path, arcname="closeout.md")
    return manifest_path, closeout_path, validated_zip


def _fetch_overlap_keys(source_db: Path, repaired_run_id: str) -> list[tuple[str, object]]:
    with duckdb.connect(str(source_db), read_only=True) as con:
        return [
            (str(symbol), bar_dt)
            for symbol, bar_dt in con.execute(
                """
                select distinct symbol, bar_dt
                from malf_wave_position
                where timeframe = 'day' and run_id = ?
                order by symbol, bar_dt
                """,
                [repaired_run_id],
            ).fetchall()
        ]


def _load_rows_for_run(
    source_db: Path,
    table_name: str,
    run_id: str,
    *,
    timeframe: str | None = None,
) -> list[tuple[object, ...]]:
    with duckdb.connect(str(source_db), read_only=True) as con:
        if not _table_exists(con, table_name):
            return []
        clauses = ["run_id = ?"]
        params: list[object] = [run_id]
        if timeframe is not None:
            clauses.append("timeframe = ?")
            params.append(timeframe)
        return con.execute(
            f"select * from {table_name} where {' and '.join(clauses)}",
            params,
        ).fetchall()


def _insert_rows(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    rows: list[tuple[object, ...]],
) -> None:
    if not rows:
        return
    placeholders = ", ".join(["?"] * len(rows[0]))
    con.executemany(f"insert into {table_name} values ({placeholders})", rows)


def _alpha_signal_focus_window_repaired(request: AlphaSignalCoverageRepairRequest) -> bool:
    focus_start = date(request.target_year, 1, 2)
    alpha_ok = all(
        _min_alpha_candidate_dt(
            request.target_data_root / f"alpha_{family.lower()}.duckdb",
            request.released_alpha_run_id,
        )
        <= focus_start
        for family in ALPHA_FAMILIES
    )
    signal_start = _min_signal_dt(
        request.target_data_root / "signal.duckdb",
        request.released_signal_run_id,
    )
    return alpha_ok and signal_start <= focus_start


def _run_system_probe_diagnosis(
    request: AlphaSignalCoverageRepairRequest,
):
    return run_system_probe_diagnosis(
        probe_root=request.run_root / "followup-system-probe",
        repo_root=request.repo_root,
        data_root=request.target_data_root,
        run_id_prefix=request.run_id,
        target_year=request.target_year,
    ).diagnosis_summary


def _min_alpha_candidate_dt(db_path: Path, run_id: str) -> date:
    with duckdb.connect(str(db_path), read_only=True) as con:
        row = con.execute(
            """
            select min(bar_dt)
            from alpha_signal_candidate
            where run_id = ? and timeframe = 'day'
            """,
            [run_id],
        ).fetchone()
    if row is None or row[0] is None:
        raise ValueError(f"missing released alpha day rows: {db_path} run_id={run_id}")
    return row[0]


def _min_signal_dt(db_path: Path, run_id: str) -> date:
    with duckdb.connect(str(db_path), read_only=True) as con:
        row = con.execute(
            """
            select min(signal_dt)
            from formal_signal_ledger
            where run_id = ? and timeframe = 'day'
            """,
            [run_id],
        ).fetchone()
    if row is None or row[0] is None:
        raise ValueError(f"missing released signal day rows: {db_path} run_id={run_id}")
    return row[0]


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


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
