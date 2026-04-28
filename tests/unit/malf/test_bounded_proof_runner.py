from __future__ import annotations

import json
from pathlib import Path

import duckdb

from asteria.data.schema import bootstrap_market_base_day_database
from asteria.malf.bootstrap import (
    run_malf_day_audit,
    run_malf_day_core_build,
    run_malf_day_lifespan_build,
    run_malf_day_service_build,
)
from asteria.malf.contracts import MalfDayRequest


def _seed_market_base_day(path: Path) -> None:
    bootstrap_market_base_day_database(path)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            insert into market_base_bar
            values
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?),
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                "600000.SH",
                "stock",
                "day",
                "2024-01-02",
                "2024-01-02",
                "analysis_price_line",
                "backward",
                10.0,
                10.5,
                9.9,
                10.2,
                1000.0,
                10200.0,
                "tdx_offline_txt",
                "seed-run-001",
                "hash001",
                "H:/seed/SH#600000.txt",
                "seed-run-001",
                "data-bootstrap-v1",
                "2026-04-28 00:00:00",
                "600000.SH",
                "stock",
                "day",
                "2024-01-03",
                "2024-01-03",
                "analysis_price_line",
                "backward",
                10.2,
                10.8,
                10.1,
                10.7,
                1100.0,
                11770.0,
                "tdx_offline_txt",
                "seed-run-001",
                "hash001",
                "H:/seed/SH#600000.txt",
                "seed-run-001",
                "data-bootstrap-v1",
                "2026-04-28 00:00:00",
            ],
        )


def _request(tmp_path: Path, run_id: str, mode: str = "bounded") -> MalfDayRequest:
    return MalfDayRequest(
        source_db=tmp_path / "asteria-data" / "market_base_day.duckdb",
        core_db=tmp_path / "asteria-data" / "malf_core_day.duckdb",
        lifespan_db=tmp_path / "asteria-data" / "malf_lifespan_day.duckdb",
        service_db=tmp_path / "asteria-data" / "malf_service_day.duckdb",
        report_root=tmp_path / "asteria-report",
        validated_root=tmp_path / "asteria-validated",
        temp_root=tmp_path / "asteria-temp",
        run_id=run_id,
        mode=mode,
        schema_version="malf-day-bounded-proof-v1",
        core_rule_version="core-rule-v1",
        lifespan_rule_version="lifespan-rule-v1",
        sample_version="sample-v1",
        service_version="service-v1",
        start_dt="2024-01-01",
        end_dt="2024-12-31",
        symbol_limit=10,
    )


def test_malf_day_core_build_bootstraps_db_and_checkpoint(tmp_path: Path) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")

    summary = run_malf_day_core_build(_request(tmp_path, "malf-core-run-001"))

    assert summary.status == "completed"
    assert summary.input_row_count == 2
    assert summary.resume_reused is False
    assert (
        tmp_path / "asteria-temp" / "malf" / "malf-core-run-001" / "core-checkpoint.json"
    ).exists()

    with duckdb.connect(
        str(tmp_path / "asteria-data" / "malf_core_day.duckdb"), read_only=True
    ) as con:
        run_row = con.execute(
            """
            select run_id, runner_name, mode, input_row_count, schema_version, core_rule_version
            from malf_core_run
            """
        ).fetchone()
        assert run_row == (
            "malf-core-run-001",
            "malf_day_core_build",
            "bounded",
            2,
            "malf-day-bounded-proof-v1",
            "core-rule-v1",
        )
        assert con.execute("select count(*) from malf_wave_ledger").fetchone()[0] == 0


def test_malf_day_core_resume_reuses_completed_checkpoint(tmp_path: Path) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")

    first = run_malf_day_core_build(_request(tmp_path, "malf-core-run-002"))
    second = run_malf_day_core_build(_request(tmp_path, "malf-core-run-002", mode="resume"))

    assert first.status == "completed"
    assert second.status == "completed"
    assert second.resume_reused is True


def test_malf_day_lifespan_service_and_audit_write_ledgers_and_report(tmp_path: Path) -> None:
    _seed_market_base_day(tmp_path / "asteria-data" / "market_base_day.duckdb")
    request = _request(tmp_path, "malf-full-run-001")

    run_malf_day_core_build(request)
    lifespan_summary = run_malf_day_lifespan_build(request)
    service_summary = run_malf_day_service_build(request)
    audit_summary = run_malf_day_audit(request)

    assert lifespan_summary.status == "completed"
    assert service_summary.status == "completed"
    assert audit_summary.status == "completed"
    assert audit_summary.report_path is not None

    with duckdb.connect(
        str(tmp_path / "asteria-data" / "malf_lifespan_day.duckdb"), read_only=True
    ) as con:
        run_row = con.execute(
            """
            select
                run_id,
                runner_name,
                mode,
                input_wave_count,
                schema_version,
                lifespan_rule_version,
                sample_version
            from malf_lifespan_run
            """
        ).fetchone()
        assert run_row == (
            "malf-full-run-001",
            "malf_day_lifespan_build",
            "bounded",
            0,
            "malf-day-bounded-proof-v1",
            "lifespan-rule-v1",
            "sample-v1",
        )

    with duckdb.connect(
        str(tmp_path / "asteria-data" / "malf_service_day.duckdb"), read_only=True
    ) as con:
        service_row = con.execute(
            """
            select run_id, runner_name, published_row_count, schema_version, service_version
            from malf_service_run
            """
        ).fetchone()
        audit_row = con.execute(
            """
            select check_name, severity, status, failed_count
            from malf_interface_audit
            """
        ).fetchone()
        assert service_row == (
            "malf-full-run-001",
            "malf_day_service_build",
            0,
            "malf-day-bounded-proof-v1",
            "service-v1",
        )
        assert audit_row == (
            "service_scaffold_no_wave_position",
            "soft",
            "observe",
            0,
        )

    report_payload = json.loads(Path(audit_summary.report_path).read_text(encoding="utf-8"))
    assert report_payload["run_id"] == "malf-full-run-001"
    assert report_payload["service_audit_rows"] == 1
