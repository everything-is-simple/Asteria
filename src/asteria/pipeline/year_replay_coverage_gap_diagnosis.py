from __future__ import annotations

from pathlib import Path

import duckdb

from asteria.pipeline.released_source_selection import (
    resolve_released_year_replay_source_selection,
)
from asteria.pipeline.year_replay_coverage_gap_contracts import (
    ALPHA_FAMILY_MODULES,
    ALPHA_SIGNAL_REPAIR_CARD,
    DATA_REPAIR_CARD,
    EVIDENCE_INCOMPLETE_CARD,
    MALF_REPAIR_CARD,
    PIPELINE_REPAIR_CARD,
    PORTFOLIO_PLAN_REPAIR_CARD,
    POSITION_REPAIR_CARD,
    SYSTEM_REPAIR_CARD,
    TRADE_REPAIR_CARD,
    CoverageMatrixRow,
    YearReplayCoverageGapDiagnosisRequest,
    YearReplayCoverageGapDiagnosisSummary,
)
from asteria.pipeline.year_replay_coverage_gap_reports import write_diagnosis_artifacts
from asteria.pipeline.year_replay_portfolio_plan_semantics import (
    evaluate_portfolio_plan_focus_window,
)
from asteria.pipeline.year_replay_position_semantics import (
    evaluate_position_focus_window,
    load_planned_signal_focus_dates,
)
from asteria.pipeline.year_replay_support import (
    all_focus_dates_present,
    load_first_week_focus_dates,
)
from asteria.pipeline.year_replay_trade_semantics import evaluate_trade_focus_window


def run_year_replay_coverage_gap_diagnosis(
    request: YearReplayCoverageGapDiagnosisRequest,
) -> YearReplayCoverageGapDiagnosisSummary:
    data_root = request.data_root
    if data_root is None:
        raise ValueError("data_root must be resolved before diagnosis")

    released_selection = resolve_released_year_replay_source_selection(
        request.source_system_db,
        target_year=request.target_year,
    )
    released_system_run_id = released_selection.released_system_run_id
    manifest = {
        module_name: {
            "source_db": entry.source_db,
            "source_run_id": entry.source_run_id,
            "source_release_version": entry.source_release_version,
        }
        for module_name, entry in released_selection.manifest.items()
    }
    focus_trading_dates, calendar_semantic_dates = load_first_week_focus_dates(request.target_year)
    matrix_rows, layer_statuses, evidence_issues = _build_coverage_matrix(
        request=request,
        data_root=data_root,
        released_system_run_id=released_system_run_id,
        manifest=manifest,
        focus_trading_dates=focus_trading_dates,
    )
    full_year_gate_ok = (
        released_selection.year_observed_start == f"{request.target_year}-01-01"
        and released_selection.year_observed_end == f"{request.target_year}-12-31"
    )
    recommended_next_card, attribution = _recommend_next_card(
        layer_statuses=layer_statuses,
        evidence_issues=evidence_issues,
        full_year_gate_ok=full_year_gate_ok,
    )
    (
        manifest_path,
        coverage_matrix_path,
        coverage_attribution_path,
        closeout_path,
        validated_zip,
    ) = write_diagnosis_artifacts(
        request=request,
        released_system_run_id=released_system_run_id,
        recommended_next_card=recommended_next_card,
        attribution=attribution,
        focus_trading_dates=focus_trading_dates,
        calendar_semantic_dates=calendar_semantic_dates,
        layer_statuses=layer_statuses,
        evidence_issues=evidence_issues,
        full_year_gate_ok=full_year_gate_ok,
        rows=matrix_rows,
    )
    return YearReplayCoverageGapDiagnosisSummary(
        run_id=request.run_id,
        target_year=request.target_year,
        released_system_run_id=released_system_run_id,
        recommended_next_card=recommended_next_card,
        attribution=attribution,
        manifest_path=str(manifest_path),
        coverage_matrix_path=str(coverage_matrix_path),
        coverage_attribution_path=str(coverage_attribution_path),
        closeout_path=str(closeout_path),
        validated_zip=str(validated_zip),
    )


