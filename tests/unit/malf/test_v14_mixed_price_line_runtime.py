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


def _seed_market_base_day(path: Path, symbols: tuple[str, ...]) -> None:
    bootstrap_market_base_day_database(path)
    with duckdb.connect(str(path)) as con:
        for symbol in symbols:
            rows = _replacement_rows(symbol) if symbol == "REPLACE.SH" else _default_rows(symbol)
            _insert_rows(con, rows)


def _add_execution_price_line_rows(path: Path) -> int:
    with duckdb.connect(str(path)) as con:
        inserted = con.execute(
            """
            insert into market_base_bar
            select
                symbol,
                asset_type,
                timeframe,
                bar_dt,
                trade_date,
                'execution_price_line',
                'none',
                open_px,
                high_px,
                low_px,
                close_px,
                volume,
                amount,
                source_vendor,
                source_batch_id,
                source_revision || '|execution',
                source_path,
                run_id,
                schema_version,
                created_at
            from market_base_bar
            where price_line = 'analysis_price_line'
              and adj_mode = 'backward'
            """
        ).rowcount
    return 0 if inserted is None else int(inserted)


def _request_v14(tmp_path: Path, run_id: str) -> MalfDayRequest:
    return MalfDayRequest(
        source_db=tmp_path / "asteria-data" / "market_base_day.duckdb",
        core_db=tmp_path / "asteria-data" / "malf_core_day.duckdb",
        lifespan_db=tmp_path / "asteria-data" / "malf_lifespan_day.duckdb",
        service_db=tmp_path / "asteria-data" / "malf_service_day.duckdb",
        report_root=tmp_path / "asteria-report",
        validated_root=tmp_path / "asteria-validated",
        temp_root=tmp_path / "asteria-temp",
        run_id=run_id,
        mode="bounded",
        schema_version="malf-v1-4-runtime-sync-v1",
        core_rule_version="core-rule-fractal-1bar-v1",
        pivot_detection_rule_version="pivot-rule-fractal-1bar-v1",
        core_event_ordering_version="core-event-order-v1",
        price_compare_policy="strict",
        epsilon_policy="none_after_price_normalization",
        lifespan_rule_version="lifespan-rule-v1",
        sample_version="sample-v1",
        service_version="service-v1",
        start_dt="2024-01-01",
        end_dt="2024-01-31",
        symbol_limit=20,
    )


def test_malf_v14_core_build_ignores_execution_price_line_rows(tmp_path: Path) -> None:
    source_db = tmp_path / "asteria-data" / "market_base_day.duckdb"
    _seed_market_base_day(source_db, symbols=("UPCASE.SH", "REPLACE.SH"))
    _add_execution_price_line_rows(source_db)
    request = _request_v14(tmp_path, "malf-v14-mixed-price-line-core-run-001")

    with duckdb.connect(str(source_db), read_only=True) as con:
        analysis_count = con.execute(
            """
            select count(*)
            from market_base_bar
            where timeframe = 'day'
              and price_line = 'analysis_price_line'
              and adj_mode = 'backward'
            """
        ).fetchone()[0]

    summary = run_malf_day_core_build(request)

    assert summary.input_row_count == analysis_count

    with duckdb.connect(str(request.core_db), read_only=True) as con:
        duplicate_candidates = con.execute(
            """
            select count(*)
            from (
                select candidate_id, count(*) row_count
                from malf_candidate_ledger
                where run_id = ?
                group by candidate_id
                having row_count > 1
            )
            """,
            [request.run_id],
        ).fetchone()

    assert duplicate_candidates == (0,)


def test_malf_v14_service_build_ignores_execution_price_line_duplicates(tmp_path: Path) -> None:
    source_db = tmp_path / "asteria-data" / "market_base_day.duckdb"
    _seed_market_base_day(source_db, symbols=("UPCASE.SH", "REPLACE.SH"))
    _add_execution_price_line_rows(source_db)
    request = _request_v14(tmp_path, "malf-v14-mixed-price-line-service-run-001")

    run_malf_day_core_build(request)
    run_malf_day_lifespan_build(request)
    run_malf_day_service_build(request)

    with duckdb.connect(str(request.service_db), read_only=True) as con:
        duplicate_rows = con.execute(
            """
            select count(*)
            from (
                select symbol, timeframe, bar_dt, service_version, count(*) row_count
                from malf_wave_position
                where run_id = ?
                group by symbol, timeframe, bar_dt, service_version
                having row_count > 1
            )
            """,
            [request.run_id],
        ).fetchone()

    assert duplicate_rows == (0,)


def test_malf_v14_audit_trace_stays_aligned_with_mixed_price_lines(tmp_path: Path) -> None:
    source_db = tmp_path / "asteria-data" / "market_base_day.duckdb"
    _seed_market_base_day(source_db, symbols=("UPCASE.SH", "REPLACE.SH"))
    _add_execution_price_line_rows(source_db)
    request = _request_v14(tmp_path, "malf-v14-mixed-price-line-audit-run-001")

    run_malf_day_core_build(request)
    run_malf_day_lifespan_build(request)
    run_malf_day_service_build(request)
    audit_summary = run_malf_day_audit(request)

    with duckdb.connect(str(request.service_db), read_only=True) as con:
        audit_rows = dict(
            con.execute(
                """
                select check_name, failed_count
                from malf_interface_audit
                where run_id = ?
                  and check_name in (
                      'core_new_candidate_replaces_previous',
                      'service_wave_position_natural_key_unique',
                      'service_v13_trace_matches_lifespan'
                  )
                """,
                [request.run_id],
            ).fetchall()
        )

    payload = json.loads(Path(audit_summary.report_path).read_text(encoding="utf-8"))

    assert audit_rows == {
        "core_new_candidate_replaces_previous": 0,
        "service_wave_position_natural_key_unique": 0,
        "service_v13_trace_matches_lifespan": 0,
    }
    assert payload["hard_fail_count"] == 0


def _insert_rows(con: duckdb.DuckDBPyConnection, rows: list[tuple[object, ...]]) -> None:
    placeholders = ", ".join(["?"] * 20)
    con.executemany(f"insert into market_base_bar values ({placeholders})", rows)


def _default_rows(symbol: str) -> list[tuple[object, ...]]:
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
    return [_bar(symbol, i, high, low) for i, (high, low) in enumerate(price_points)]


def _replacement_rows(symbol: str) -> list[tuple[object, ...]]:
    price_points = [
        (10.0, 9.0),
        (12.0, 10.0),
        (9.5, 8.0),
        (14.0, 9.0),
        (12.0, 10.0),
        (15.0, 11.0),
        (14.0, 10.5),
        (11.0, 7.0),
        (13.5, 8.5),
        (12.0, 8.2),
        (16.0, 9.5),
        (13.0, 10.0),
    ]
    return [_bar(symbol, i, high, low) for i, (high, low) in enumerate(price_points)]


def _bar(symbol: str, offset: int, high: float, low: float) -> tuple[object, ...]:
    bar_dt = date(2024, 1, 1) + timedelta(days=offset)
    close = round((high + low) / 2, 2)
    return (
        symbol,
        "stock",
        "day",
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
        "2026-05-04 00:00:00",
    )
