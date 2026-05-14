from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import duckdb
import pytest

from asteria.alpha.pas_bounded_proof import (
    PasBoundedProofRequest,
    run_alpha_pas_bounded_proof,
)
from asteria.alpha.pas_contracts import (
    PAS_FORBIDDEN_OUTPUT_FIELDS,
    PAS_LIFECYCLE_STATES,
    PAS_REQUIRED_SERVICE_FIELDS,
)


def _seed_malf_service(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = """
        symbol varchar,
        timeframe varchar,
        bar_dt date,
        system_state varchar,
        wave_id varchar,
        old_wave_id varchar,
        wave_core_state varchar,
        direction varchar,
        new_count bigint,
        no_new_span bigint,
        transition_span bigint,
        update_rank double,
        stagnation_rank double,
        life_state varchar,
        position_quadrant varchar,
        guard_boundary_price double,
        sample_scope varchar,
        sample_version varchar,
        lifespan_rule_version varchar,
        service_version varchar,
        run_id varchar,
        schema_version varchar,
        source_core_run_id varchar,
        source_lifespan_run_id varchar,
        created_at timestamp
    """
    with duckdb.connect(str(path)) as con:
        con.execute(f"create table malf_wave_position ({columns})")
        con.execute(f"create table malf_wave_position_latest ({columns})")
        con.execute(
            """
            create table malf_interface_audit (
                audit_id varchar,
                run_id varchar,
                check_name varchar,
                severity varchar,
                status varchar,
                failed_count bigint,
                sample_payload varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            insert into malf_interface_audit
            values ('audit-1', 'malf-run-1', 'source_ok', 'hard', 'pass', 0, '{}', now())
            """
        )
        rows = [_wave_row(i) for i in range(10)]
        placeholders = ", ".join(["?"] * 25)
        con.executemany(f"insert into malf_wave_position values ({placeholders})", rows)
        con.executemany(f"insert into malf_wave_position_latest values ({placeholders})", rows[-2:])


def _wave_row(offset: int) -> tuple[object, ...]:
    states = [
        ("up_alive", "alive", "up", 1, 0, 0, 0.95, 0.30, "developing", "developing"),
        ("up_alive", "alive", "up", 2, 0, 0, 0.90, 0.50, "extended", "extended_active"),
        ("up_alive", "alive", "up", 2, 1, 0, 0.80, 0.90, "stagnant", "extended_stagnant"),
        ("down_alive", "alive", "down", 1, 1, 0, 0.70, 0.80, "stagnant", "extended_stagnant"),
        ("transition", "terminated", "down", 2, 0, 1, 0.50, 0.50, "terminal", "extended_stagnant"),
        ("transition", "terminated", "up", 1, 0, 2, 0.60, 0.60, "terminal", "extended_active"),
        ("down_alive", "alive", "down", 0, 0, 0, 0.20, 0.20, "developing", "developing"),
        ("up_alive", "alive", "up", 1, 3, 0, 0.30, 0.95, "stagnant", "extended_stagnant"),
        ("up_alive", "alive", "up", 3, 0, 0, 0.99, 0.99, "extended", "extended_active"),
        ("up_alive", "alive", "up", 3, 0, 0, 0.99, 0.99, "extended", "extended_active"),
    ][offset]
    system_state, wave_core_state, direction, new_count, no_new_span, transition_span = states[:6]
    update_rank, stagnation_rank, life_state, quadrant = states[6:]
    bar_dt = date(2024, 1, 1) + timedelta(days=offset)
    return (
        "600000.SH",
        "day",
        bar_dt,
        system_state,
        f"wave-{offset}" if system_state != "transition" else None,
        f"old-wave-{offset}" if system_state == "transition" else None,
        wave_core_state,
        direction,
        new_count,
        no_new_span,
        transition_span,
        update_rank,
        stagnation_rank,
        life_state,
        quadrant,
        10.0 + offset,
        "unit-scope",
        "sample-v1",
        "lifespan-rule-v1",
        "malf-wave-position-dense-v1",
        "malf-run-1",
        "malf-schema-v1",
        "core-run-1",
        "lifespan-run-1",
        "2026-05-14 00:00:00",
    )


def _request(tmp_path: Path, **overrides: object) -> PasBoundedProofRequest:
    params = {
        "source_malf_db": tmp_path / "data" / "malf_service_day.duckdb",
        "temp_root": tmp_path / "temp",
        "report_root": tmp_path / "report",
        "validated_root": tmp_path / "validated",
        "run_id": "v1-alpha-pas-bounded-proof-build-card-unit",
        "source_malf_service_version": "malf-wave-position-dense-v1",
        "source_malf_run_id": "malf-run-1",
        "start_dt": "2024-01-01",
        "end_dt": "2024-01-31",
        "symbol_limit": 31,
    }
    params.update(overrides)
    return PasBoundedProofRequest(**params)


def test_pas_bounded_proof_writes_required_contract_fields_to_temp_only(
    tmp_path: Path,
) -> None:
    _seed_malf_service(tmp_path / "data" / "malf_service_day.duckdb")

    summary = run_alpha_pas_bounded_proof(_request(tmp_path))

    assert summary.status == "completed"
    assert summary.hard_fail_count == 0
    assert str(summary.output_db_path).startswith(str(tmp_path / "temp"))
    assert not str(summary.output_db_path).startswith("H:\\Asteria-data")
    assert (
        tmp_path / "validated" / "Asteria-v1-alpha-pas-bounded-proof-build-card-unit.zip"
    ).exists()
    with duckdb.connect(str(summary.output_db_path), read_only=True) as con:
        columns = {
            row[1] for row in con.execute("pragma table_info(pas_entry_candidate)").fetchall()
        }
        assert PAS_REQUIRED_SERVICE_FIELDS.issubset(columns)
        assert columns.isdisjoint(PAS_FORBIDDEN_OUTPUT_FIELDS)
        assert con.execute("select count(*) from pas_entry_candidate").fetchone()[0] > 0
    coverage = json.loads((summary.report_dir / "contract-coverage.json").read_text())
    assert coverage["required_fields_missing"] == []
    assert coverage["forbidden_fields_present"] == []


def test_pas_lifecycle_states_are_available_and_current_state_is_unique(tmp_path: Path) -> None:
    _seed_malf_service(tmp_path / "data" / "malf_service_day.duckdb")

    summary = run_alpha_pas_bounded_proof(_request(tmp_path))

    assert set(summary.covered_lifecycle_states) == PAS_LIFECYCLE_STATES
    with duckdb.connect(str(summary.output_db_path), read_only=True) as con:
        assert {
            row[0]
            for row in con.execute(
                "select lifecycle_state from pas_lifecycle_state_catalog"
            ).fetchall()
        } == PAS_LIFECYCLE_STATES
        duplicate_current = con.execute(
            """
            select count(*)
            from (
                select candidate_id, count(*) row_count
                from pas_candidate_lifecycle
                where is_current
                group by 1
                having row_count <> 1
            )
            """
        ).fetchone()[0]
        assert duplicate_current == 0


def test_strength_profile_uses_setup_visible_completed_baseline_only(tmp_path: Path) -> None:
    source_db = tmp_path / "data" / "malf_service_day.duckdb"
    _seed_malf_service(source_db)

    first = run_alpha_pas_bounded_proof(_request(tmp_path, end_dt="2024-01-05"))
    second = run_alpha_pas_bounded_proof(
        _request(tmp_path, run_id="future-row-check", end_dt="2024-01-10")
    )

    with duckdb.connect(str(first.output_db_path), read_only=True) as con:
        first_row = con.execute(
            """
            select completed_same_direction_baseline, in_flight_confirmation, strength_score
            from pas_strength_profile
            where symbol = '600000.SH' and setup_date = date '2024-01-05'
            """
        ).fetchone()
    with duckdb.connect(str(second.output_db_path), read_only=True) as con:
        second_row = con.execute(
            """
            select completed_same_direction_baseline, in_flight_confirmation, strength_score
            from pas_strength_profile
            where symbol = '600000.SH' and setup_date = date '2024-01-05'
            """
        ).fetchone()
    assert first_row == second_row
    assert "transition_span" not in str(first_row[0])
    assert "transition_span" in str(first_row[1])


def test_request_rejects_non_day_and_formal_output_intent(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="day-only"):
        _request(tmp_path, timeframe="week")
    with pytest.raises(ValueError, match="formal data"):
        _request(tmp_path, formal_output_root=Path("H:/Asteria-data"))
