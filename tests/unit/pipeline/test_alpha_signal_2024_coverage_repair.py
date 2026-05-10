from __future__ import annotations

from dataclasses import replace
from datetime import date
from pathlib import Path

import duckdb
from tests.unit.alpha.test_alpha_bounded_proof_runner import _seed_malf_service
from tests.unit.pipeline.alpha_signal_2024_coverage_repair_support import (
    ALPHA_RELEASED_RUN_ID,
    BASELINE_MALF_RUN_ID,
    MALF_SAMPLE_VERSION,
    MALF_SERVICE_VERSION,
    REPAIRED_MALF_RUN_ID,
    SIGNAL_RELEASED_RUN_ID,
    ensure_malf_run_tables,
    repair_request,
    seed_live_released_chain,
)
from tests.unit.pipeline.support import (
    build_governance_repo,
    build_year_replay_rerun_authorized_repo,
)

from asteria.pipeline.alpha_signal_2024_coverage_repair import (
    build_merged_malf_service_day,
    run_alpha_signal_2024_coverage_repair,
)


def test_build_merged_malf_service_day_prefers_repaired_rows_and_keeps_baseline_elsewhere(
    tmp_path: Path,
) -> None:
    data_root = tmp_path / "data"
    source_db = data_root / "malf_service_day.duckdb"
    _seed_malf_service(
        source_db,
        service_version=MALF_SERVICE_VERSION,
        sample_version=MALF_SAMPLE_VERSION,
    )
    ensure_malf_run_tables(source_db, BASELINE_MALF_RUN_ID, MALF_SERVICE_VERSION)
    with duckdb.connect(str(source_db)) as con:
        con.execute(
            """
            update malf_wave_position
            set run_id = ?, bar_dt = date '2024-01-08'
            """,
            [BASELINE_MALF_RUN_ID],
        )
        con.execute(
            """
            update malf_wave_position_latest
            set run_id = ?, bar_dt = date '2024-01-08'
            """,
            [BASELINE_MALF_RUN_ID],
        )
        con.executemany(
            f"insert into malf_wave_position values ({', '.join(['?'] * 25)})",
            [
                (
                    "000020.SZ",
                    "day",
                    date(2024, 1, 2),
                    "up_alive",
                    "repair-wave-1",
                    None,
                    "alive",
                    "up",
                    1,
                    0,
                    0,
                    0.95,
                    0.15,
                    "developing",
                    "developing",
                    11.0,
                    "repair-scope",
                    MALF_SAMPLE_VERSION,
                    "lifespan-rule-v1",
                    MALF_SERVICE_VERSION,
                    REPAIRED_MALF_RUN_ID,
                    "malf-schema-v1",
                    "repair-core-run",
                    "repair-lifespan-run",
                    "2026-05-09 00:00:00",
                ),
                (
                    "000020.SZ",
                    "day",
                    date(2024, 1, 8),
                    "up_alive",
                    "repair-wave-8",
                    None,
                    "alive",
                    "up",
                    2,
                    0,
                    0,
                    0.88,
                    0.10,
                    "extended",
                    "extended_active",
                    12.0,
                    "repair-scope",
                    MALF_SAMPLE_VERSION,
                    "lifespan-rule-v1",
                    MALF_SERVICE_VERSION,
                    REPAIRED_MALF_RUN_ID,
                    "malf-schema-v1",
                    "repair-core-run",
                    "repair-lifespan-run",
                    "2026-05-09 00:00:00",
                ),
            ],
        )
        con.executemany(
            f"insert into malf_wave_position_latest values ({', '.join(['?'] * 25)})",
            [
                (
                    "000020.SZ",
                    "day",
                    date(2024, 1, 8),
                    "up_alive",
                    "repair-wave-8",
                    None,
                    "alive",
                    "up",
                    2,
                    0,
                    0,
                    0.88,
                    0.10,
                    "extended",
                    "extended_active",
                    12.0,
                    "repair-scope",
                    MALF_SAMPLE_VERSION,
                    "lifespan-rule-v1",
                    MALF_SERVICE_VERSION,
                    REPAIRED_MALF_RUN_ID,
                    "malf-schema-v1",
                    "repair-core-run",
                    "repair-lifespan-run",
                    "2026-05-09 00:00:00",
                ),
            ],
        )
        con.execute(
            """
            insert into malf_service_run
            select ?, runner_name, mode, timeframe, status, source_core_run_id,
                   source_lifespan_run_id, published_row_count, schema_version,
                   service_version, created_at
            from malf_service_run
            where run_id = ?
            limit 1
            """,
            [REPAIRED_MALF_RUN_ID, BASELINE_MALF_RUN_ID],
        )
        con.execute(
            """
            insert into malf_interface_audit
            select replace(audit_id, ?, ?), ?, check_name, severity, status, failed_count,
                   sample_payload, created_at
            from malf_interface_audit
            where run_id = ?
            """,
            [
                BASELINE_MALF_RUN_ID,
                REPAIRED_MALF_RUN_ID,
                REPAIRED_MALF_RUN_ID,
                BASELINE_MALF_RUN_ID,
            ],
        )

    request = repair_request(tmp_path, followup=False)
    request = replace(
        request,
        baseline_malf_service_db=source_db,
        repaired_malf_service_db=source_db,
        target_data_root=data_root,
    )

    merged_db = build_merged_malf_service_day(request)

    with duckdb.connect(str(merged_db), read_only=True) as con:
        rows = con.execute(
            """
            select symbol, bar_dt, run_id
            from malf_wave_position
            where timeframe = 'day'
            order by symbol, bar_dt
            """
        ).fetchall()
        run_rows = con.execute(
            "select distinct run_id from malf_service_run order by run_id"
        ).fetchall()

    assert ("000020.SZ", date(2024, 1, 2), REPAIRED_MALF_RUN_ID) in rows
    assert ("000020.SZ", date(2024, 1, 8), REPAIRED_MALF_RUN_ID) in rows
    assert all(
        row[2] != BASELINE_MALF_RUN_ID for row in rows if row[:2] == ("000020.SZ", date(2024, 1, 8))
    )
    assert set(run_rows) == {(BASELINE_MALF_RUN_ID,), (REPAIRED_MALF_RUN_ID,)}


