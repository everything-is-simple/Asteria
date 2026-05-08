from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import duckdb
import pytest
from tests.unit.system_readout.support import (
    SOURCE_CHAIN_RELEASE_VERSION,
    build_request,
    seed_chain,
)

from asteria.system_readout.bootstrap import (
    run_system_readout_audit,
    run_system_readout_bounded_proof,
    run_system_readout_build,
)
from asteria.system_readout.contracts import SystemReadoutBuildRequest
from asteria.system_readout.rules import ReadoutRefs, classify_readout_status
from asteria.system_readout.schema import SYSTEM_READOUT_TABLES


def test_request_rejects_out_of_scope_modes_and_timeframes(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsupported System Readout run mode"):
        build_request(tmp_path, mode="full")
    with pytest.raises(ValueError, match="Unsupported System Readout timeframe"):
        SystemReadoutBuildRequest(
            source_malf_service_db=tmp_path / "data" / "malf_service_day.duckdb",
            source_alpha_root=tmp_path / "data",
            source_signal_db=tmp_path / "data" / "signal.duckdb",
            source_position_db=tmp_path / "data" / "position.duckdb",
            source_portfolio_plan_db=tmp_path / "data" / "portfolio_plan.duckdb",
            source_trade_db=tmp_path / "data" / "trade.duckdb",
            target_system_db=tmp_path / "data" / "system.duckdb",
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id="run-1",
            mode="bounded",
            timeframe="week",
            source_chain_release_version=SOURCE_CHAIN_RELEASE_VERSION,
            symbol_limit=1,
        )


def test_build_writes_traceable_chain_readout_and_snapshot_outputs(tmp_path: Path) -> None:
    seed_chain(tmp_path)

    summary = run_system_readout_build(build_request(tmp_path))

    assert summary.status == "completed"
    assert summary.source_manifest_count == 10
    assert summary.module_status_count == 6
    with duckdb.connect(str(tmp_path / "data" / "system.duckdb"), read_only=True) as con:
        tables = {
            row[0]
            for row in con.execute(
                "select table_name from information_schema.tables where table_schema = 'main'"
            ).fetchall()
        }
        statuses = dict(
            con.execute(
                """
                select readout_status, count(*)
                from system_chain_readout
                group by 1
                """
            ).fetchall()
        )
        refs = con.execute(
            """
            select symbol, readout_status, trade_ref
            from system_chain_readout
            order by symbol
            """
        ).fetchall()
        module_names = {
            row[0]
            for row in con.execute(
                "select module_name from system_module_status_snapshot"
            ).fetchall()
        }

    assert tables == set(SYSTEM_READOUT_TABLES)
    assert statuses["complete"] == 1
    assert statuses["partial"] == 1
    assert statuses["source_gap"] == 1
    assert ("600000.SH", "complete", "intent-600000") in refs
    assert ("600001.SH", "partial", None) in refs
    assert ("600002.SH", "source_gap", None) in refs
    assert module_names == {"malf", "alpha", "signal", "position", "portfolio_plan", "trade"}


def test_classify_readout_status_supports_audit_gap() -> None:
    status = classify_readout_status(
        ReadoutRefs(
            malf_ref="wave-1",
            alpha_ref="alpha-1",
            signal_ref="signal-1",
            position_ref="position-1",
            portfolio_plan_ref=None,
            trade_ref=None,
        ),
        has_upstream_audit_gap=True,
    )

    assert status == "audit_gap"


def test_audit_rejects_forbidden_trade_output_columns(tmp_path: Path) -> None:
    seed_chain(tmp_path)
    request = build_request(tmp_path)
    run_system_readout_build(request)
    with duckdb.connect(str(request.target_system_db)) as con:
        con.execute("alter table system_chain_readout add column fill_price double")

    summary = run_system_readout_audit(request)

    assert summary.hard_fail_count > 0
    report_payload = json.loads(Path(summary.report_path or "").read_text(encoding="utf-8"))
    failed_checks = {
        row["check_name"]
        for row in report_payload["checks"]
        if row["severity"] == "hard" and row["status"] == "fail"
    }
    assert "system_readout_forbidden_columns_absent" in failed_checks


def test_bounded_proof_writes_closeout_and_validated_zip(tmp_path: Path) -> None:
    seed_chain(tmp_path)

    summary = run_system_readout_bounded_proof(
        source_malf_service_db=tmp_path / "data" / "malf_service_day.duckdb",
        source_alpha_root=tmp_path / "data",
        source_signal_db=tmp_path / "data" / "signal.duckdb",
        source_position_db=tmp_path / "data" / "position.duckdb",
        source_portfolio_plan_db=tmp_path / "data" / "portfolio_plan.duckdb",
        source_trade_db=tmp_path / "data" / "trade.duckdb",
        target_system_db=tmp_path / "data" / "system.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="system-readout-bounded-proof-unit-001",
        source_chain_release_version=SOURCE_CHAIN_RELEASE_VERSION,
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
        / "system_readout"
        / date.today().isoformat()
        / "system-readout-bounded-proof-unit-001"
        / "manifest.json"
    ).exists()
    with pytest.raises(ValueError, match="already contains run_id"):
        run_system_readout_build(build_request(tmp_path))


def test_build_does_not_promote_when_source_trade_audit_fails(tmp_path: Path) -> None:
    seed_chain(tmp_path, trade_hard_fail_count=2)

    summary = run_system_readout_build(build_request(tmp_path))

    assert summary.status == "failed"
    assert summary.hard_fail_count > 0
    assert not (tmp_path / "data" / "system.duckdb").exists()


def test_resume_reuses_completed_checkpoint(tmp_path: Path) -> None:
    seed_chain(tmp_path)
    run_system_readout_build(build_request(tmp_path))

    summary = run_system_readout_build(build_request(tmp_path, mode="resume"))

    assert summary.status == "completed"
    assert summary.resume_reused is True