def _build_coverage_matrix(
    *,
    request: YearReplayCoverageGapDiagnosisRequest,
    data_root: Path,
    released_system_run_id: str,
    manifest: dict[str, dict[str, str]],
    focus_trading_dates: list[str],
) -> tuple[list[CoverageMatrixRow], dict[str, bool], list[str]]:
    rows: list[CoverageMatrixRow] = []
    evidence_issues: list[str] = []
    layer_statuses: dict[str, bool] = {}

    data_rows = [
        _query_surface(
            db_path=data_root / "market_base_day.duckdb",
            layer="data",
            surface_name="market_base_day",
            table_name="market_base_bar",
            date_column="bar_dt",
            run_selector="timeframe='day'",
            start_iso=f"{request.target_year}-01-01",
            end_iso=f"{request.target_year}-12-31",
            focus_dates=focus_trading_dates,
            where_clause="timeframe = 'day'",
            notes="Data foundation day surface; timeframe fixed to day.",
        ),
        _query_surface(
            db_path=data_root / "market_meta.duckdb",
            layer="data",
            surface_name="trade_calendar",
            table_name="trade_calendar",
            date_column="trade_date",
            run_selector="all released rows",
            start_iso=f"{request.target_year}-01-01",
            end_iso=f"{request.target_year}-12-31",
            focus_dates=focus_trading_dates,
            notes="Calendar reference surface for released trading dates.",
        ),
        _query_surface(
            db_path=data_root / "market_meta.duckdb",
            layer="data",
            surface_name="tradability_fact",
            table_name="tradability_fact",
            date_column="trade_date",
            run_selector="all released rows",
            start_iso=f"{request.target_year}-01-01",
            end_iso=f"{request.target_year}-12-31",
            focus_dates=focus_trading_dates,
            notes="Tradability reference surface for released trading dates.",
        ),
    ]
    rows.extend(data_rows)
    layer_statuses["data"] = all_focus_dates_present(data_rows)

    if "malf" not in manifest:
        evidence_issues.append("system_source_manifest is missing malf entry")
    else:
        malf_row = _query_surface(
            db_path=Path(manifest["malf"]["source_db"]),
            layer="malf",
            surface_name="malf_wave_position",
            table_name="malf_wave_position",
            date_column="bar_dt",
            run_selector=f"run_id = '{manifest['malf']['source_run_id']}'",
            start_iso=f"{request.target_year}-01-01",
            end_iso=f"{request.target_year}-12-31",
            focus_dates=focus_trading_dates,
            where_clause="run_id = ?",
            params=[manifest["malf"]["source_run_id"]],
            notes="Released MALF service surface locked by system_source_manifest.",
        )
        rows.append(malf_row)
        layer_statuses["malf"] = all_focus_dates_present([malf_row])

    alpha_rows: list[CoverageMatrixRow] = []
    for module_name in ALPHA_FAMILY_MODULES:
        if module_name not in manifest:
            evidence_issues.append(f"system_source_manifest is missing {module_name} entry")
            continue
        alpha_rows.append(
            _query_surface(
                db_path=Path(manifest[module_name]["source_db"]),
                layer="alpha",
                surface_name=module_name,
                table_name="alpha_signal_candidate",
                date_column="bar_dt",
                run_selector=f"run_id = '{manifest[module_name]['source_run_id']}'",
                start_iso=f"{request.target_year}-01-01",
                end_iso=f"{request.target_year}-12-31",
                focus_dates=focus_trading_dates,
                where_clause="run_id = ?",
                params=[manifest[module_name]["source_run_id"]],
                notes=("Alpha family released candidate surface locked by system_source_manifest."),
            )
        )
    rows.extend(alpha_rows)
    layer_statuses["alpha"] = len(alpha_rows) == len(ALPHA_FAMILY_MODULES) and (
        all_focus_dates_present(alpha_rows)
    )

    if "signal" not in manifest:
        evidence_issues.append("system_source_manifest is missing signal entry")
        planned_signal_focus_dates = list(focus_trading_dates)
    else:
        signal_row = _query_surface(
            db_path=Path(manifest["signal"]["source_db"]),
            layer="signal",
            surface_name="formal_signal_ledger",
            table_name="formal_signal_ledger",
            date_column="signal_dt",
            run_selector=f"run_id = '{manifest['signal']['source_run_id']}'",
            start_iso=f"{request.target_year}-01-01",
            end_iso=f"{request.target_year}-12-31",
            focus_dates=focus_trading_dates,
            where_clause="run_id = ?",
            params=[manifest["signal"]["source_run_id"]],
            notes="Released Signal ledger surface locked by system_source_manifest.",
        )
        rows.append(signal_row)
        layer_statuses["signal"] = all_focus_dates_present([signal_row])
        planned_signal_focus_dates = load_planned_signal_focus_dates(
            signal_db=Path(manifest["signal"]["source_db"]),
            signal_run_id=manifest["signal"]["source_run_id"],
            focus_dates=focus_trading_dates,
        )

    position_rows = _optional_group_rows(
        manifest=manifest,
        module_name="position",
        layer="position",
        surfaces=(
            ("position_candidate_ledger", "candidate_dt", "position candidate surface"),
            ("position_entry_plan", "entry_reference_dt", "entry plan surface"),
            ("position_exit_plan", "exit_reference_dt", "exit plan surface"),
        ),
        start_iso=f"{request.target_year}-01-01",
        end_iso=f"{request.target_year}-12-31",
        focus_dates=focus_trading_dates,
        evidence_issues=evidence_issues,
    )
    rows.extend(position_rows)
    position_ok = evaluate_position_focus_window(
        position_rows=position_rows,
        focus_dates=focus_trading_dates,
        planned_signal_focus_dates=planned_signal_focus_dates,
    )
    layer_statuses["position"] = position_ok

    portfolio_rows = _optional_group_rows(
        manifest=manifest,
        module_name="portfolio_plan",
        layer="portfolio_plan",
        surfaces=(
            ("portfolio_admission_ledger", "plan_dt", "portfolio admission surface"),
            (
                "portfolio_target_exposure",
                "exposure_valid_from",
                "portfolio target exposure surface",
            ),
        ),
        start_iso=f"{request.target_year}-01-01",
        end_iso=f"{request.target_year}-12-31",
        focus_dates=focus_trading_dates,
        evidence_issues=evidence_issues,
    )
    rows.extend(portfolio_rows)
    layer_statuses["portfolio_plan"] = evaluate_portfolio_plan_focus_window(
        portfolio_rows=portfolio_rows,
        portfolio_db=Path(manifest["portfolio_plan"]["source_db"])
        if "portfolio_plan" in manifest
        else data_root / "portfolio_plan.duckdb",
        portfolio_run_id=manifest["portfolio_plan"]["source_run_id"]
        if "portfolio_plan" in manifest
        else "",
        focus_dates=focus_trading_dates,
    )

    trade_rows = _optional_group_rows(
        manifest=manifest,
        module_name="trade",
        layer="trade",
        surfaces=(
            ("order_intent_ledger", "intent_dt", "order intent surface"),
            ("execution_plan_ledger", "execution_valid_from", "execution plan surface"),
            ("order_rejection_ledger", "rejection_dt", "order rejection surface"),
            ("fill_ledger", "execution_dt", "retained fill gap only; not sufficient condition"),
        ),
        start_iso=f"{request.target_year}-01-01",
        end_iso=f"{request.target_year}-12-31",
        focus_dates=focus_trading_dates,
        evidence_issues=evidence_issues,
    )
    rows.extend(trade_rows)
    layer_statuses["trade"] = evaluate_trade_focus_window(
        trade_rows=trade_rows,
        trade_db=Path(manifest["trade"]["source_db"])
        if "trade" in manifest
        else data_root / "trade.duckdb",
        trade_run_id=manifest["trade"]["source_run_id"] if "trade" in manifest else "",
        focus_dates=focus_trading_dates,
    )

    system_row = _query_surface(
        db_path=request.source_system_db,
        layer="system_readout",
        surface_name="system_chain_readout",
        table_name="system_chain_readout",
        date_column="readout_dt",
        run_selector=f"system_readout_run_id = '{released_system_run_id}'",
        start_iso=f"{request.target_year}-01-01",
        end_iso=f"{request.target_year}-12-31",
        focus_dates=focus_trading_dates,
        where_clause="system_readout_run_id = ?",
        params=[released_system_run_id],
        notes="Released System Readout surface locked to latest completed system_readout_run.",
    )
    rows.append(system_row)
    layer_statuses["system_readout"] = all_focus_dates_present([system_row])
    return rows, layer_statuses, evidence_issues


