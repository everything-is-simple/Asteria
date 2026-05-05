from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import duckdb
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


def test_malf_lifespan_cli_requires_source_db_for_dense_bars(tmp_path: Path) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    request = _request(tmp_path, "malf-cli-core-run-001")
    run_malf_day_core_build(request)
    script = (
        Path(__file__).resolve().parents[3]
        / "scripts"
        / "malf"
        / ("run_malf_day_lifespan_build.py")
    )

    missing_source = subprocess.run(
        [
            sys.executable,
            str(script),
            "--core-db",
            str(request.core_db),
            "--target-db",
            str(request.lifespan_db),
            "--mode",
            "bounded",
            "--run-id",
            "malf-cli-lifespan-run-missing-source",
            "--rule-version",
            "lifespan-rule-v1",
            "--sample-version",
            "sample-v1",
            "--start-dt",
            "2024-01-01",
            "--end-dt",
            "2024-01-31",
            "--symbol-limit",
            "10",
        ],
        capture_output=True,
        text=True,
    )
    assert missing_source.returncode != 0
    assert "--source-db" in missing_source.stderr

    with_source = subprocess.run(
        [
            sys.executable,
            str(script),
            "--source-db",
            str(request.source_db),
            "--core-db",
            str(request.core_db),
            "--target-db",
            str(request.lifespan_db),
            "--mode",
            "bounded",
            "--run-id",
            "malf-cli-lifespan-run-001",
            "--rule-version",
            "lifespan-rule-v1",
            "--sample-version",
            "sample-v1",
            "--start-dt",
            "2024-01-01",
            "--end-dt",
            "2024-01-31",
            "--symbol-limit",
            "10",
        ],
        capture_output=True,
        text=True,
    )
    assert with_source.returncode == 0, with_source.stderr
    payload = json.loads(with_source.stdout)
    assert payload["status"] == "completed"

    with duckdb.connect(str(request.lifespan_db), read_only=True) as con:
        dense_dates = [
            row[0]
            for row in con.execute(
                """
                select bar_dt
                from malf_lifespan_snapshot
                where symbol = 'UPCASE.SH'
                order by bar_dt
                """
            ).fetchall()
        ]
        first_dense_dt = dense_dates[0]
    with duckdb.connect(str(request.source_db), read_only=True) as con:
        source_dates = [
            row[0]
            for row in con.execute(
                """
                select bar_dt
                from market_base_bar
                where symbol = 'UPCASE.SH' and timeframe = 'day'
                  and bar_dt >= ?
                order by bar_dt
                """,
                [first_dense_dt],
            ).fetchall()
        ]
    assert dense_dates == source_dates


def test_malf_audit_fails_when_dense_source_bar_snapshot_is_missing(tmp_path: Path) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    request = _request(tmp_path, "malf-dense-audit-run-001")

    run_malf_day_core_build(request)
    run_malf_day_lifespan_build(request)
    run_malf_day_service_build(request)

    with duckdb.connect(str(request.lifespan_db)) as con:
        con.execute(
            """
            delete from malf_lifespan_snapshot
            where snapshot_id = (
                select snapshot_id
                from malf_lifespan_snapshot
                where symbol = 'UPCASE.SH'
                order by bar_dt
                limit 1
            )
            """
        )

    run_malf_day_audit(request)

    with duckdb.connect(str(request.service_db), read_only=True) as con:
        audit_row = con.execute(
            """
            select status, failed_count
            from malf_interface_audit
            where run_id = ? and check_name = 'lifespan_dense_source_bar_coverage'
            """,
            [request.run_id],
        ).fetchone()

    assert audit_row == ("fail", 1)


