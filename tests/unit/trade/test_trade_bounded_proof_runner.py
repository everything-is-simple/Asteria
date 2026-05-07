from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import duckdb
import pytest

from asteria.trade.bootstrap import (
    run_trade_audit,
    run_trade_bounded_proof,
    run_trade_build,
)
from asteria.trade.contracts import TradeBuildRequest
from asteria.trade.schema import TRADE_TABLES

SOURCE_PORTFOLIO_PLAN_RUN_ID = "portfolio-plan-bounded-proof-build-card-20260507-01"


def _request(tmp_path: Path, mode: str = "bounded") -> TradeBuildRequest:
    return TradeBuildRequest(
        source_portfolio_plan_db=tmp_path / "data" / "portfolio_plan.duckdb",
        target_trade_db=tmp_path / "data" / "trade.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="trade-bounded-proof-unit-001",
        mode=mode,
        source_portfolio_plan_release_version=SOURCE_PORTFOLIO_PLAN_RUN_ID,
        source_portfolio_plan_run_id=SOURCE_PORTFOLIO_PLAN_RUN_ID,
        start_dt="2024-01-01",
        end_dt="2024-01-31",
        symbol_limit=10,
    )


def _seed_portfolio_plan_db(path: Path, hard_fail_count: int = 0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table portfolio_plan_run (
                run_id varchar,
                runner_name varchar,
                mode varchar,
                timeframe varchar,
                status varchar,
                source_position_db varchar,
                input_position_count bigint,
                admission_count bigint,
                target_exposure_count bigint,
                trim_count bigint,
                hard_fail_count bigint,
                schema_version varchar,
                portfolio_plan_rule_version varchar,
                source_position_release_version varchar,
                source_position_run_id varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table portfolio_plan_audit (
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
            create table portfolio_admission_ledger (
                portfolio_admission_id varchar,
                position_candidate_id varchar,
                symbol varchar,
                timeframe varchar,
                plan_dt date,
                admission_state varchar,
                admission_reason varchar,
                source_position_release_version varchar,
                run_id varchar,
                schema_version varchar,
                portfolio_plan_rule_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table portfolio_target_exposure (
                target_exposure_id varchar,
                portfolio_admission_id varchar,
                exposure_type varchar,
                target_weight double,
                target_notional double,
                target_quantity_hint double,
                exposure_valid_from date,
                exposure_valid_until date,
                run_id varchar,
                schema_version varchar,
                portfolio_plan_rule_version varchar,
                source_position_release_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table portfolio_trim_ledger (
                portfolio_trim_id varchar,
                portfolio_admission_id varchar,
                trim_reason varchar,
                pre_trim_exposure double,
                post_trim_exposure double,
                constraint_name varchar,
                run_id varchar,
                schema_version varchar,
                portfolio_plan_rule_version varchar,
                source_position_release_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            insert into portfolio_plan_run
            values (?, 'portfolio_plan_build', 'bounded', 'day', 'completed', 'position.duckdb',
                    4, 4, 3, 1, ?, 'portfolio-plan-bounded-proof-v1',
                    'portfolio-plan-minimal-v1',
                    'position-bounded-proof-build-card-20260506-01',
                    'position-bounded-proof-build-card-20260506-01', now())
            """,
            [SOURCE_PORTFOLIO_PLAN_RUN_ID, hard_fail_count],
        )
        con.execute(
            """
            insert into portfolio_plan_audit
            values ('portfolio-plan-unit|audit', ?, 'unit_seed', 'hard', ?, ?, '{}', now())
            """,
            [
                SOURCE_PORTFOLIO_PLAN_RUN_ID,
                "fail" if hard_fail_count else "pass",
                hard_fail_count,
            ],
        )
        admissions = [
            (
                "adm-600000",
                "pc-600000",
                "600000.SH",
                date(2024, 1, 2),
                "admitted",
                "within_capacity_constraint",
            ),
            (
                "adm-600001",
                "pc-600001",
                "600001.SH",
                date(2024, 1, 3),
                "admitted",
                "within_capacity_constraint",
            ),
            (
                "adm-600002",
                "pc-600002",
                "600002.SH",
                date(2024, 1, 4),
                "trimmed",
                "max_active_symbols_constraint",
            ),
            (
                "adm-600003",
                "pc-600003",
                "600003.SH",
                date(2024, 1, 5),
                "rejected",
                "position_candidate_rejected",
            ),
        ]
        con.executemany(
            """
            insert into portfolio_admission_ledger
            values (?, ?, ?, 'day', ?, ?, ?, 'position-bounded-proof-build-card-20260506-01',
                    ?, 'portfolio-plan-bounded-proof-v1', 'portfolio-plan-minimal-v1', now())
            """,
            [
                (
                    admission_id,
                    candidate_id,
                    symbol,
                    plan_dt,
                    state,
                    reason,
                    SOURCE_PORTFOLIO_PLAN_RUN_ID,
                )
                for admission_id, candidate_id, symbol, plan_dt, state, reason in admissions
            ],
        )
        exposures = [
            ("exp-600000", "adm-600000", 0.25, 125000.0, 100.0),
            ("exp-600001", "adm-600001", 0.25, 130000.0, 120.0),
            ("exp-600002", "adm-600002", 0.0, 0.0, 0.0),
        ]
        exposure_rows = []
        for exposure in exposures:
            (
                target_exposure_id,
                admission_id,
                target_weight,
                target_notional,
                target_quantity_hint,
            ) = exposure
            exposure_rows.append(
                (
                    target_exposure_id,
                    admission_id,
                    target_weight,
                    target_notional,
                    target_quantity_hint,
                    SOURCE_PORTFOLIO_PLAN_RUN_ID,
                )
            )
        con.executemany(
            """
            insert into portfolio_target_exposure
            values (?, ?, 'target_weight', ?, ?, ?, '2024-01-02', null,
                    ?, 'portfolio-plan-bounded-proof-v1', 'portfolio-plan-minimal-v1',
                    'position-bounded-proof-build-card-20260506-01', now())
            """,
            exposure_rows,
        )
        con.execute(
            """
            insert into portfolio_trim_ledger
            values ('trim-600002', 'adm-600002', 'max_active_symbols_constraint', 0.25, 0.0,
                    'max_active_symbols', ?, 'portfolio-plan-bounded-proof-v1',
                    'portfolio-plan-minimal-v1',
                    'position-bounded-proof-build-card-20260506-01',
                    now())
            """,
            [SOURCE_PORTFOLIO_PLAN_RUN_ID],
        )


def test_trade_request_rejects_out_of_scope_modes_and_timeframes(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsupported Trade run mode"):
        _request(tmp_path, mode="full")
    with pytest.raises(ValueError, match="Unsupported Trade timeframe"):
        TradeBuildRequest(
            source_portfolio_plan_db=tmp_path / "data" / "portfolio_plan.duckdb",
            target_trade_db=tmp_path / "data" / "trade.duckdb",
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id="run-1",
            mode="bounded",
            timeframe="week",
            source_portfolio_plan_release_version="portfolio-plan-release",
        )


def test_trade_build_writes_traceable_intent_execution_and_retained_fill_gap(
    tmp_path: Path,
) -> None:
    _seed_portfolio_plan_db(tmp_path / "data" / "portfolio_plan.duckdb")

    summary = run_trade_build(_request(tmp_path))

    assert summary.status == "completed"
    assert summary.input_portfolio_plan_count == 4
    assert summary.order_intent_count == 2
    assert summary.execution_plan_count == 2
    assert summary.fill_count == 0
    assert summary.rejection_count == 2
    with duckdb.connect(str(tmp_path / "data" / "trade.duckdb"), read_only=True) as con:
        tables = {
            row[0]
            for row in con.execute(
                "select table_name from information_schema.tables where table_schema = 'main'"
            ).fetchall()
        }
        assert tables == set(TRADE_TABLES)
        intents = con.execute(
            """
            select portfolio_admission_id, order_side, order_intent_state
            from order_intent_ledger
            order by portfolio_admission_id
            """
        ).fetchall()
        fills = con.execute("select count(*) from fill_ledger").fetchone()[0]
        missing_exec = con.execute(
            """
            select count(*)
            from order_intent_ledger i
            left join execution_plan_ledger e
              on i.order_intent_id = e.order_intent_id
            where i.order_intent_state = 'intended'
              and e.order_intent_id is null
            """
        ).fetchone()[0]

    assert intents == [
        ("adm-600000", "buy", "intended"),
        ("adm-600001", "buy", "intended"),
    ]
    assert fills == 0
    assert missing_exec == 0


def test_trade_audit_rejects_forbidden_downstream_columns(tmp_path: Path) -> None:
    _seed_portfolio_plan_db(tmp_path / "data" / "portfolio_plan.duckdb")
    request = _request(tmp_path)
    run_trade_build(request)
    with duckdb.connect(str(request.target_trade_db)) as con:
        con.execute("alter table order_intent_ledger add column strategy_score double")

    summary = run_trade_audit(request)

    assert summary.hard_fail_count > 0
    report_payload = json.loads(Path(summary.report_path or "").read_text(encoding="utf-8"))
    assert any(
        row["check_name"] == "forbidden_trade_columns_absent" and row["status"] == "fail"
        for row in report_payload["checks"]
    )


def test_trade_bounded_proof_writes_closeout_and_validated_zip(tmp_path: Path) -> None:
    _seed_portfolio_plan_db(tmp_path / "data" / "portfolio_plan.duckdb")

    summary = run_trade_bounded_proof(
        source_portfolio_plan_db=tmp_path / "data" / "portfolio_plan.duckdb",
        target_trade_db=tmp_path / "data" / "trade.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="trade-bounded-proof-unit-001",
        source_portfolio_plan_release_version=SOURCE_PORTFOLIO_PLAN_RUN_ID,
        source_portfolio_plan_run_id=SOURCE_PORTFOLIO_PLAN_RUN_ID,
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
        / "trade"
        / date.today().isoformat()
        / "trade-bounded-proof-unit-001"
        / "manifest.json"
    ).exists()
