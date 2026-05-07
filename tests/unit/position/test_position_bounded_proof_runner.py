from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import duckdb
import pytest

from asteria.position.bootstrap import (
    run_position_audit,
    run_position_bounded_proof,
    run_position_build,
)
from asteria.position.contracts import PositionBuildRequest
from asteria.position.schema import POSITION_TABLES


def _request(tmp_path: Path, mode: str = "bounded") -> PositionBuildRequest:
    return PositionBuildRequest(
        source_signal_db=tmp_path / "data" / "signal.duckdb",
        target_position_db=tmp_path / "data" / "position.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="position-bounded-proof-unit-001",
        mode=mode,
        source_signal_release_version="signal-production-builder-hardening-20260506-01",
        source_signal_run_id="signal-production-builder-hardening-20260506-01",
        start_dt="2024-01-01",
        end_dt="2024-01-31",
        symbol_limit=10,
    )


def _seed_signal_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table formal_signal_ledger (
                signal_id varchar,
                symbol varchar,
                timeframe varchar,
                signal_dt date,
                signal_type varchar,
                signal_state varchar,
                signal_bias varchar,
                signal_strength double,
                confidence_bucket varchar,
                reason_code varchar,
                support_count bigint,
                conflict_count bigint,
                rejected_component_count bigint,
                source_alpha_release_version varchar,
                run_id varchar,
                schema_version varchar,
                signal_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table signal_audit (
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
            insert into signal_audit
            values (
                'signal-unit|audit',
                'signal-production-builder-hardening-20260506-01',
                'unit_seed_ok',
                'hard',
                'pass',
                0,
                '{}',
                now()
            )
            """
        )
        rows = [
            (
                "sig-long",
                "600000.SH",
                "day",
                date(2024, 1, 2),
                "directional_opportunity",
                "active",
                "up_opportunity",
                0.82,
                "high",
                "alpha_candidate_support",
            ),
            (
                "sig-short",
                "600001.SH",
                "day",
                date(2024, 1, 3),
                "directional_opportunity",
                "active",
                "down_opportunity",
                0.76,
                "medium",
                "alpha_candidate_support",
            ),
            (
                "sig-rejected",
                "600002.SH",
                "day",
                date(2024, 1, 4),
                "conflict_or_weak_signal",
                "rejected",
                "neutral",
                0.1,
                "low",
                "signal_strength_below_threshold",
            ),
        ]
        con.executemany(
            """
            insert into formal_signal_ledger
            values (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0, 0,
                'alpha-production-builder-hardening-20260506-01',
                'signal-production-builder-hardening-20260506-01',
                'signal-bounded-proof-v1',
                'signal-alpha-aggregation-minimal-v1',
                now()
            )
            """,
            rows,
        )


def test_position_request_rejects_out_of_scope_modes_and_timeframes(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsupported Position run mode"):
        _request(tmp_path, mode="manual")
    with pytest.raises(ValueError, match="Unsupported Position timeframe"):
        PositionBuildRequest(
            source_signal_db=tmp_path / "data" / "signal.duckdb",
            target_position_db=tmp_path / "data" / "position.duckdb",
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id="run-1",
            mode="bounded",
            timeframe="week",
            source_signal_release_version="signal-release",
            symbol_limit=1,
        )


def test_position_build_writes_traceable_candidate_and_plan_outputs(tmp_path: Path) -> None:
    _seed_signal_db(tmp_path / "data" / "signal.duckdb")

    summary = run_position_build(_request(tmp_path))

    assert summary.status == "completed"
    assert summary.input_signal_count == 3
    assert summary.position_candidate_count == 3
    assert summary.entry_plan_count == 2
    assert summary.exit_plan_count == 2
    with duckdb.connect(str(tmp_path / "data" / "position.duckdb"), read_only=True) as con:
        tables = {
            row[0]
            for row in con.execute(
                "select table_name from information_schema.tables where table_schema = 'main'"
            ).fetchall()
        }
        assert tables == set(POSITION_TABLES)
        candidates = con.execute(
            """
            select signal_id, candidate_state, position_bias
            from position_candidate_ledger
            order by signal_id
            """
        ).fetchall()
        missing_entry = con.execute(
            """
            select count(*)
            from position_candidate_ledger c
            left join position_entry_plan e
              on c.position_candidate_id = e.position_candidate_id
            where c.candidate_state = 'planned'
              and e.position_candidate_id is null
            """
        ).fetchone()[0]
        forbidden_columns = [
            row
            for table in ("position_candidate_ledger", "position_entry_plan", "position_exit_plan")
            for row in con.execute(f"describe {table}").fetchall()
            if row[0] in {"target_weight", "portfolio_allocation", "order_intent_id", "fill_id"}
        ]

    assert ("sig-long", "planned", "long_candidate") in candidates
    assert ("sig-short", "planned", "short_candidate") in candidates
    assert ("sig-rejected", "rejected", "neutral_candidate") in candidates
    assert missing_entry == 0
    assert forbidden_columns == []


def test_position_audit_rejects_forbidden_downstream_columns(tmp_path: Path) -> None:
    _seed_signal_db(tmp_path / "data" / "signal.duckdb")
    request = _request(tmp_path)
    run_position_build(request)
    with duckdb.connect(str(request.target_position_db)) as con:
        con.execute("alter table position_candidate_ledger add column target_weight double")

    summary = run_position_audit(request)

    assert summary.hard_fail_count > 0
    report_payload = json.loads(Path(summary.report_path or "").read_text(encoding="utf-8"))
    assert any(
        row["check_name"] == "position_forbidden_columns" and row["status"] == "fail"
        for row in report_payload["checks"]
    )


def test_position_bounded_proof_writes_closeout_and_validated_zip(tmp_path: Path) -> None:
    _seed_signal_db(tmp_path / "data" / "signal.duckdb")

    summary = run_position_bounded_proof(
        source_signal_db=tmp_path / "data" / "signal.duckdb",
        target_position_db=tmp_path / "data" / "position.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="position-bounded-proof-unit-001",
        source_signal_release_version="signal-production-builder-hardening-20260506-01",
        source_signal_run_id="signal-production-builder-hardening-20260506-01",
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
        / "position"
        / date.today().isoformat()
        / "position-bounded-proof-unit-001"
        / "manifest.json"
    ).exists()
