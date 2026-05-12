from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb
from scripts.pipeline.run_downstream_daily_incremental_ledger import main
from tests.unit.position.test_position_bounded_proof_runner import _seed_signal_db
from tests.unit.position.test_position_daily_incremental_ledger import _write_signal_artifacts
from tests.unit.system_readout.support import seed_chain


def _argv(tmp_path: Path, run_id: str, *, mode: str) -> list[str]:
    scope_path, lineage_path, checkpoint_path = _write_signal_artifacts(
        tmp_path, source_run_id="signal-production-builder-hardening-20260506-01"
    )
    return [
        "run_downstream_daily_incremental_ledger.py",
        "--malf-service-db",
        str(tmp_path / "data" / "malf_service_day.duckdb"),
        "--alpha-root",
        str(tmp_path / "data"),
        "--signal-db",
        str(tmp_path / "data" / "signal.duckdb"),
        "--position-db",
        str(tmp_path / "asteria-temp" / "position-target" / "position.duckdb"),
        "--portfolio-plan-db",
        str(tmp_path / "asteria-temp" / "portfolio-plan-target" / "portfolio_plan.duckdb"),
        "--trade-db",
        str(tmp_path / "asteria-temp" / "trade-target" / "trade.duckdb"),
        "--system-db",
        str(tmp_path / "asteria-temp" / "system-target" / "system.duckdb"),
        "--temp-root",
        str(tmp_path / "asteria-temp"),
        "--report-root",
        str(tmp_path / "asteria-report"),
        "--run-id",
        run_id,
        "--mode",
        mode,
        "--signal-daily-impact-scope-path",
        str(scope_path),
        "--signal-lineage-path",
        str(lineage_path),
        "--signal-checkpoint-path",
        str(checkpoint_path),
    ]


def _seed_pipeline_signal_db(path: Path) -> None:
    _seed_signal_db(path)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table signal_run (
                run_id varchar,
                runner_name varchar,
                mode varchar,
                timeframe varchar,
                status varchar,
                source_alpha_root varchar,
                input_candidate_count bigint,
                formal_signal_count bigint,
                component_count bigint,
                hard_fail_count bigint,
                schema_version varchar,
                signal_rule_version varchar,
                source_alpha_release_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table signal_component_ledger (
                signal_component_id varchar,
                signal_id varchar,
                signal_run_id varchar,
                alpha_family varchar,
                alpha_candidate_id varchar,
                component_role varchar,
                component_weight double,
                alpha_rule_version varchar
            )
            """
        )
        con.execute(
            """
            insert into signal_run
            values (
                'signal-production-builder-hardening-20260506-01',
                'signal_build',
                'daily_incremental',
                'day',
                'completed',
                'H:\\Asteria-temp',
                3,
                3,
                3,
                0,
                'signal-bounded-proof-v1',
                'signal-alpha-aggregation-minimal-v1',
                'alpha-production-builder-hardening-20260506-01',
                now()
            )
            """
        )
        con.executemany(
            """
            insert into signal_component_ledger
            values (
                ?,
                ?,
                'signal-production-builder-hardening-20260506-01',
                'BOF',
                ?,
                'support',
                1.0,
                'alpha-waveposition-production-v1'
            )
            """,
            [
                ("component-600000", "sig-long", "BOF-candidate-600000"),
                ("component-600001", "sig-short", "BOF-candidate-600001"),
                ("component-600002", "sig-rejected", "BOF-candidate-missing"),
            ],
        )


def test_downstream_daily_incremental_pipeline_chain_writes_summary_closeout_and_resume(
    tmp_path: Path,
    monkeypatch,
) -> None:
    seed_chain(tmp_path)
    signal_db = tmp_path / "data" / "signal.duckdb"
    signal_db.unlink()
    _seed_pipeline_signal_db(signal_db)
    run_id = "downstream-daily-incremental-runner-build-card"

    monkeypatch.setattr(sys, "argv", _argv(tmp_path, run_id, mode="daily_incremental"))
    assert main() == 0

    monkeypatch.setattr(sys, "argv", _argv(tmp_path, run_id, mode="resume"))
    assert main() == 0

    summary_path = tmp_path / "asteria-report" / "pipeline" / "2026-05-12" / run_id / "summary.json"
    closeout_path = summary_path.with_name("closeout.md")
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    system_audit_path = (
        tmp_path
        / "asteria-report"
        / "system_readout"
        / "2026-05-12"
        / run_id
        / "audit-summary.json"
    )
    system_audit = json.loads(system_audit_path.read_text(encoding="utf-8"))

    assert payload["status"] == "passed"
    assert payload["position"]["status"] == "passed"
    assert payload["portfolio_plan"]["status"] == "passed"
    assert payload["trade"]["status"] == "passed"
    assert payload["system_readout"]["status"] == "passed"
    assert payload["position"]["resume_reused"] is True
    assert payload["portfolio_plan"]["resume_reused"] is True
    assert payload["trade"]["resume_reused"] is True
    assert payload["system_readout"]["resume_reused"] is True
    assert closeout_path.exists()
    assert "pipeline_full_daily_incremental_chain_build_card" in closeout_path.read_text(
        encoding="utf-8"
    )
    assert system_audit["boundaries"]["system_readout_read_only_consumer"] is True
