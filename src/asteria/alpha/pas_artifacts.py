from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

import duckdb

from asteria.alpha.pas_contracts import (
    PAS_FORBIDDEN_OUTPUT_FIELDS,
    PAS_LIFECYCLE_STATES,
    PAS_REQUIRED_SERVICE_FIELDS,
    PAS_SOURCE_CONCEPT_TRACE,
)


def write_proof_db(path: Path, payload: dict[str, list[tuple[object, ...]]]) -> None:
    if path.exists():
        path.unlink()
    wal_path = path.with_name(f"{path.name}.wal")
    if wal_path.exists():
        wal_path.unlink()
    with duckdb.connect(str(path)) as con:
        con.execute("begin transaction")
        _create_tables(con)
        for table_name, rows in payload.items():
            if rows:
                placeholders = ", ".join(["?"] * len(rows[0]))
                con.executemany(f"insert into {table_name} values ({placeholders})", rows)
        con.execute("commit")
        con.execute("checkpoint")


def contract_coverage(db_path: Path) -> dict[str, Any]:
    with duckdb.connect(str(db_path), read_only=True) as con:
        columns = {
            str(row[1]) for row in con.execute("pragma table_info(pas_entry_candidate)").fetchall()
        }
    return {
        "required_fields": sorted(PAS_REQUIRED_SERVICE_FIELDS),
        "required_fields_missing": sorted(PAS_REQUIRED_SERVICE_FIELDS - columns),
        "forbidden_fields_present": sorted(PAS_FORBIDDEN_OUTPUT_FIELDS.intersection(columns)),
    }


def lineage_summary(payload: dict[str, list[tuple[object, ...]]], request: Any) -> dict[str, Any]:
    states = sorted({str(row[1]) for row in payload["pas_candidate_lifecycle"]})
    return {
        "run_id": request.run_id,
        "source_malf_db": str(request.source_malf_db),
        "source_malf_run_id": request.source_malf_run_id,
        "candidate_states_observed": states,
        "lifecycle_states_expressible": sorted(PAS_LIFECYCLE_STATES),
        "source_concept_trace": PAS_SOURCE_CONCEPT_TRACE,
    }


def write_report_files(
    request: Any,
    summary: Any,
    coverage: dict[str, Any],
    lineage: dict[str, Any],
    audit: dict[str, Any],
) -> None:
    reports = {
        "proof-summary.json": summary.as_dict(),
        "contract-coverage.json": coverage,
        "lineage-summary.json": lineage,
        "audit-summary.json": audit,
        "manifest.json": {
            "run_id": request.run_id,
            "output_db": str(request.output_db_path),
            "formal_data_mutation": "no",
            "validated_zip": str(request.validated_zip_path),
        },
    }
    for name, payload in reports.items():
        (request.report_dir / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def write_validated_zip(request: Any) -> None:
    request.validated_root.mkdir(parents=True, exist_ok=True)
    if request.validated_zip_path.exists():
        request.validated_zip_path.unlink()
    with zipfile.ZipFile(request.validated_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(request.report_dir.glob("*")):
            zf.write(path, arcname=f"report/{path.name}")
        zf.write(request.output_db_path, arcname="temp/alpha_pas_bounded_proof.duckdb")


def _create_tables(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        create table pas_proof_run (
            run_id varchar, status varchar, mode varchar, timeframe varchar,
            source_malf_db varchar, input_row_count bigint, candidate_count bigint,
            schema_version varchar, rule_version varchar, source_malf_service_version varchar,
            source_malf_run_id varchar, formal_data_mutation varchar, created_at timestamp
        )
        """
    )
    con.execute(
        """
        create table pas_lifecycle_state_catalog (
            lifecycle_state varchar, definition varchar, created_at timestamp
        )
        """
    )
    shared = """
        candidate_id varchar, symbol varchar, timeframe varchar, setup_date date,
        setup_family varchar, source_run_id varchar, malf_wave_position_run_id varchar,
        rule_version varchar, schema_version varchar, lineage varchar, created_at timestamp
    """
    con.execute(
        f"""
        create table pas_market_context (
            {shared}, context_reason_code varchar, system_state varchar,
            wave_core_state varchar, direction varchar, life_state varchar,
            position_quadrant varchar, guard_boundary_price double,
            boundary_interaction varchar
        )
        """
    )
    con.execute(
        f"""
        create table pas_strength_profile (
            {shared}, completed_same_direction_baseline varchar,
            completed_opposite_direction_comparison varchar,
            in_flight_confirmation varchar, boundary_interaction varchar,
            stagnation_or_no_followthrough varchar, historical_sample_count bigint,
            sparsity_label varchar, strength_score double, strength_bucket varchar
        )
        """
    )
    con.execute(
        f"""
        create table pas_trigger_event (
            {shared}, candidate_state varchar, trigger_reason_code varchar,
            trigger_event_state varchar
        )
        """
    )
    con.execute(
        f"""
        create table pas_historical_rank_profile (
            {shared}, sample_count bigint, sparsity_label varchar,
            percentile_bucket varchar, forward_readout_field varchar,
            failure_cancellation_ranking varchar
        )
        """
    )
    con.execute(
        """
        create table pas_entry_candidate (
            symbol varchar, timeframe varchar, setup_date date, signal_date date,
            setup_family varchar, candidate_state varchar, context_reason_code varchar,
            trigger_reason_code varchar, failure_reason_code varchar, confidence varchar,
            strength_score double, strength_bucket varchar, source_run_id varchar,
            malf_wave_position_run_id varchar, rule_version varchar, schema_version varchar,
            source_concept_trace varchar, lineage varchar, execution_hint varchar,
            execution_trade_date_policy varchar, execution_price_field varchar,
            pas_management_handoff_hint varchar, candidate_id varchar, created_at timestamp
        )
        """
    )
    con.execute(
        """
        create table pas_candidate_lifecycle (
            candidate_id varchar, lifecycle_state varchar, reason_code varchar,
            is_current boolean, lineage varchar, created_at timestamp
        )
        """
    )
    con.execute(
        """
        create table pas_failure_state (
            candidate_id varchar, symbol varchar, timeframe varchar, setup_date date,
            failure_reason_code varchar, is_failure_state boolean, in_flight_evidence varchar,
            source_run_id varchar, malf_wave_position_run_id varchar, rule_version varchar,
            schema_version varchar, created_at timestamp
        )
        """
    )
    con.execute(
        """
        create table pas_source_lineage (
            candidate_id varchar, source_run_id varchar, malf_wave_position_run_id varchar,
            malf_service_version varchar, malf_sample_version varchar,
            source_concept_trace varchar, lineage varchar, created_at timestamp
        )
        """
    )
