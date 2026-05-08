from __future__ import annotations

from pathlib import Path

import duckdb

PIPELINE_TABLES = (
    "pipeline_run",
    "pipeline_step_run",
    "module_gate_snapshot",
    "build_manifest",
    "pipeline_audit",
)


def bootstrap_pipeline_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table if not exists pipeline_run (
                pipeline_run_id varchar,
                runner_name varchar,
                module_scope varchar,
                run_mode varchar,
                run_status varchar,
                source_module varchar,
                source_release_version varchar,
                source_db varchar,
                step_count bigint,
                gate_snapshot_count bigint,
                manifest_count bigint,
                audit_count bigint,
                schema_version varchar,
                pipeline_version varchar,
                gate_registry_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists pipeline_step_run (
                pipeline_step_run_id varchar,
                pipeline_run_id varchar,
                step_seq bigint,
                module_name varchar,
                step_name varchar,
                step_status varchar,
                source_db varchar,
                source_run_id varchar,
                source_release_version varchar,
                started_at timestamp,
                completed_at timestamp,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists module_gate_snapshot (
                gate_snapshot_id varchar,
                pipeline_run_id varchar,
                module_name varchar,
                gate_name varchar,
                gate_value varchar,
                source_registry_version varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists build_manifest (
                manifest_entry_id varchar,
                pipeline_run_id varchar,
                artifact_name varchar,
                artifact_role varchar,
                artifact_path varchar,
                source_ref varchar,
                source_type varchar,
                checksum_hint varchar,
                created_at timestamp
            )
            """
        )
        con.execute(
            """
            create table if not exists pipeline_audit (
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