def test_malf_audit_hard_fails_for_core_design_rule_violations(tmp_path: Path) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    request = _request(tmp_path, "malf-core-hard-audit-run-001")

    run_malf_day_core_build(request)
    run_malf_day_lifespan_build(request)
    run_malf_day_service_build(request)

    with duckdb.connect(str(request.core_db)) as con:
        terminated_wave_id = con.execute(
            """
            select wave_id
            from malf_wave_ledger
            where terminated_by_break_id is not null
            limit 1
            """
        ).fetchone()[0]
        con.execute(
            """
            update malf_wave_ledger
            set wave_core_state = 'alive'
            where wave_id = ?
            """,
            [terminated_wave_id],
        )
        con.execute(
            """
            update malf_wave_ledger
            set final_progress_extreme_pivot_id = (
                select p.pivot_id
                from malf_pivot_ledger p
                where p.pivot_dt >= (
                    select terminated_dt
                    from malf_wave_ledger
                    where wave_id = ?
                )
                order by p.pivot_dt desc
                limit 1
            )
            where wave_id = ?
            """,
            [terminated_wave_id, terminated_wave_id],
        )
        con.execute(
            """
            insert into malf_candidate_ledger
            select candidate_id || '|dup-active', transition_id, candidate_guard_pivot_id,
                   candidate_direction, candidate_dt, true, invalidated_by_candidate_id,
                   reference_progress_extreme_price, confirmed_by_pivot_id, confirmed_wave_id,
                   run_id, schema_version, core_rule_version, created_at,
                   candidate_status, confirmation_pivot_id, new_wave_id, candidate_event_type
            from malf_candidate_ledger
            where run_id = ?
            limit 1
            """,
            [request.run_id],
        )
        con.execute(
            """
            insert into malf_candidate_ledger
            select '000-stale-candidate|' || candidate_id, transition_id, candidate_guard_pivot_id,
                   candidate_direction, candidate_dt, false, null,
                   reference_progress_extreme_price, null, null,
                   run_id, schema_version, core_rule_version, created_at,
                   'invalidated', null, null, 'opposite_direction_candidate_replacement'
            from malf_candidate_ledger
            where run_id = ?
            limit 1
            """,
            [request.run_id],
        )
        con.execute(
            """
            update malf_wave_ledger
            set candidate_guard_pivot_id = null
            where wave_id = (
                select wave_id
                from malf_wave_ledger
                where run_id = ? and birth_type <> 'initial'
                limit 1
            )
            """,
            [request.run_id],
        )
        con.execute(
            """
            update malf_candidate_ledger
            set reference_progress_extreme_price =
                case when candidate_direction = 'up' then 999999.0 else -999999.0 end
            where candidate_id = (
                select candidate_id
                from malf_candidate_ledger
                where run_id = ? and confirmed_wave_id is not null
                limit 1
            )
            """,
            [request.run_id],
        )

    run_malf_day_audit(request)

    expected_failures = {
        "core_terminated_wave_not_alive",
        "core_break_does_not_extend_old_wave",
        "core_single_active_candidate_per_transition",
        "core_new_candidate_replaces_previous",
        "core_new_wave_candidate_confirmation_required",
        "core_candidate_confirmation_threshold",
    }
    with duckdb.connect(str(request.service_db), read_only=True) as con:
        rows = dict(
            con.execute(
                """
                select check_name, failed_count
                from malf_interface_audit
                where run_id = ? and check_name in (
                    'core_terminated_wave_not_alive',
                    'core_break_does_not_extend_old_wave',
                    'core_single_active_candidate_per_transition',
                    'core_new_candidate_replaces_previous',
                    'core_new_wave_candidate_confirmation_required',
                    'core_candidate_confirmation_threshold'
                )
                """,
                [request.run_id],
            ).fetchall()
        )

    assert set(rows) == expected_failures
    assert all(failed_count > 0 for failed_count in rows.values())


def test_malf_audit_hard_fails_for_wave_position_natural_key_duplicate(
    tmp_path: Path,
) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    request = _request(tmp_path, "malf-service-natural-key-audit-run-001")

    run_malf_day_core_build(request)
    run_malf_day_lifespan_build(request)
    run_malf_day_service_build(request)

    with duckdb.connect(str(request.service_db)) as con:
        con.execute(
            """
            insert into malf_wave_position
            select *
            from malf_wave_position
            where run_id = ?
            limit 1
            """,
            [request.run_id],
        )

    run_malf_day_audit(request)

    with duckdb.connect(str(request.service_db), read_only=True) as con:
        audit_row = con.execute(
            """
            select status, failed_count
            from malf_interface_audit
            where run_id = ? and check_name = 'service_wave_position_natural_key_unique'
            """,
            [request.run_id],
        ).fetchone()

    assert audit_row == ("fail", 1)


def test_malf_audit_passes_alignment_hardening_checks_for_clean_run(
    tmp_path: Path,
) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    request = _request(tmp_path, "malf-alignment-clean-audit-run-001")

    run_malf_day_core_build(request)
    run_malf_day_lifespan_build(request)
    run_malf_day_service_build(request)
    run_malf_day_audit(request)

    expected_checks = {
        "core_terminated_wave_not_alive",
        "core_break_does_not_extend_old_wave",
        "core_single_active_candidate_per_transition",
        "core_new_candidate_replaces_previous",
        "core_new_wave_candidate_confirmation_required",
        "core_candidate_confirmation_threshold",
        "service_wave_position_natural_key_unique",
    }
    with duckdb.connect(str(request.service_db), read_only=True) as con:
        rows = dict(
            con.execute(
                """
                select check_name, status
                from malf_interface_audit
                where run_id = ? and check_name in (
                    'core_terminated_wave_not_alive',
                    'core_break_does_not_extend_old_wave',
                    'core_single_active_candidate_per_transition',
                    'core_new_candidate_replaces_previous',
                    'core_new_wave_candidate_confirmation_required',
                    'core_candidate_confirmation_threshold',
                    'service_wave_position_natural_key_unique'
                )
                """,
                [request.run_id],
            ).fetchall()
        )

    assert set(rows) == expected_checks
    assert set(rows.values()) == {"pass"}


def test_malf_service_publishes_only_current_lifespan_run(tmp_path: Path) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    first = _request(tmp_path, "malf-service-source-run-001")
    second = _request(tmp_path, "malf-service-source-run-002")

    run_malf_day_core_build(first)
    run_malf_day_lifespan_build(first)
    run_malf_day_lifespan_build(second)
    run_malf_day_service_build(second)

    with duckdb.connect(str(second.lifespan_db), read_only=True) as con:
        second_lifespan_count = con.execute(
            "select count(*) from malf_lifespan_snapshot where run_id = ?",
            [second.run_id],
        ).fetchone()[0]
        all_lifespan_count = con.execute("select count(*) from malf_lifespan_snapshot").fetchone()[
            0
        ]
    with duckdb.connect(str(second.service_db), read_only=True) as con:
        second_service_count = con.execute(
            "select count(*) from malf_wave_position where run_id = ?",
            [second.run_id],
        ).fetchone()[0]

    assert all_lifespan_count > second_lifespan_count
    assert second_service_count == second_lifespan_count
