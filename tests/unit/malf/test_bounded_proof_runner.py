from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import duckdb
import pytest

from asteria.data.schema import bootstrap_market_base_day_database
from asteria.malf.bootstrap import (
    run_malf_day_audit,
    run_malf_day_core_build,
    run_malf_day_lifespan_build,
    run_malf_day_service_build,
)
from asteria.malf.contracts import MalfDayRequest


def _seed_market_base_day(path: Path, symbols: tuple[str, ...] = ("UPCASE.SH",)) -> None:
    bootstrap_market_base_day_database(path)
    with duckdb.connect(str(path)) as con:
        for symbol in symbols:
            rows = _opposite_break_rows(symbol)
            if symbol == "SAME.SH":
                rows = _same_direction_rows(symbol)
            _insert_rows(con, rows)


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
        "2026-04-28 00:00:00",
    )


def _opposite_break_rows(symbol: str) -> list[tuple[object, ...]]:
    price_points = [
        (10.0, 9.0),
        (12.0, 10.0),  # H0
        (9.5, 8.0),  # L1
        (14.0, 9.0),  # H2 initial up
        (12.0, 10.0),  # HL
        (15.0, 11.0),  # HH progress
        (13.0, 10.5),
        (14.0, 10.8),
        (11.0, 7.0),  # break HL
        (13.5, 8.5),  # candidate down guard
        (9.0, 6.0),  # opposite down confirmation
        (10.0, 7.0),
        (8.5, 5.5),
    ]
    return [_bar(symbol, i, high, low) for i, (high, low) in enumerate(price_points)]


def _same_direction_rows(symbol: str) -> list[tuple[object, ...]]:
    price_points = [
        (20.0, 19.0),
        (22.0, 20.0),  # H0
        (19.0, 17.0),  # L1
        (24.0, 18.0),  # H2 initial up
        (21.0, 18.5),  # HL
        (25.0, 20.0),  # HH progress
        (23.0, 19.0),
        (24.0, 19.5),
        (20.0, 16.0),  # break HL
        (20.5, 20.0),
        (21.0, 15.5),  # candidate up guard
        (24.0, 20.0),
        (27.0, 21.0),  # same-direction up confirmation
        (25.0, 22.0),
    ]
    return [_bar(symbol, i, high, low) for i, (high, low) in enumerate(price_points)]


def _request(tmp_path: Path, run_id: str, mode: str = "bounded") -> MalfDayRequest:
    return MalfDayRequest(
        source_db=tmp_path / "asteria-data" / "market_base_day.duckdb",
        core_db=tmp_path / "asteria-data" / "malf_core_day.duckdb",
        lifespan_db=tmp_path / "asteria-data" / "malf_lifespan_day.duckdb",
        service_db=tmp_path / "asteria-data" / "malf_service_day.duckdb",
        report_root=tmp_path / "asteria-report",
        validated_root=tmp_path / "asteria-validated",
        temp_root=tmp_path / "asteria-temp",
        run_id=run_id,
        mode=mode,
        schema_version="malf-day-bounded-proof-v1",
        core_rule_version="core-rule-fractal-1bar-v1",
        lifespan_rule_version="lifespan-rule-v1",
        sample_version="sample-v1",
        service_version="service-v1",
        start_dt="2024-01-01",
        end_dt="2024-01-31",
        symbol_limit=10,
    )


