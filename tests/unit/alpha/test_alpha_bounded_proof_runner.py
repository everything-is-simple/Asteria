from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import duckdb
import pytest

from asteria.alpha.bootstrap import (
    ALPHA_FAMILY_DATABASES,
    run_alpha_bounded_proof,
    run_alpha_family_audit,
    run_alpha_family_build,
)
from asteria.alpha.contracts import AlphaFamilyRequest
from asteria.alpha.schema import ALPHA_TABLES


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
        rows = [_wave_row(i) for i in range(8)]
        placeholders = ", ".join(["?"] * 25)
        con.executemany(f"insert into malf_wave_position values ({placeholders})", rows)
        con.executemany(f"insert into malf_wave_position_latest values ({placeholders})", rows[-2:])


def _wave_row(offset: int) -> tuple[object, ...]:
    states = [
        ("up_alive", "alive", "up", 1, 0, 0, 0.95, 0.30, "developing", "developing"),
        ("up_alive", "alive", "up", 2, 0, 0, 0.90, 0.50, "extended", "extended_active"),
        ("up_alive", "alive", "up", 2, 2, 0, 0.80, 0.90, "stagnant", "extended_stagnant"),
        ("down_alive", "alive", "down", 1, 1, 0, 0.70, 0.80, "stagnant", "extended_stagnant"),
        ("transition", "terminated", "down", 2, 0, 1, 0.50, 0.50, "terminal", "extended_stagnant"),
        ("transition", "terminated", "up", 1, 0, 2, 0.60, 0.60, "terminal", "extended_active"),
        ("down_alive", "alive", "down", 0, 0, 0, 0.20, 0.20, "developing", "developing"),
        ("up_alive", "alive", "up", 1, 3, 0, 0.30, 0.95, "stagnant", "extended_stagnant"),
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
        "service-v1",
        "malf-run-1",
        "malf-schema-v1",
        "core-run-1",
        "lifespan-run-1",
        "2026-04-29 00:00:00",
    )


def _request(tmp_path: Path, family: str, mode: str = "bounded") -> AlphaFamilyRequest:
    return AlphaFamilyRequest(
        source_malf_db=tmp_path / "data" / "malf_service_day.duckdb",
        target_alpha_db=tmp_path / "data" / ALPHA_FAMILY_DATABASES[family],
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="alpha-proof-unit-001",
        mode=mode,
        alpha_family=family,
        source_malf_service_version="service-v1",
        start_dt="2024-01-01",
        end_dt="2024-01-31",
        symbol_limit=10,
    )


def test_alpha_request_rejects_out_of_scope_modes_and_timeframes(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsupported Alpha run mode"):
        _request(tmp_path, "BOF", mode="full")
    with pytest.raises(ValueError, match="Unsupported Alpha timeframe"):
        AlphaFamilyRequest(
            source_malf_db=tmp_path / "source.duckdb",
            target_alpha_db=tmp_path / "alpha.duckdb",
            report_root=tmp_path,
            validated_root=tmp_path,
            temp_root=tmp_path,
            run_id="run-1",
            mode="bounded",
            alpha_family="BOF",
            timeframe="week",
            source_malf_service_version="service-v1",
            symbol_limit=1,
        )


def test_family_build_writes_only_alpha_tables_and_real_outputs(tmp_path: Path) -> None:
    _seed_malf_service(tmp_path / "data" / "malf_service_day.duckdb")

    summary = run_alpha_family_build(_request(tmp_path, "BOF"))

    assert summary.status == "completed"
    assert summary.event_count > 0
    assert summary.candidate_count > 0
    with duckdb.connect(str(tmp_path / "data" / "alpha_bof.duckdb"), read_only=True) as con:
        tables = {
            row[0]
            for row in con.execute(
                "select table_name from information_schema.tables where table_schema = 'main'"
            ).fetchall()
        }
        assert tables == set(ALPHA_TABLES)
        assert con.execute("select count(*) from alpha_event_ledger").fetchone()[0] > 0
        assert con.execute("select count(*) from alpha_score_ledger").fetchone()[0] > 0
        assert con.execute("select count(*) from alpha_signal_candidate").fetchone()[0] > 0
        assert con.execute("select distinct alpha_family from alpha_event_ledger").fetchall() == [
            ("BOF",)
        ]


def test_family_build_canonicalizes_duplicate_waveposition_dates(tmp_path: Path) -> None:
    source_db = tmp_path / "data" / "malf_service_day.duckdb"
    _seed_malf_service(source_db)
    with duckdb.connect(str(source_db)) as con:
        duplicate = list(_wave_row(4))
        duplicate[3] = "down_alive"
        duplicate[4] = f"duplicate-{duplicate[4]}"
        duplicate[5] = None
        con.execute(
            f"insert into malf_wave_position values ({', '.join(['?'] * 25)})",
            duplicate,
        )

    summary = run_alpha_family_build(_request(tmp_path, "BPB"))

    assert summary.hard_fail_count == 0
    with duckdb.connect(str(tmp_path / "data" / "alpha_bpb.duckdb"), read_only=True) as con:
        assert (
            con.execute(
                """
                select count(*) from (
                    select alpha_family, symbol, timeframe, bar_dt, event_type,
                           alpha_rule_version, count(*) row_count
                    from alpha_event_ledger
                    group by 1, 2, 3, 4, 5, 6
                    having row_count > 1
                )
                """
            ).fetchone()[0]
            == 0
        )


def test_bounded_proof_runs_all_families_and_writes_closeout(tmp_path: Path) -> None:
    _seed_malf_service(tmp_path / "data" / "malf_service_day.duckdb")

    summaries = run_alpha_bounded_proof(
        source_malf_db=tmp_path / "data" / "malf_service_day.duckdb",
        target_data_root=tmp_path / "data",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="alpha-proof-unit-001",
        start_dt="2024-01-01",
        end_dt="2024-01-31",
        symbol_limit=10,
    )

    assert {summary.alpha_family for summary in summaries} == {"BOF", "TST", "PB", "CPB", "BPB"}
    assert all(summary.hard_fail_count == 0 for summary in summaries)
    closeout = tmp_path / "report" / "alpha" / date.today().isoformat()
    payloads = list(closeout.glob("alpha-proof-unit-001*summary.json"))
    assert payloads


def test_audit_only_does_not_write_business_rows(tmp_path: Path) -> None:
    _seed_malf_service(tmp_path / "data" / "malf_service_day.duckdb")
    request = _request(tmp_path, "TST", mode="audit-only")

    summary = run_alpha_family_audit(request)

    assert summary.status == "completed"
    assert summary.event_count == 0
    with duckdb.connect(str(tmp_path / "data" / "alpha_tst.duckdb"), read_only=True) as con:
        assert con.execute("select count(*) from alpha_event_ledger").fetchone()[0] == 0
        assert con.execute("select count(*) from alpha_source_audit").fetchone()[0] > 0


def test_audit_fails_for_forbidden_candidate_columns(tmp_path: Path) -> None:
    _seed_malf_service(tmp_path / "data" / "malf_service_day.duckdb")
    request = _request(tmp_path, "PB")
    run_alpha_family_build(request)
    with duckdb.connect(str(request.target_alpha_db)) as con:
        con.execute("alter table alpha_signal_candidate add column position_size double")

    summary = run_alpha_family_audit(request)

    assert summary.hard_fail_count > 0
    report_payload = json.loads(Path(summary.report_path or "").read_text(encoding="utf-8"))
    assert any(
        row["check_name"] == "candidate_forbidden_columns" and row["status"] == "fail"
        for row in report_payload["checks"]
    )
