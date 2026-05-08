from __future__ import annotations

from pathlib import Path

import duckdb

SYSTEM_READOUT_TABLES = (
    "system_readout_run",
    "system_schema_version",
    "system_readout_version",
    "system_source_manifest",
    "system_module_status_snapshot",
    "system_chain_readout",
    "system_summary_snapshot",
    "system_audit_snapshot",
    "system_readout_audit",
)


def bootstrap_system_readout_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table if not exists system_readout_run (
                run_id varchar,
                runner_name varchar,
                mode varchar,
                timeframe varchar,
                status varchar,
                source_chain_release_version varchar,
                source_manifest_count bigint,
                module_status_count bigint,
                readout_count bigint,
                summary_count bigint,
                audit_snapshot_count bigint,
                hard_fail_count bigint,
                schema_version varchar,
                system_readout_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists system_schema_version (
                schema_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists system_readout_version (
                system_readout_version varchar,
                timeframe varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists system_source_manifest (
                source_manifest_id varchar,
                system_readout_run_id varchar,
                module_name varchar,
                source_db varchar,
                source_run_id varchar,
                source_release_version varchar,
                source_schema_version varchar,
                source_audit_ref varchar,
                source_audit_status varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists system_module_status_snapshot (
                module_status_snapshot_id varchar,
                system_readout_run_id varchar,
                module_name varchar,
                module_release_version varchar,
                module_run_id varchar,
                module_status varchar,
                source_manifest_id varchar,
                source_audit_ref varchar,
                source_audit_status varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists system_chain_readout (
                system_readout_id varchar,
                system_readout_run_id varchar,
                symbol varchar,
                timeframe varchar,
                readout_dt date,
                readout_status varchar,
                malf_state_ref varchar,
                alpha_ref varchar,
                signal_ref varchar,
                position_ref varchar,
                portfolio_plan_ref varchar,
                trade_ref varchar,
                wave_core_state varchar,
                system_state varchar,
                source_chain_release_version varchar,
                system_readout_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists system_summary_snapshot (
                summary_id varchar,
                system_readout_run_id varchar,
                summary_scope varchar,
                summary_dt date,
                summary_payload varchar,
                readout_status varchar,
                source_chain_release_version varchar,
                system_readout_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists system_audit_snapshot (
                system_audit_snapshot_id varchar,
                system_readout_run_id varchar,
                audit_scope varchar,
                audit_dt date,
                module_name varchar,
                source_audit_ref varchar,
                source_audit_status varchar,
                system_readout_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists system_readout_audit (
                audit_id varchar,
                run_id varchar,
                check_name varchar,
                severity varchar,
                status varchar,
                failed_count bigint,
                sample_payload varchar,
                created_at timestamp
            )
            """
        )
