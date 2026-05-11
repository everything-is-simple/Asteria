from __future__ import annotations

import json
from pathlib import Path

import duckdb

try:
    from asteria.alpha.daily_incremental_ledger import (
        AlphaDailyIncrementalLedgerRequest,
        run_alpha_daily_incremental_ledger,
    )
except ImportError:  # pragma: no cover - TDD red phase
    AlphaDailyIncrementalLedgerRequest = None
    run_alpha_daily_incremental_ledger = None

try:
    from asteria.signal.daily_incremental_ledger import (
        SignalDailyIncrementalLedgerRequest,
        run_signal_daily_incremental_ledger,
    )
except ImportError:  # pragma: no cover - TDD red phase
    SignalDailyIncrementalLedgerRequest = None
    run_signal_daily_incremental_ledger = None

from tests.unit.alpha.test_daily_incremental_ledger import _alpha_request


def _prepare_alpha_sample(tmp_path: Path) -> tuple[Path, Path, Path]:
    assert run_alpha_daily_incremental_ledger is not None
    run_root = tmp_path / "asteria-temp" / "alpha" / "alpha-daily-source-001"
    cached_paths = (
        run_root / "daily-impact-scope.json",
        run_root / "lineage.json",
        run_root / "checkpoint.json",
    )
    if all(path.exists() for path in cached_paths):
        return cached_paths
    request = _alpha_request(tmp_path, "alpha-daily-source-001")
    assert request is not None
    summary = run_alpha_daily_incremental_ledger(request)
    return (
        Path(summary.daily_impact_scope_path),
        Path(summary.lineage_path),
        Path(summary.checkpoint_path),
    )


def _signal_request(tmp_path: Path, run_id: str, *, mode: str = "daily_incremental") -> object:
    daily_impact_scope_path, lineage_path, checkpoint_path = _prepare_alpha_sample(tmp_path)
    if SignalDailyIncrementalLedgerRequest is None:
        return None
    return SignalDailyIncrementalLedgerRequest(
        source_alpha_root=tmp_path / "asteria-temp" / "alpha-target",
        target_signal_db=tmp_path / "asteria-temp" / "signal-target" / "signal.duckdb",
        temp_root=tmp_path / "asteria-temp",
        report_root=tmp_path / "asteria-report",
        run_id=run_id,
        mode=mode,
        alpha_daily_impact_scope_path=daily_impact_scope_path,
        alpha_lineage_path=lineage_path,
        alpha_checkpoint_path=checkpoint_path,
    )


def test_signal_daily_incremental_ledger_writes_scope_lineage_checkpoint_and_formal_signal(
    tmp_path: Path,
) -> None:
    assert run_signal_daily_incremental_ledger is not None
    request = _signal_request(tmp_path, "signal-daily-001")
    assert request is not None

    summary = run_signal_daily_incremental_ledger(request)

    assert summary.status == "passed"
    assert summary.replay_scope_count == 1
    assert summary.impact_scope_count >= 1
    impact_scope = json.loads(Path(summary.daily_impact_scope_path).read_text(encoding="utf-8"))
    lineage = json.loads(Path(summary.lineage_path).read_text(encoding="utf-8"))
    checkpoint = json.loads(Path(summary.checkpoint_path).read_text(encoding="utf-8"))
    assert all(item["trade_date"] >= "2024-01-02" for item in impact_scope["scopes"])
    assert len(lineage["lineage"]) == 1
    assert checkpoint["status"] == "completed"
    with duckdb.connect(
        str(tmp_path / "asteria-temp" / "signal-target" / "signal.duckdb"), read_only=True
    ) as con:
        assert con.execute("select count(*) from formal_signal_ledger").fetchone()[0] > 0


def test_signal_daily_incremental_ledger_consumes_alpha_batch_run_id_only(
    tmp_path: Path,
) -> None:
    assert run_signal_daily_incremental_ledger is not None
    request = _signal_request(tmp_path, "signal-daily-source-run-001")
    assert request is not None

    summary = run_signal_daily_incremental_ledger(request)
    lineage = json.loads(Path(summary.lineage_path).read_text(encoding="utf-8"))

    with duckdb.connect(
        str(tmp_path / "asteria-temp" / "signal-target" / "signal.duckdb"), read_only=True
    ) as con:
        source_run_ids = {
            row[0]
            for row in con.execute(
                "select distinct source_alpha_run_id from signal_input_snapshot"
            ).fetchall()
        }
    assert source_run_ids == {lineage["lineage"][0]["source_run_id"]}


def test_signal_daily_incremental_ledger_resume_reuses_completed_checkpoint(
    tmp_path: Path,
) -> None:
    assert run_signal_daily_incremental_ledger is not None
    request = _signal_request(tmp_path, "signal-daily-resume-001")
    assert request is not None
    run_signal_daily_incremental_ledger(request)

    resumed_request = _signal_request(tmp_path, "signal-daily-resume-001", mode="resume")
    assert resumed_request is not None
    resumed = run_signal_daily_incremental_ledger(resumed_request)

    assert resumed.resume_reused is True


def test_signal_daily_incremental_ledger_rerun_keeps_formal_signal_natural_keys_unique(
    tmp_path: Path,
) -> None:
    assert run_signal_daily_incremental_ledger is not None
    request = _signal_request(tmp_path, "signal-daily-rerun-001")
    assert request is not None

    run_signal_daily_incremental_ledger(request)
    run_signal_daily_incremental_ledger(request)

    with duckdb.connect(
        str(tmp_path / "asteria-temp" / "signal-target" / "signal.duckdb"), read_only=True
    ) as con:
        duplicates = con.execute(
            """
            select count(*) from (
                select symbol, timeframe, signal_dt, signal_type, signal_rule_version,
                       count(*) as row_count
                from formal_signal_ledger
                group by 1, 2, 3, 4, 5
                having row_count > 1
            )
            """
        ).fetchone()[0]
    assert duplicates == 0
