from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import duckdb
from tests.unit.system_readout.support_upstream import (
    ALPHA_FAMILIES,
    ALPHA_RUN_ID,
    MALF_RUN_ID,
    PORTFOLIO_RUN_ID,
    POSITION_RUN_ID,
    SIGNAL_RUN_ID,
    TRADE_RUN_ID,
)

from asteria.system_readout.contracts import (
    SYSTEM_READOUT_SCHEMA_VERSION,
    SYSTEM_READOUT_VERSION,
)
from asteria.system_readout.schema import bootstrap_system_readout_database


def seed_late_system_release_db(path: Path, data_root: Path, *, system_run_id: str) -> None:
    bootstrap_system_readout_database(path)
    created_at = datetime(2026, 5, 8, 12, 0, 0)
    readout_dates = [date(2024, 1, 9), date(2024, 1, 10)]
    with duckdb.connect(str(path)) as con:
        con.execute(
            "insert into system_schema_version values (?, ?)",
            [SYSTEM_READOUT_SCHEMA_VERSION, created_at],
        )
        con.execute(
            "insert into system_readout_version values (?, 'day', ?)",
            [SYSTEM_READOUT_VERSION, created_at],
        )
        con.execute(
            """
            insert into system_readout_run values (
                ?, 'system_readout_build', 'bounded', 'day', 'completed',
                ?, 10, 6, 2, 2, 6, 0, ?, ?, ?
            )
            """,
            [
                system_run_id,
                TRADE_RUN_ID,
                SYSTEM_READOUT_SCHEMA_VERSION,
                SYSTEM_READOUT_VERSION,
                created_at,
            ],
        )
        manifest_rows = [
            (
                "malf",
                data_root / "malf_service_day.duckdb",
                MALF_RUN_ID,
                MALF_RUN_ID,
                "malf-day-bounded-proof-v1",
                "malf-unit|audit",
            ),
            (
                "signal",
                data_root / "signal.duckdb",
                SIGNAL_RUN_ID,
                SIGNAL_RUN_ID,
                "signal-bounded-proof-v1",
                "signal-unit|audit",
            ),
            (
                "position",
                data_root / "position.duckdb",
                POSITION_RUN_ID,
                POSITION_RUN_ID,
                "position-bounded-proof-v1",
                "position-unit|audit",
            ),
            (
                "portfolio_plan",
                data_root / "portfolio_plan.duckdb",
                PORTFOLIO_RUN_ID,
                PORTFOLIO_RUN_ID,
                "portfolio-plan-bounded-proof-v1",
                "portfolio-unit|audit",
            ),
            (
                "trade",
                data_root / "trade.duckdb",
                TRADE_RUN_ID,
                TRADE_RUN_ID,
                "trade-bounded-proof-v1",
                "trade-unit|audit",
            ),
        ]
        manifest_rows.extend(
            [
                (
                    f"alpha_{family}",
                    data_root / f"alpha_{family}.duckdb",
                    ALPHA_RUN_ID,
                    ALPHA_RUN_ID,
                    "alpha-family-schema-v1",
                    "alpha-unit|audit",
                )
                for family in ALPHA_FAMILIES
            ]
        )
        con.executemany(
            """
            insert into system_source_manifest
            values (?, ?, ?, ?, ?, ?, ?, ?, 'pass', ?)
            """,
            [
                (
                    f"{system_run_id}|{module_name}",
                    system_run_id,
                    module_name,
                    str(db_path),
                    source_run_id,
                    source_release_version,
                    schema_version,
                    audit_ref,
                    created_at,
                )
                for (
                    module_name,
                    db_path,
                    source_run_id,
                    source_release_version,
                    schema_version,
                    audit_ref,
                ) in manifest_rows
            ],
        )
        con.executemany(
            """
            insert into system_module_status_snapshot
            values (?, ?, ?, ?, ?, 'released', ?, ?, 'pass', ?)
            """,
            [
                (
                    f"{system_run_id}|{module_name}",
                    system_run_id,
                    module_name,
                    release_version,
                    run_id,
                    f"{system_run_id}|{manifest_name}",
                    audit_ref,
                    created_at,
                )
                for module_name, manifest_name, release_version, run_id, audit_ref in [
                    ("malf", "malf", MALF_RUN_ID, MALF_RUN_ID, "malf-unit|audit"),
                    ("alpha", "alpha_bof", ALPHA_RUN_ID, ALPHA_RUN_ID, "alpha-unit|audit"),
                    ("signal", "signal", SIGNAL_RUN_ID, SIGNAL_RUN_ID, "signal-unit|audit"),
                    (
                        "position",
                        "position",
                        POSITION_RUN_ID,
                        POSITION_RUN_ID,
                        "position-unit|audit",
                    ),
                    (
                        "portfolio_plan",
                        "portfolio_plan",
                        PORTFOLIO_RUN_ID,
                        PORTFOLIO_RUN_ID,
                        "portfolio-unit|audit",
                    ),
                    ("trade", "trade", TRADE_RUN_ID, TRADE_RUN_ID, "trade-unit|audit"),
                ]
            ],
        )
        con.executemany(
            """
            insert into system_chain_readout
            values (?, ?, '600000.SH', 'day', ?, 'partial', 'wave-ref', 'alpha-ref',
                    'signal-ref', 'position-ref', 'portfolio-ref', 'trade-ref',
                    'impulse', 'trend_up', ?, ?, ?)
            """,
            [
                (
                    f"{system_run_id}|600000.SH|{readout_dt.isoformat()}|{SYSTEM_READOUT_VERSION}",
                    system_run_id,
                    readout_dt,
                    TRADE_RUN_ID,
                    SYSTEM_READOUT_VERSION,
                    created_at,
                )
                for readout_dt in readout_dates
            ],
        )
        con.executemany(
            """
            insert into system_summary_snapshot
            values (?, ?, '600000.SH', ?, ?, 'partial', ?, ?, ?)
            """,
            [
                (
                    f"{system_run_id}|summary|600000.SH|{readout_dt.isoformat()}",
                    system_run_id,
                    readout_dt,
                    '{"symbol":"600000.SH","readout_status":"partial"}',
                    TRADE_RUN_ID,
                    SYSTEM_READOUT_VERSION,
                    created_at,
                )
                for readout_dt in readout_dates
            ],
        )
        con.executemany(
            """
            insert into system_audit_snapshot
            values (?, ?, 'module_release', ?, ?, ?, 'pass', ?, ?)
            """,
            [
                (
                    f"{system_run_id}|audit_snapshot|{module_name}",
                    system_run_id,
                    date(2024, 1, 9),
                    module_name,
                    audit_ref,
                    SYSTEM_READOUT_VERSION,
                    created_at,
                )
                for module_name, audit_ref in [
                    ("malf", "malf-unit|audit"),
                    ("alpha", "alpha-unit|audit"),
                    ("signal", "signal-unit|audit"),
                    ("position", "position-unit|audit"),
                    ("portfolio_plan", "portfolio-unit|audit"),
                    ("trade", "trade-unit|audit"),
                ]
            ],
        )
        con.execute(
            """
            insert into system_readout_audit
            values (?, ?, 'unit_seed_ok', 'hard', 'pass', 0, '{}', ?)
            """,
            [f"{system_run_id}|day|unit_seed_ok", system_run_id, created_at],
        )
