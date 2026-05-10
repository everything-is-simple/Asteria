from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb
import pytest
from tests.unit.portfolio_plan.portfolio_plan_2024_coverage_repair_support import (
    request,
    seed_repo_root,
)
from tests.unit.position.position_2024_coverage_repair_source_fixtures import (
    seed_alpha_family_dbs,
    seed_data_foundation,
    seed_malf_db,
    seed_signal_db,
)
from tests.unit.position.position_2024_coverage_repair_support import (
    PORTFOLIO_RUN_ID,
    POSITION_RUN_ID,
    SIGNAL_RUN_ID,
    created_at,
    trading_dates,
)
from tests.unit.position.position_2024_coverage_repair_system_fixtures import (
    seed_system_db,
)
from tests.unit.position.position_2024_coverage_repair_target_fixtures import seed_trade_db

from asteria.pipeline.year_replay_coverage_gap_contracts import TRADE_REPAIR_CARD
from asteria.portfolio_plan.contracts import (
    PORTFOLIO_PLAN_RULE_VERSION,
    PORTFOLIO_PLAN_SCHEMA_VERSION,
)
from asteria.portfolio_plan.coverage_repair import run_portfolio_plan_2024_coverage_repair
from asteria.portfolio_plan.schema import bootstrap_portfolio_plan_database
from asteria.position.contracts import POSITION_RULE_VERSION, POSITION_SCHEMA_VERSION
from asteria.position.schema import bootstrap_position_database


def test_repair_rewrites_only_focus_window_for_released_portfolio_run(tmp_path: Path) -> None:
    repo_root = seed_repo_root(tmp_path)
    data_root = tmp_path / "data"
    dates = trading_dates()
    seed_data_foundation(data_root, dates)
    seed_malf_db(data_root / "malf_service_day.duckdb", dates)
    seed_alpha_family_dbs(data_root, dates)
    seed_signal_db(data_root / "signal.duckdb", dates)
    seed_position_release_db(data_root / "position.duckdb")
    seed_portfolio_plan_release_db(data_root / "portfolio_plan.duckdb")
    late_dates = trading_dates(start="2024-01-09")
    seed_trade_db(data_root / "trade.duckdb", late_dates)
    seed_system_db(data_root / "system.duckdb", data_root)

    registry_before = (repo_root / "governance" / "module_gate_registry.toml").read_text(
        encoding="utf-8"
    )
    summary = run_portfolio_plan_2024_coverage_repair(request(tmp_path, repo_root=repo_root))

    assert summary.status == "completed"
    assert summary.released_portfolio_plan_run_id == PORTFOLIO_RUN_ID
    assert summary.released_position_run_id == POSITION_RUN_ID
    assert summary.released_trade_run_id == "trade-bounded-proof-build-card-20260507-01"
    with duckdb.connect(str(data_root / "portfolio_plan.duckdb"), read_only=True) as con:
        admission_dates = con.execute(
            """
            select distinct plan_dt
            from portfolio_admission_ledger
            where run_id = ?
            order by 1
            """,
            [PORTFOLIO_RUN_ID],
        ).fetchall()
        exposure_dates = con.execute(
            """
            select distinct exposure_valid_from
            from portfolio_target_exposure
            where run_id = ?
            order by 1
            """,
            [PORTFOLIO_RUN_ID],
        ).fetchall()
        run_row = con.execute(
            """
            select input_position_count, admission_count, target_exposure_count, trim_count,
                   hard_fail_count, status
            from portfolio_plan_run
            where run_id = ?
            """,
            [PORTFOLIO_RUN_ID],
        ).fetchone()
        audit_hard_fails = con.execute(
            """
            select coalesce(sum(failed_count), 0)
            from portfolio_plan_audit
            where run_id = ? and severity = 'hard' and status = 'fail'
            """,
            [PORTFOLIO_RUN_ID],
        ).fetchone()[0]

    assert admission_dates == [
        (date(2024, 1, 2),),
        (date(2024, 1, 3),),
        (date(2024, 1, 4),),
        (date(2024, 1, 5),),
        (date(2024, 1, 9),),
        (date(2024, 1, 10),),
    ]
    assert exposure_dates == admission_dates
    assert run_row == (8, 8, 6, 1, 0, "completed")
    assert audit_hard_fails == 0
    assert summary.followup_next_card == TRADE_REPAIR_CARD
    assert summary.followup_attribution == "downstream_surface_gap:trade"
    assert (repo_root / "governance" / "module_gate_registry.toml").read_text(
        encoding="utf-8"
    ) == registry_before


