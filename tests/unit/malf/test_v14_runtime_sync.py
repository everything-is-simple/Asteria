from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import duckdb
from tests.unit.malf.test_bounded_proof_runner import _insert_rows, _request

from asteria.malf.bootstrap import run_malf_day_core_build
from asteria.malf.core_engine import Candidate, Pivot, _candidate_event_type


def _seed_v14_market_base_day(path: Path) -> None:
    from asteria.data.schema import bootstrap_market_base_day_database

    bootstrap_market_base_day_database(path)
    with duckdb.connect(str(path)) as con:
        _insert_rows(con, _raw_break_before_pivot_rows("EARLYBREAK.SH"))
        _insert_rows(con, _candidate_churn_rows("CHURN.SH"))


def _bar(symbol: str, offset: int, high: float, low: float) -> tuple[object, ...]:
    bar_dt = date(2024, 2, 1) + timedelta(days=offset)
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
        "malf-v14-fixture",
        f"rev-{symbol}",
        f"H:/fixture/{symbol}.txt",
        "seed-run-v14-001",
        "data-bootstrap-v1",
        "2026-05-05 00:00:00",
    )


def _raw_break_before_pivot_rows(symbol: str) -> list[tuple[object, ...]]:
    price_points = [
        (10.0, 9.0),
        (12.0, 10.0),  # H0
        (9.5, 8.0),  # L1
        (14.0, 9.0),  # H2 initial up
        (12.0, 10.0),
        (15.0, 11.0),  # HH progress
        (14.0, 10.5),
        (13.8, 7.5),  # first raw-bar break; not a pivot low against guard 8
        (13.2, 7.0),  # later pivot low
        (14.4, 9.2),
        (12.0, 7.4),
        (14.0, 8.5),
        (9.0, 6.0),
    ]
    return [_bar(symbol, i, high, low) for i, (high, low) in enumerate(price_points)]


def _candidate_churn_rows(symbol: str) -> list[tuple[object, ...]]:
    price_points = [
        (20.0, 19.0),
        (22.0, 20.0),  # H0
        (19.0, 17.0),  # L1
        (24.0, 18.0),  # H2 initial up
        (21.0, 18.5),  # HL guard
        (26.0, 20.0),  # HH progress
        (24.0, 19.5),
        (21.0, 16.0),  # raw-bar break
        (22.0, 15.8),  # first L candidate -> up created
        (22.2, 18.0),
        (22.5, 15.5),  # second L candidate -> up refresh
        (23.0, 17.0),
        (25.0, 18.0),  # H candidate -> opposite replacement to down
        (24.0, 18.2),
        (23.0, 15.0),  # L confirm < boundary_low
        (24.0, 16.0),
    ]
    return [_bar(symbol, i, high, low) for i, (high, low) in enumerate(price_points)]


def _execution_line_dupes(rows: list[tuple[object, ...]]) -> list[tuple[object, ...]]:
    dupes: list[tuple[object, ...]] = []
    for row in rows:
        row_list = list(row)
        row_list[5] = "execution_price_line"
        row_list[6] = "none"
        row_list[7] = float(row_list[7]) + 1000.0
        row_list[8] = float(row_list[8]) + 1000.0
        row_list[9] = float(row_list[9]) + 1000.0
        row_list[10] = float(row_list[10]) + 1000.0
        row_list[17] = "seed-run-v14-execution"
        dupes.append(tuple(row_list))
    return dupes


def _v14_request(tmp_path: Path, run_id: str) -> object:
    from dataclasses import replace

    return replace(
        _request(tmp_path, run_id),
        start_dt="2024-02-01",
        end_dt="2024-02-29",
    )


