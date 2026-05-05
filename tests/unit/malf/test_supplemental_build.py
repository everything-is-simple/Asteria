from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import duckdb
import pytest

from asteria.data.schema import bootstrap_market_base_day_database
from asteria.malf.supplemental import (
    MalfSupplementalBuildRequest,
    make_scope,
    run_malf_day_supplemental_build,
)


def _seed_market_base_day(path: Path, symbols: tuple[str, ...]) -> None:
    bootstrap_market_base_day_database(path)
    with duckdb.connect(str(path)) as con:
        for symbol in symbols:
            placeholders = ", ".join(["?"] * 20)
            con.executemany(
                f"insert into market_base_bar values ({placeholders})",
                [_bar(symbol, offset, high, low) for offset, (high, low) in enumerate(_prices())],
            )


def _bar(symbol: str, offset: int, high: float, low: float) -> tuple[object, ...]:
    bar_dt = date(2024, 1, 1) + timedelta(days=offset)
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
        "seed-run-001",
        f"rev-{symbol}",
        f"H:/fixture/{symbol}.txt",
        "source-run-001",
        "data-bootstrap-v1",
        "2026-05-06 00:00:00",
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
    ]


def _request(tmp_path: Path, run_id: str, mode: str = "segmented") -> MalfSupplementalBuildRequest:
    return MalfSupplementalBuildRequest(
        source_db=tmp_path / "asteria-data" / "market_base_day.duckdb",
        core_db=tmp_path / "asteria-data" / "malf_core_day.duckdb",
        lifespan_db=tmp_path / "asteria-data" / "malf_lifespan_day.duckdb",
        service_db=tmp_path / "asteria-data" / "malf_service_day.duckdb",
        report_root=tmp_path / "asteria-report",
        validated_root=tmp_path / "asteria-validated",
        temp_root=tmp_path / "asteria-temp",
        run_id=run_id,
        mode=mode,
        scope=make_scope(start_dt="2024-01-01", end_dt="2024-01-31"),
        batch_size=1,
        symbols=("AAA.SZ", "BBB.SZ"),
        sample_version="sample-v1",
        service_version="service-v1",
    )


def test_supplemental_build_promotes_batches_and_resume_skips_completed(
    tmp_path: Path,
) -> None:
    source_db = tmp_path / "asteria-data" / "market_base_day.duckdb"
    _seed_market_base_day(source_db, ("AAA.SZ", "BBB.SZ"))

    first = run_malf_day_supplemental_build(_request(tmp_path, "malf-supp-run-001"))
    second = run_malf_day_supplemental_build(_request(tmp_path, "malf-supp-run-001", mode="resume"))

    assert first.promoted_batch_count == 2
    assert second.skipped_batch_count == 2
    with duckdb.connect(str(tmp_path / "asteria-data" / "malf_service_day.duckdb")) as con:
        symbol_count = con.execute(
            "select count(distinct symbol) from malf_wave_position"
        ).fetchone()[0]
    assert symbol_count == 2


def test_supplemental_build_rerun_does_not_duplicate_wave_position_natural_key(
    tmp_path: Path,
) -> None:
    source_db = tmp_path / "asteria-data" / "market_base_day.duckdb"
    _seed_market_base_day(source_db, ("AAA.SZ", "BBB.SZ"))
    request = _request(tmp_path, "malf-supp-run-002")

    run_malf_day_supplemental_build(request)
    run_malf_day_supplemental_build(request)

    with duckdb.connect(str(tmp_path / "asteria-data" / "malf_service_day.duckdb")) as con:
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


def test_supplemental_failed_batch_does_not_promote(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_db = tmp_path / "asteria-data" / "market_base_day.duckdb"
    _seed_market_base_day(source_db, ("AAA.SZ",))

    def fail_audit(stage_request: object) -> object:
        service_db = stage_request.service_db  # type: ignore[attr-defined]
        run_id = stage_request.run_id  # type: ignore[attr-defined]
        with duckdb.connect(str(service_db)) as con:
            con.execute(
                "insert into malf_interface_audit values (?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    "forced-fail",
                    run_id,
                    "forced_failure",
                    "hard",
                    "fail",
                    1,
                    "{}",
                    "2026-05-06 00:00:00",
                ],
            )
        return type("Summary", (), {"report_path": None})()

    monkeypatch.setattr("asteria.malf.supplemental.run_malf_day_audit", fail_audit)

    with pytest.raises(ValueError, match="hard_fail_count=1"):
        run_malf_day_supplemental_build(_request(tmp_path, "malf-supp-run-003"))

    assert not (tmp_path / "asteria-data" / "malf_service_day.duckdb").exists()
