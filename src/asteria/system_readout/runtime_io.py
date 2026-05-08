from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import duckdb

from asteria.system_readout.contracts import SystemReadoutBuildRequest
from asteria.system_readout.rules import (
    ModuleStatusInput,
    ReadoutInput,
    ReadoutRefs,
    SourceManifestInput,
)


def load_chain_inputs(
    request: SystemReadoutBuildRequest,
) -> tuple[list[SourceManifestInput], list[ModuleStatusInput], list[ReadoutInput]]:
    malf_run_id, malf_schema, malf_audit_ref, malf_audit_status = _load_latest_run(
        request.source_malf_service_db,
        "malf_service_run",
        "malf_interface_audit",
    )
    alpha_manifest: list[SourceManifestInput] = []
    alpha_candidates: dict[tuple[str, date], list[str]] = {}
    alpha_release_versions: set[str] = set()
    alpha_audit_refs: list[str] = []
    alpha_audit_statuses: list[str] = []
    for family, path in request.alpha_db_paths.items():
        run_id, schema_version, audit_ref, audit_status = _load_latest_run(
            path,
            "alpha_family_run",
            "alpha_source_audit",
            family=family,
        )
        alpha_release_versions.add(run_id)
        alpha_audit_refs.append(audit_ref)
        alpha_audit_statuses.append(audit_status)
        alpha_manifest.append(
            SourceManifestInput(
                module_name=f"alpha_{family.lower()}",
                source_db=str(path),
                source_run_id=run_id,
                source_release_version=run_id,
                source_schema_version=schema_version,
                source_audit_ref=audit_ref,
                source_audit_status=audit_status,
            )
        )
        for key, candidate_ids in _load_alpha_candidates(path, run_id).items():
            alpha_candidates.setdefault(key, []).extend(candidate_ids)
    signal_run_id, signal_schema, signal_audit_ref, signal_audit_status = _load_latest_run(
        request.source_signal_db,
        "signal_run",
        "signal_audit",
    )
    (
        position_run_id,
        position_schema,
        position_audit_ref,
        position_audit_status,
    ) = _load_latest_run(
        request.source_position_db,
        "position_run",
        "position_audit",
    )
    (
        portfolio_run_id,
        portfolio_schema,
        portfolio_audit_ref,
        portfolio_audit_status,
    ) = _load_latest_run(
        request.source_portfolio_plan_db,
        "portfolio_plan_run",
        "portfolio_plan_audit",
    )
    trade_run_id, trade_schema, trade_audit_ref, trade_audit_status = _load_latest_run(
        request.source_trade_db,
        "trade_run",
        "trade_audit",
    )
    source_manifests = [
        SourceManifestInput(
            "malf",
            str(request.source_malf_service_db),
            malf_run_id,
            malf_run_id,
            malf_schema,
            malf_audit_ref,
            malf_audit_status,
        ),
        *alpha_manifest,
        SourceManifestInput(
            "signal",
            str(request.source_signal_db),
            signal_run_id,
            signal_run_id,
            signal_schema,
            signal_audit_ref,
            signal_audit_status,
        ),
        SourceManifestInput(
            "position",
            str(request.source_position_db),
            position_run_id,
            position_run_id,
            position_schema,
            position_audit_ref,
            position_audit_status,
        ),
        SourceManifestInput(
            "portfolio_plan",
            str(request.source_portfolio_plan_db),
            portfolio_run_id,
            portfolio_run_id,
            portfolio_schema,
            portfolio_audit_ref,
            portfolio_audit_status,
        ),
        SourceManifestInput(
            "trade",
            str(request.source_trade_db),
            trade_run_id,
            trade_run_id,
            trade_schema,
            trade_audit_ref,
            trade_audit_status,
        ),
    ]
    alpha_latest_release = sorted(alpha_release_versions)[-1]
    alpha_audit_status = "pass" if set(alpha_audit_statuses) == {"pass"} else "fail"
    module_statuses = [
        ModuleStatusInput(
            "malf",
            malf_run_id,
            malf_run_id,
            "released",
            malf_audit_ref,
            malf_audit_status,
        ),
        ModuleStatusInput(
            "alpha",
            alpha_latest_release,
            alpha_latest_release,
            "released",
            ";".join(alpha_audit_refs),
            alpha_audit_status,
        ),
        ModuleStatusInput(
            "signal",
            signal_run_id,
            signal_run_id,
            "released",
            signal_audit_ref,
            signal_audit_status,
        ),
        ModuleStatusInput(
            "position",
            position_run_id,
            position_run_id,
            "released",
            position_audit_ref,
            position_audit_status,
        ),
        ModuleStatusInput(
            "portfolio_plan",
            portfolio_run_id,
            portfolio_run_id,
            "released",
            portfolio_audit_ref,
            portfolio_audit_status,
        ),
        ModuleStatusInput(
            "trade",
            trade_run_id,
            trade_run_id,
            "released",
            trade_audit_ref,
            trade_audit_status,
        ),
    ]
    readouts = _build_readout_inputs(
        request,
        malf_wave_positions=_load_malf_rows(request.source_malf_service_db, malf_run_id, request),
        alpha_candidates=alpha_candidates,
        signal_rows=_load_signal_rows(request.source_signal_db, signal_run_id, request),
        position_rows=_load_position_rows(request.source_position_db, position_run_id, request),
        portfolio_rows=_load_portfolio_rows(
            request.source_portfolio_plan_db,
            portfolio_run_id,
            request,
        ),
        trade_rows=_load_trade_rows(request.source_trade_db, trade_run_id, request),
        has_upstream_audit_gap=any(item.source_audit_status != "pass" for item in source_manifests),
    )
    return source_manifests, module_statuses, readouts