def test_repair_orchestration_rewrites_day_only_and_preserves_released_run_ids(
    tmp_path: Path,
) -> None:
    seed_live_released_chain(tmp_path)
    request = repair_request(tmp_path, followup=False)

    summary = run_alpha_signal_2024_coverage_repair(request)

    assert summary.status == "completed"
    assert summary.followup_next_card is None
    for family in ("bof", "tst", "pb", "cpb", "bpb"):
        with duckdb.connect(
            str(tmp_path / "data" / f"alpha_{family}.duckdb"),
            read_only=True,
        ) as con:
            day_rows = con.execute(
                """
                select distinct source_malf_run_id
                from alpha_signal_candidate
                where run_id = ? and timeframe = 'day'
                order by 1
                """,
                [ALPHA_RELEASED_RUN_ID],
            ).fetchall()
            week_rows = con.execute(
                """
                select count(*)
                from alpha_signal_candidate
                where run_id = ? and timeframe = 'week'
                """,
                [ALPHA_RELEASED_RUN_ID],
            ).fetchone()[0]
        assert (REPAIRED_MALF_RUN_ID,) in day_rows
        assert week_rows > 0

    with duckdb.connect(str(tmp_path / "data" / "signal.duckdb"), read_only=True) as con:
        day_release = con.execute(
            """
            select distinct run_id, source_alpha_release_version
            from formal_signal_ledger
            where timeframe = 'day'
            order by 1, 2
            """
        ).fetchall()
        day_alpha_run = con.execute(
            """
            select distinct source_alpha_run_id
            from signal_input_snapshot
            where signal_run_id = ? and timeframe = 'day'
            order by 1
            """,
            [SIGNAL_RELEASED_RUN_ID],
        ).fetchall()
        week_count = con.execute(
            """
            select count(*)
            from formal_signal_ledger
            where run_id = ? and timeframe = 'week'
            """,
            [SIGNAL_RELEASED_RUN_ID],
        ).fetchone()[0]

    assert day_release == [(SIGNAL_RELEASED_RUN_ID, ALPHA_RELEASED_RUN_ID)]
    assert day_alpha_run == [(ALPHA_RELEASED_RUN_ID,)]
    assert week_count > 0


def test_followup_uses_temp_repo_view_and_reports_truthful_next_card(tmp_path: Path) -> None:
    seed_live_released_chain(tmp_path)
    (tmp_path / "live").mkdir()
    (tmp_path / "rerun").mkdir()
    live_repo_root = build_governance_repo(tmp_path / "live")
    rerun_repo_root = build_year_replay_rerun_authorized_repo(tmp_path / "rerun")
    request = repair_request(tmp_path, followup=True, repo_root=rerun_repo_root)

    summary = run_alpha_signal_2024_coverage_repair(request)
    live_registry = (live_repo_root / "governance" / "module_gate_registry.toml").read_text(
        encoding="utf-8"
    )
    followup_registry = (
        request.followup_repo_root / "governance" / "module_gate_registry.toml"
    ).read_text(encoding="utf-8")

    assert summary.followup_rerun_status == "failed"
    assert summary.followup_next_card in {
        "coverage-gap-evidence-incomplete-closeout-card-20260509-01",
        "system-readout-2024-coverage-repair-card-20260509-01",
        "pipeline-year-replay-source-selection-repair-card-20260509-01",
    }
    assert 'current_allowed_next_card = "position_2024_coverage_repair_card"' in live_registry
    assert (
        'current_allowed_next_card = "pipeline_one_year_strategy_behavior_replay_rerun_build_card"'
        in followup_registry
    )
