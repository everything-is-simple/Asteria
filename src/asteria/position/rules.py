from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from asteria.position.contracts import PositionBuildRequest


@dataclass(frozen=True)
class SignalInput:
    signal_id: str
    symbol: str
    timeframe: str
    signal_dt: date
    signal_type: str
    signal_state: str
    signal_bias: str
    signal_strength: float
    confidence_bucket: str
    reason_code: str
    source_alpha_release_version: str
    run_id: str
    schema_version: str
    signal_rule_version: str


@dataclass(frozen=True)
class PositionRows:
    snapshots: list[tuple[object, ...]]
    candidates: list[tuple[object, ...]]
    entries: list[tuple[object, ...]]
    exits: list[tuple[object, ...]]


def signal_from_row(row: tuple[object, ...]) -> SignalInput:
    return SignalInput(
        signal_id=str(row[0]),
        symbol=str(row[1]),
        timeframe=str(row[2]),
        signal_dt=_coerce_date(row[3]),
        signal_type=str(row[4]),
        signal_state=str(row[5]),
        signal_bias=str(row[6]),
        signal_strength=float(str(row[7])),
        confidence_bucket=str(row[8]),
        reason_code=str(row[9]),
        source_alpha_release_version=str(row[10]),
        run_id=str(row[11]),
        schema_version=str(row[12]),
        signal_rule_version=str(row[13]),
    )


def build_position_rows(
    signals: list[SignalInput],
    request: PositionBuildRequest,
    created_at: datetime,
) -> PositionRows:
    ordered = sorted(signals, key=lambda row: (row.symbol, row.timeframe, row.signal_dt))
    snapshots = [_snapshot_row(row, request, created_at) for row in ordered]
    candidates: list[tuple[object, ...]] = []
    entries: list[tuple[object, ...]] = []
    exits: list[tuple[object, ...]] = []
    for row in ordered:
        candidate = _candidate_row(row, request, created_at)
        candidates.append(candidate)
        if candidate[6] == "planned":
            entries.append(_entry_row(str(candidate[0]), row, request, created_at))
            exits.append(_exit_row(str(candidate[0]), row, request, created_at))
    return PositionRows(
        snapshots=snapshots,
        candidates=candidates,
        entries=entries,
        exits=exits,
    )


def _snapshot_row(
    row: SignalInput,
    request: PositionBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    return (
        "|".join([request.run_id, row.signal_id]),
        request.run_id,
        row.signal_id,
        row.symbol,
        row.timeframe,
        row.signal_dt,
        row.signal_type,
        row.signal_state,
        row.signal_bias,
        row.signal_strength,
        row.confidence_bucket,
        row.reason_code,
        row.signal_rule_version,
        request.source_signal_release_version,
        row.run_id,
        request.schema_version,
        request.position_rule_version,
        created_at,
    )


def _candidate_row(
    row: SignalInput,
    request: PositionBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    planned = row.signal_state == "active" and row.signal_type == "directional_opportunity"
    candidate_type = "directional_position_candidate" if planned else "rejected_position_candidate"
    candidate_state = "planned" if planned else "rejected"
    position_bias = _position_bias(row.signal_bias) if planned else "neutral_candidate"
    reason_code = "signal_released_for_position" if planned else row.reason_code
    candidate_id = "|".join([row.signal_id, candidate_type, request.position_rule_version])
    return (
        candidate_id,
        row.signal_id,
        row.symbol,
        row.timeframe,
        row.signal_dt,
        candidate_type,
        candidate_state,
        position_bias,
        reason_code,
        request.source_signal_release_version,
        request.run_id,
        request.schema_version,
        request.position_rule_version,
        created_at,
    )


def _entry_row(
    candidate_id: str,
    row: SignalInput,
    request: PositionBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    entry_type = "signal_follow_entry"
    return (
        "|".join([candidate_id, entry_type, request.position_rule_version]),
        candidate_id,
        entry_type,
        "next_session_open_plan",
        row.signal_dt,
        row.signal_dt,
        None,
        "planned",
        request.run_id,
        request.schema_version,
        request.position_rule_version,
        request.source_signal_release_version,
        created_at,
    )


def _exit_row(
    candidate_id: str,
    row: SignalInput,
    request: PositionBuildRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    exit_type = "signal_invalidation_exit"
    return (
        "|".join([candidate_id, exit_type, request.position_rule_version]),
        candidate_id,
        exit_type,
        "signal_invalidated_or_expired",
        row.signal_dt,
        row.signal_dt,
        None,
        "planned",
        request.run_id,
        request.schema_version,
        request.position_rule_version,
        request.source_signal_release_version,
        created_at,
    )


def _position_bias(signal_bias: str) -> str:
    if signal_bias == "up_opportunity":
        return "long_candidate"
    if signal_bias == "down_opportunity":
        return "short_candidate"
    return "neutral_candidate"


def _coerce_date(value: object) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise TypeError(f"unsupported signal_dt value: {value!r}")
