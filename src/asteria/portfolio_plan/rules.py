from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from asteria.portfolio_plan.contracts import PortfolioPlanBuildRequest


@dataclass(frozen=True)
class PositionPlanInput:
    position_candidate_id: str
    signal_id: str
    symbol: str
    timeframe: str
    candidate_dt: date
    candidate_type: str
    candidate_state: str
    position_bias: str
    reason_code: str
    source_position_run_id: str
    position_rule_version: str
    entry_plan_id: str | None
    exit_plan_id: str | None


@dataclass(frozen=True)
class PortfolioPlanRows:
    snapshots: list[tuple[object, ...]]
    constraints: list[tuple[object, ...]]
    admissions: list[tuple[object, ...]]
    exposures: list[tuple[object, ...]]
    trims: list[tuple[object, ...]]


def position_input_from_row(row: tuple[object, ...]) -> PositionPlanInput:
    return PositionPlanInput(
        position_candidate_id=str(row[0]),
        signal_id=str(row[1]),
        symbol=str(row[2]),
        timeframe=str(row[3]),
        candidate_dt=_coerce_date(row[4]),
        candidate_type=str(row[5]),
        candidate_state=str(row[6]),
        position_bias=str(row[7]),
        reason_code=str(row[8]),
        source_position_run_id=str(row[9]),
        position_rule_version=str(row[10]),
        entry_plan_id=None if row[11] is None else str(row[11]),
        exit_plan_id=None if row[12] is None else str(row[12]),
    )


def build_portfolio_plan_rows(
    positions: list[PositionPlanInput],
    request: PortfolioPlanBuildRequest,
    created_at: datetime,
) -> PortfolioPlanRows:
    ordered = sorted(
        positions,
        key=lambda row: (row.symbol, row.timeframe, row.candidate_dt, row.position_candidate_id),
    )
    latest_planned_ids = _latest_planned_candidate_ids(ordered)
    admitted_ids = set(
        _rank_latest_planned(ordered, latest_planned_ids)[: request.max_active_symbols]
    )
    snapshots = [_snapshot_row(row, request, created_at) for row in ordered]
    constraints = [_capacity_constraint_row(request, created_at)]
    admissions: list[tuple[object, ...]] = []
    exposures: list[tuple[object, ...]] = []
    trims: list[tuple[object, ...]] = []
    for row in ordered:
        state, reason = _admission_decision(row, latest_planned_ids, admitted_ids)
        admission_id = _admission_id(row.position_candidate_id, request)
        admissions.append(_admission_row(row, request, created_at, admission_id, state, reason))
        if state in {"admitted", "trimmed"}:
            target_weight = 1.0 / request.max_active_symbols if state == "admitted" else 0.0
            exposures.append(
                _target_exposure_row(row, request, created_at, admission_id, target_weight)
            )
        if state == "trimmed":
            trims.append(_trim_row(request, created_at, admission_id))
    return PortfolioPlanRows(
        snapshots=snapshots,
        constraints=constraints,
        admissions=admissions,
        exposures=exposures,
        trims=trims,
    )


def _latest_planned_candidate_ids(rows: list[PositionPlanInput]) -> set[str]:
    latest_by_symbol: dict[str, PositionPlanInput] = {}
    for row in rows:
        if row.candidate_state != "planned":
            continue
        current = latest_by_symbol.get(row.symbol)
        if current is None or (row.candidate_dt, row.position_candidate_id) > (
            current.candidate_dt,
            current.position_candidate_id,
        ):
            latest_by_symbol[row.symbol] = row
    return {row.position_candidate_id for row in latest_by_symbol.values()}


def _rank_latest_planned(
    rows: list[PositionPlanInput],
    latest_planned_ids: set[str],
) -> list[str]:
    latest = [row for row in rows if row.position_candidate_id in latest_planned_ids]
    ranked = sorted(latest, key=lambda row: (-row.candidate_dt.toordinal(), row.symbol))
    return [row.position_candidate_id for row in ranked]


def _admission_decision(
    row: PositionPlanInput,
    latest_planned_ids: set[str],
    admitted_ids: set[str],
) -> tuple[str, str]:
    if row.candidate_state != "planned":
        return "rejected", "position_candidate_rejected"
    if row.position_candidate_id not in latest_planned_ids:
        return "expired", "superseded_by_newer_position_candidate"
    if row.position_candidate_id in admitted_ids:
        return "admitted", "within_capacity_constraint"
    return "trimmed", "max_active_symbols_constraint"


def _snapshot_row(
    row: PositionPlanInput,
    request: PortfolioPlanBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    return (
        "|".join([request.run_id, row.position_candidate_id]),
        request.run_id,
        row.position_candidate_id,
        row.symbol,
        row.timeframe,
        row.candidate_dt,
        row.candidate_state,
        row.position_bias,
        row.entry_plan_id,
        row.exit_plan_id,
        row.position_rule_version,
        request.source_position_release_version,
        row.source_position_run_id,
        request.schema_version,
        request.portfolio_plan_rule_version,
        created_at,
    )


def _capacity_constraint_row(
    request: PortfolioPlanBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    return (
        "|".join(["global", "max_active_symbols", request.portfolio_plan_rule_version]),
        "global",
        "max_active_symbols",
        "capacity",
        float(request.max_active_symbols),
        "active",
        request.run_id,
        request.schema_version,
        request.portfolio_plan_rule_version,
        request.source_position_release_version,
        created_at,
    )


def _admission_row(
    row: PositionPlanInput,
    request: PortfolioPlanBuildRequest,
    created_at: datetime,
    admission_id: str,
    state: str,
    reason: str,
) -> tuple[object, ...]:
    return (
        admission_id,
        row.position_candidate_id,
        row.symbol,
        row.timeframe,
        row.candidate_dt,
        state,
        reason,
        request.source_position_release_version,
        request.run_id,
        request.schema_version,
        request.portfolio_plan_rule_version,
        created_at,
    )


def _target_exposure_row(
    row: PositionPlanInput,
    request: PortfolioPlanBuildRequest,
    created_at: datetime,
    admission_id: str,
    target_weight: float,
) -> tuple[object, ...]:
    return (
        "|".join([admission_id, "target_weight", request.portfolio_plan_rule_version]),
        admission_id,
        "target_weight",
        target_weight,
        None,
        None,
        row.candidate_dt,
        None,
        request.run_id,
        request.schema_version,
        request.portfolio_plan_rule_version,
        request.source_position_release_version,
        created_at,
    )


def _trim_row(
    request: PortfolioPlanBuildRequest,
    created_at: datetime,
    admission_id: str,
) -> tuple[object, ...]:
    pre_trim = 1.0 / request.max_active_symbols
    return (
        "|".join(
            [admission_id, "max_active_symbols_constraint", request.portfolio_plan_rule_version]
        ),
        admission_id,
        "max_active_symbols_constraint",
        pre_trim,
        0.0,
        "max_active_symbols",
        request.run_id,
        request.schema_version,
        request.portfolio_plan_rule_version,
        request.source_position_release_version,
        created_at,
    )


def _admission_id(position_candidate_id: str, request: PortfolioPlanBuildRequest) -> str:
    return "|".join([position_candidate_id, request.portfolio_plan_rule_version])


def _coerce_date(value: object) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise TypeError(f"unsupported candidate_dt value: {value!r}")
