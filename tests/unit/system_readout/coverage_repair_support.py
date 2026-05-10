from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb
from tests.unit.system_readout.coverage_repair_release_support import (
    seed_late_system_release_db,
)
from tests.unit.system_readout.coverage_repair_seed_support import (
    clear_seed_day,
    seed_data_foundation,
)
from tests.unit.system_readout.support import seed_chain
from tests.unit.system_readout.support_upstream import (
    ALPHA_FAMILIES,
    ALPHA_RUN_ID,
    MALF_RUN_ID,
    PORTFOLIO_RUN_ID,
    POSITION_RUN_ID,
    SIGNAL_RUN_ID,
    TRADE_RUN_ID,
)

SYSTEM_RUN_ID = "system-readout-bounded-proof-build-card-20260508-01"


def build_repair_request(tmp_path: Path, *, repo_root: Path):
    from asteria.system_readout.coverage_repair_contracts import (
        SystemReadout2024CoverageRepairRequest,
    )

    return SystemReadout2024CoverageRepairRequest(
        repo_root=repo_root,
        source_system_db=tmp_path / "data" / "system.duckdb",
        report_root=tmp_path / "report",
        validated_root=tmp_path / "validated",
        temp_root=tmp_path / "temp",
        run_id="system-readout-2024-coverage-repair-card-20260509-01",
    )


def seed_repair_scenario(tmp_path: Path) -> tuple[Path, Path]:
    seed_chain(tmp_path)
    data_root = tmp_path / "data"
    seed_data_foundation(data_root)
    clear_seed_day(data_root, target_dt=date(2024, 1, 4))
    _extend_malf(data_root / "malf_service_day.duckdb")
    for family in ALPHA_FAMILIES:
        _extend_alpha(data_root / f"alpha_{family}.duckdb", family.upper())
    _extend_signal(data_root / "signal.duckdb")
    _extend_position(data_root / "position.duckdb")
    _extend_portfolio_plan(data_root / "portfolio_plan.duckdb")
    _extend_trade(data_root / "trade.duckdb")
    seed_late_system_release_db(
        data_root / "system.duckdb",
        data_root,
        system_run_id=SYSTEM_RUN_ID,
    )
    repo_root = tmp_path / "repo"
    governance_root = repo_root / "governance"
    governance_root.mkdir(parents=True, exist_ok=True)
    (governance_root / "module_gate_registry.toml").write_text(
        'current_allowed_next_card = "system_readout_2024_coverage_repair_card"\n',
        encoding="utf-8",
    )
    return repo_root, data_root


def count_rows(db_path: Path, table_name: str, key_name: str, run_id: str) -> int:
    with duckdb.connect(str(db_path), read_only=True) as con:
        row = con.execute(
            f"select count(*) from {table_name} where {key_name} = ?",
            [run_id],
        ).fetchone()
    return 0 if row is None or row[0] is None else int(row[0])


def _extend_malf(path: Path) -> None:
    with duckdb.connect(str(path)) as con:
        con.executemany(
            """
            insert into malf_wave_position
            values (?, 'day', ?, ?, ?, null, ?, 'up', 'malf-wave-position-dense-v1', ?)
            """,
            [
                (
                    "600000.SH",
                    date(2024, 1, 4),
                    "trend_up",
                    "wave-600000-0104",
                    "impulse",
                    MALF_RUN_ID,
                ),
                (
                    "600000.SH",
                    date(2024, 1, 5),
                    "trend_up",
                    "wave-600000-0105",
                    "impulse",
                    MALF_RUN_ID,
                ),
                (
                    "600000.SH",
                    date(2024, 1, 9),
                    "trend_up",
                    "wave-600000-0109",
                    "impulse",
                    MALF_RUN_ID,
                ),
                (
                    "600000.SH",
                    date(2024, 1, 10),
                    "trend_up",
                    "wave-600000-0110",
                    "impulse",
                    MALF_RUN_ID,
                ),
            ],
        )


