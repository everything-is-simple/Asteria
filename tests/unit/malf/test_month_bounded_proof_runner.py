from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import duckdb

from asteria.data.schema import bootstrap_market_base_day_database
from asteria.malf.bootstrap import (
    run_malf_day_audit,
    run_malf_day_core_build,
    run_malf_day_lifespan_build,
    run_malf_day_service_build,
)
from asteria.malf.contracts import MalfDayRequest


def _seed_market_base_month(path: Path, symbols: tuple[str, ...] = ("UPCASE.SH",)) -> None:
    bootstrap_market_base_day_database(path)
    with duckdb.connect(str(path)) as con:
        for symbol in symbols:
            rows = _opposite_break_rows(symbol, timeframe="month", step_days=31)
            if symbol == "SAME.SH":
                rows = _same_direction_rows(symbol, timeframe="month", step_days=31)
            placeholders = ", ".join(["?"] * 20)
            con.executemany(f"insert into market_base_bar values ({placeholders})", rows)


def _bar(
    symbol: str,
    offset: int,
    high: float,
    low: float,
    *,
    timeframe: str,
    step_days: int,
) -> tuple[object, ...]:
    bar_dt = date(2024, 1, 1) + timedelta(days=offset * step_days)
    close = round((high + low) / 2, 2)
    return (
        symbol,
        "stock",
        timeframe,
        bar_dt.isoformat(),
        bar_dt.isoformat(),
        "analysis_price_line",
        "backward",
        close,
        high,
        low,
        close,
        1000.0 + offset,
        10000.0 + offset,
        "unit_fixture",
        "malf-fixture",
        f"rev-{symbol}",
        f"H:/fixture/{symbol}.txt",
        "seed-run-001",
        "data-bootstrap-v1",
        "2026-04-28 00:00:00",
    )


def _opposite_break_rows(
    symbol: str, *, timeframe: str, step_days: int
) -> list[tuple[object, ...]]:
    price_points = [
        (10.0, 9.0),
        (12.0, 10.0),
        (9.5, 8.0),
        (14.0, 9.0),
        (12.0, 10.0),
        (15.0, 11.0),
        (13.0, 10.5),
        (14.0, 10.8),
        (11.0, 7.0),
        (13.5, 8.5),
        (9.0, 6.0),
        (10.0, 7.0),
        (8.5, 5.5),
    ]
    return [
        _bar(symbol, i, high, low, timeframe=timeframe, step_days=step_days)
        for i, (high, low) in enumerate(price_points)
    ]


def _same_direction_rows(
    symbol: str, *, timeframe: str, step_days: int
) -> list[tuple[object, ...]]:
    price_points = [
        (20.0, 19.0),
        (22.0, 20.0),
        (19.0, 17.0),
        (24.0, 18.0),
        (21.0, 18.5),
        (25.0, 20.0),
        (23.0, 19.0),
        (24.0, 19.5),
        (20.0, 16.0),
        (20.5, 20.0),
        (21.0, 15.5),
        (24.0, 20.0),
        (27.0, 21.0),
        (25.0, 22.0),
    ]
    return [
        _bar(symbol, i, high, low, timeframe=timeframe, step_days=step_days)
        for i, (high, low) in enumerate(price_points)
    ]


def test_malf_month_bounded_proof_uses_month_timeframe_and_passes_audit(
    tmp_path: Path,
) -> None:
    _seed_market_base_month(
        tmp_path / "asteria-data" / "market_base_month.duckdb",
        symbols=("UPCASE.SH", "SAME.SH"),
    )
    request = MalfDayRequest(
        source_db=tmp_path / "asteria-data" / "market_base_month.duckdb",
        core_db=tmp_path / "asteria-data" / "malf_core_month.duckdb",
        lifespan_db=tmp_path / "asteria-data" / "malf_lifespan_month.duckdb",
        service_db=tmp_path / "asteria-data" / "malf_service_month.duckdb",
        report_root=tmp_path / "asteria-report",
        validated_root=tmp_path / "asteria-validated",
        temp_root=tmp_path / "asteria-temp",
        run_id="malf-month-bounded-run-001",
        mode="bounded",
        schema_version="malf-v1-4-runtime-sync-v1",
        timeframe="month",
        core_rule_version="core-rule-fractal-1bar-v1",
        lifespan_rule_version="lifespan-dense-month-v1",
        sample_version="malf-month-formal-2024-s2-v1",
        service_version="malf-wave-position-month-v1",
        start_dt="2024-01-01",
        end_dt="2024-12-31",
        symbol_limit=10,
    )

    core_summary = run_malf_day_core_build(request)
    run_malf_day_lifespan_build(request)
    service_summary = run_malf_day_service_build(request)
    audit_summary = run_malf_day_audit(request)

    assert core_summary.input_row_count == 24
    assert service_summary.published_row_count > 0

    with duckdb.connect(str(request.core_db), read_only=True) as con:
        assert (
            con.execute(
                "select distinct timeframe from malf_core_run where run_id = ?",
                [request.run_id],
            ).fetchone()[0]
            == "month"
        )
    with duckdb.connect(str(request.service_db), read_only=True) as con:
        assert (
            con.execute(
                "select count(*) from malf_wave_position where timeframe <> 'month'"
            ).fetchone()[0]
            == 0
        )

    report_payload = json.loads(Path(audit_summary.report_path).read_text(encoding="utf-8"))
    assert report_payload["timeframe"] == "month"
    assert report_payload["hard_fail_count"] == 0