def test_repair_followup_truthfully_moves_next_break_to_trade(tmp_path: Path) -> None:
    repo_root = seed_repo_root(tmp_path)
    data_root = tmp_path / "data"
    dates = trading_dates()
    seed_data_foundation(data_root, dates)
    seed_malf_db(data_root / "malf_service_day.duckdb", dates)
    seed_alpha_family_dbs(data_root, dates)
    seed_signal_db(data_root / "signal.duckdb", dates)
    seed_position_release_db(data_root / "position.duckdb")
    seed_portfolio_plan_release_db(data_root / "portfolio_plan.duckdb")
    late_dates = trading_dates(start="2024-01-09")
    seed_trade_db(data_root / "trade.duckdb", late_dates)
    seed_system_db(data_root / "system.duckdb", data_root)

    summary = run_portfolio_plan_2024_coverage_repair(request(tmp_path, repo_root=repo_root))

    assert summary.status == "completed"
    assert summary.followup_next_card == TRADE_REPAIR_CARD
    assert summary.followup_attribution == "downstream_surface_gap:trade"


def test_repair_rejects_missing_portfolio_manifest_entry(tmp_path: Path) -> None:
    repo_root = seed_repo_root(tmp_path)
    data_root = tmp_path / "data"
    dates = trading_dates()
    seed_data_foundation(data_root, dates)
    seed_malf_db(data_root / "malf_service_day.duckdb", dates)
    seed_alpha_family_dbs(data_root, dates)
    seed_signal_db(data_root / "signal.duckdb", dates)
    seed_position_release_db(data_root / "position.duckdb")
    seed_portfolio_plan_release_db(data_root / "portfolio_plan.duckdb")
    late_dates = trading_dates(start="2024-01-09")
    seed_trade_db(data_root / "trade.duckdb", late_dates)
    seed_system_db(data_root / "system.duckdb", data_root)
    with duckdb.connect(str(data_root / "system.duckdb")) as con:
        con.execute("delete from system_source_manifest where module_name = 'portfolio_plan'")

    with pytest.raises(ValueError, match="expected exactly one portfolio_plan manifest row"):
        run_portfolio_plan_2024_coverage_repair(request(tmp_path, repo_root=repo_root))


def test_repair_rejects_duplicate_portfolio_manifest_rows(tmp_path: Path) -> None:
    repo_root = seed_repo_root(tmp_path)
    data_root = tmp_path / "data"
    dates = trading_dates()
    seed_data_foundation(data_root, dates)
    seed_malf_db(data_root / "malf_service_day.duckdb", dates)
    seed_alpha_family_dbs(data_root, dates)
    seed_signal_db(data_root / "signal.duckdb", dates)
    seed_position_release_db(data_root / "position.duckdb")
    seed_portfolio_plan_release_db(data_root / "portfolio_plan.duckdb")
    late_dates = trading_dates(start="2024-01-09")
    seed_trade_db(data_root / "trade.duckdb", late_dates)
    seed_system_db(data_root / "system.duckdb", data_root)
    with duckdb.connect(str(data_root / "system.duckdb")) as con:
        con.execute(
            """
            insert into system_source_manifest
            values (?, 'portfolio_plan', ?, ?, ?)
            """,
            [
                "system-readout-bounded-proof-build-card-20260508-01",
                str(data_root / "portfolio_plan.duckdb"),
                PORTFOLIO_RUN_ID,
                PORTFOLIO_RUN_ID,
            ],
        )

    with pytest.raises(ValueError, match="expected exactly one portfolio_plan manifest row"):
        run_portfolio_plan_2024_coverage_repair(request(tmp_path, repo_root=repo_root))


