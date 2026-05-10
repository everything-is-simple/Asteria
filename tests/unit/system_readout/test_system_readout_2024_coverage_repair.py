from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import duckdb
import pytest
from tests.unit.system_readout.coverage_repair_support import (
    SYSTEM_RUN_ID,
    build_repair_request,
    count_rows,
    seed_repair_scenario,
)
from tests.unit.system_readout.support_upstream import TRADE_RUN_ID


def test_repair_rewrites_system_focus_window_and_moves_break_to_pipeline(tmp_path: Path) -> None:
    from asteria.pipeline.year_replay_coverage_gap_contracts import PIPELINE_REPAIR_CARD
    from asteria.system_readout.coverage_repair import (
        run_system_readout_2024_coverage_repair,
    )

    repo_root, data_root = seed_repair_scenario(tmp_path)
    request = build_repair_request(tmp_path, repo_root=repo_root)
    registry_before = (repo_root / "governance" / "module_gate_registry.toml").read_text(
        encoding="utf-8"
    )
    trade_count_before = count_rows(
        data_root / "trade.duckdb",
        "order_intent_ledger",
        "run_id",
        TRADE_RUN_ID,
    )

    summary = run_system_readout_2024_coverage_repair(request)

    assert summary.status == "completed"
    assert summary.released_system_run_id == SYSTEM_RUN_ID
    assert summary.followup_next_card == PIPELINE_REPAIR_CARD
    assert summary.followup_attribution == "calendar_semantic_gap_only"
    assert summary.hard_fail_count == 0
    assert Path(summary.validated_zip).exists()
    with duckdb.connect(str(data_root / "system.duckdb"), read_only=True) as con:
        readout_dates = con.execute(
            """
            select distinct readout_dt
            from system_chain_readout
            where system_readout_run_id = ?
            order by 1
            """,
            [SYSTEM_RUN_ID],
        ).fetchall()
        summary_dates = con.execute(
            """
            select distinct summary_dt
            from system_summary_snapshot
            where system_readout_run_id = ?
            order by 1
            """,
            [SYSTEM_RUN_ID],
        ).fetchall()
        run_row = con.execute(
            """
            select source_manifest_count, module_status_count, readout_count,
                   summary_count, audit_snapshot_count, hard_fail_count, status
            from system_readout_run
            where run_id = ?
            """,
            [SYSTEM_RUN_ID],
        ).fetchone()
        manifest_count = con.execute(
            """
            select count(*)
            from system_source_manifest
            where system_readout_run_id = ?
            """,
            [SYSTEM_RUN_ID],
        ).fetchone()[0]

    assert readout_dates == [
        (date(2024, 1, 2),),
        (date(2024, 1, 3),),
        (date(2024, 1, 4),),
        (date(2024, 1, 5),),
        (date(2024, 1, 9),),
        (date(2024, 1, 10),),
    ]
    assert summary_dates == readout_dates
    assert run_row == (10, 6, 6, 6, 6, 0, "completed")
    assert manifest_count == 10
    assert (
        count_rows(data_root / "trade.duckdb", "order_intent_ledger", "run_id", TRADE_RUN_ID)
        == trade_count_before
    )
    assert (repo_root / "governance" / "module_gate_registry.toml").read_text(
        encoding="utf-8"
    ) == registry_before


def test_repair_rejects_missing_signal_manifest_entry(tmp_path: Path) -> None:
    from asteria.system_readout.coverage_repair import (
        run_system_readout_2024_coverage_repair,
    )

    repo_root, data_root = seed_repair_scenario(tmp_path)
    with duckdb.connect(str(data_root / "system.duckdb")) as con:
        con.execute(
            """
            delete from system_source_manifest
            where system_readout_run_id = ? and module_name = 'signal'
            """,
            [SYSTEM_RUN_ID],
        )

    with pytest.raises(ValueError, match="expected exactly one signal manifest row"):
        run_system_readout_2024_coverage_repair(build_repair_request(tmp_path, repo_root=repo_root))


def test_repair_rejects_duplicate_trade_manifest_rows(tmp_path: Path) -> None:
    from asteria.system_readout.coverage_repair import (
        run_system_readout_2024_coverage_repair,
    )

    repo_root, data_root = seed_repair_scenario(tmp_path)
    with duckdb.connect(str(data_root / "system.duckdb")) as con:
        con.execute(
            """
            insert into system_source_manifest values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                f"{SYSTEM_RUN_ID}|trade|duplicate",
                SYSTEM_RUN_ID,
                "trade",
                str(data_root / "trade.duckdb"),
                TRADE_RUN_ID,
                TRADE_RUN_ID,
                "trade-bounded-proof-v1",
                "trade-unit|audit",
                "pass",
                datetime(2026, 5, 8, 12, 0, 0),
            ],
        )

    with pytest.raises(ValueError, match="expected exactly one trade manifest row"):
        run_system_readout_2024_coverage_repair(build_repair_request(tmp_path, repo_root=repo_root))


def test_request_rejects_non_2024_or_changed_focus_window(tmp_path: Path) -> None:
    from asteria.system_readout.coverage_repair_contracts import (
        SystemReadout2024CoverageRepairRequest,
    )

    with pytest.raises(ValueError, match="locked to target_year=2024"):
        SystemReadout2024CoverageRepairRequest(
            repo_root=tmp_path,
            source_system_db=tmp_path / "data" / "system.duckdb",
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id="system-readout-2024-coverage-repair-card-20260509-01",
            target_year=2025,
        )
    with pytest.raises(ValueError, match="focus window is fixed"):
        SystemReadout2024CoverageRepairRequest(
            repo_root=tmp_path,
            source_system_db=tmp_path / "data" / "system.duckdb",
            report_root=tmp_path / "report",
            validated_root=tmp_path / "validated",
            temp_root=tmp_path / "temp",
            run_id="system-readout-2024-coverage-repair-card-20260509-01",
            focus_start_dt="2024-01-03",
        )
