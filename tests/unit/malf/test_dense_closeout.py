from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import duckdb
from tests.unit.malf.test_bounded_proof_runner import (
    _request,
    _seed_market_base_day,
)

from asteria.malf.bootstrap import (
    run_malf_day_audit,
    run_malf_day_core_build,
    run_malf_day_lifespan_build,
    run_malf_day_service_build,
)


def test_malf_lifespan_cli_requires_source_db_for_dense_bars(tmp_path: Path) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    request = _request(tmp_path, "malf-cli-core-run-001")
    run_malf_day_core_build(request)
    script = (
        Path(__file__).resolve().parents[3]
        / "scripts"
        / "malf"
        / ("run_malf_day_lifespan_build.py")
    )

    missing_source = subprocess.run(
        [
            sys.executable,
            str(script),
            "--core-db",
            str(request.core_db),
            "--target-db",
            str(request.lifespan_db),
            "--mode",
            "bounded",
            "--run-id",
            "malf-cli-lifespan-run-missing-source",
            "--rule-version",
            "lifespan-rule-v1",
            "--sample-version",
            "sample-v1",
            "--start-dt",
            "2024-01-01",
            "--end-dt",
            "2024-01-31",
            "--symbol-limit",
            "10",
        ],
        capture_output=True,
        text=True,
    )
    assert missing_source.returncode != 0
    assert "--source-db" in missing_source.stderr

    with_source = subprocess.run(
        [
            sys.executable,
            str(script),
            "--source-db",
            str(request.source_db),
            "--core-db",
            str(request.core_db),
            "--target-db",
            str(request.lifespan_db),
            "--mode",
            "bounded",
            "--run-id",
            "malf-cli-lifespan-run-001",
            "--rule-version",
            "lifespan-rule-v1",
            "--sample-version",
            "sample-v1",
            "--start-dt",
            "2024-01-01",
            "--end-dt",
            "2024-01-31",
            "--symbol-limit",
            "10",
        ],
        capture_output=True,
        text=True,
    )
    assert with_source.returncode == 0, with_source.stderr
    payload = json.loads(with_source.stdout)
    assert payload["status"] == "completed"

    with duckdb.connect(str(request.lifespan_db), read_only=True) as con:
        dense_dates = [
            row[0]
            for row in con.execute(
                """
                select bar_dt
                from malf_lifespan_snapshot
                where symbol = 'UPCASE.SH'
                order by bar_dt
                """
            ).fetchall()
        ]
        first_dense_dt = dense_dates[0]
    with duckdb.connect(str(request.source_db), read_only=True) as con:
        source_dates = [
            row[0]
            for row in con.execute(
                """
                select bar_dt
                from market_base_bar
                where symbol = 'UPCASE.SH' and timeframe = 'day'
                  and bar_dt >= ?
                order by bar_dt
                """,
                [first_dense_dt],
            ).fetchall()
        ]
    assert dense_dates == source_dates


def test_malf_audit_fails_when_dense_source_bar_snapshot_is_missing(tmp_path: Path) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    request = _request(tmp_path, "malf-dense-audit-run-001")

    run_malf_day_core_build(request)
    run_malf_day_lifespan_build(request)
    run_malf_day_service_build(request)

    with duckdb.connect(str(request.lifespan_db)) as con:
        con.execute(
            """
            delete from malf_lifespan_snapshot
            where snapshot_id = (
                select snapshot_id
                from malf_lifespan_snapshot
                where symbol = 'UPCASE.SH'
                order by bar_dt
                limit 1
            )
            """
        )

    run_malf_day_audit(request)

    with duckdb.connect(str(request.service_db), read_only=True) as con:
        audit_row = con.execute(
            """
            select status, failed_count
            from malf_interface_audit
            where run_id = ? and check_name = 'lifespan_dense_source_bar_coverage'
            """,
            [request.run_id],
        ).fetchone()

    assert audit_row == ("fail", 1)


def test_malf_service_publishes_only_current_lifespan_run(tmp_path: Path) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    first = _request(tmp_path, "malf-service-source-run-001")
    second = _request(tmp_path, "malf-service-source-run-002")

    run_malf_day_core_build(first)
    run_malf_day_lifespan_build(first)
    run_malf_day_lifespan_build(second)
    run_malf_day_service_build(second)

    with duckdb.connect(str(second.lifespan_db), read_only=True) as con:
        second_lifespan_count = con.execute(
            "select count(*) from malf_lifespan_snapshot where run_id = ?",
            [second.run_id],
        ).fetchone()[0]
        all_lifespan_count = con.execute("select count(*) from malf_lifespan_snapshot").fetchone()[
            0
        ]
    with duckdb.connect(str(second.service_db), read_only=True) as con:
        second_service_count = con.execute(
            "select count(*) from malf_wave_position where run_id = ?",
            [second.run_id],
        ).fetchone()[0]

    assert all_lifespan_count > second_lifespan_count
    assert second_service_count == second_lifespan_count
