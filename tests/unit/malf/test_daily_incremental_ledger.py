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
    high, low = _prices()[offset]
    close = round((high + low) / 2, 2)
    return (
        symbol,
        "stock",
        "day",
        bar_dt,
        bar_dt,
        "analysis_price_line",
        "backward",
        close,
        high,
        low,
        close,
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
            {"status": "completed", "summary": {"run_id": run_id}}, ensure_ascii=False, indent=2
        ),
        encoding="utf-8",
    )
    return source_manifest_path, dirty_scope_path, checkpoint_path


def _request(
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


def test_daily_incremental_ledger_writes_manifest_scope_lineage_checkpoint_and_audit(
    tmp_path: Path,
) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb", ("AAA.SZ",))

    summary = run_malf_daily_incremental_ledger(_request(tmp_path, "malf-daily-001"))

    assert summary.status == "passed"
    assert summary.replay_scope_count == 1
    assert summary.impact_scope_count >= 1
    manifest = json.loads(Path(summary.source_manifest_path).read_text(encoding="utf-8"))
    replay_scope = json.loads(Path(summary.derived_replay_scope_path).read_text(encoding="utf-8"))
    impact_scope = json.loads(Path(summary.daily_impact_scope_path).read_text(encoding="utf-8"))
    lineage = json.loads(Path(summary.lineage_path).read_text(encoding="utf-8"))
    checkpoint = json.loads(Path(summary.checkpoint_path).read_text(encoding="utf-8"))
    audit = json.loads(Path(summary.audit_summary_path).read_text(encoding="utf-8"))

    assert manifest["source_data_run_id"] == "data-hardening-001"
    assert replay_scope["scopes"][0]["target_start_dt"] == "2024-01-02"
    assert replay_scope["scopes"][0]["symbol"] == "AAA.SZ"
    assert all(item["trade_date"] >= "2024-01-02" for item in impact_scope["scopes"])
    assert lineage["lineage"][0]["source_run_id"] == "data-hardening-001"
    assert checkpoint["status"] == "completed"
    assert audit["status"] == "passed"


def test_daily_incremental_ledger_resume_reuses_completed_checkpoint(
    tmp_path: Path,
) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb", ("AAA.SZ",))
    run_malf_daily_incremental_ledger(_request(tmp_path, "malf-daily-resume-001"))

    resumed = run_malf_daily_incremental_ledger(
        _request(tmp_path, "malf-daily-resume-001", mode="resume")
    )

    assert resumed.resume_reused is True
    with duckdb.connect(
        str(tmp_path / "asteria-temp" / "malf-target" / "malf_service_day.duckdb")
    ) as con:
        assert con.execute("select count(*) from malf_wave_position").fetchone()[0] > 0


def test_daily_incremental_ledger_rerun_keeps_wave_position_natural_key_unique(
    tmp_path: Path,
) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb", ("AAA.SZ",))
    request = _request(tmp_path, "malf-daily-rerun-001")

    run_malf_daily_incremental_ledger(request)
    run_malf_daily_incremental_ledger(request)

    with duckdb.connect(
        str(tmp_path / "asteria-temp" / "malf-target" / "malf_service_day.duckdb")
    ) as con:
        duplicate_count = con.execute(
            """
            select count(*) from (
                select symbol, timeframe, bar_dt, service_version, count(*) as row_count
                from malf_wave_position
                group by 1, 2, 3, 4
                having row_count > 1
            )
            """
        ).fetchone()[0]
    assert duplicate_count == 0


def test_daily_incremental_ledger_replays_forward_from_dirty_date_not_only_single_day(
    tmp_path: Path,
) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb", ("AAA.SZ",))

    summary = run_malf_daily_incremental_ledger(_request(tmp_path, "malf-daily-forward-001"))
    replay_scope = json.loads(Path(summary.derived_replay_scope_path).read_text(encoding="utf-8"))
    impact_scope = json.loads(Path(summary.daily_impact_scope_path).read_text(encoding="utf-8"))

    assert replay_scope["scopes"][0]["target_start_dt"] == "2024-01-02"
    assert replay_scope["scopes"][0]["target_end_dt"] > "2024-01-03"
    assert len({item["trade_date"] for item in impact_scope["scopes"]}) > 1
    assert all(item["trade_date"] >= "2024-01-02" for item in impact_scope["scopes"])


def test_daily_incremental_ledger_keeps_week_month_unwritten(
    tmp_path: Path,
) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb", ("AAA.SZ",))

    run_malf_daily_incremental_ledger(_request(tmp_path, "malf-daily-day-only-001"))

    target_root = tmp_path / "asteria-temp" / "malf-target"
    assert (target_root / "malf_core_day.duckdb").exists()
    assert (target_root / "malf_lifespan_day.duckdb").exists()
    assert (target_root / "malf_service_day.duckdb").exists()
    assert not (target_root / "malf_core_week.duckdb").exists()
    assert not (target_root / "malf_lifespan_week.duckdb").exists()
    assert not (target_root / "malf_service_week.duckdb").exists()