def test_malf_day_core_build_writes_real_structure_ledgers(tmp_path: Path) -> None:
    _seed_market_base_day(
        tmp_path / "asteria-data" / "market_base_day.duckdb",
        symbols=("UPCASE.SH", "SAME.SH"),
    )

    summary = run_malf_day_core_build(_request(tmp_path, "malf-core-run-001"))

    assert summary.status == "completed"
    assert summary.input_row_count == 27
    assert summary.resume_reused is False

    with duckdb.connect(
        str(tmp_path / "asteria-data" / "malf_core_day.duckdb"), read_only=True
    ) as con:
        assert con.execute("select count(*) from malf_pivot_ledger").fetchone()[0] >= 12
        primitives = {
            row[0]
            for row in con.execute(
                "select distinct primitive from malf_structure_ledger"
            ).fetchall()
        }
        assert {"HH", "HL", "LL", "LH"}.issubset(primitives)

        birth_types = {
            row[0]
            for row in con.execute("select distinct birth_type from malf_wave_ledger").fetchall()
        }
        assert "initial" in birth_types
        assert "opposite_direction_after_break" in birth_types

        transition_row = con.execute(
            """
            select old_wave_id, old_direction, old_progress_extreme_pivot_id,
                   old_progress_extreme_price, state, new_wave_id
            from malf_transition_ledger
            where state = 'confirmed'
            limit 1
            """
        ).fetchone()
        assert transition_row is not None
        assert transition_row[0] is not None
        assert transition_row[1] in {"up", "down"}
        assert transition_row[2] is not None
        assert transition_row[3] is not None
        assert transition_row[4] == "confirmed"
        assert transition_row[5] is not None

        candidate_row = con.execute(
            """
            select candidate_direction, reference_progress_extreme_price,
                   confirmed_by_pivot_id, confirmed_wave_id
            from malf_candidate_ledger
            where confirmed_wave_id is not null
            limit 1
            """
        ).fetchone()
        assert candidate_row is not None
        assert candidate_row[0] in {"up", "down"}
        assert candidate_row[1] is not None
        assert candidate_row[2] is not None
        assert candidate_row[3] is not None


def test_malf_day_core_resume_reuses_completed_checkpoint(tmp_path: Path) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")

    first = run_malf_day_core_build(_request(tmp_path, "malf-core-run-002"))
    second = run_malf_day_core_build(_request(tmp_path, "malf-core-run-002", mode="resume"))

    assert first.status == "completed"
    assert second.status == "completed"
    assert second.resume_reused is True


@pytest.mark.parametrize(
    ("runner_name", "runner"),
    [
        ("core", run_malf_day_core_build),
        ("lifespan", run_malf_day_lifespan_build),
        ("service", run_malf_day_service_build),
    ],
)
def test_malf_day_build_runners_reject_audit_only_mode(
    tmp_path: Path,
    runner_name: str,
    runner,
) -> None:
    request = _request(tmp_path, f"malf-audit-only-{runner_name}-run-001", mode="audit-only")

    with pytest.raises(ValueError, match="audit-only mode"):
        runner(request)


def test_malf_lifespan_service_and_audit_publish_wave_position(tmp_path: Path) -> None:
    _seed_market_base_day(
        tmp_path / "asteria-data" / "market_base_day.duckdb",
        symbols=("UPCASE.SH", "SAME.SH"),
    )
    request = _request(tmp_path, "malf-full-run-001")

    run_malf_day_core_build(request)
    lifespan_summary = run_malf_day_lifespan_build(request)
    service_summary = run_malf_day_service_build(request)
    audit_summary = run_malf_day_audit(request)

    assert lifespan_summary.status == "completed"
    assert lifespan_summary.input_wave_count >= 3
    assert service_summary.status == "completed"
    assert service_summary.published_row_count > 0
    assert audit_summary.status == "completed"
    assert audit_summary.report_path is not None

    with duckdb.connect(
        str(tmp_path / "asteria-data" / "malf_lifespan_day.duckdb"), read_only=True
    ) as con:
        assert (
            con.execute(
                """
                select count(*)
                from malf_lifespan_snapshot
                where progress_updated and new_count >= 1 and no_new_span = 0
                """
            ).fetchone()[0]
            > 0
        )
        assert (
            con.execute(
                """
                select count(*)
                from malf_lifespan_snapshot
                where not progress_updated and no_new_span > 0
                """
            ).fetchone()[0]
            > 0
        )
        assert (
            con.execute(
                """
                select count(*)
                from malf_lifespan_snapshot
                where system_state = 'transition'
                  and transition_span > 0
                  and life_state = 'terminal'
                """
            ).fetchone()[0]
            > 0
        )

    with duckdb.connect(
        str(tmp_path / "asteria-data" / "malf_service_day.duckdb"), read_only=True
    ) as con:
        assert (
            con.execute(
                """
                select count(*)
                from malf_wave_position
                where wave_core_state = 'transition'
                """
            ).fetchone()[0]
            == 0
        )
        assert (
            con.execute(
                """
                select count(*)
                from malf_wave_position
                where system_state = 'transition'
                  and wave_id is null
                  and old_wave_id is not null
                  and wave_core_state = 'terminated'
                  and direction is not null
                """
            ).fetchone()[0]
            > 0
        )
        assert (
            con.execute(
                """
                select count(*)
                from (
                    select symbol, timeframe, service_version, count(*) row_count
                    from malf_wave_position_latest
                    group by symbol, timeframe, service_version
                    having row_count > 1
                )
                """
            ).fetchone()[0]
            == 0
        )
        assert (
            con.execute(
                "select count(*) from malf_interface_audit where status = 'fail'"
            ).fetchone()[0]
            == 0
        )

    report_payload = json.loads(Path(audit_summary.report_path).read_text(encoding="utf-8"))
    assert report_payload["run_id"] == "malf-full-run-001"
    assert report_payload["hard_fail_count"] == 0
    assert report_payload["published_row_count"] > 0