def _extend_alpha(path: Path, family: str) -> None:
    with duckdb.connect(str(path)) as con:
        rows = [
            ("600000", date(2024, 1, 4)),
            ("600000", date(2024, 1, 5)),
            ("600000", date(2024, 1, 9)),
            ("600000", date(2024, 1, 10)),
        ]
        con.executemany(
            """
            insert into alpha_event_ledger
            values (?, ?, ?, 'day', ?, 'directional_opportunity', 'active', 'wave-ref', ?)
            """,
            [
                (
                    f"{family}-event-{symbol}-{bar_dt:%Y%m%d}",
                    family,
                    f"{symbol}.SH",
                    bar_dt,
                    ALPHA_RUN_ID,
                )
                for symbol, bar_dt in rows
            ],
        )
        con.executemany(
            """
            insert into alpha_score_ledger
            values (?, ?, ?, 'alpha_score', 0.8, 'positive', 'high',
                    'malf-wave-position-dense-v1', ?)
            """,
            [
                (
                    f"{family}-event-{symbol}-{bar_dt:%Y%m%d}|score",
                    f"{family}-event-{symbol}-{bar_dt:%Y%m%d}",
                    family,
                    ALPHA_RUN_ID,
                )
                for symbol, bar_dt in rows
            ],
        )
        con.executemany(
            """
            insert into alpha_signal_candidate
            values (?, ?, ?, ?, 'day', ?, 'directional_candidate', 'active', ?)
            """,
            [
                (
                    f"{family}-candidate-{symbol}-{bar_dt:%Y%m%d}",
                    f"{family}-event-{symbol}-{bar_dt:%Y%m%d}",
                    family,
                    f"{symbol}.SH",
                    bar_dt,
                    ALPHA_RUN_ID,
                )
                for symbol, bar_dt in rows
            ],
        )


def _extend_signal(path: Path) -> None:
    with duckdb.connect(str(path)) as con:
        rows = [
            ("sig-600000-0104", date(2024, 1, 4)),
            ("sig-600000-0105", date(2024, 1, 5)),
            ("sig-600000-0109", date(2024, 1, 9)),
            ("sig-600000-0110", date(2024, 1, 10)),
        ]
        con.executemany(
            """
            insert into formal_signal_ledger
            values (?, '600000.SH', 'day', ?, 'directional_opportunity', 'active',
                    'long_bias', 0.8, ?, ?)
            """,
            [(signal_id, signal_dt, ALPHA_RUN_ID, SIGNAL_RUN_ID) for signal_id, signal_dt in rows],
        )
        con.executemany(
            """
            insert into signal_component_ledger
            values (?, ?, ?, 'BOF', ?, 'support', 1.0, 'alpha-waveposition-production-v1')
            """,
            [
                (
                    f"component-{signal_dt:%Y%m%d}",
                    signal_id,
                    SIGNAL_RUN_ID,
                    f"BOF-candidate-600000-{signal_dt:%Y%m%d}",
                )
                for signal_id, signal_dt in rows
            ],
        )


def _extend_position(path: Path) -> None:
    with duckdb.connect(str(path)) as con:
        rows = [
            ("pc-600000-0104", date(2024, 1, 4)),
            ("pc-600000-0105", date(2024, 1, 5)),
            ("pc-600000-0109", date(2024, 1, 9)),
            ("pc-600000-0110", date(2024, 1, 10)),
        ]
        con.executemany(
            """
            insert into position_candidate_ledger
            values (?, ?, '600000.SH', 'day', ?, 'directional_position_candidate',
                    'planned', 'long_candidate', ?, ?)
            """,
            [
                (
                    candidate_id,
                    f"sig-600000-{candidate_dt:%m%d}",
                    candidate_dt,
                    SIGNAL_RUN_ID,
                    POSITION_RUN_ID,
                )
                for candidate_id, candidate_dt in rows
            ],
        )
        con.executemany(
            """
            insert into position_entry_plan
            values (?, ?, 'signal_follow_entry', 'next_session_open_plan', ?, ?, null, 'planned', ?)
            """,
            [
                (f"entry-{candidate_id}", candidate_id, candidate_dt, candidate_dt, POSITION_RUN_ID)
                for candidate_id, candidate_dt in rows
            ],
        )
        con.executemany(
            """
            insert into position_exit_plan
            values (
                ?, ?, 'signal_invalidation_exit', 'signal_invalidated_or_expired',
                ?, ?, null, 'planned', ?
            )
            """,
            [
                (f"exit-{candidate_id}", candidate_id, candidate_dt, candidate_dt, POSITION_RUN_ID)
                for candidate_id, candidate_dt in rows
            ],
        )


