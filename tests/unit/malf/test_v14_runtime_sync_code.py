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
from asteria.malf.core_engine import (
    Candidate,
    Pivot,
    Transition,
    _candidate_from_pivot,
    _replace_active_candidate,
)


def _seed_market_base_day(path: Path, symbols: tuple[str, ...]) -> None:
    bootstrap_market_base_day_database(path)
    with duckdb.connect(str(path)) as con:
        for symbol in symbols:
            if symbol == "DELAY.SH":
                rows = _delayed_break_rows(symbol)
            elif symbol == "REPLACE.SH":
                rows = _replacement_rows(symbol)
            elif symbol == "REFRESH.SH":
                rows = _refresh_rows(symbol)
            else:
                rows = _default_rows(symbol)
            _insert_rows(con, rows)


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


def test_malf_v14_core_policy_fields_and_snapshot_surface(tmp_path: Path) -> None:
    _seed_market_base_day(
        tmp_path / "asteria-data" / "market_base_day.duckdb",
        symbols=("UPCASE.SH", "REPLACE.SH"),
    )
    request = _request_v14(tmp_path, "malf-v14-policy-run-001")

    run_malf_day_core_build(request)
    run_malf_day_lifespan_build(request)
    run_malf_day_service_build(request)
    audit_summary = run_malf_day_audit(request)

    with duckdb.connect(str(request.core_db), read_only=True) as con:
        core_run_columns = {
            row[1] for row in con.execute("pragma table_info('malf_core_run')").fetchall()
        }
        assert {
            "pivot_detection_rule_version",
            "core_event_ordering_version",
            "price_compare_policy",
            "epsilon_policy",
        }.issubset(core_run_columns)

        pivot_columns = {
            row[1] for row in con.execute("pragma table_info('malf_pivot_ledger')").fetchall()
        }
        assert "pivot_detection_rule_version" in pivot_columns

        candidate_columns = {
            row[1] for row in con.execute("pragma table_info('malf_candidate_ledger')").fetchall()
        }
        assert "candidate_event_type" in candidate_columns

        snapshot_columns = {
            row[1]
            for row in con.execute("pragma table_info('malf_core_state_snapshot')").fetchall()
        }
        assert {
            "system_state",
            "wave_core_state",
            "direction",
            "transition_boundary_high",
            "transition_boundary_low",
            "active_candidate_guard_pivot_id",
            "pivot_detection_rule_version",
            "core_event_ordering_version",
            "price_compare_policy",
            "epsilon_policy",
        }.issubset(snapshot_columns)

        core_run_row = con.execute(
            """
            select pivot_detection_rule_version, core_event_ordering_version,
                   price_compare_policy, epsilon_policy
            from malf_core_run
            where run_id = ?
            """,
            [request.run_id],
        ).fetchone()
        assert core_run_row == (
            request.pivot_detection_rule_version,
            request.core_event_ordering_version,
            request.price_compare_policy,
            request.epsilon_policy,
        )

    payload = json.loads(Path(audit_summary.report_path).read_text(encoding="utf-8"))
    assert payload["pivot_detection_rule_version"] == request.pivot_detection_rule_version
    assert payload["core_event_ordering_version"] == request.core_event_ordering_version
    assert payload["price_compare_policy"] == request.price_compare_policy
    assert payload["epsilon_policy"] == request.epsilon_policy
    assert payload["core_snapshot_count"] > 0


def test_malf_v14_break_uses_bar_level_break_and_transition_snapshot(tmp_path: Path) -> None:
    _seed_market_base_day(
        tmp_path / "asteria-data" / "market_base_day.duckdb",
        symbols=("DELAY.SH",),
    )
    request = _request_v14(tmp_path, "malf-v14-break-run-001")

    run_malf_day_core_build(request)

    with duckdb.connect(str(request.core_db), read_only=True) as con:
        break_row = con.execute(
            """
            select break_dt
            from malf_break_ledger
            where run_id = ?
            """,
            [request.run_id],
        ).fetchone()
        assert break_row is not None
        assert break_row[0] == date(2024, 1, 8)

        snapshot_row = con.execute(
            """
            select system_state, wave_core_state, old_wave_id
            from malf_core_state_snapshot
            where run_id = ? and symbol = 'DELAY.SH' and bar_dt = ?
            """,
            [request.run_id, date(2024, 1, 8)],
        ).fetchone()
        assert snapshot_row == ("transition", "terminated", snapshot_row[2])


def test_malf_v14_candidate_event_types_cover_refresh_replacement_and_confirmed(
    tmp_path: Path,
) -> None:
    _seed_market_base_day(
        tmp_path / "asteria-data" / "market_base_day.duckdb",
        symbols=("REPLACE.SH",),
    )
    request = _request_v14(tmp_path, "malf-v14-candidate-events-run-001")

    run_malf_day_core_build(request)

    with duckdb.connect(str(request.core_db), read_only=True) as con:
        event_types = {
            row[0]
            for row in con.execute(
                """
                select distinct candidate_event_type
                from malf_candidate_ledger
                where run_id = ?
                """,
                [request.run_id],
            ).fetchall()
        }

    assert {"opposite_direction_candidate_replacement", "confirmed"}.issubset(event_types)


