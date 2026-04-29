from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from asteria.alpha.contracts import AlphaFamilyRequest


@dataclass(frozen=True)
class WavePosition:
    symbol: str
    timeframe: str
    bar_dt: date
    system_state: str
    wave_core_state: str
    direction: str | None
    new_count: int
    no_new_span: int
    transition_span: int
    update_rank: float | None
    stagnation_rank: float | None
    life_state: str
    position_quadrant: str
    service_version: str
    run_id: str


@dataclass(frozen=True)
class AlphaRows:
    events: list[tuple[object, ...]]
    scores: list[tuple[object, ...]]
    candidates: list[tuple[object, ...]]


def build_alpha_rows(
    source_rows: list[WavePosition],
    request: AlphaFamilyRequest,
    created_at: datetime,
) -> AlphaRows:
    events: list[tuple[object, ...]] = []
    scores: list[tuple[object, ...]] = []
    candidates: list[tuple[object, ...]] = []
    for source in source_rows:
        score = _score(source, request.alpha_family)
        qualified = _qualified(source, request.alpha_family, score)
        event_type = f"{request.alpha_family.lower()}_waveposition_opportunity"
        event_id = _id(
            request.alpha_family,
            source.symbol,
            source.timeframe,
            source.bar_dt.isoformat(),
            event_type,
            request.alpha_rule_version,
        )
        score_id = f"{event_id}|score"
        candidate_type = f"{request.alpha_family.lower()}_signal_candidate"
        candidate_id = f"{event_id}|{candidate_type}"
        source_key = _id(
            source.symbol, source.timeframe, source.bar_dt.isoformat(), source.service_version
        )
        events.append(
            (
                event_id,
                request.alpha_family,
                source.symbol,
                source.timeframe,
                source.bar_dt,
                event_type,
                "qualified" if qualified else "rejected",
                source_key,
                source.service_version,
                source.run_id,
                request.run_id,
                request.schema_version,
                request.alpha_rule_version,
                created_at,
            )
        )
        scores.append(
            (
                score_id,
                event_id,
                request.alpha_family,
                f"{request.alpha_family.lower()}_waveposition_score",
                score,
                "higher_is_stronger",
                _score_bucket(score),
                source.service_version,
                source.run_id,
                request.run_id,
                request.schema_version,
                request.alpha_rule_version,
                created_at,
            )
        )
        candidates.append(
            (
                candidate_id,
                event_id,
                request.alpha_family,
                source.symbol,
                source.timeframe,
                source.bar_dt,
                candidate_type,
                "candidate" if qualified else "filtered",
                _bias(source.direction),
                _confidence(score),
                "waveposition_rule_qualified" if qualified else "waveposition_rule_rejected",
                score,
                source.service_version,
                source.run_id,
                request.run_id,
                request.schema_version,
                request.alpha_rule_version,
                created_at,
            )
        )
    return AlphaRows(events=events, scores=scores, candidates=candidates)


def wave_position_from_row(row: tuple[Any, ...]) -> WavePosition:
    return WavePosition(
        symbol=str(row[0]),
        timeframe=str(row[1]),
        bar_dt=row[2],
        system_state=str(row[3]),
        wave_core_state=str(row[4]),
        direction=None if row[5] is None else str(row[5]),
        new_count=int(row[6] or 0),
        no_new_span=int(row[7] or 0),
        transition_span=int(row[8] or 0),
        update_rank=None if row[9] is None else float(row[9]),
        stagnation_rank=None if row[10] is None else float(row[10]),
        life_state=str(row[11]),
        position_quadrant=str(row[12]),
        service_version=str(row[13]),
        run_id=str(row[14]),
    )


def _score(source: WavePosition, family: str) -> float:
    update_rank = source.update_rank or 0.0
    stagnation_rank = source.stagnation_rank or 0.0
    if family == "BOF":
        return _clamp(update_rank * 0.7 + min(source.new_count, 3) / 3 * 0.3)
    if family == "TST":
        return _clamp(stagnation_rank * 0.75 + min(source.no_new_span, 3) / 3 * 0.25)
    if family == "PB":
        return _clamp(update_rank * 0.55 + min(source.no_new_span, 3) / 3 * 0.45)
    if family == "CPB":
        quadrant_bonus = 0.15 if source.position_quadrant == "extended_stagnant" else 0.0
        return _clamp(stagnation_rank * 0.85 + quadrant_bonus)
    if family == "BPB":
        return _clamp(min(source.transition_span, 3) / 3 * 0.7 + stagnation_rank * 0.3)
    raise ValueError(f"Unsupported Alpha family: {family}")


def _qualified(source: WavePosition, family: str, score: float) -> bool:
    alive = source.system_state in {"up_alive", "down_alive"}
    if family == "BOF":
        return alive and source.new_count > 0 and source.no_new_span == 0 and score >= 0.65
    if family == "TST":
        return alive and source.no_new_span >= 1 and score >= 0.65
    if family == "PB":
        return alive and source.no_new_span > 0 and source.update_rank is not None and score >= 0.55
    if family == "CPB":
        return source.position_quadrant == "extended_stagnant" and score >= 0.80
    if family == "BPB":
        return source.system_state == "transition" and source.transition_span >= 1 and score >= 0.35
    return False


def _score_bucket(score: float) -> str:
    if score >= 0.8:
        return "high"
    if score >= 0.5:
        return "medium"
    return "low"


def _confidence(score: float) -> str:
    if score >= 0.8:
        return "high"
    if score >= 0.5:
        return "medium"
    return "low"


def _bias(direction: str | None) -> str:
    if direction == "up":
        return "up_opportunity"
    if direction == "down":
        return "down_opportunity"
    return "neutral"


def _id(*parts: object) -> str:
    return "|".join(str(part) for part in parts)


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 6)