def seed_position_release_db(path: Path) -> None:
    bootstrap_position_database(path)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            insert into position_run
            values (?, 'position_build', 'bounded', 'day', 'completed', 'signal.duckdb',
                    8, 8, 8, 8, 0, ?, ?, ?, ?, ?)
            """,
            [
                POSITION_RUN_ID,
                POSITION_SCHEMA_VERSION,
                POSITION_RULE_VERSION,
                SIGNAL_RUN_ID,
                SIGNAL_RUN_ID,
                created_at(),
            ],
        )
        con.execute(
            "insert into position_schema_version values (?, ?)",
            [POSITION_SCHEMA_VERSION, created_at()],
        )
        con.execute(
            "insert into position_rule_version values (?, 'signal_to_position_plan', ?)",
            [POSITION_RULE_VERSION, created_at()],
        )
        con.execute(
            """
            insert into position_audit
            values ('position-audit', ?, 'hard_audit_zero', 'hard', 'pass', 0, '{}', ?)
            """,
            [POSITION_RUN_ID, created_at()],
        )
        candidate_rows = [
            ("pos-ddd-0102", "sig-ddd-0102", "600100.SH", date(2024, 1, 2), "planned"),
            ("pos-aaa-0102", "sig-aaa-0102", "600200.SH", date(2024, 1, 2), "planned"),
            ("pos-bbb-0103", "sig-bbb-0103", "600300.SH", date(2024, 1, 3), "planned"),
            ("pos-rrr-0103", "sig-rrr-0103", "600400.SH", date(2024, 1, 3), "rejected"),
            ("pos-aaa-0104", "sig-aaa-0104", "600200.SH", date(2024, 1, 4), "planned"),
            ("pos-ccc-0105", "sig-ccc-0105", "600500.SH", date(2024, 1, 5), "planned"),
            ("pos-eee-0109", "sig-eee-0109", "600600.SH", date(2024, 1, 9), "planned"),
            ("pos-fff-0110", "sig-fff-0110", "600700.SH", date(2024, 1, 10), "planned"),
        ]
        con.executemany(
            """
            insert into position_candidate_ledger
            values (?, ?, ?, 'day', ?, 'directional_position_candidate',
                    ?, 'long_candidate', 'portfolio_repair_fixture',
                    ?, ?, ?, ?, ?)
            """,
            [
                (
                    candidate_id,
                    signal_id,
                    symbol,
                    candidate_dt,
                    state,
                    SIGNAL_RUN_ID,
                    POSITION_RUN_ID,
                    POSITION_SCHEMA_VERSION,
                    POSITION_RULE_VERSION,
                    created_at(),
                )
                for candidate_id, signal_id, symbol, candidate_dt, state in candidate_rows
            ],
        )
        planned_ids = [row[0] for row in candidate_rows if row[4] == "planned"]
        con.executemany(
            """
            insert into position_entry_plan
            values (?, ?, 'signal_follow_entry', 'next_session_open_plan',
                    ?, ?, null, 'planned', ?, ?, ?, ?, ?)
            """,
            [
                (
                    f"entry-{candidate_id}",
                    candidate_id,
                    _candidate_date(candidate_id),
                    _candidate_date(candidate_id),
                    POSITION_RUN_ID,
                    POSITION_SCHEMA_VERSION,
                    POSITION_RULE_VERSION,
                    SIGNAL_RUN_ID,
                    created_at(),
                )
                for candidate_id in planned_ids
            ],
        )
        con.executemany(
            """
            insert into position_exit_plan
            values (?, ?, 'signal_invalidation_exit', 'signal_invalidated_or_expired',
                    ?, ?, null, 'planned', ?, ?, ?, ?, ?)
            """,
            [
                (
                    f"exit-{candidate_id}",
                    candidate_id,
                    _candidate_date(candidate_id),
                    _candidate_date(candidate_id),
                    POSITION_RUN_ID,
                    POSITION_SCHEMA_VERSION,
                    POSITION_RULE_VERSION,
                    SIGNAL_RUN_ID,
                    created_at(),
                )
                for candidate_id in planned_ids
            ],
        )


def seed_portfolio_plan_release_db(path: Path) -> None:
    bootstrap_portfolio_plan_database(path)
    with duckdb.connect(str(path)) as con:
        con.execute(
            "insert into portfolio_plan_schema_version values (?, ?)",
            [PORTFOLIO_PLAN_SCHEMA_VERSION, created_at()],
        )
        con.execute(
            """
            insert into portfolio_plan_rule_version
            values (?, 'position_capacity_admission', 3, ?)
            """,
            [PORTFOLIO_PLAN_RULE_VERSION, created_at()],
        )
        con.executemany(
            """
            insert into portfolio_position_snapshot
            values (?, ?, ?, ?, 'day', ?, 'planned', 'long_candidate', ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    f"{PORTFOLIO_RUN_ID}|pos-eee-0109",
                    PORTFOLIO_RUN_ID,
                    "pos-eee-0109",
                    "600600.SH",
                    date(2024, 1, 9),
                    "entry-pos-eee-0109",
                    "exit-pos-eee-0109",
                    POSITION_RULE_VERSION,
                    POSITION_RUN_ID,
                    POSITION_RUN_ID,
                    PORTFOLIO_PLAN_SCHEMA_VERSION,
                    PORTFOLIO_PLAN_RULE_VERSION,
                    created_at(),
                ),
                (
                    f"{PORTFOLIO_RUN_ID}|pos-fff-0110",
                    PORTFOLIO_RUN_ID,
                    "pos-fff-0110",
                    "600700.SH",
                    date(2024, 1, 10),
                    "entry-pos-fff-0110",
                    "exit-pos-fff-0110",
                    POSITION_RULE_VERSION,
                    POSITION_RUN_ID,
                    POSITION_RUN_ID,
                    PORTFOLIO_PLAN_SCHEMA_VERSION,
                    PORTFOLIO_PLAN_RULE_VERSION,
                    created_at(),
                ),
            ],
        )
        con.execute(
            """
            insert into portfolio_constraint_ledger
            values (?, 'global', 'max_active_symbols', 'capacity', 3.0, 'active',
                    ?, ?, ?, ?, ?)
            """,
            [
                f"global|max_active_symbols|{PORTFOLIO_PLAN_RULE_VERSION}",
                PORTFOLIO_RUN_ID,
                PORTFOLIO_PLAN_SCHEMA_VERSION,
                PORTFOLIO_PLAN_RULE_VERSION,
                POSITION_RUN_ID,
                created_at(),
            ],
        )
        con.executemany(
            """
            insert into portfolio_admission_ledger
            values (?, ?, ?, 'day', ?, 'admitted', 'within_capacity_constraint',
                    ?, ?, ?, ?, ?)
            """,
            [
                (
                    f"pos-eee-0109|{PORTFOLIO_PLAN_RULE_VERSION}",
                    "pos-eee-0109",
                    "600600.SH",
                    date(2024, 1, 9),
                    POSITION_RUN_ID,
                    PORTFOLIO_RUN_ID,
                    PORTFOLIO_PLAN_SCHEMA_VERSION,
                    PORTFOLIO_PLAN_RULE_VERSION,
                    created_at(),
                ),
                (
                    f"pos-fff-0110|{PORTFOLIO_PLAN_RULE_VERSION}",
                    "pos-fff-0110",
                    "600700.SH",
                    date(2024, 1, 10),
                    POSITION_RUN_ID,
                    PORTFOLIO_RUN_ID,
                    PORTFOLIO_PLAN_SCHEMA_VERSION,
                    PORTFOLIO_PLAN_RULE_VERSION,
                    created_at(),
                ),
            ],
        )
        con.executemany(
            """
            insert into portfolio_target_exposure
            values (?, ?, 'target_weight', 0.5, null, null, ?, null,
                    ?, ?, ?, ?, ?)
            """,
            [
                (
                    f"pos-eee-0109|{PORTFOLIO_PLAN_RULE_VERSION}|target_weight",
                    f"pos-eee-0109|{PORTFOLIO_PLAN_RULE_VERSION}",
                    date(2024, 1, 9),
                    PORTFOLIO_RUN_ID,
                    PORTFOLIO_PLAN_SCHEMA_VERSION,
                    PORTFOLIO_PLAN_RULE_VERSION,
                    POSITION_RUN_ID,
                    created_at(),
                ),
                (
                    f"pos-fff-0110|{PORTFOLIO_PLAN_RULE_VERSION}|target_weight",
                    f"pos-fff-0110|{PORTFOLIO_PLAN_RULE_VERSION}",
                    date(2024, 1, 10),
                    PORTFOLIO_RUN_ID,
                    PORTFOLIO_PLAN_SCHEMA_VERSION,
                    PORTFOLIO_PLAN_RULE_VERSION,
                    POSITION_RUN_ID,
                    created_at(),
                ),
            ],
        )
        con.execute(
            """
            insert into portfolio_plan_run
            values (?, 'portfolio_plan_build', 'bounded', 'day', 'completed', 'position.duckdb',
                    2, 2, 2, 0, 0, ?, ?, ?, ?, ?)
            """,
            [
                PORTFOLIO_RUN_ID,
                PORTFOLIO_PLAN_SCHEMA_VERSION,
                PORTFOLIO_PLAN_RULE_VERSION,
                POSITION_RUN_ID,
                POSITION_RUN_ID,
                created_at(),
            ],
        )
        con.execute(
            """
            insert into portfolio_plan_audit
            values ('portfolio-audit', ?, 'hard_audit_zero', 'hard', 'pass', 0, '{}', ?)
            """,
            [PORTFOLIO_RUN_ID, created_at()],
        )


def _candidate_date(candidate_id: str) -> date:
    suffix = candidate_id.rsplit("-", maxsplit=1)[1]
    return date(2024, 1, int(suffix[-2:]))
