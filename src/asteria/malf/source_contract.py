from __future__ import annotations

from asteria.malf.contracts import MalfDayRequest

MALF_SOURCE_PRICE_LINE = "analysis_price_line"
MALF_SOURCE_ADJ_MODE = "backward"


def market_base_day_clauses(request: MalfDayRequest) -> tuple[list[str], list[object]]:
    clauses = [
        "timeframe = ?",
        "price_line = ?",
        "adj_mode = ?",
    ]
    params: list[object] = [
        request.timeframe,
        MALF_SOURCE_PRICE_LINE,
        MALF_SOURCE_ADJ_MODE,
    ]
    if request.start_date:
        clauses.append("bar_dt >= ?")
        params.append(request.start_date)
    if request.end_date:
        clauses.append("bar_dt <= ?")
        params.append(request.end_date)
    if request.symbols:
        clauses.append(f"symbol in ({', '.join(['?'] * len(request.symbols))})")
        params.extend(request.symbols)
    return clauses, params