def test_malf_lifespan_and_service_publish_dense_bar_level_wave_position(
    tmp_path: Path,
) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    request = _request(tmp_path, "malf-dense-run-001")

    run_malf_day_core_build(request)
    run_malf_day_lifespan_build(request)
    service_summary = run_malf_day_service_build(request)

    with duckdb.connect(
        str(tmp_path / "asteria-data" / "malf_lifespan_day.duckdb"), read_only=True
    ) as con:
        dense_rows = con.execute(
            """
            select symbol, bar_dt, system_state, new_count, no_new_span
            from malf_lifespan_snapshot
            where symbol = 'UPCASE.SH'
            order by bar_dt
            """
        ).fetchall()
        first_dense_dt = con.execute("select min(bar_dt) from malf_lifespan_snapshot").fetchone()[0]
    with duckdb.connect(
        str(tmp_path / "asteria-data" / "market_base_day.duckdb"), read_only=True
    ) as con:
        source_dates = [
            row[0]
            for row in con.execute(
                """
                select bar_dt
                from market_base_bar
                where symbol = 'UPCASE.SH'
                  and timeframe = 'day'
                  and bar_dt >= ?
                order by bar_dt
                """,
                [first_dense_dt],
            ).fetchall()
        ]

    dense_dates = [row[1] for row in dense_rows]
    assert dense_dates == source_dates
    assert any(row[2] == "transition" for row in dense_rows)
    assert any(row[2] != "transition" and row[4] > 1 for row in dense_rows)

    with duckdb.connect(
        str(tmp_path / "asteria-data" / "malf_service_day.duckdb"), read_only=True
    ) as con:
        service_dates = [
            row[0]
            for row in con.execute(
                """
                select bar_dt
                from malf_wave_position
                where symbol = 'UPCASE.SH'
                order by bar_dt
                """
            ).fetchall()
        ]

    assert service_dates == source_dates
    assert service_summary.published_row_count >= len(source_dates)


def test_malf_dense_transition_rows_increment_span_per_bar(tmp_path: Path) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    request = _request(tmp_path, "malf-dense-transition-run-001")

    run_malf_day_core_build(request)
    run_malf_day_lifespan_build(request)
    run_malf_day_service_build(request)

    with duckdb.connect(
        str(tmp_path / "asteria-data" / "malf_service_day.duckdb"), read_only=True
    ) as con:
        transition_rows = con.execute(
            """
            select bar_dt, wave_core_state, system_state, direction, transition_span
            from malf_wave_position
            where symbol = 'UPCASE.SH' and system_state = 'transition'
            order by bar_dt
            """
        ).fetchall()

    assert len(transition_rows) >= 2
    assert [row[4] for row in transition_rows] == list(range(1, len(transition_rows) + 1))
    assert {row[1] for row in transition_rows} == {"terminated"}
    assert {row[2] for row in transition_rows} == {"transition"}
    assert {row[3] for row in transition_rows} == {"up"}
