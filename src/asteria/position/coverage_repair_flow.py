from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb

from asteria.position.audit_engine import build_position_audit_rows
from asteria.position.contracts import PositionBuildRequest
from asteria.position.coverage_repair_contracts import (
    FOCUS_DATES,
    FOCUS_END,
    FOCUS_START,
    Position2024CoverageRepairRequest,
)
from asteria.position.coverage_repair_shared import position_report_dir
from asteria.position.rules import signal_from_row
from asteria.position.schema import bootstrap_position_database


def resolve_released_chain(system_db: Path) -> dict[str, Any]:
    with duckdb.connect(str(system_db), read_only=True) as con:
        row = con.execute(
            """
            select run_id
            from system_readout_run
            where status = 'completed'
            order by created_at desc
            limit 1
            """
        ).fetchone()
        if row is None or row[0] is None:
            raise ValueError("missing completed system_readout_run row")
        released_system_run_id = str(row[0])
        manifest_rows = [
            {
                "module_name": str(item[0]),
                "source_db": str(item[1]),
                "source_run_id": str(item[2]),
                "source_release_version": str(item[3]),
            }
            for item in con.execute(
                """
                select module_name, source_db, source_run_id, source_release_version
                from system_source_manifest
                where system_readout_run_id = ?
                """,
                [released_system_run_id],
            ).fetchall()
        ]
    return {
        "released_system_run_id": released_system_run_id,
        "manifest_rows": manifest_rows,
    }


def single_manifest_row(
    manifest_rows: list[dict[str, str]],
    module_name: str,
) -> dict[str, str]:
    matches = [row for row in manifest_rows if row["module_name"] == module_name]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {module_name} manifest row")
    return matches[0]


def load_focus_signals(signal_db: Path, signal_run_id: str) -> list[Any]:
    if not signal_db.exists():
        raise FileNotFoundError(f"Missing Signal DB: {signal_db}")
    with duckdb.connect(str(signal_db), read_only=True) as con:
        rows = con.execute(
            """
            select signal_id, symbol, timeframe, signal_dt, signal_type, signal_state,
                   signal_bias, signal_strength, confidence_bucket, reason_code,
                   source_alpha_release_version, run_id, schema_version, signal_rule_version
            from formal_signal_ledger
            where timeframe = 'day'
              and run_id = ?
              and signal_dt >= ?
              and signal_dt <= ?
            order by symbol, signal_dt, signal_id
            """,
            [signal_run_id, FOCUS_START, FOCUS_END],
        ).fetchall()
    signals = [signal_from_row(row) for row in rows]
    distinct_dates = {item.signal_dt.isoformat() for item in signals}
    missing = sorted(set(FOCUS_DATES) - distinct_dates)
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"released Signal day surface missing focus dates: {joined}")
    return signals