def test_malf_v14_core_run_records_runtime_policy_fields_and_snapshot_surface(
    tmp_path: Path,
) -> None:
    _seed_v14_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    request = _v14_request(tmp_path, "malf-v14-core-meta-run-001")

    run_malf_day_core_build(request)

    with duckdb.connect(str(request.core_db), read_only=True) as con:
        core_run_row = con.execute(
            """
            select pivot_detection_rule_version, core_event_ordering_version,
                   price_compare_policy, epsilon_policy, source_market_base_run_id
            from malf_core_run
            where run_id = ?
            """,
            [request.run_id],
        ).fetchone()
        assert core_run_row is not None
        assert core_run_row == (
            "pivot-fractal-1bar-v1",
            "core-event-order-v1",
            "strict",
            "none_after_price_normalization",
            "seed-run-v14-001",
        )

        snapshot_count = con.execute(
            "select count(*) from malf_core_state_snapshot where run_id = ?",
            [request.run_id],
        ).fetchone()[0]
        assert snapshot_count > 0

        uninitialized_rows = con.execute(
            """
            select count(*) from malf_core_state_snapshot
            where run_id = ? and system_state = 'uninitialized'
            """,
            [request.run_id],
        ).fetchone()[0]
        assert uninitialized_rows > 0


def test_malf_v14_core_break_uses_first_raw_bar_breach_not_later_pivot(
    tmp_path: Path,
) -> None:
    _seed_v14_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    request = _v14_request(tmp_path, "malf-v14-raw-break-run-001")

    run_malf_day_core_build(request)

    with duckdb.connect(str(request.core_db), read_only=True) as con:
        first_break_dt = con.execute(
            """
            select min(break_dt)
            from malf_break_ledger
            where run_id = ? and wave_id like 'EARLYBREAK.SH|%'
            """,
            [request.run_id],
        ).fetchone()[0]
        assert first_break_dt == date(2024, 2, 8)


def test_malf_v14_candidate_ledger_distinguishes_runtime_event_types(
    tmp_path: Path,
) -> None:
    _seed_v14_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    request = _v14_request(tmp_path, "malf-v14-candidate-types-run-001")

    run_malf_day_core_build(request)

    with duckdb.connect(str(request.core_db), read_only=True) as con:
        event_types = {
            row[0]
            for row in con.execute(
                """
                select distinct candidate_event_type
                from malf_candidate_ledger
                where run_id = ? and candidate_event_type is not null
                """,
                [request.run_id],
            ).fetchall()
        }

    assert {"candidate_created", "confirmed"}.issubset(event_types)


def test_malf_v14_candidate_event_type_classification_covers_refresh_and_replacement() -> None:
    active = Candidate(
        candidate_id="c1",
        transition_id="t1",
        guard=Pivot("p1", "TEST.SH", date(2024, 2, 9), date(2024, 2, 10), "L", 10.0, 0),
        direction="up",
        reference_price=15.0,
        event_type="candidate_created",
    )

    assert _candidate_event_type(None, "up") == "candidate_created"
    assert _candidate_event_type(active, "up") == "same_direction_candidate_refresh"
    assert _candidate_event_type(active, "down") == "opposite_direction_candidate_replacement"


def test_malf_v14_core_filters_to_analysis_backward_line_only(tmp_path: Path) -> None:
    from asteria.data.schema import bootstrap_market_base_day_database

    source_db = tmp_path / "asteria-data" / "market_base_day.duckdb"
    bootstrap_market_base_day_database(source_db)
    base_rows = _raw_break_before_pivot_rows("DUALLINE.SH")
    with duckdb.connect(str(source_db)) as con:
        _insert_rows(con, base_rows)
        _insert_rows(con, _execution_line_dupes(base_rows))

    request = _v14_request(tmp_path, "malf-v14-line-filter-run-001")
    run_malf_day_core_build(request)

    expected_bar_count = len(base_rows)
    with duckdb.connect(str(request.core_db), read_only=True) as con:
        snapshot_count = con.execute(
            "select count(*) from malf_core_state_snapshot where run_id = ?",
            [request.run_id],
        ).fetchone()[0]
        max_pivot_price = con.execute(
            "select max(pivot_price) from malf_pivot_ledger where run_id = ?",
            [request.run_id],
        ).fetchone()[0]

    assert snapshot_count == expected_bar_count
    assert max_pivot_price < 100.0
