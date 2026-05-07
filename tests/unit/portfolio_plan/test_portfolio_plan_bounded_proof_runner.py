from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import duckdb
import pytest

from asteria.portfolio_plan.bootstrap import (
    run_portfolio_plan_audit,
    run_portfolio_plan_bounded_proof,
    run_portfolio_plan_build,
)
from asteria.portfolio_plan.contracts import PortfolioPlanBuildRequest
from asteria.portfolio_plan.schema import PORTFOLIO_PLAN_TABLES

SOURCE_POSITION_RUN_ID = "position-bounded-proof-build-card-20260506-01"


def _request(tmp_path: Path, mode: str = "bounded") -> PortfolioPlanBuildRequest:
    return PortfolioPlanBuildRequest(
        source_position_db=tmp_path / "data" / "position.duckdb",
        target_portfolio_plan_db=tmp_path / "data" / "portfolio_plan.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="portfolio-plan-bounded-proof-unit-001",
        mode=mode,
        source_position_release_version=SOURCE_POSITION_RUN_ID,
        source_position_run_id=SOURCE_POSITION_RUN_ID,
        start_dt="2024-01-01",
        end_dt="2024-01-31",
        symbol_limit=10,
    )


def _seed_position_db(path: Path, hard_fail_count: int = 0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table position_run (
                run_id varchar,
                runner_name varchar,
                mode varchar,
                timeframe varchar,
                status varchar,
                source_signal_db varchar,
                input_signal_count bigint,
                position_candidate_count bigint,
                entry_plan_count bigint,
                exit_plan_count bigint,
                hard_fail_count bigint,
                schema_version varchar,
                position_rule_version varchar,
                source_signal_release_version varchar,
                source_signal_run_id varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table position_candidate_ledger (
                position_candidate_id varchar,
                signal_id varchar,
                symbol varchar,
                timeframe varchar,
                candidate_dt date,
                candidate_type varchar,
                candidate_state varchar,
                position_bias varchar,
                reason_code varchar,
                source_signal_release_version varchar,
                run_id varchar,
                schema_version varchar,
                position_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table position_entry_plan (
                entry_plan_id varchar,
                position_candidate_id varchar,
                entry_plan_type varchar,
                entry_trigger_type varchar,
                entry_reference_dt date,
                entry_valid_from date,
                entry_valid_until date,
                entry_state varchar,
                run_id varchar,
                schema_version varchar,
                position_rule_version varchar,
                source_signal_release_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table position_exit_plan (
                exit_plan_id varchar,
                position_candidate_id varchar,
                exit_plan_type varchar,
                exit_trigger_type varchar,
                exit_reference_dt date,
                exit_valid_from date,
                exit_valid_until date,
                exit_state varchar,
                run_id varchar,
                schema_version varchar,
                position_rule_version varchar,
                source_signal_release_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table position_audit (
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
            insert into position_run
            values (?, 'position_build', 'bounded', 'day', 'completed', 'signal.duckdb',
                    6, 6, 5, 5, ?, 'position-bounded-proof-v1',
                    'position-signal-plan-minimal-v1',
                    'signal-production-builder-hardening-20260506-01',
                    'signal-production-builder-hardening-20260506-01', now())
            """,
            [SOURCE_POSITION_RUN_ID, hard_fail_count],
        )
        con.execute(
            """
            insert into position_audit
            values ('position-unit|audit', ?, 'unit_seed', 'hard', ?, ?, '{}', now())
            """,
            [
                SOURCE_POSITION_RUN_ID,
                "fail" if hard_fail_count else "pass",
                hard_fail_count,
            ],
        )
        candidates = [
            ("cand-600000-old", "sig-600000-old", "600000.SH", date(2024, 1, 2), "planned"),
            ("cand-600000-new", "sig-600000-new", "600000.SH", date(2024, 1, 10), "planned"),
            ("cand-600001", "sig-600001", "600001.SH", date(2024, 1, 9), "planned"),
            ("cand-600002", "sig-600002", "600002.SH", date(2024, 1, 8), "planned"),
            ("cand-600003", "sig-600003", "600003.SH", date(2024, 1, 7), "planned"),
            ("cand-600004", "sig-600004", "600004.SH", date(2024, 1, 6), "rejected"),
        ]
        con.executemany(
            """
            insert into position_candidate_ledger
            values (?, ?, ?, 'day', ?, 'directional_position_candidate',
                    ?, 'long_candidate', 'unit_fixture',
                    'signal-production-builder-hardening-20260506-01',
                    ?, 'position-bounded-proof-v1',
                    'position-signal-plan-minimal-v1', now())
            """,
            [
                (candidate_id, signal_id, symbol, candidate_dt, state, SOURCE_POSITION_RUN_ID)
                for candidate_id, signal_id, symbol, candidate_dt, state in candidates
            ],
        )
        planned_candidate_ids = [
            candidate_id for candidate_id, *_rest, state in candidates if state == "planned"
        ]
        con.executemany(
            """
            insert into position_entry_plan
            values (?, ?, 'signal_follow_entry', 'next_session_open_plan',
                    '2024-01-02', '2024-01-02', null, 'planned',
                    ?, 'position-bounded-proof-v1', 'position-signal-plan-minimal-v1',
                    'signal-production-builder-hardening-20260506-01', now())
            """,
            [
                (f"entry-{candidate_id}", candidate_id, SOURCE_POSITION_RUN_ID)
                for candidate_id in planned_candidate_ids
            ],
        )
        con.executemany(
            """
            insert into position_exit_plan
            values (?, ?, 'signal_invalidation_exit', 'signal_invalidated_or_expired',
                    '2024-01-02', '2024-01-02', null, 'planned',
                    ?, 'position-bounded-proof-v1', 'position-signal-plan-minimal-v1',
                    'signal-production-builder-hardening-20260506-01', now())
            """,
            [
                (f"exit-{candidate_id}", candidate_id, SOURCE_POSITION_RUN_ID)
                for candidate_id in planned_candidate_ids
            ],
        )


def test_portfolio_plan_request_rejects_out_of_scope_modes_and_timeframes(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="Unsupported Portfolio Plan run mode"):
        _request(tmp_path, mode="full")
    with pytest.raises(ValueError, match="Unsupported Portfolio Plan timeframe"):
        PortfolioPlanBuildRequest(
            source_position_db=tmp_path / "data" / "position.duckdb",
            target_portfolio_plan_db=tmp_path / "data" / "portfolio_plan.duckdb",
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id="run-1",
            mode="bounded",
            timeframe="week",
            source_position_release_version="position-release",
            symbol_limit=1,
        )
    with pytest.raises(ValueError, match="bounded Portfolio Plan runs require"):
        PortfolioPlanBuildRequest(
            source_position_db=tmp_path / "data" / "position.duckdb",
            target_portfolio_plan_db=tmp_path / "data" / "portfolio_plan.duckdb",
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id="run-2",
            mode="bounded",
            source_position_release_version="position-release",
        )


def test_portfolio_plan_build_writes_traceable_admission_exposure_and_trim(
    tmp_path: Path,
) -> None:
    _seed_position_db(tmp_path / "data" / "position.duckdb")

    summary = run_portfolio_plan_build(_request(tmp_path))

    assert summary.status == "completed"
    assert summary.input_position_count == 6
    assert summary.admission_count == 6
    assert summary.target_exposure_count == 4
    assert summary.trim_count == 1
    with duckdb.connect(str(tmp_path / "data" / "portfolio_plan.duckdb"), read_only=True) as con:
        tables = {
            row[0]
            for row in con.execute(
                "select table_name from information_schema.tables where table_schema = 'main'"
            ).fetchall()
        }
        states = con.execute(
            """
            select admission_state, count(*)
            from portfolio_admission_ledger
            group by 1
            order by 1
            """
        ).fetchall()
        forbidden_columns = [
            row
            for table in (
                "portfolio_admission_ledger",
                "portfolio_target_exposure",
                "portfolio_trim_ledger",
            )
            for row in con.execute(f"describe {table}").fetchall()
            if row[0] in {"order_intent_id", "execution_price", "fill_id", "broker_order_id"}
        ]

    assert tables == set(PORTFOLIO_PLAN_TABLES)
    assert states == [("admitted", 3), ("expired", 1), ("rejected", 1), ("trimmed", 1)]
    assert forbidden_columns == []


def test_portfolio_plan_audit_rejects_boundary_and_trace_failures(tmp_path: Path) -> None:
    _seed_position_db(tmp_path / "data" / "position.duckdb")
    request = _request(tmp_path)
    run_portfolio_plan_build(request)
    with duckdb.connect(str(request.target_portfolio_plan_db)) as con:
        con.execute("alter table portfolio_admission_ledger add column fill_id varchar")
        con.execute(
            """
            delete from portfolio_target_exposure
            where portfolio_admission_id in (
                select portfolio_admission_id
                from portfolio_admission_ledger
                where admission_state = 'admitted'
                limit 1
            )
            """
        )

    summary = run_portfolio_plan_audit(request)

    assert summary.hard_fail_count > 0
    report_payload = json.loads(Path(summary.report_path or "").read_text(encoding="utf-8"))
    failed_checks = {
        row["check_name"]
        for row in report_payload["checks"]
        if row["severity"] == "hard" and row["status"] == "fail"
    }
    assert "portfolio_forbidden_columns" in failed_checks
    assert "admitted_or_trimmed_has_target_exposure" in failed_checks


def test_portfolio_plan_bounded_proof_promotes_once_and_writes_evidence(
    tmp_path: Path,
) -> None:
    _seed_position_db(tmp_path / "data" / "position.duckdb")

    summary = run_portfolio_plan_bounded_proof(
        source_position_db=tmp_path / "data" / "position.duckdb",
        target_portfolio_plan_db=tmp_path / "data" / "portfolio_plan.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="portfolio-plan-bounded-proof-unit-001",
        source_position_release_version=SOURCE_POSITION_RUN_ID,
        source_position_run_id=SOURCE_POSITION_RUN_ID,
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
        / "portfolio_plan"
        / date.today().isoformat()
        / "portfolio-plan-bounded-proof-unit-001"
        / "manifest.json"
    ).exists()
    with pytest.raises(ValueError, match="already contains run_id"):
        run_portfolio_plan_build(_request(tmp_path))


def test_portfolio_plan_build_does_not_promote_when_source_position_audit_fails(
    tmp_path: Path,
) -> None:
    _seed_position_db(tmp_path / "data" / "position.duckdb", hard_fail_count=2)

    summary = run_portfolio_plan_build(_request(tmp_path))

    assert summary.status == "failed"
    assert summary.hard_fail_count > 0
    assert not (tmp_path / "data" / "portfolio_plan.duckdb").exists()


def test_portfolio_plan_resume_reuses_completed_checkpoint(tmp_path: Path) -> None:
    _seed_position_db(tmp_path / "data" / "position.duckdb")
    run_portfolio_plan_build(_request(tmp_path))

    summary = run_portfolio_plan_build(_request(tmp_path, mode="resume"))

    assert summary.status == "completed"
    assert summary.resume_reused is True