def apply_focus_window_repair(
    *,
    target_position_db: Path,
    build_request: PositionBuildRequest,
    rows: Any,
    created_at: datetime,
) -> None:
    bootstrap_position_database(target_position_db)
    with duckdb.connect(str(target_position_db)) as con:
        existing = con.execute(
            """
            select runner_name, mode, timeframe, status, source_signal_db,
                   schema_version, position_rule_version, source_signal_release_version,
                   source_signal_run_id
            from position_run
            where run_id = ?
            """,
            [build_request.run_id],
        ).fetchone()
        if existing is None:
            raise ValueError(f"missing released position run row: {build_request.run_id}")
        con.execute("begin transaction")
        delete_focus_window_rows(con, build_request.run_id)
        con.execute(
            "delete from position_schema_version where schema_version = ?",
            [build_request.schema_version],
        )
        con.execute(
            "delete from position_rule_version where position_rule_version = ?",
            [build_request.position_rule_version],
        )
        con.execute(
            "insert into position_schema_version values (?, ?)",
            [build_request.schema_version, created_at],
        )
        con.execute(
            "insert into position_rule_version values (?, ?, ?)",
            [build_request.position_rule_version, "signal_to_position_plan", created_at],
        )
        con.executemany(
            (
                "insert into position_signal_snapshot "
                "values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            ),
            rows.snapshots,
        )
        con.executemany(
            (
                "insert into position_candidate_ledger "
                "values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            ),
            rows.candidates,
        )
        con.executemany(
            "insert into position_entry_plan values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows.entries,
        )
        con.executemany(
            "insert into position_exit_plan values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows.exits,
        )
        snapshot_count = count_rows(
            con,
            table_name="position_signal_snapshot",
            key_name="position_run_id",
            run_id=build_request.run_id,
        )
        candidate_count = count_rows(
            con,
            table_name="position_candidate_ledger",
            key_name="run_id",
            run_id=build_request.run_id,
        )
        entry_count = count_rows(
            con,
            table_name="position_entry_plan",
            key_name="run_id",
            run_id=build_request.run_id,
        )
        exit_count = count_rows(
            con,
            table_name="position_exit_plan",
            key_name="run_id",
            run_id=build_request.run_id,
        )
        con.execute(
            """
            update position_run
            set input_signal_count = ?,
                position_candidate_count = ?,
                entry_plan_count = ?,
                exit_plan_count = ?,
                hard_fail_count = 0,
                status = 'completed',
                source_signal_db = ?,
                schema_version = ?,
                position_rule_version = ?,
                source_signal_release_version = ?,
                source_signal_run_id = ?,
                created_at = ?
            where run_id = ?
            """,
            [
                snapshot_count,
                candidate_count,
                entry_count,
                exit_count,
                str(build_request.source_signal_db),
                str(existing[5]),
                str(existing[6]),
                build_request.source_signal_release_version,
                build_request.source_signal_run_id,
                created_at,
                build_request.run_id,
            ],
        )
        con.execute("commit")


def delete_focus_window_rows(con: duckdb.DuckDBPyConnection, run_id: str) -> None:
    focus_args = [run_id, FOCUS_START, FOCUS_END]
    con.execute(
        """
        delete from position_signal_snapshot
        where position_run_id = ?
          and timeframe = 'day'
          and signal_dt >= ?
          and signal_dt <= ?
        """,
        focus_args,
    )
    con.execute(
        """
        delete from position_candidate_ledger
        where run_id = ?
          and timeframe = 'day'
          and candidate_dt >= ?
          and candidate_dt <= ?
        """,
        focus_args,
    )
    con.execute(
        """
        delete from position_entry_plan
        where run_id = ?
          and entry_reference_dt >= ?
          and entry_reference_dt <= ?
        """,
        focus_args,
    )
    con.execute(
        """
        delete from position_exit_plan
        where run_id = ?
          and exit_reference_dt >= ?
          and exit_reference_dt <= ?
        """,
        focus_args,
    )


def count_rows(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    key_name: str,
    run_id: str,
) -> int:
    row = con.execute(
        f"select count(*) from {table_name} where {key_name} = ?",
        [run_id],
    ).fetchone()
    return 0 if row is None or row[0] is None else int(row[0])


def run_repair_audit(
    *,
    build_request: PositionBuildRequest,
    repair_request: Position2024CoverageRepairRequest,
    created_at: datetime,
) -> tuple[Path, dict[str, Any]]:
    audit_rows, payload = build_position_audit_rows(build_request, created_at)
    with duckdb.connect(str(build_request.target_position_db)) as con:
        con.execute("begin transaction")
        con.execute(
            "delete from position_audit where audit_id like ?",
            [f"{build_request.run_id}|{build_request.timeframe}|%"],
        )
        con.executemany("insert into position_audit values (?, ?, ?, ?, ?, ?, ?, ?)", audit_rows)
        con.execute(
            """
            update position_run
            set hard_fail_count = ?,
                status = ?,
                input_signal_count = ?,
                position_candidate_count = ?,
                entry_plan_count = ?,
                exit_plan_count = ?
            where run_id = ?
            """,
            [
                payload["hard_fail_count"],
                "completed" if int(payload["hard_fail_count"]) == 0 else "failed",
                payload["input_signal_count"],
                payload["position_candidate_count"],
                payload["entry_plan_count"],
                payload["exit_plan_count"],
                build_request.run_id,
            ],
        )
        con.execute("commit")
    report_dir = position_report_dir(repair_request.report_root, repair_request.run_id)
    report_dir.mkdir(parents=True, exist_ok=True)
    audit_report_path = report_dir / "position-day-audit-summary.json"
    audit_report_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return audit_report_path, payload