def _load_latest_run(
    db_path: Path,
    run_table: str,
    audit_table: str,
    *,
    family: str | None = None,
) -> tuple[str, str, str, str]:
    if not db_path.exists():
        raise FileNotFoundError(f"Missing source DB: {db_path}")
    where = " where status = 'completed'"
    params: list[object] = []
    if family is not None:
        where += " and alpha_family = ?"
        params.append(family)
    query = f"select * from {run_table}{where} order by created_at desc limit 1"
    with duckdb.connect(str(db_path), read_only=True) as con:
        row = con.execute(query, params).fetchone()
        if row is None:
            raise ValueError(f"Missing completed run row in {run_table}: {db_path}")
        run_id = str(row[0])
        schema_version = str(
            row[11]
            if "alpha" in run_table
            or run_table in {"position_run", "portfolio_plan_run", "trade_run", "signal_run"}
            else row[8]
        )
        audit_query = (
            f"select count(*), min(audit_id) from {audit_table} "
            "where run_id = ? and severity = 'hard' and status = 'fail'"
        )
        audit_row = con.execute(audit_query, [run_id]).fetchone()
    if audit_row is None:
        return run_id, schema_version, "", "pass"
    audit_fail_count, audit_ref = audit_row
    return (
        run_id,
        schema_version,
        "" if audit_ref is None else str(audit_ref),
        "pass" if int(audit_fail_count) == 0 else "fail",
    )


def _load_malf_rows(
    db_path: Path,
    run_id: str,
    request: SystemReadoutBuildRequest,
) -> dict[tuple[str, date], tuple[str, str | None, str | None]]:
    query = """
        select symbol, bar_dt, wave_id, wave_core_state, system_state
        from malf_wave_position
        where timeframe = 'day' and run_id = ?
    """
    rows = _filtered_rows(
        db_path,
        query,
        [run_id],
        request,
        date_column_index=1,
        symbol_index=0,
    )
    return {
        (str(row[0]), coerce_date(row[1])): (
            str(row[2]),
            nullable_str(row[3]),
            nullable_str(row[4]),
        )
        for row in rows
    }


def _load_alpha_candidates(db_path: Path, run_id: str) -> dict[tuple[str, date], list[str]]:
    with duckdb.connect(str(db_path), read_only=True) as con:
        rows = con.execute(
            """
            select symbol, bar_dt, alpha_candidate_id
            from alpha_signal_candidate
            where run_id = ?
            """,
            [run_id],
        ).fetchall()
    result: dict[tuple[str, date], list[str]] = {}
    for symbol, bar_dt, candidate_id in rows:
        key = (str(symbol), coerce_date(bar_dt))
        result.setdefault(key, []).append(str(candidate_id))
    return result


def _load_signal_rows(
    db_path: Path,
    run_id: str,
    request: SystemReadoutBuildRequest,
) -> dict[tuple[str, date], tuple[str, list[str]]]:
    query = """
        select s.symbol, s.signal_dt, s.signal_id, c.alpha_candidate_id
        from formal_signal_ledger s
        left join signal_component_ledger c on s.signal_id = c.signal_id
        where s.timeframe = 'day' and s.run_id = ?
        order by s.symbol, s.signal_dt, c.alpha_candidate_id
    """
    rows = _filtered_rows(db_path, query, [run_id], request, date_column_index=1, symbol_index=0)
    result: dict[tuple[str, date], tuple[str, list[str]]] = {}
    for symbol, signal_dt, signal_id, alpha_candidate_id in rows:
        key = (str(symbol), coerce_date(signal_dt))
        current = result.get(key)
        if current is None:
            current = (str(signal_id), [])
        if alpha_candidate_id is not None:
            current[1].append(str(alpha_candidate_id))
        result[key] = current
    return result