def _optional_group_rows(
    *,
    manifest: dict[str, dict[str, str]],
    module_name: str,
    layer: str,
    surfaces: tuple[tuple[str, str, str], ...],
    start_iso: str,
    end_iso: str,
    focus_dates: list[str],
    evidence_issues: list[str],
) -> list[CoverageMatrixRow]:
    if module_name not in manifest:
        evidence_issues.append(f"system_source_manifest is missing {module_name} entry")
        return []
    module = manifest[module_name]
    rows: list[CoverageMatrixRow] = []
    for table_name, date_column, note in surfaces:
        rows.append(
            _query_surface(
                db_path=Path(module["source_db"]),
                layer=layer,
                surface_name=table_name,
                table_name=table_name,
                date_column=date_column,
                run_selector=f"run_id = '{module['source_run_id']}'",
                start_iso=start_iso,
                end_iso=end_iso,
                focus_dates=focus_dates,
                where_clause="run_id = ?",
                params=[module["source_run_id"]],
                notes=note,
            )
        )
    return rows


def _recommend_next_card(
    *,
    layer_statuses: dict[str, bool],
    evidence_issues: list[str],
    full_year_gate_ok: bool,
) -> tuple[str, str]:
    if evidence_issues:
        return EVIDENCE_INCOMPLETE_CARD, "evidence_incomplete"
    if not layer_statuses.get("data", False):
        return DATA_REPAIR_CARD, "released_surface_gap:data"
    if not layer_statuses.get("malf", False):
        return MALF_REPAIR_CARD, "released_surface_gap:malf"
    if not layer_statuses.get("alpha", False) or not layer_statuses.get("signal", False):
        return ALPHA_SIGNAL_REPAIR_CARD, "released_surface_gap:alpha_signal"
    if not layer_statuses.get("position", False):
        return POSITION_REPAIR_CARD, "downstream_surface_gap:position"
    if not layer_statuses.get("portfolio_plan", False):
        return PORTFOLIO_PLAN_REPAIR_CARD, "downstream_surface_gap:portfolio_plan"
    if not layer_statuses.get("trade", False):
        return TRADE_REPAIR_CARD, "downstream_surface_gap:trade"
    if not layer_statuses.get("system_readout", False):
        return SYSTEM_REPAIR_CARD, "released_surface_gap:system_readout"
    if not full_year_gate_ok:
        return PIPELINE_REPAIR_CARD, "calendar_semantic_gap_only"
    return EVIDENCE_INCOMPLETE_CARD, "no_replay_gap_detected"


