from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import duckdb
import pytest
from tests.unit.malf.test_bounded_proof_runner import (
    _request,
    _seed_market_base_day,
)

from asteria.malf.bootstrap import (
    run_malf_day_audit,
    run_malf_day_core_build,
    run_malf_day_lifespan_build,
    run_malf_day_service_build,
)


def test_malf_segmented_mode_requires_explicit_scope(tmp_path: Path) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    scoped = _request(tmp_path, "malf-v13-segmented-scope-run-001", mode="segmented")

    with pytest.raises(ValueError, match="segmented MALF runs require segmented scope"):
        replace(scoped, start_dt=None, end_dt=None, symbol_limit=None)


def test_malf_v13_core_lifespan_and_service_publish_trace_fields(
    tmp_path: Path,
) -> None:
    _seed_market_base_day(
        tmp_path / "asteria-data" / "market_base_day.duckdb",
        symbols=("UPCASE.SH", "SAME.SH"),
    )
    request = _request(tmp_path, "malf-v13-trace-run-001")

    run_malf_day_core_build(request)
    run_malf_day_lifespan_build(request)
    run_malf_day_service_build(request)

    with duckdb.connect(str(request.core_db), read_only=True) as con:
        transitions = con.execute(
            """
            select old_direction, transition_boundary_high, transition_boundary_low,
                   broken_guard_pivot_id
            from malf_transition_ledger
            where run_id = ?
            order by transition_id
            """,
            [request.run_id],
        ).fetchall()
        assert transitions
        for old_direction, boundary_high, boundary_low, broken_guard in transitions:
            assert old_direction in {"up", "down"}
            assert boundary_high is not None
            assert boundary_low is not None
            assert boundary_high > boundary_low
            assert broken_guard is not None

        candidate_rows = con.execute(
            """
            select candidate_status, confirmed_by_pivot_id, confirmation_pivot_id,
                   confirmed_wave_id, new_wave_id
            from malf_candidate_ledger
            where run_id = ? and confirmed_wave_id is not null
            """,
            [request.run_id],
        ).fetchall()
        assert candidate_rows
        assert all(row == ("confirmed", row[1], row[1], row[3], row[3]) for row in candidate_rows)

    with duckdb.connect(str(request.lifespan_db), read_only=True) as con:
        birth_rows = con.execute(
            """
            select distinct birth_type, candidate_wait_span, candidate_replacement_count,
                   confirmation_distance_abs, confirmation_distance_pct
            from malf_lifespan_snapshot
            where run_id = ? and birth_type <> 'initial'
            """,
            [request.run_id],
        ).fetchall()
        assert birth_rows
        assert all(wait is not None and wait >= 1 for _, wait, *_ in birth_rows)
        assert all(
            replacements is not None and replacements >= 0 for *_, replacements, _, _ in birth_rows
        )
        assert all(distance is not None and distance > 0 for *_, distance, _ in birth_rows)

    with duckdb.connect(str(request.service_db), read_only=True) as con:
        service_row = con.execute(
            """
            select transition_boundary_high, transition_boundary_low,
                   active_candidate_guard_pivot_id, confirmation_pivot_id,
                   new_wave_id, birth_type, candidate_wait_span,
                   candidate_replacement_count, confirmation_distance_abs,
                   confirmation_distance_pct
            from malf_wave_position
            where run_id = ? and birth_type <> 'initial'
            limit 1
            """,
            [request.run_id],
        ).fetchone()
        assert service_row is not None
        assert service_row[0] > service_row[1]
        assert service_row[2] is not None
        assert service_row[3] is not None
        assert service_row[4] is not None
        assert service_row[5] in {"same_direction_after_break", "opposite_direction_after_break"}
        assert service_row[6] >= 1
        assert service_row[7] >= 0
        assert service_row[8] > 0
        assert service_row[9] > 0


def test_malf_v13_structure_contexts_include_transition_candidate(tmp_path: Path) -> None:
    _seed_market_base_day(
        tmp_path / "asteria-data" / "market_base_day.duckdb",
        symbols=("UPCASE.SH", "SAME.SH"),
    )
    request = _request(tmp_path, "malf-v13-structure-context-run-001")

    run_malf_day_core_build(request)

    with duckdb.connect(str(request.core_db), read_only=True) as con:
        contexts = {
            row[0]
            for row in con.execute(
                """
                select distinct structure_context
                from malf_structure_ledger
                where run_id = ?
                """,
                [request.run_id],
            ).fetchall()
        }

    assert "initial_candidate" in contexts
    assert "active_wave" in contexts
    assert "transition_candidate" in contexts


def test_malf_v13_lifespan_reads_only_current_core_run_id(tmp_path: Path) -> None:
    _seed_market_base_day(
        tmp_path / "asteria-data" / "market_base_day.duckdb",
        symbols=("UPCASE.SH", "SAME.SH"),
    )
    old_request = _request(tmp_path, "malf-v13-old-core-run-001")
    current_request = replace(
        _request(tmp_path, "malf-v13-current-core-run-001"),
        symbol_limit=1,
    )

    run_malf_day_core_build(old_request)
    run_malf_day_core_build(current_request)
    run_malf_day_lifespan_build(current_request)

    with duckdb.connect(str(current_request.core_db), read_only=True) as con:
        current_symbols = {
            row[0]
            for row in con.execute(
                "select distinct symbol from malf_wave_ledger where run_id = ?",
                [current_request.run_id],
            ).fetchall()
        }
    with duckdb.connect(str(current_request.lifespan_db), read_only=True) as con:
        lifespan_symbols = {
            row[0]
            for row in con.execute(
                "select distinct symbol from malf_lifespan_snapshot where run_id = ?",
                [current_request.run_id],
            ).fetchall()
        }

    assert lifespan_symbols == current_symbols


def test_malf_v13_hard_audit_detects_trace_inconsistency(tmp_path: Path) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    request = _request(tmp_path, "malf-v13-hard-audit-run-001")

    run_malf_day_core_build(request)
    run_malf_day_lifespan_build(request)
    run_malf_day_service_build(request)

    with duckdb.connect(str(request.service_db)) as con:
        con.execute(
            """
            update malf_wave_position
            set transition_boundary_high = null
            where run_id = ? and birth_type <> 'initial'
            """,
            [request.run_id],
        )

    run_malf_day_audit(request)

    with duckdb.connect(str(request.service_db), read_only=True) as con:
        audit_row = con.execute(
            """
            select status, failed_count
            from malf_interface_audit
            where run_id = ? and check_name = 'service_v13_trace_matches_lifespan'
            """,
            [request.run_id],
        ).fetchone()

    assert audit_row is not None
    assert audit_row[0] == "fail"
    assert audit_row[1] > 0
