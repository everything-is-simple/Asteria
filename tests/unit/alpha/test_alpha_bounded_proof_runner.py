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


def _seed_malf_service(
    path: Path,
    timeframe: str = "day",
    service_version: str = "service-v1",
    sample_version: str = "sample-v1",
) -> None:
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
        rows = [
            _wave_row(
                i,
                timeframe=timeframe,
                service_version=service_version,
                sample_version=sample_version,
            )
            for i in range(8)
        ]
        placeholders = ", ".join(["?"] * 25)
        con.executemany(f"insert into malf_wave_position values ({placeholders})", rows)
        con.executemany(f"insert into malf_wave_position_latest values ({placeholders})", rows[-2:])


def _wave_row(
    offset: int,
    timeframe: str = "day",
    service_version: str = "service-v1",
    sample_version: str = "sample-v1",
) -> tuple[object, ...]:
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
        timeframe,
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
        sample_version,
        "lifespan-rule-v1",
        service_version,
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
        _request(tmp_path, "BOF", mode="unsafe")
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
            timeframe="quarter",
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


def test_family_build_accepts_week_and_month_timeframes(tmp_path: Path) -> None:
    _seed_malf_service(
        tmp_path / "data" / "malf_service_week.duckdb",
        timeframe="week",
        service_version="malf-wave-position-week-v1",
        sample_version="malf-week-sample-v1",
    )
    request = AlphaFamilyRequest(
        source_malf_db=tmp_path / "data" / "malf_service_week.duckdb",
        target_alpha_db=tmp_path / "data" / "alpha_bof.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="alpha-proof-unit-001",
        mode="segmented",
        alpha_family="BOF",
        source_malf_service_version="malf-wave-position-week-v1",
        timeframe="week",
        symbol_limit=10,
    )

    summary = run_alpha_family_build(request)

    assert summary.status == "completed"
    assert summary.timeframe == "week"
    with duckdb.connect(str(request.target_alpha_db), read_only=True) as con:
        assert con.execute("select distinct timeframe from alpha_event_ledger").fetchall() == [
            ("week",)
        ]


def test_same_run_id_keeps_distinct_timeframe_outputs(tmp_path: Path) -> None:
    day_db = tmp_path / "data" / "malf_service_day.duckdb"
    week_db = tmp_path / "data" / "malf_service_week.duckdb"
    target_db = tmp_path / "data" / "alpha_bof.duckdb"
    _seed_malf_service(day_db)
    _seed_malf_service(
        week_db,
        timeframe="week",
        service_version="malf-wave-position-week-v1",
        sample_version="malf-week-sample-v1",
    )

    day_request = _request(tmp_path, "BOF")
    week_request = AlphaFamilyRequest(
        source_malf_db=week_db,
        target_alpha_db=target_db,
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id=day_request.run_id,
        mode="segmented",
        alpha_family="BOF",
        source_malf_service_version="malf-wave-position-week-v1",
        timeframe="week",
        symbol_limit=10,
    )

    run_alpha_family_build(day_request)
    run_alpha_family_build(week_request)

    with duckdb.connect(str(target_db), read_only=True) as con:
        assert con.execute(
            """
            select timeframe, count(*)
            from alpha_event_ledger
            group by 1
            order by 1
            """
        ).fetchall() == [("day", 8), ("week", 8)]


def test_family_build_can_lock_source_run_and_sample_version(tmp_path: Path) -> None:
    source_db = tmp_path / "data" / "malf_service_day.duckdb"
    _seed_malf_service(
        source_db,
        service_version="malf-wave-position-dense-v1",
        sample_version="current-sample",
    )
    with duckdb.connect(str(source_db)) as con:
        old_rows = [
            _wave_row(
                i,
                service_version="malf-wave-position-dense-v1",
                sample_version="old-sample",
            )
            for i in range(8)
        ]
        placeholders = ", ".join(["?"] * 25)
        con.executemany(f"insert into malf_wave_position values ({placeholders})", old_rows)
        con.execute(
            """
            update malf_wave_position
            set run_id = 'old-run'
            where sample_version = 'old-sample'
            """
        )
        con.execute(
            """
            update malf_wave_position
            set run_id = 'current-run'
            where sample_version = 'current-sample'
            """
        )

    request = AlphaFamilyRequest(
        source_malf_db=source_db,
        target_alpha_db=tmp_path / "data" / "alpha_bof.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="alpha-proof-unit-001",
        mode="bounded",
        alpha_family="BOF",
        source_malf_service_version="malf-wave-position-dense-v1",
        source_malf_run_id="current-run",
        source_malf_sample_version="current-sample",
        symbol_limit=10,
    )

    summary = run_alpha_family_build(request)

    assert summary.event_count == 8
    with duckdb.connect(str(request.target_alpha_db), read_only=True) as con:
        assert con.execute(
            "select distinct source_malf_run_id from alpha_event_ledger"
        ).fetchall() == [("current-run",)]


def test_production_builder_runs_configured_timeframes(tmp_path: Path) -> None:
    from asteria.alpha.bootstrap import run_alpha_production_builder

    _seed_malf_service(tmp_path / "data" / "malf_service_day.duckdb")
    _seed_malf_service(
        tmp_path / "data" / "malf_service_week.duckdb",
        timeframe="week",
        service_version="malf-wave-position-week-v1",
        sample_version="malf-week-sample-v1",
    )

    summaries = run_alpha_production_builder(
        source_malf_dbs={
            "day": tmp_path / "data" / "malf_service_day.duckdb",
            "week": tmp_path / "data" / "malf_service_week.duckdb",
        },
        source_malf_service_versions={
            "day": "service-v1",
            "week": "malf-wave-position-week-v1",
        },
        target_data_root=tmp_path / "data",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="alpha-production-unit-001",
        mode="segmented",
        symbol_limit=10,
        timeframes=("day", "week"),
    )

    assert len(summaries) == 10
    assert {summary.timeframe for summary in summaries} == {"day", "week"}
    assert all(summary.hard_fail_count == 0 for summary in summaries)
    assert (tmp_path / "validated" / "Asteria-alpha-production-unit-001.zip").exists()


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
