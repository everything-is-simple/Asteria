from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from asteria.trade.contracts import TradeBuildRequest


@dataclass(frozen=True)
class PortfolioPlanInput:
    portfolio_admission_id: str
    position_candidate_id: str
    symbol: str
    timeframe: str
    plan_dt: date
    admission_state: str
    admission_reason: str
    target_exposure_id: str | None
    exposure_type: str | None
    target_weight: float | None
    target_notional: float | None
    target_quantity_hint: float | None
    source_position_release_version: str
    portfolio_plan_rule_version: str
    source_portfolio_plan_release_version: str
    source_portfolio_plan_run_id: str
    trim_reason: str | None


@dataclass(frozen=True)
class TradeRows:
    snapshots: list[tuple[object, ...]]
    intents: list[tuple[object, ...]]
    execution_plans: list[tuple[object, ...]]
    fills: list[tuple[object, ...]]
    rejections: list[tuple[object, ...]]


def portfolio_plan_input_from_row(row: tuple[object, ...]) -> PortfolioPlanInput:
    return PortfolioPlanInput(
        portfolio_admission_id=str(row[0]),
        position_candidate_id=str(row[1]),
        symbol=str(row[2]),
        timeframe=str(row[3]),
        plan_dt=_coerce_date(row[4]),
        admission_state=str(row[5]),
        admission_reason="" if row[6] is None else str(row[6]),
        target_exposure_id=None if row[7] is None else str(row[7]),
        exposure_type=None if row[8] is None else str(row[8]),
        target_weight=None if row[9] is None else _coerce_float(row[9]),
        target_notional=None if row[10] is None else _coerce_float(row[10]),
        target_quantity_hint=None if row[11] is None else _coerce_float(row[11]),
        source_position_release_version=str(row[12]),
        portfolio_plan_rule_version=str(row[13]),
        source_portfolio_plan_release_version=str(row[14]),
        source_portfolio_plan_run_id=str(row[15]),
        trim_reason=None if row[16] is None else str(row[16]),
    )


def build_trade_rows(
    inputs: list[PortfolioPlanInput],
    request: TradeBuildRequest,
    created_at: datetime,
) -> TradeRows:
    ordered = sorted(
        inputs,
        key=lambda row: (row.symbol, row.timeframe, row.plan_dt, row.portfolio_admission_id),
    )
    snapshots = [_snapshot_row(row, request, created_at) for row in ordered]
    intents: list[tuple[object, ...]] = []
    execution_plans: list[tuple[object, ...]] = []
    fills: list[tuple[object, ...]] = []
    rejections: list[tuple[object, ...]] = []
    for row in ordered:
        if _is_tradeable(row):
            order_intent_id = _order_intent_id(row, request)
            intents.append(_order_intent_row(row, request, created_at, order_intent_id))
            execution_plan_id = _execution_plan_id(order_intent_id, request)
            execution_plans.append(
                _execution_plan_row(row, request, created_at, order_intent_id, execution_plan_id)
            )
            continue
        rejections.append(_rejection_row(row, request, created_at))
    return TradeRows(
        snapshots=snapshots,
        intents=intents,
        execution_plans=execution_plans,
        fills=fills,
        rejections=rejections,
    )


def _is_tradeable(row: PortfolioPlanInput) -> bool:
    return row.admission_state == "admitted" and row.target_exposure_id is not None


def _snapshot_row(
    row: PortfolioPlanInput,
    request: TradeBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    return (
        "|".join([request.run_id, row.portfolio_admission_id]),
        request.run_id,
        row.portfolio_admission_id,
        row.position_candidate_id,
        row.symbol,
        row.timeframe,
        row.plan_dt,
        row.admission_state,
        row.admission_reason,
        row.target_exposure_id,
        row.exposure_type,
        row.target_weight,
        row.target_notional,
        row.target_quantity_hint,
        row.portfolio_plan_rule_version,
        row.source_position_release_version,
        request.source_portfolio_plan_release_version,
        request.run_id,
        request.schema_version,
        request.trade_rule_version,
        created_at,
    )


def _order_intent_row(
    row: PortfolioPlanInput,
    request: TradeBuildRequest,
    created_at: datetime,
    order_intent_id: str,
) -> tuple[object, ...]:
    return (
        order_intent_id,
        request.run_id,
        row.portfolio_admission_id,
        row.position_candidate_id,
        row.symbol,
        row.timeframe,
        row.plan_dt,
        _order_side(row),
        "intended",
        row.target_quantity_hint,
        row.target_weight,
        row.target_notional,
        row.source_position_release_version,
        request.source_portfolio_plan_release_version,
        request.run_id,
        request.schema_version,
        request.trade_rule_version,
        created_at,
    )


def _execution_plan_row(
    row: PortfolioPlanInput,
    request: TradeBuildRequest,
    created_at: datetime,
    order_intent_id: str,
    execution_plan_id: str,
) -> tuple[object, ...]:
    return (
        execution_plan_id,
        request.run_id,
        order_intent_id,
        "portfolio_plan_target",
        None,
        row.plan_dt,
        row.plan_dt,
        "planned",
        request.source_portfolio_plan_release_version,
        request.run_id,
        request.schema_version,
        request.trade_rule_version,
        created_at,
    )


def _rejection_row(
    row: PortfolioPlanInput,
    request: TradeBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    reason = row.admission_reason or row.trim_reason or "portfolio_plan_not_tradeable"
    return (
        "|".join([request.run_id, row.portfolio_admission_id, reason, request.trade_rule_version]),
        request.run_id,
        row.portfolio_admission_id,
        row.plan_dt,
        reason,
        "intent",
        request.source_portfolio_plan_release_version,
        request.run_id,
        request.schema_version,
        request.trade_rule_version,
        created_at,
    )


def _order_intent_id(row: PortfolioPlanInput, request: TradeBuildRequest) -> str:
    return "|".join(
        [request.run_id, row.portfolio_admission_id, _order_side(row), request.trade_rule_version]
    )


def _execution_plan_id(order_intent_id: str, request: TradeBuildRequest) -> str:
    return "|".join([order_intent_id, "planned", request.trade_rule_version])


def _order_side(row: PortfolioPlanInput) -> str:
    if row.target_weight is not None and row.target_weight < 0:
        return "sell"
    return "buy"


def _coerce_date(value: object) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise TypeError(f"unsupported plan_dt value: {value!r}")


def _coerce_float(value: object) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        return float(value)
    raise TypeError(f"unsupported numeric value: {value!r}")