def _extend_portfolio_plan(path: Path) -> None:
    with duckdb.connect(str(path)) as con:
        rows = [
            ("adm-600000-0104", "pc-600000-0104", date(2024, 1, 4)),
            ("adm-600000-0105", "pc-600000-0105", date(2024, 1, 5)),
            ("adm-600000-0109", "pc-600000-0109", date(2024, 1, 9)),
            ("adm-600000-0110", "pc-600000-0110", date(2024, 1, 10)),
        ]
        con.executemany(
            """
            insert into portfolio_admission_ledger
            values (?, ?, '600000.SH', 'day', ?, 'admitted', 'within_capacity_constraint', ?, ?)
            """,
            [
                (admission_id, candidate_id, plan_dt, POSITION_RUN_ID, PORTFOLIO_RUN_ID)
                for admission_id, candidate_id, plan_dt in rows
            ],
        )
        con.executemany(
            """
            insert into portfolio_target_exposure
            values (?, ?, 'target_weight', 0.25, 100000.0, 100.0, ?, null, ?)
            """,
            [
                (f"exp-{plan_dt:%Y%m%d}", admission_id, plan_dt, PORTFOLIO_RUN_ID)
                for admission_id, _, plan_dt in rows
            ],
        )


def _extend_trade(path: Path) -> None:
    with duckdb.connect(str(path)) as con:
        snapshot_rows = [
            ("snapshot-600000-0104", "adm-600000-0104", "pc-600000-0104", date(2024, 1, 4)),
            ("snapshot-600000-0105", "adm-600000-0105", "pc-600000-0105", date(2024, 1, 5)),
            ("snapshot-600000-0109", "adm-600000-0109", "pc-600000-0109", date(2024, 1, 9)),
            ("snapshot-600000-0110", "adm-600000-0110", "pc-600000-0110", date(2024, 1, 10)),
        ]
        con.executemany(
            """
            insert into trade_portfolio_snapshot
            values (?, ?, ?, ?, '600000.SH', 'day', ?, 'admitted', ?)
            """,
            [
                (snapshot_id, TRADE_RUN_ID, admission_id, candidate_id, plan_dt, TRADE_RUN_ID)
                for snapshot_id, admission_id, candidate_id, plan_dt in snapshot_rows
            ],
        )
        intent_rows = [
            ("intent-600000-0104", "adm-600000-0104", "pc-600000-0104", date(2024, 1, 4)),
            ("intent-600000-0105", "adm-600000-0105", "pc-600000-0105", date(2024, 1, 5)),
            ("intent-600000-0109", "adm-600000-0109", "pc-600000-0109", date(2024, 1, 9)),
            ("intent-600000-0110", "adm-600000-0110", "pc-600000-0110", date(2024, 1, 10)),
        ]
        con.executemany(
            """
            insert into order_intent_ledger
            values (?, ?, ?, ?, '600000.SH', 'day', ?, 'buy', ?)
            """,
            [
                (intent_id, TRADE_RUN_ID, admission_id, candidate_id, intent_dt, TRADE_RUN_ID)
                for intent_id, admission_id, candidate_id, intent_dt in intent_rows
            ],
        )
        con.executemany(
            """
            insert into execution_plan_ledger
            values (?, ?, ?, 'portfolio_plan_target', null, ?, ?, 'planned', ?)
            """,
            [
                (
                    f"plan-{intent_dt:%Y%m%d}",
                    TRADE_RUN_ID,
                    intent_id,
                    intent_dt,
                    intent_dt,
                    TRADE_RUN_ID,
                )
                for intent_id, _, _, intent_dt in intent_rows
            ],
        )
