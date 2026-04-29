from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from itertools import groupby

from asteria.signal.contracts import SignalBuildRequest


@dataclass(frozen=True)
class AlphaCandidate:
    alpha_candidate_id: str
    alpha_event_id: str
    alpha_family: str
    symbol: str
    timeframe: str
    bar_dt: date
    candidate_type: str
    candidate_state: str
    opportunity_bias: str
    confidence_bucket: str
    reason_code: str
    candidate_score: float
    source_malf_service_version: str
    run_id: str
    alpha_rule_version: str


@dataclass(frozen=True)
class SignalRows:
    snapshots: list[tuple[object, ...]]
    signals: list[tuple[object, ...]]
    components: list[tuple[object, ...]]


def candidate_from_row(row: tuple[object, ...]) -> AlphaCandidate:
    return AlphaCandidate(
        alpha_candidate_id=str(row[0]),
        alpha_event_id=str(row[1]),
        alpha_family=str(row[2]),
        symbol=str(row[3]),
        timeframe=str(row[4]),
        bar_dt=_coerce_date(row[5]),
        candidate_type=str(row[6]),
        candidate_state=str(row[7]),
        opportunity_bias=str(row[8]),
        confidence_bucket=str(row[9]),
        reason_code=str(row[10]),
        candidate_score=float(str(row[11])),
        source_malf_service_version=str(row[12]),
        run_id=str(row[13]),
        alpha_rule_version=str(row[14]),
    )


def _coerce_date(value: object) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise TypeError(f"unsupported bar_dt value: {value!r}")


def build_signal_rows(
    candidates: list[AlphaCandidate],
    request: SignalBuildRequest,
    created_at: datetime,
) -> SignalRows:
    ordered = sorted(candidates, key=lambda row: (row.symbol, row.timeframe, row.bar_dt))
    snapshots = [_snapshot_row(row, request, created_at) for row in ordered]
    signals: list[tuple[object, ...]] = []
    components: list[tuple[object, ...]] = []
    for key, group in groupby(ordered, key=lambda row: (row.symbol, row.timeframe, row.bar_dt)):
        group_rows = list(group)
        signal_row, component_rows = _aggregate_group(key, group_rows, request, created_at)
        signals.append(signal_row)
        components.extend(component_rows)
    return SignalRows(snapshots=snapshots, signals=signals, components=components)


def _snapshot_row(
    row: AlphaCandidate,
    request: SignalBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    snapshot_id = "|".join([request.run_id, row.alpha_family, row.alpha_candidate_id])
    return (
        snapshot_id,
        request.run_id,
        row.alpha_family,
        row.alpha_candidate_id,
        row.alpha_event_id,
        row.symbol,
        row.timeframe,
        row.bar_dt,
        row.candidate_type,
        row.candidate_state,
        row.opportunity_bias,
        row.confidence_bucket,
        row.reason_code,
        row.candidate_score,
        row.alpha_rule_version,
        row.source_malf_service_version,
        request.source_alpha_release_version,
        request.schema_version,
        request.signal_rule_version,
        created_at,
    )


def _aggregate_group(
    key: tuple[str, str, date],
    rows: list[AlphaCandidate],
    request: SignalBuildRequest,
    created_at: datetime,
) -> tuple[tuple[object, ...], list[tuple[object, ...]]]:
    symbol, timeframe, signal_dt = key
    active_rows = [row for row in rows if row.candidate_state == "candidate"]
    up_score = sum(row.candidate_score for row in active_rows if _bias_side(row) == "up")
    down_score = sum(row.candidate_score for row in active_rows if _bias_side(row) == "down")
    active_count = len(active_rows)
    raw_bias = _raw_signal_bias(up_score, down_score)
    signal_strength = (
        0.0 if active_count == 0 else round(abs(up_score - down_score) / active_count, 6)
    )
    signal_state = "active" if active_count > 0 and signal_strength >= 0.35 else "rejected"
    signal_bias = _published_signal_bias(raw_bias)
    signal_type = _signal_type(active_count, raw_bias, signal_state)
    reason_code = _reason_code(active_count, raw_bias, signal_state)
    confidence_bucket = _confidence_bucket(signal_strength, rows)
    signal_id = "|".join(
        [
            symbol,
            timeframe,
            signal_dt.isoformat(),
            signal_type,
            request.signal_rule_version,
        ]
    )
    component_rows = [
        _component_row(signal_id, row, request, raw_bias, active_count, created_at) for row in rows
    ]
    support_count = sum(1 for row in component_rows if row[5] == "support")
    conflict_count = sum(1 for row in component_rows if row[5] == "conflict")
    rejected_count = sum(1 for row in component_rows if row[5] == "rejected")
    signal_row = (
        signal_id,
        symbol,
        timeframe,
        signal_dt,
        signal_type,
        signal_state,
        signal_bias,
        signal_strength,
        confidence_bucket,
        reason_code,
        support_count,
        conflict_count,
        rejected_count,
        request.source_alpha_release_version,
        request.run_id,
        request.schema_version,
        request.signal_rule_version,
        created_at,
    )
    return signal_row, component_rows


def _raw_signal_bias(up_score: float, down_score: float) -> str:
    if up_score > down_score:
        return "up"
    if down_score > up_score:
        return "down"
    return "neutral"


def _published_signal_bias(raw_bias: str) -> str:
    if raw_bias == "up":
        return "up_opportunity"
    if raw_bias == "down":
        return "down_opportunity"
    return "neutral"


def _signal_type(active_count: int, raw_bias: str, signal_state: str) -> str:
    if active_count == 0:
        return "no_candidate_signal"
    if raw_bias == "neutral" or signal_state == "rejected":
        return "conflict_or_weak_signal"
    return "directional_opportunity"


def _reason_code(active_count: int, raw_bias: str, signal_state: str) -> str:
    if active_count == 0:
        return "no_active_alpha_candidate"
    if raw_bias == "neutral":
        return "alpha_family_conflict"
    if signal_state == "rejected":
        return "signal_strength_below_threshold"
    return "alpha_candidate_support"


def _confidence_bucket(strength: float, rows: list[AlphaCandidate]) -> str:
    if strength >= 0.65:
        return "high"
    if strength >= 0.35:
        return "medium"
    if any(row.confidence_bucket == "low" for row in rows):
        return "low"
    return "unranked"


def _component_row(
    signal_id: str,
    row: AlphaCandidate,
    request: SignalBuildRequest,
    raw_bias: str,
    active_count: int,
    created_at: datetime,
) -> tuple[object, ...]:
    role = _component_role(row, raw_bias, active_count)
    component_id = "|".join(
        [signal_id, row.alpha_family, row.alpha_candidate_id, request.signal_rule_version]
    )
    return (
        component_id,
        signal_id,
        request.run_id,
        row.alpha_family,
        row.alpha_candidate_id,
        role,
        round(row.candidate_score, 6),
        row.alpha_rule_version,
        request.signal_rule_version,
        request.source_alpha_release_version,
        created_at,
    )


def _component_role(row: AlphaCandidate, raw_bias: str, active_count: int) -> str:
    if row.candidate_state != "candidate":
        return "rejected"
    if active_count == 0:
        return "neutral"
    if raw_bias == "neutral":
        return "conflict"
    if _bias_side(row) == raw_bias:
        return "support"
    return "conflict"


def _bias_side(row: AlphaCandidate) -> str:
    if row.opportunity_bias in {"up", "up_opportunity"}:
        return "up"
    if row.opportunity_bias in {"down", "down_opportunity"}:
        return "down"
    return "neutral"
