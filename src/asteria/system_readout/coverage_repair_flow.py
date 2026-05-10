from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

import duckdb

from asteria.system_readout.audit_engine import build_system_readout_audit_rows
from asteria.system_readout.contracts import SystemReadoutBuildRequest
from asteria.system_readout.coverage_repair_contracts import (
    FOCUS_END,
    FOCUS_START,
    SystemReadout2024CoverageRepairRequest,
)
from asteria.system_readout.coverage_repair_shared import (
    count_rows,
    key_in_focus_window,
    system_readout_report_dir,
)
from asteria.system_readout.rules import (
    ModuleStatusInput,
    SourceManifestInput,
    build_system_readout_rows,
)
from asteria.system_readout.runtime_io import (
    _build_readout_inputs,
    _load_alpha_candidates,
    _load_latest_run,
    _load_malf_rows,
    _load_portfolio_rows,
    _load_position_rows,
    _load_signal_rows,
    _load_trade_rows,
)
from asteria.system_readout.schema import bootstrap_system_readout_database

EXPECTED_MANIFEST_MODULES = (
    "malf",
    "alpha_bof",
    "alpha_tst",
    "alpha_pb",
    "alpha_cpb",
    "alpha_bpb",
    "signal",
    "position",
    "portfolio_plan",
    "trade",
)
ALPHA_FAMILIES = ("bof", "tst", "pb", "cpb", "bpb")


