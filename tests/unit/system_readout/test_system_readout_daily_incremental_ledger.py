from __future__ import annotations

import json
from pathlib import Path

import duckdb
from tests.unit.system_readout.support import seed_chain
from tests.unit.system_readout.support_upstream import TRADE_RUN_ID

from asteria.system_readout.contracts import SystemReadoutDailyIncrementalLedgerRequest
from asteria.system_readout.daily_incremental_ledger import (
    run_system_readout_daily_incremental_ledger,
)


def _write_trade_artifacts(tmp_path: Path, *, source_run_id: str) -> tuple[Path, Path, Path]:
    run_root = (
        tmp_path / "asteria-temp" / "trade" / "downstream-daily-incremental-runner-build-card"
    )
    run_root.mkdir(parents=True, exist_ok=True)
    impact_scope_path = run_root / "daily-impact-scope.json"
    lineage_path = run_root / "lineage.json"
    checkpoint_path = run_root / "checkpoint.json"
    impact_scope_path.write_text(
        json.dumps(
            {
                "scopes": [
                    {
                        "symbol": "600000.SH",
                        "trade_date": "2024-01-02",
                        "timeframe": "day",
                        "upstream_module": "trade",
                        "source_run_id": "portfolio-plan-sample-001",
                    },
                    {
                        "symbol": "600001.SH",
                        "trade_date": "2024-01-03",
                        "timeframe": "day",
                        "upstream_module": "trade",
                        "source_run_id": "portfolio-plan-sample-001",
                    },
                ]
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    lineage_path.write_text(
        json.dumps(
            {
                "lineage": [
                    {
                        "source_run_id": "portfolio-plan-sample-001",
                        "target_run_id": source_run_id,
                    }
                ]
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    checkpoint_path.write_text(json.dumps({"status": "completed"}, indent=2), encoding="utf-8")
    return impact_scope_path, lineage_path, checkpoint_path


def _request(
    tmp_path: Path,
    run_id: str,
    *,
    mode: str = "daily_incremental",
) -> SystemReadoutDailyIncrementalLedgerRequest:
    impact_scope_path, lineage_path, checkpoint_path = _write_trade_artifacts(
        tmp_path, source_run_id=TRADE_RUN_ID
    )
    return SystemReadoutDailyIncrementalLedgerRequest(
        source_malf_service_db=tmp_path / "data" / "malf_service_day.duckdb",
        source_alpha_root=tmp_path / "data",
        source_signal_db=tmp_path / "data" / "signal.duckdb",
        source_position_db=tmp_path / "data" / "position.duckdb",
        source_portfolio_plan_db=tmp_path / "data" / "portfolio_plan.duckdb",
        source_trade_db=tmp_path / "data" / "trade.duckdb",
        target_system_db=tmp_path / "asteria-temp" / "system-target" / "system.duckdb",
        temp_root=tmp_path / "asteria-temp",
        report_root=tmp_path / "asteria-report",
        run_id=run_id,
        mode=mode,
        trade_daily_impact_scope_path=impact_scope_path,
        trade_lineage_path=lineage_path,
        trade_checkpoint_path=checkpoint_path,
    )


def _count_runs(path: Path, run_id: str) -> int:
    with duckdb.connect(str(path), read_only=True) as con:
        return int(
            con.execute(
                "select count(*) from system_readout_run where run_id like ?",
                [f"{run_id}-%"],
            ).fetchone()[0]
        )


def test_system_readout_daily_incremental_ledger_writes_scope_lineage_checkpoint_and_temp_target(
    tmp_path: Path,
) -> None:
    seed_chain(tmp_path)
    request = _request(tmp_path, "system-daily-001")

    summary = run_system_readout_daily_incremental_ledger(request)

    assert summary.status == "passed"
    assert Path(summary.daily_impact_scope_path).exists()
    assert Path(summary.lineage_path).exists()
    assert Path(summary.checkpoint_path).exists()
    assert Path(summary.audit_summary_path).exists()
    assert str(tmp_path / "asteria-temp") in summary.daily_impact_scope_path
    assert str(tmp_path / "asteria-report") in summary.audit_summary_path
    assert _count_runs(request.target_system_db, request.run_id) > 0
    audit_summary = json.loads(Path(summary.audit_summary_path).read_text(encoding="utf-8"))
    assert audit_summary["boundaries"]["system_readout_read_only_consumer"] is True


def test_system_readout_daily_incremental_ledger_resume_reuses_checkpoint(
    tmp_path: Path,
) -> None:
    seed_chain(tmp_path)
    request = _request(tmp_path, "system-daily-resume-001")
    run_system_readout_daily_incremental_ledger(request)

    resumed = run_system_readout_daily_incremental_ledger(
        _request(tmp_path, "system-daily-resume-001", mode="resume")
    )

    assert resumed.status == "passed"
    assert resumed.resume_reused is True


def test_system_readout_daily_incremental_ledger_audit_only_does_not_write_target_db(
    tmp_path: Path,
) -> None:
    seed_chain(tmp_path)
    request = _request(tmp_path, "system-daily-audit-001", mode="audit-only")

    summary = run_system_readout_daily_incremental_ledger(request)

    assert summary.status == "passed"
    assert request.target_system_db.exists() is False
    assert Path(summary.audit_summary_path).exists()
