from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from tests.unit.data.test_daily_incremental_hardening import (
    _seed_week_month_ledgers,
    _write_tdx_file,
)

from asteria.pipeline.full_daily_incremental_chain import (
    PipelineFullDailyIncrementalChainRequest,
    run_pipeline_full_daily_incremental_chain,
)

RUN_ID = "pipeline-full-daily-incremental-chain-build-card"
MODULE_ORDER = [
    "data",
    "malf",
    "alpha",
    "signal",
    "position",
    "portfolio_plan",
    "trade",
    "system_readout",
]


def _rows() -> tuple[str, ...]:
    prices = [
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
    base_dt = date(2023, 12, 25)
    rows: list[str] = []
    for offset, (high, low) in enumerate(prices):
        bar_dt = base_dt + timedelta(days=offset)
        close = round((high + low) / 2, 2)
        rows.append(f"{bar_dt.isoformat()}\t{close}\t{high}\t{low}\t{close}\t1000\t10000")
    return tuple(rows)


def _seed_source(tmp_path: Path) -> None:
    _write_tdx_file(
        tmp_path / "tdx" / "stock-day" / "Backward-Adjusted" / "SH#600000.txt",
        "SH#600000",
        _rows(),
    )
    _seed_week_month_ledgers(
        tmp_path / "asteria-temp" / "pipeline-full-daily-incremental-chain" / RUN_ID / "data"
    )


def _request(
    tmp_path: Path,
    *,
    mode: str = "daily_incremental",
) -> PipelineFullDailyIncrementalChainRequest:
    return PipelineFullDailyIncrementalChainRequest(
        source_root=tmp_path / "tdx",
        temp_root=tmp_path / "asteria-temp",
        report_root=tmp_path / "asteria-report",
        run_id=RUN_ID,
        mode=mode,
        start_dt="2023-12-25",
        end_dt="2024-01-08",
        symbol_limit=1,
    )


def test_full_daily_incremental_chain_writes_unified_report_lineage_and_checkpoint(
    tmp_path: Path,
) -> None:
    _seed_source(tmp_path)

    summary = run_pipeline_full_daily_incremental_chain(_request(tmp_path))

    assert summary.status == "passed"
    assert summary.module_order == tuple(MODULE_ORDER)
    assert summary.module_statuses == {module: "passed" for module in MODULE_ORDER}
    assert summary.boundaries["formal_data_mutation"] is False
    assert summary.boundaries["release_closeout_opened"] is False
    assert summary.boundaries["full_rebuild_opened"] is False
    assert summary.boundaries["v1_complete_claim"] is False
    assert Path(summary.summary_path).exists()
    assert Path(summary.closeout_path).exists()
    assert Path(summary.chain_lineage_path).exists()
    assert Path(summary.checkpoint_manifest_path).exists()
    assert (tmp_path / "asteria-data").exists() is False

    payload = json.loads(Path(summary.summary_path).read_text(encoding="utf-8"))
    lineage = json.loads(Path(summary.chain_lineage_path).read_text(encoding="utf-8"))
    checkpoint_manifest = json.loads(
        Path(summary.checkpoint_manifest_path).read_text(encoding="utf-8")
    )

    assert payload["run_id"] == RUN_ID
    assert payload["module_order"] == MODULE_ORDER
    assert lineage["edges"][0]["source_module"] == "data"
    assert lineage["edges"][-1]["target_module"] == "system_readout"
    assert checkpoint_manifest["module_order"] == MODULE_ORDER
    assert "pipeline full daily incremental chain proof passed" in Path(
        summary.closeout_path
    ).read_text(encoding="utf-8")
    assert "v1 complete" not in Path(summary.closeout_path).read_text(encoding="utf-8")


def test_full_daily_incremental_chain_resume_reuses_module_checkpoints(tmp_path: Path) -> None:
    _seed_source(tmp_path)
    run_pipeline_full_daily_incremental_chain(_request(tmp_path))

    resumed = run_pipeline_full_daily_incremental_chain(_request(tmp_path, mode="resume"))

    assert resumed.status == "passed"
    assert resumed.resume_reused is True
    assert all(resumed.module_resume_reused.values())


def test_full_daily_incremental_chain_audit_only_writes_report_without_target_dbs(
    tmp_path: Path,
) -> None:
    summary = run_pipeline_full_daily_incremental_chain(_request(tmp_path, mode="audit-only"))

    assert summary.status == "passed"
    assert summary.module_statuses == {module: "passed" for module in MODULE_ORDER}
    assert summary.boundaries["formal_data_mutation"] is False
    assert Path(summary.summary_path).exists()
    assert Path(summary.closeout_path).exists()
    assert (tmp_path / "asteria-temp" / "pipeline-full-daily-incremental-chain").exists()
    assert (
        tmp_path / "asteria-temp" / "pipeline-full-daily-incremental-chain" / RUN_ID / "data"
    ).exists() is False