def resolve_released_chain(system_db: Path) -> dict[str, Any]:
    with duckdb.connect(str(system_db), read_only=True) as con:
        run_row = con.execute(
            """
            select run_id, source_chain_release_version, schema_version, system_readout_version
            from system_readout_run
            where status = 'completed'
            order by created_at desc
            limit 1
            """
        ).fetchone()
        if run_row is None or run_row[0] is None:
            raise ValueError("missing completed system_readout_run row")
        released_system_run_id = str(run_row[0])
        manifest_rows = [
            {
                "module_name": str(item[0]),
                "source_db": str(item[1]),
                "source_run_id": str(item[2]),
                "source_release_version": str(item[3]),
                "source_schema_version": str(item[4]),
                "source_audit_ref": "" if item[5] is None else str(item[5]),
                "source_audit_status": str(item[6]),
            }
            for item in con.execute(
                """
                select module_name, source_db, source_run_id, source_release_version,
                       source_schema_version, source_audit_ref, source_audit_status
                from system_source_manifest
                where system_readout_run_id = ?
                """,
                [released_system_run_id],
            ).fetchall()
        ]
    return {
        "released_system_run_id": released_system_run_id,
        "source_chain_release_version": str(run_row[1]),
        "schema_version": str(run_row[2]),
        "system_readout_version": str(run_row[3]),
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


def load_released_chain_inputs(
    *,
    build_request: SystemReadoutBuildRequest,
    manifest_rows: list[dict[str, str]],
) -> tuple[list[SourceManifestInput], list[ModuleStatusInput], Any]:
    released_manifest_map = {
        module_name: single_manifest_row(manifest_rows, module_name)
        for module_name in EXPECTED_MANIFEST_MODULES
    }
    manifest_map = _resolve_latest_manifest_map(released_manifest_map)
    source_manifests = [
        SourceManifestInput(
            module_name=module_name,
            source_db=row["source_db"],
            source_run_id=row["source_run_id"],
            source_release_version=row["source_release_version"],
            source_schema_version=row["source_schema_version"],
            source_audit_ref=row["source_audit_ref"],
            source_audit_status=row["source_audit_status"],
        )
        for module_name, row in manifest_map.items()
    ]
    alpha_refs = [manifest_map[f"alpha_{family}"]["source_audit_ref"] for family in ALPHA_FAMILIES]
    alpha_statuses = [
        manifest_map[f"alpha_{family}"]["source_audit_status"] for family in ALPHA_FAMILIES
    ]
    alpha_release_versions = [
        manifest_map[f"alpha_{family}"]["source_release_version"] for family in ALPHA_FAMILIES
    ]
    module_statuses = [
        ModuleStatusInput(
            "malf",
            manifest_map["malf"]["source_release_version"],
            manifest_map["malf"]["source_run_id"],
            "released",
            manifest_map["malf"]["source_audit_ref"],
            manifest_map["malf"]["source_audit_status"],
        ),
        ModuleStatusInput(
            "alpha",
            sorted(alpha_release_versions)[-1],
            sorted(alpha_release_versions)[-1],
            "released",
            ";".join(ref for ref in alpha_refs if ref),
            "pass" if set(alpha_statuses) == {"pass"} else "fail",
        ),
        ModuleStatusInput(
            "signal",
            manifest_map["signal"]["source_release_version"],
            manifest_map["signal"]["source_run_id"],
            "released",
            manifest_map["signal"]["source_audit_ref"],
            manifest_map["signal"]["source_audit_status"],
        ),
        ModuleStatusInput(
            "position",
            manifest_map["position"]["source_release_version"],
            manifest_map["position"]["source_run_id"],
            "released",
            manifest_map["position"]["source_audit_ref"],
            manifest_map["position"]["source_audit_status"],
        ),
        ModuleStatusInput(
            "portfolio_plan",
            manifest_map["portfolio_plan"]["source_release_version"],
            manifest_map["portfolio_plan"]["source_run_id"],
            "released",
            manifest_map["portfolio_plan"]["source_audit_ref"],
            manifest_map["portfolio_plan"]["source_audit_status"],
        ),
        ModuleStatusInput(
            "trade",
            manifest_map["trade"]["source_release_version"],
            manifest_map["trade"]["source_run_id"],
            "released",
            manifest_map["trade"]["source_audit_ref"],
            manifest_map["trade"]["source_audit_status"],
        ),
    ]
    alpha_candidates: dict[tuple[str, date], list[str]] = {}
    for family in ALPHA_FAMILIES:
        alpha_row = manifest_map[f"alpha_{family}"]
        for key, candidate_ids in _load_alpha_candidates(
            Path(alpha_row["source_db"]),
            alpha_row["source_run_id"],
        ).items():
            if not key_in_focus_window(key, build_request.start_date, build_request.end_date):
                continue
            alpha_candidates.setdefault(key, []).extend(candidate_ids)
    readouts = _build_readout_inputs(
        build_request,
        malf_wave_positions=_load_malf_rows(
            Path(manifest_map["malf"]["source_db"]),
            manifest_map["malf"]["source_run_id"],
            build_request,
        ),
        alpha_candidates=alpha_candidates,
        signal_rows=_load_signal_rows(
            Path(manifest_map["signal"]["source_db"]),
            manifest_map["signal"]["source_run_id"],
            build_request,
        ),
        position_rows=_load_position_rows(
            Path(manifest_map["position"]["source_db"]),
            manifest_map["position"]["source_run_id"],
            build_request,
        ),
        portfolio_rows=_load_portfolio_rows(
            Path(manifest_map["portfolio_plan"]["source_db"]),
            manifest_map["portfolio_plan"]["source_run_id"],
            build_request,
        ),
        trade_rows=_load_trade_rows(
            Path(manifest_map["trade"]["source_db"]),
            manifest_map["trade"]["source_run_id"],
            build_request,
        ),
        has_upstream_audit_gap=any(item.source_audit_status != "pass" for item in source_manifests),
    )
    return source_manifests, module_statuses, readouts


def apply_focus_window_repair(
    *,
    target_system_db: Path,
    released_system_run_id: str,
    build_request: SystemReadoutBuildRequest,
    created_at: datetime,
) -> dict[str, int]:
    bootstrap_system_readout_database(target_system_db)
    source_manifests, module_statuses, readouts = load_released_chain_inputs(
        build_request=build_request,
        manifest_rows=resolve_released_chain(target_system_db)["manifest_rows"],
    )
    built = build_system_readout_rows(
        source_manifests=source_manifests,
        module_statuses=module_statuses,
        readouts=readouts,
        request=build_request,
        created_at=created_at,
    )
    with duckdb.connect(str(target_system_db)) as con:
        existing = con.execute(
            "select run_id from system_readout_run where run_id = ?",
            [released_system_run_id],
        ).fetchone()
        if existing is None:
            raise ValueError(f"missing released system run row: {released_system_run_id}")
        con.execute("begin transaction")
        _ensure_reference_rows(con, build_request, created_at)
        _delete_run_metadata(con, released_system_run_id)
        _delete_focus_window_rows(con, released_system_run_id)
        con.executemany(
            "insert into system_source_manifest values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            built.source_manifests,
        )
        con.executemany(
            "insert into system_module_status_snapshot values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            built.module_statuses,
        )
        con.executemany(
            (
                "insert into system_chain_readout "
                "values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            ),
            built.chain_readouts,
        )
        con.executemany(
            "insert into system_summary_snapshot values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            built.summary_snapshots,
        )
        con.executemany(
            "insert into system_audit_snapshot values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            built.audit_snapshots,
        )
        counts = _system_counts(con, released_system_run_id)
        con.execute(
            """
            update system_readout_run
            set status = 'completed',
                source_chain_release_version = ?,
                source_manifest_count = ?,
                module_status_count = ?,
                readout_count = ?,
                summary_count = ?,
                audit_snapshot_count = ?,
                hard_fail_count = 0,
                schema_version = ?,
                system_readout_version = ?,
                created_at = ?
            where run_id = ?
            """,
            [
                build_request.source_chain_release_version,
                counts["source_manifest_count"],
                counts["module_status_count"],
                counts["readout_count"],
                counts["summary_count"],
                counts["audit_snapshot_count"],
                build_request.schema_version,
                build_request.system_readout_version,
                created_at,
                released_system_run_id,
            ],
        )
        con.execute("commit")
    return counts


def run_repair_audit(
    *,
    build_request: SystemReadoutBuildRequest,
    repair_request: SystemReadout2024CoverageRepairRequest,
    created_at: datetime,
) -> tuple[Path, dict[str, Any]]:
    audit_rows, payload = build_system_readout_audit_rows(
        build_request,
        created_at,
        build_request.target_system_db,
    )
    with duckdb.connect(str(build_request.target_system_db)) as con:
        con.execute("begin transaction")
        con.execute(
            "delete from system_readout_audit where audit_id like ?",
            [f"{build_request.run_id}|{build_request.timeframe}|%"],
        )
        con.executemany(
            "insert into system_readout_audit values (?, ?, ?, ?, ?, ?, ?, ?)",
            audit_rows,
        )
        con.execute(
            """
            update system_readout_run
            set hard_fail_count = ?,
                status = ?
            where run_id = ?
            """,
            [
                payload["hard_fail_count"],
                "completed" if int(payload["hard_fail_count"]) == 0 else "failed",
                build_request.run_id,
            ],
        )
        con.execute("commit")
    report_dir = system_readout_report_dir(repair_request.report_root, repair_request.run_id)
    report_dir.mkdir(parents=True, exist_ok=True)
    audit_report_path = report_dir / "system-readout-day-audit-summary.json"
    audit_report_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return audit_report_path, payload


def _ensure_reference_rows(
    con: duckdb.DuckDBPyConnection,
    build_request: SystemReadoutBuildRequest,
    created_at: datetime,
) -> None:
    schema_row = con.execute(
        "select 1 from system_schema_version where schema_version = ? limit 1",
        [build_request.schema_version],
    ).fetchone()
    if schema_row is None:
        con.execute(
            "insert into system_schema_version values (?, ?)",
            [build_request.schema_version, created_at],
        )
    version_row = con.execute(
        "select 1 from system_readout_version where system_readout_version = ? limit 1",
        [build_request.system_readout_version],
    ).fetchone()
    if version_row is None:
        con.execute(
            "insert into system_readout_version values (?, ?, ?)",
            [build_request.system_readout_version, build_request.timeframe, created_at],
        )


def _delete_run_metadata(con: duckdb.DuckDBPyConnection, run_id: str) -> None:
    con.execute("delete from system_readout_audit where run_id = ?", [run_id])
    con.execute(
        "delete from system_audit_snapshot where system_readout_run_id = ?",
        [run_id],
    )
    con.execute(
        "delete from system_module_status_snapshot where system_readout_run_id = ?",
        [run_id],
    )
    con.execute(
        "delete from system_source_manifest where system_readout_run_id = ?",
        [run_id],
    )


def _delete_focus_window_rows(con: duckdb.DuckDBPyConnection, run_id: str) -> None:
    con.execute(
        """
        delete from system_chain_readout
        where system_readout_run_id = ? and readout_dt >= ? and readout_dt <= ?
        """,
        [run_id, FOCUS_START, FOCUS_END],
    )
    con.execute(
        """
        delete from system_summary_snapshot
        where system_readout_run_id = ? and summary_dt >= ? and summary_dt <= ?
        """,
        [run_id, FOCUS_START, FOCUS_END],
    )


def _system_counts(con: duckdb.DuckDBPyConnection, run_id: str) -> dict[str, int]:
    return {
        "source_manifest_count": count_rows(
            con, "system_source_manifest", "system_readout_run_id", run_id
        ),
        "module_status_count": count_rows(
            con, "system_module_status_snapshot", "system_readout_run_id", run_id
        ),
        "readout_count": count_rows(con, "system_chain_readout", "system_readout_run_id", run_id),
        "summary_count": count_rows(
            con, "system_summary_snapshot", "system_readout_run_id", run_id
        ),
        "audit_snapshot_count": count_rows(
            con, "system_audit_snapshot", "system_readout_run_id", run_id
        ),
    }


def _resolve_latest_manifest_map(
    released_manifest_map: dict[str, dict[str, str]],
) -> dict[str, dict[str, str]]:
    manifest_map: dict[str, dict[str, str]] = {}
    for module_name, released_row in released_manifest_map.items():
        db_path = Path(released_row["source_db"])
        if module_name == "malf":
            run_id, schema_version, audit_ref, audit_status = _load_latest_run(
                db_path,
                "malf_service_run",
                "malf_interface_audit",
            )
        elif module_name.startswith("alpha_"):
            run_id, schema_version, audit_ref, audit_status = _load_latest_run(
                db_path,
                "alpha_family_run",
                "alpha_source_audit",
                family=module_name.removeprefix("alpha_").upper(),
            )
        elif module_name == "signal":
            run_id, schema_version, audit_ref, audit_status = _load_latest_run(
                db_path,
                "signal_run",
                "signal_audit",
            )
        elif module_name == "position":
            run_id, schema_version, audit_ref, audit_status = _load_latest_run(
                db_path,
                "position_run",
                "position_audit",
            )
        elif module_name == "portfolio_plan":
            run_id, schema_version, audit_ref, audit_status = _load_latest_run(
                db_path,
                "portfolio_plan_run",
                "portfolio_plan_audit",
            )
        elif module_name == "trade":
            run_id, schema_version, audit_ref, audit_status = _load_latest_run(
                db_path,
                "trade_run",
                "trade_audit",
            )
        else:
            raise ValueError(f"unsupported manifest module: {module_name}")
        updated = dict(released_row)
        updated["source_run_id"] = run_id
        updated["source_release_version"] = run_id
        updated["source_schema_version"] = schema_version
        updated["source_audit_ref"] = audit_ref
        updated["source_audit_status"] = audit_status
        manifest_map[module_name] = updated
    return manifest_map
