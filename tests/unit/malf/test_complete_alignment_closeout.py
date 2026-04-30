from __future__ import annotations

from pathlib import Path

import duckdb
from tests.unit.malf.test_bounded_proof_runner import _request, _seed_market_base_day

from asteria.malf.bootstrap import (
    run_malf_day_audit,
    run_malf_day_core_build,
    run_malf_day_lifespan_build,
    run_malf_day_service_build,
)


def test_malf_lifespan_zero_day_wave_publishes_transition_only_for_bar(
    tmp_path: Path,
) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    request = _request(tmp_path, "malf-zero-day-wave-run-001")

    run_malf_day_core_build(request)
    zero_day = _force_first_terminated_wave_to_zero_day(request.core_db)

    run_malf_day_lifespan_build(request)
    run_malf_day_service_build(request)

    with duckdb.connect(str(request.service_db), read_only=True) as con:
        duplicates = con.execute(
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
        ).fetchone()[0]
        zero_day_rows = con.execute(
            """
            select system_state
            from malf_wave_position
            where run_id = ? and wave_id is null and old_wave_id = ? and bar_dt = ?
            """,
            [request.run_id, zero_day[0], zero_day[1]],
        ).fetchall()

    assert duplicates == 0
    assert zero_day_rows == [("transition",)]


def test_malf_service_formal_style_run_has_no_wave_position_natural_duplicates(
    tmp_path: Path,
) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    request = _request(tmp_path, "malf-formal-natural-key-run-001")

    run_malf_day_core_build(request)
    _force_first_terminated_wave_to_zero_day(request.core_db)
    run_malf_day_lifespan_build(request)
    run_malf_day_service_build(request)
    run_malf_day_audit(request)

    with duckdb.connect(str(request.service_db), read_only=True) as con:
        duplicate_count = con.execute(
            """
            select count(*)
            from (
                select symbol, timeframe, bar_dt, service_version, count(*) row_count
                from malf_wave_position
                group by symbol, timeframe, bar_dt, service_version
                having row_count > 1
            )
            """
        ).fetchone()[0]
        break_audit_row = con.execute(
            """
            select status, failed_count
            from malf_interface_audit
            where run_id = ?
              and check_name = 'core_break_does_not_extend_old_wave'
            """,
            [request.run_id],
        ).fetchone()

    assert duplicate_count == 0
    assert break_audit_row == ("pass", 0)


def test_malf_audit_uses_service_source_core_run_for_core_hard_checks(
    tmp_path: Path,
) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    core_request = _request(tmp_path, "malf-source-core-run-001")
    audit_request = _request(tmp_path, "malf-source-bound-audit-run-001")

    run_malf_day_core_build(core_request)
    run_malf_day_lifespan_build(audit_request)
    run_malf_day_service_build(audit_request)

    with duckdb.connect(str(core_request.core_db)) as con:
        terminated_wave_id = con.execute(
            """
            select wave_id
            from malf_wave_ledger
            where run_id = ? and terminated_by_break_id is not null
            limit 1
            """,
            [core_request.run_id],
        ).fetchone()[0]
        con.execute(
            """
            update malf_wave_ledger
            set wave_core_state = 'alive'
            where wave_id = ?
            """,
            [terminated_wave_id],
        )

    run_malf_day_audit(audit_request)

    with duckdb.connect(str(audit_request.service_db), read_only=True) as con:
        audit_row = con.execute(
            """
            select status, failed_count
            from malf_interface_audit
            where run_id = ? and check_name = 'core_terminated_wave_not_alive'
            """,
            [audit_request.run_id],
        ).fetchone()

    assert audit_row == ("fail", 1)


def test_malf_core_candidate_reference_uses_old_progress_for_all_directions(
    tmp_path: Path,
) -> None:
    _seed_market_base_day(
        tmp_path / "asteria-data" / "market_base_day.duckdb",
        symbols=("UPCASE.SH", "SAME.SH"),
    )
    request = _request(tmp_path, "malf-candidate-reference-run-001")

    run_malf_day_core_build(request)

    with duckdb.connect(str(request.core_db), read_only=True) as con:
        rows = con.execute(
            """
            select c.candidate_direction, t.old_direction,
                   c.reference_progress_extreme_price,
                   t.old_progress_extreme_price
            from malf_candidate_ledger c
            join malf_transition_ledger t on t.transition_id = c.transition_id
            where c.run_id = ? and c.confirmed_wave_id is not null
            order by c.candidate_dt, c.candidate_id
            """,
            [request.run_id],
        ).fetchall()

    assert rows
    assert any(
        candidate_direction != old_direction for candidate_direction, old_direction, *_ in rows
    )
    assert all(reference == old_progress for *_, reference, old_progress in rows)


def _force_first_terminated_wave_to_zero_day(core_db: Path) -> tuple[str, object]:
    with duckdb.connect(str(core_db)) as con:
        zero_day = con.execute(
            """
            select wave_id, terminated_dt
            from malf_wave_ledger
            where terminated_dt is not null
            order by terminated_dt
            limit 1
            """
        ).fetchone()
        assert zero_day is not None
        con.execute(
            """
            update malf_wave_ledger
            set confirm_dt = ?
            where wave_id = ?
            """,
            [zero_day[1], zero_day[0]],
        )
    return str(zero_day[0]), zero_day[1]