def _query_surface(
    *,
    db_path: Path,
    layer: str,
    surface_name: str,
    table_name: str,
    date_column: str,
    run_selector: str,
    start_iso: str,
    end_iso: str,
    focus_dates: list[str],
    where_clause: str | None = None,
    params: list[object] | None = None,
    notes: str,
) -> CoverageMatrixRow:
    filters = [f"{date_column} >= ?", f"{date_column} <= ?"]
    query_params = list(params or [])
    query_params.extend([start_iso, end_iso])
    if where_clause:
        filters.insert(0, where_clause)
    where_sql = " where " + " and ".join(filters)
    with duckdb.connect(str(db_path), read_only=True) as con:
        row = con.execute(
            f"""
            select min({date_column}), max({date_column}), count(*)
            from {table_name}
            {where_sql}
            """,
            query_params,
        ).fetchone()
        distinct_dates = {
            str(item[0])
            for item in con.execute(
                f"""
                select distinct {date_column}
                from {table_name}
                {where_sql}
                """,
                query_params,
            ).fetchall()
        }
    observed_start = None if row is None or row[0] is None else str(row[0])
    observed_end = None if row is None or row[1] is None else str(row[1])
    row_count = 0 if row is None or row[2] is None else int(row[2])
    missing_focus_dates = tuple(sorted(set(focus_dates) - distinct_dates))
    if missing_focus_dates:
        notes = f"{notes} missing focus dates: {', '.join(missing_focus_dates)}."
    return CoverageMatrixRow(
        layer=layer,
        surface_name=surface_name,
        db_path=str(db_path),
        table_name=table_name,
        run_selector=run_selector,
        date_column=date_column,
        observed_start=observed_start,
        observed_end=observed_end,
        row_count_2024=row_count,
        missing_focus_dates=missing_focus_dates,
        notes=notes,
    )
