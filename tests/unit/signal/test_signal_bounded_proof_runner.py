from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import duckdb
import pytest

from asteria.signal.bootstrap import (
    SIGNAL_FAMILY_DATABASES,
    run_signal_audit,
    run_signal_bounded_proof,
    run_signal_build,
)
from asteria.signal.contracts import SignalBuildRequest
from asteria.signal.schema import SIGNAL_TABLES


def _request(tmp_path: Path, mode: str = "bounded") -> SignalBuildRequest:
    return SignalBuildRequest(
        source_alpha_root=tmp_path / "data",
        target_signal_db=tmp_path / "data" / "signal.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="signal-bounded-proof-unit-001",
        mode=mode,
        source_alpha_release_version="alpha-bounded-proof-unit",
        start_dt="2024-01-01",
        end_dt="2024-01-31",
        symbol_limit=10,
    )


def _seed_alpha_family(path: Path, family: str, rows: list[tuple[object, ...]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table alpha_signal_candidate (
                alpha_candidate_id varchar,
                alpha_event_id varchar,
                alpha_family varchar,
                symbol varchar,
                timeframe varchar,
                bar_dt date,
                candidate_type varchar,
                candidate_state varchar,
                opportunity_bias varchar,
                confidence_bucket varchar,
                reason_code varchar,
                candidate_score double,
                source_malf_service_version varchar,
                source_malf_run_id varchar,
                run_id varchar,
                schema_version varchar,
                alpha_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table alpha_source_audit (
                audit_id varchar,
                run_id varchar,
                alpha_family varchar,
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
            insert into alpha_source_audit
            values (?, ?, ?, 'unit_seed_ok', 'hard', 'pass', 0, '{}', now())
            """,
            [f"{family}|audit", "alpha-unit-run", family],
        )
        con.executemany(
            """
            insert into alpha_signal_candidate
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, now())
            """,
            rows,
        )


def _alpha_row(
    family: str,
    symbol: str,
    bar_dt: date,
    state: str,
    bias: str,
    score: float,
    bucket: str = "high",
) -> tuple[object, ...]:
    candidate_id = f"{family}|{symbol}|{bar_dt.isoformat()}|{state}|{bias}"
    return (
        candidate_id,
        f"event|{candidate_id}",
        family,
        symbol,
        "day",
        bar_dt,
        f"{family.lower()}_candidate",
        state,
        bias,
        bucket,
        f"{family.lower()}_{state}",
        score,
        "service-v1",
        "malf-run-1",
        "alpha-run-1",
        "alpha-schema-v1",
        "alpha-rule-v1",
    )


def _seed_all_alpha_sources(root: Path) -> None:
    scenarios = {
        "BOF": [
            _alpha_row("BOF", "600000.SH", date(2024, 1, 2), "candidate", "up", 0.90),
            _alpha_row("BOF", "600001.SH", date(2024, 1, 2), "candidate", "up", 0.80),
            _alpha_row("BOF", "600002.SH", date(2024, 1, 2), "filtered", "up", 0.95),
        ],
        "TST": [
            _alpha_row("TST", "600000.SH", date(2024, 1, 2), "candidate", "up", 0.70),
            _alpha_row("TST", "600001.SH", date(2024, 1, 2), "candidate", "down", 0.80),
        ],
        "PB": [
            _alpha_row("PB", "600000.SH", date(2024, 1, 2), "candidate", "up", 0.60),
            _alpha_row("PB", "600003.SH", date(2024, 1, 2), "candidate", "down", 0.20),
        ],
        "CPB": [
            _alpha_row("CPB", "600000.SH", date(2024, 1, 3), "candidate", "down", 0.90),
        ],
        "BPB": [
            _alpha_row("BPB", "600000.SH", date(2024, 1, 3), "candidate", "down", 0.80),
        ],
    }
    for family, rows in scenarios.items():
        _seed_alpha_family(root / SIGNAL_FAMILY_DATABASES[family], family, rows)


def test_signal_request_rejects_out_of_scope_modes_and_timeframes(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsupported Signal run mode"):
        _request(tmp_path, mode="full")
    with pytest.raises(ValueError, match="Unsupported Signal timeframe"):
        SignalBuildRequest(
            source_alpha_root=tmp_path / "data",
            target_signal_db=tmp_path / "data" / "signal.duckdb",
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id="run-1",
            mode="bounded",
            timeframe="week",
            source_alpha_release_version="alpha-release",
            symbol_limit=1,
        )


def test_signal_build_writes_schema_and_traceable_outputs(tmp_path: Path) -> None:
    _seed_all_alpha_sources(tmp_path / "data")

    summary = run_signal_build(_request(tmp_path))

    assert summary.status == "completed"
    assert summary.input_candidate_count == 9
    assert summary.formal_signal_count == 5
    assert summary.component_count == 9
    with duckdb.connect(str(tmp_path / "data" / "signal.duckdb"), read_only=True) as con:
        tables = {
            row[0]
            for row in con.execute(
                "select table_name from information_schema.tables where table_schema = 'main'"
            ).fetchall()
        }
        assert tables == set(SIGNAL_TABLES)
        active_rows = con.execute(
            """
            select symbol, signal_dt, signal_state, signal_bias, signal_type
            from formal_signal_ledger
            where signal_state = 'active'
            order by symbol, signal_dt
            """
        ).fetchall()
        rejected_rows = con.execute(
            """
            select symbol, signal_state, signal_bias, signal_type
            from formal_signal_ledger
            where signal_state = 'rejected'
            order by symbol
            """
        ).fetchall()
        component_roles = {
            row[0]
            for row in con.execute(
                "select distinct component_role from signal_component_ledger"
            ).fetchall()
        }
        missing_trace_count = con.execute(
            """
            select count(*)
            from signal_component_ledger c
            left join signal_input_snapshot s
              on c.signal_run_id = s.signal_run_id
             and c.alpha_family = s.alpha_family
             and c.alpha_candidate_id = s.alpha_candidate_id
            where s.alpha_candidate_id is null
            """
        ).fetchone()[0]

    assert active_rows == [
        (
            "600000.SH",
            date(2024, 1, 2),
            "active",
            "up_opportunity",
            "directional_opportunity",
        ),
        (
            "600000.SH",
            date(2024, 1, 3),
            "active",
            "down_opportunity",
            "directional_opportunity",
        ),
    ]
    assert ("600001.SH", "rejected", "neutral", "conflict_or_weak_signal") in rejected_rows
    assert ("600002.SH", "rejected", "neutral", "no_candidate_signal") in rejected_rows
    assert {"support", "conflict", "rejected"}.issubset(component_roles)
    assert missing_trace_count == 0


def test_signal_audit_rejects_forbidden_downstream_columns(tmp_path: Path) -> None:
    _seed_all_alpha_sources(tmp_path / "data")
    request = _request(tmp_path)
    run_signal_build(request)
    with duckdb.connect(str(request.target_signal_db)) as con:
        con.execute("alter table formal_signal_ledger add column position_size double")

    summary = run_signal_audit(request)

    assert summary.hard_fail_count > 0
    report_payload = json.loads(Path(summary.report_path or "").read_text(encoding="utf-8"))
    assert any(
        row["check_name"] == "signal_forbidden_columns" and row["status"] == "fail"
        for row in report_payload["checks"]
    )


def test_audit_only_does_not_write_business_rows(tmp_path: Path) -> None:
    _seed_all_alpha_sources(tmp_path / "data")
    request = _request(tmp_path, mode="audit-only")

    summary = run_signal_audit(request)

    assert summary.status == "failed"
    assert summary.formal_signal_count == 0
    with duckdb.connect(str(tmp_path / "data" / "signal.duckdb"), read_only=True) as con:
        assert con.execute("select count(*) from formal_signal_ledger").fetchone()[0] == 0
        assert con.execute("select count(*) from signal_audit").fetchone()[0] > 0


def test_bounded_proof_writes_closeout_and_validated_zip(tmp_path: Path) -> None:
    _seed_all_alpha_sources(tmp_path / "data")

    summary = run_signal_bounded_proof(
        source_alpha_root=tmp_path / "data",
        target_signal_db=tmp_path / "data" / "signal.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="signal-bounded-proof-unit-001",
        source_alpha_release_version="alpha-bounded-proof-unit",
        start_dt="2024-01-01",
        end_dt="2024-01-31",
        symbol_limit=10,
    )

    assert summary.hard_fail_count == 0
    assert summary.validated_zip is not None
    assert Path(summary.validated_zip).exists()
    assert (
        tmp_path
        / "report"
        / "signal"
        / date.today().isoformat()
        / "signal-bounded-proof-unit-001"
        / "manifest.json"
    ).exists()
