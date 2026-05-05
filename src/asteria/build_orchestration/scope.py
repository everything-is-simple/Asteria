from __future__ import annotations

from calendar import monthrange
from dataclasses import asdict, dataclass
from datetime import date


@dataclass(frozen=True)
class BuildScope:
    timeframe: str
    target_start_dt: date
    target_end_dt: date
    compute_start_dt: date | None = None
    compute_end_dt: date | None = None

    def as_dict(self) -> dict[str, str | None]:
        payload = asdict(self)
        return {
            key: value.isoformat() if isinstance(value, date) else value
            for key, value in payload.items()
        }


def resolve_target_scope(
    *,
    timeframe: str = "day",
    year: int | None = None,
    month: int | None = None,
    day: str | None = None,
    start_dt: str | None = None,
    end_dt: str | None = None,
) -> BuildScope:
    _validate_timeframe(timeframe)
    supplied_modes = sum(
        [
            day is not None,
            start_dt is not None or end_dt is not None,
            year is not None,
        ]
    )
    if supplied_modes != 1:
        raise ValueError("Specify exactly one date scope: --date, --start/end, or --year")
    if month is not None and year is None:
        raise ValueError("--month requires --year")

    if day is not None:
        target = date.fromisoformat(day)
        return BuildScope(timeframe, target, target, target, target)

    if start_dt is not None or end_dt is not None:
        if not (start_dt and end_dt):
            raise ValueError("--start-dt and --end-dt must be provided together")
        start = date.fromisoformat(start_dt)
        end = date.fromisoformat(end_dt)
        if start > end:
            raise ValueError("start_dt cannot be later than end_dt")
        return BuildScope(timeframe, start, end, start, end)

    assert year is not None
    if month is None:
        start = date(year, 1, 1)
        end = date(year, 12, 31)
    else:
        if month < 1 or month > 12:
            raise ValueError("--month must be between 1 and 12")
        start = date(year, month, 1)
        end = date(year, month, monthrange(year, month)[1])
    return BuildScope(timeframe, start, end, start, end)


def _validate_timeframe(timeframe: str) -> None:
    if timeframe != "day":
        raise ValueError("Only day timeframe is implemented for the first builder sample")