def test_malf_v14_same_direction_refresh_marks_old_candidate() -> None:
    old_guard = Pivot("old-guard", "TEST.SH", date(2024, 1, 10), date(2024, 1, 11), "L", 10.0, 0)
    new_guard = Pivot("new-guard", "TEST.SH", date(2024, 1, 12), date(2024, 1, 13), "L", 10.5, 0)
    transition = Transition(
        transition_id="transition-1",
        old_wave_id="wave-1",
        break_id="break-1",
        old_direction="up",
        old_progress=Pivot(
            "old-progress", "TEST.SH", date(2024, 1, 9), date(2024, 1, 10), "H", 15.0, 0
        ),
        old_guard=old_guard,
        break_dt=date(2024, 1, 11),
        transition_boundary_high=15.0,
        transition_boundary_low=10.0,
    )
    request = _request_v14(Path("H:/Asteria-temp"), "malf-v14-candidate-helper-run-001")
    active_candidate = Candidate(
        candidate_id="candidate-old",
        transition_id=transition.transition_id,
        guard=old_guard,
        direction="up",
        reference_price=transition.transition_boundary_high,
    )

    refreshed_candidate = _candidate_from_pivot(transition, new_guard, request)

    assert refreshed_candidate is not None
    assert refreshed_candidate.event_type == "candidate_created"

    _replace_active_candidate(active_candidate, refreshed_candidate)

    assert active_candidate.event_type == "same_direction_candidate_refresh"
    assert active_candidate.invalidated_by_candidate_id == refreshed_candidate.candidate_id


def test_malf_v14_transition_reference_is_context_scoped_and_service_matches_core_snapshot(
    tmp_path: Path,
) -> None:
    _seed_market_base_day(
        tmp_path / "asteria-data" / "market_base_day.duckdb",
        symbols=("REPLACE.SH",),
    )
    request = _request_v14(tmp_path, "malf-v14-reference-run-001")

    run_malf_day_core_build(request)
    run_malf_day_lifespan_build(request)
    run_malf_day_service_build(request)

    with duckdb.connect(str(request.core_db), read_only=True) as con:
        confirm_row = con.execute(
            """
            select w.symbol, w.confirm_dt, w.confirm_pivot_id,
                   t.old_progress_extreme_pivot_id, t.transition_boundary_high,
                   t.transition_boundary_low
            from malf_wave_ledger w
            join malf_transition_ledger t on t.new_wave_id = w.wave_id and t.run_id = w.run_id
            where w.run_id = ? and w.birth_type <> 'initial'
            """,
            [request.run_id],
        ).fetchone()
        assert confirm_row is not None
        symbol, confirm_dt, confirm_pivot_id, boundary_ref_pivot_id, boundary_high, boundary_low = (
            confirm_row
        )

        structure_row = con.execute(
            """
            select reference_pivot_id
            from malf_structure_ledger
            where run_id = ?
              and pivot_id = ?
              and structure_context = 'transition_candidate'
            """,
            [request.run_id, confirm_pivot_id],
        ).fetchone()
        assert structure_row is not None
        assert structure_row[0] == boundary_ref_pivot_id

        core_snapshot_row = con.execute(
            """
            select transition_boundary_high, transition_boundary_low, new_wave_id
            from malf_core_state_snapshot
            where run_id = ? and symbol = ? and bar_dt = ?
            """,
            [request.run_id, symbol, confirm_dt],
        ).fetchone()
        assert core_snapshot_row is not None
        assert core_snapshot_row[0] == boundary_high
        assert core_snapshot_row[1] == boundary_low

    with duckdb.connect(str(request.lifespan_db), read_only=True) as con:
        lifespan_row = con.execute(
            """
            select transition_boundary_high, transition_boundary_low, new_wave_id
            from malf_lifespan_snapshot
            where run_id = ? and symbol = ? and bar_dt = ? and new_wave_id is not null
            """,
            [request.run_id, symbol, confirm_dt],
        ).fetchone()
        assert lifespan_row == core_snapshot_row

    with duckdb.connect(str(request.service_db), read_only=True) as con:
        service_row = con.execute(
            """
            select transition_boundary_high, transition_boundary_low, new_wave_id
            from malf_wave_position
            where run_id = ? and symbol = ? and bar_dt = ? and new_wave_id is not null
            """,
            [request.run_id, symbol, confirm_dt],
        ).fetchone()
        assert service_row == core_snapshot_row


def _insert_rows(con: duckdb.DuckDBPyConnection, rows: list[tuple[object, ...]]) -> None:
    placeholders = ", ".join(["?"] * 20)
    con.executemany(f"insert into market_base_bar values ({placeholders})", rows)


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


def _delayed_break_rows(symbol: str) -> list[tuple[object, ...]]:
    price_points = [
        (10.0, 9.0),
        (12.0, 10.0),
        (9.5, 8.0),
        (14.0, 9.0),
        (13.0, 10.5),
        (12.0, 10.0),
        (15.0, 10.5),
        (14.5, 9.5),
        (13.0, 8.5),
        (13.5, 9.0),
        (12.5, 7.5),
        (11.0, 8.0),
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


def _refresh_rows(symbol: str) -> list[tuple[object, ...]]:
    price_points = [
        (20.0, 19.0),
        (22.0, 20.0),
        (19.0, 17.0),
        (24.0, 18.0),
        (21.0, 18.5),
        (25.0, 20.0),
        (23.0, 19.0),
        (21.0, 16.0),
        (20.5, 17.0),
        (20.0, 15.8),
        (20.5, 16.5),
        (21.0, 15.0),
        (24.0, 17.0),
        (26.0, 18.0),
        (23.0, 19.0),
    ]
    return [_bar(symbol, i, high, low) for i, (high, low) in enumerate(price_points)]