def _load_position_rows(
    db_path: Path,
    run_id: str,
    request: SystemReadoutBuildRequest,
) -> dict[tuple[str, date], str]:
    query = """
        select symbol, candidate_dt, position_candidate_id
        from position_candidate_ledger
        where timeframe = 'day' and run_id = ?
    """
    rows = _filtered_rows(db_path, query, [run_id], request, date_column_index=1, symbol_index=0)
    return {(str(row[0]), coerce_date(row[1])): str(row[2]) for row in rows}


def _load_portfolio_rows(
    db_path: Path,
    run_id: str,
    request: SystemReadoutBuildRequest,
) -> dict[tuple[str, date], str]:
    query = """
        select symbol, plan_dt, portfolio_admission_id
        from portfolio_admission_ledger
        where timeframe = 'day' and run_id = ?
    """
    rows = _filtered_rows(db_path, query, [run_id], request, date_column_index=1, symbol_index=0)
    return {(str(row[0]), coerce_date(row[1])): str(row[2]) for row in rows}


def _load_trade_rows(
    db_path: Path,
    run_id: str,
    request: SystemReadoutBuildRequest,
) -> dict[tuple[str, date], str]:
    query = """
        select symbol, intent_dt, order_intent_id
        from order_intent_ledger
        where timeframe = 'day' and run_id = ?
    """
    rows = _filtered_rows(db_path, query, [run_id], request, date_column_index=1, symbol_index=0)
    return {(str(row[0]), coerce_date(row[1])): str(row[2]) for row in rows}


def _filtered_rows(
    db_path: Path,
    query: str,
    params: list[object],
    request: SystemReadoutBuildRequest,
    *,
    date_column_index: int,
    symbol_index: int,
) -> list[tuple[object, ...]]:
    with duckdb.connect(str(db_path), read_only=True) as con:
        rows = con.execute(query, params).fetchall()
    filtered: list[tuple[object, ...]] = []
    for row in rows:
        row_date = coerce_date(row[date_column_index])
        if request.start_date and row_date < request.start_date:
            continue
        if request.end_date and row_date > request.end_date:
            continue
        filtered.append(row)
    if request.symbol_limit is None:
        return filtered
    allowed_symbols = sorted({str(row[symbol_index]) for row in filtered})[: request.symbol_limit]
    return [row for row in filtered if str(row[symbol_index]) in set(allowed_symbols)]


def _build_readout_inputs(
    request: SystemReadoutBuildRequest,
    *,
    malf_wave_positions: dict[tuple[str, date], tuple[str, str | None, str | None]],
    alpha_candidates: dict[tuple[str, date], list[str]],
    signal_rows: dict[tuple[str, date], tuple[str, list[str]]],
    position_rows: dict[tuple[str, date], str],
    portfolio_rows: dict[tuple[str, date], str],
    trade_rows: dict[tuple[str, date], str],
    has_upstream_audit_gap: bool,
) -> list[ReadoutInput]:
    keys = sorted(
        set(malf_wave_positions)
        | set(alpha_candidates)
        | set(signal_rows)
        | set(position_rows)
        | set(portfolio_rows)
        | set(trade_rows)
    )
    readouts: list[ReadoutInput] = []
    for symbol, readout_dt in keys:
        malf = malf_wave_positions.get((symbol, readout_dt))
        alpha_ids = alpha_candidates.get((symbol, readout_dt), [])
        signal = signal_rows.get((symbol, readout_dt))
        alpha_ref = (
            None
            if signal
            and any(alpha_candidate_id not in set(alpha_ids) for alpha_candidate_id in signal[1])
            else ";".join(alpha_ids) or None
        )
        refs = ReadoutRefs(
            malf_ref=None if malf is None else malf[0],
            alpha_ref=alpha_ref,
            signal_ref=None if signal is None else signal[0],
            position_ref=position_rows.get((symbol, readout_dt)),
            portfolio_plan_ref=portfolio_rows.get((symbol, readout_dt)),
            trade_ref=trade_rows.get((symbol, readout_dt)),
        )
        readouts.append(
            ReadoutInput(
                symbol=symbol,
                timeframe=request.timeframe,
                readout_dt=readout_dt,
                refs=refs,
                wave_core_state=None if malf is None else malf[1],
                system_state=None if malf is None else malf[2],
                has_upstream_audit_gap=has_upstream_audit_gap,
            )
        )
    return readouts


def coerce_date(value: object) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise TypeError(f"unsupported date value: {value!r}")


def nullable_str(value: object) -> str | None:
    return None if value is None else str(value)
