from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import duckdb

from asteria.data.schema import bootstrap_market_base_day_database
from asteria.malf.daily_incremental_ledger import (
    MalfDailyIncrementalLedgerRequest,
    run_malf_daily_incremental_ledger,
)

try:
    from asteria.alpha.daily_incremental_ledger import (
        AlphaDailyIncrementalLedgerRequest,
        run_alpha_daily_incremental_ledger,
    )
except ImportError:  # pragma: no cover - TDD red phase
    AlphaDailyIncrementalLedgerRequest = None
    run_alpha_daily_incremental_ledger = None


def _seed_market_base_day(
    path: Path,
    symbols: tuple[str, ...],
    *,
    base_dt: date = date(2023, 12, 25),
    days: int = 15,
) -> None:
    bootstrap_market_base_day_database(path)
    with duckdb.connect(str(path)) as con:
        for symbol in symbols:
            con.executemany(
                (
                    "insert into market_base_bar values "
                    "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                ),
                [_bar(symbol, offset, base_dt) for offset in range(days)],
            )


def _bar(symbol: str, offset: int, base_dt: date) -> tuple[object, ...]:
    bar_dt = base_dt + timedelta(days=offset)
    high_px, low_px = _prices()[offset]
    close_px = round((high_px + low_px) / 2, 2)
    return (
        symbol,
        "stock",
        "day",
        bar_dt,
        bar_dt,
        "analysis_price_line",
        "backward",
        close_px,
        high_px,
        low_px,
        close_px,
        1000.0 + offset,
        10000.0 + offset,
        "unit_fixture",
        f"data-run-{symbol}",
        f"rev-{symbol}",
        f"H:/fixture/{symbol}.txt",
        f"source-{symbol}",
        "data-bootstrap-v1",
        "2026-05-11 00:00:00",
    )


def _prices() -> list[tuple[float, float]]:
    return [
        (10.0, 9.0),
        (12.0, 10.0),
        (9.5, 8.0),
        (14.0, 9.0),
        (12.0, 10.0),
        (15.0, 11.0),
        (13.0, 10.5),
        (14.0, 10.8),
        (11.0, 7.0),
        (13.5, 8.5),
        (9.0, 6.0),
        (10.0, 7.0),
        (8.5, 5.5),
        (11.0, 6.5),
        (12.0, 8.0),
    ]


def _write_data_artifacts(
    tmp_path: Path, run_id: str, dirty_start_dt: str
) -> tuple[Path, Path, Path]:
    run_root = tmp_path / "asteria-temp" / "data" / run_id
    run_root.mkdir(parents=True, exist_ok=True)
    source_manifest_path = run_root / "source-manifest.json"
    dirty_scope_path = run_root / "daily-dirty-scope.json"
    checkpoint_path = run_root / "checkpoint.json"
    source_manifest_path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "schema_version": "data-daily-incremental-hardening-v1",
                "source_count": 1,
                "sources": [{"symbol": "AAA.SZ", "run_id": run_id}],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    dirty_scope_path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "schema_version": "data-daily-incremental-hardening-v1",
                "protocol_fields": ["symbol", "trade_date", "timeframe", "source_run_id"],
                "scope_count": 1,
                "scopes": [
                    {
                        "symbol": "AAA.SZ",
                        "timeframe": "day",
                        "dirty_start_dt": dirty_start_dt,
                        "dirty_end_dt": "2024-01-03",
                        "source_run_id": run_id,
                        "run_id": run_id,
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    checkpoint_path.write_text(
        json.dumps(
            {"status": "completed", "summary": {"run_id": run_id}},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return source_manifest_path, dirty_scope_path, checkpoint_path


def _malf_request(
    tmp_path: Path, run_id: str, *, mode: str = "daily_incremental"
) -> MalfDailyIncrementalLedgerRequest:
    source_manifest_path, dirty_scope_path, checkpoint_path = _write_data_artifacts(
        tmp_path, "data-hardening-001", "2024-01-02"
    )
    return MalfDailyIncrementalLedgerRequest(
        source_db=tmp_path / "asteria-data" / "market_base_day.duckdb",
        target_root=tmp_path / "asteria-temp" / "malf-target",
        temp_root=tmp_path / "asteria-temp",
        report_root=tmp_path / "asteria-report",
        run_id=run_id,
        mode=mode,
        data_source_manifest_path=source_manifest_path,
        data_daily_dirty_scope_path=dirty_scope_path,
        data_checkpoint_path=checkpoint_path,
    )


def _prepare_malf_sample(tmp_path: Path) -> tuple[Path, Path, Path]:
    run_root = tmp_path / "asteria-temp" / "malf" / "malf-daily-001"
    cached_paths = (
        run_root / "daily-impact-scope.json",
        run_root / "lineage.json",
        run_root / "checkpoint.json",
    )
    if all(path.exists() for path in cached_paths):
        return cached_paths
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb", ("AAA.SZ",))
    malf_summary = run_malf_daily_incremental_ledger(_malf_request(tmp_path, "malf-daily-001"))
    return (
        Path(malf_summary.daily_impact_scope_path),
        Path(malf_summary.lineage_path),
        Path(malf_summary.checkpoint_path),
    )


def _alpha_request(tmp_path: Path, run_id: str, *, mode: str = "daily_incremental") -> object:
    daily_impact_scope_path, lineage_path, checkpoint_path = _prepare_malf_sample(tmp_path)
    if AlphaDailyIncrementalLedgerRequest is None:
        return None
    return AlphaDailyIncrementalLedgerRequest(
        source_malf_root=tmp_path / "asteria-temp" / "malf-target",
        target_root=tmp_path / "asteria-temp" / "alpha-target",
        temp_root=tmp_path / "asteria-temp",
        report_root=tmp_path / "asteria-report",
        run_id=run_id,
        mode=mode,
        malf_daily_impact_scope_path=daily_impact_scope_path,
        malf_lineage_path=lineage_path,
        malf_checkpoint_path=checkpoint_path,
    )


def _count_alpha_candidates(path: Path, family: str) -> int:
    with duckdb.connect(str(path), read_only=True) as con:
        return int(
            con.execute(
                """
                select count(*) from alpha_signal_candidate
                where alpha_family = ?
                """,
                [family],
            ).fetchone()[0]
        )


def test_alpha_daily_incremental_ledger_writes_scope_lineage_checkpoint_and_candidates(
    tmp_path: Path,
) -> None:
    assert run_alpha_daily_incremental_ledger is not None
    request = _alpha_request(tmp_path, "alpha-daily-001")
    assert request is not None

    summary = run_alpha_daily_incremental_ledger(request)

    assert summary.status == "passed"
    assert summary.replay_scope_count == 1
    assert summary.impact_scope_count >= 5
    replay_scope = json.loads(Path(summary.derived_replay_scope_path).read_text(encoding="utf-8"))
    impact_scope = json.loads(Path(summary.daily_impact_scope_path).read_text(encoding="utf-8"))
    lineage = json.loads(Path(summary.lineage_path).read_text(encoding="utf-8"))
    checkpoint = json.loads(Path(summary.checkpoint_path).read_text(encoding="utf-8"))
    assert replay_scope["scopes"][0]["symbol"] == "AAA.SZ"
    assert all(item["trade_date"] >= "2024-01-02" for item in impact_scope["scopes"])
    assert len(lineage["lineage"]) == 5
    assert checkpoint["status"] == "completed"
    for family in ("BOF", "TST", "PB", "CPB", "BPB"):
        db_name = f"alpha_{family.lower()}.duckdb"
        assert (
            _count_alpha_candidates(tmp_path / "asteria-temp" / "alpha-target" / db_name, family)
            > 0
        )


def test_alpha_daily_incremental_ledger_resume_reuses_completed_checkpoint(
    tmp_path: Path,
) -> None:
    assert run_alpha_daily_incremental_ledger is not None
    request = _alpha_request(tmp_path, "alpha-daily-resume-001")
    assert request is not None
    run_alpha_daily_incremental_ledger(request)

    resumed_request = _alpha_request(tmp_path, "alpha-daily-resume-001", mode="resume")
    assert resumed_request is not None
    resumed = run_alpha_daily_incremental_ledger(resumed_request)

    assert resumed.resume_reused is True


def test_alpha_daily_incremental_ledger_rerun_keeps_candidate_natural_keys_unique(
    tmp_path: Path,
) -> None:
    assert run_alpha_daily_incremental_ledger is not None
    request = _alpha_request(tmp_path, "alpha-daily-rerun-001")
    assert request is not None

    run_alpha_daily_incremental_ledger(request)
    run_alpha_daily_incremental_ledger(request)

    target_db = tmp_path / "asteria-temp" / "alpha-target" / "alpha_bof.duckdb"
    with duckdb.connect(str(target_db), read_only=True) as con:
        duplicates = con.execute(
            """
            select count(*) from (
                select alpha_family, symbol, timeframe, bar_dt, candidate_type, alpha_rule_version,
                       count(*) as row_count
                from alpha_signal_candidate
                group by 1, 2, 3, 4, 5, 6
                having row_count > 1
            )
            """
        ).fetchone()[0]
    assert duplicates == 0


def test_alpha_daily_incremental_ledger_keeps_week_month_outputs_unwritten(
    tmp_path: Path,
) -> None:
    assert run_alpha_daily_incremental_ledger is not None
    request = _alpha_request(tmp_path, "alpha-daily-day-only-001")
    assert request is not None

    run_alpha_daily_incremental_ledger(request)

    target_root = tmp_path / "asteria-temp" / "alpha-target"
    assert (target_root / "alpha_bof.duckdb").exists()
    assert not (target_root / "alpha_week.duckdb").exists()
    assert not (target_root / "alpha_month.duckdb").exists()
