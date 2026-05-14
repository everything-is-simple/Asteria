from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

import duckdb

from asteria.signal.pas_contracts import (
    SIGNAL_PAS_FORBIDDEN_OUTPUT_FIELDS,
    SIGNAL_PAS_REQUIRED_OUTPUT_FIELDS,
)


def write_alignment_db(path: Path, payload: dict[str, list[tuple[object, ...]]]) -> None:
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
        formal_columns = {
            str(row[1])
            for row in con.execute("pragma table_info(signal_pas_formal_signal)").fetchall()
        }
        all_columns = set(formal_columns)
        for table_name in (
            "signal_pas_input_snapshot",
            "signal_pas_component_ledger",
            "signal_pas_audit",
        ):
            all_columns.update(
                str(row[1]) for row in con.execute(f"pragma table_info({table_name})").fetchall()
            )
    return {
        "required_fields": sorted(SIGNAL_PAS_REQUIRED_OUTPUT_FIELDS),
        "required_fields_missing": sorted(SIGNAL_PAS_REQUIRED_OUTPUT_FIELDS - formal_columns),
        "forbidden_fields_present": sorted(
            SIGNAL_PAS_FORBIDDEN_OUTPUT_FIELDS.intersection(all_columns)
        ),
    }


def write_report_files(
    request: Any,
    summary: Any,
    coverage: dict[str, Any],
    lineage: dict[str, Any],
    audit: dict[str, Any],
) -> None:
    reports = {
        "alignment-summary.json": summary.as_dict(),
        "contract-coverage.json": coverage,
        "lineage-summary.json": lineage,
        "audit-summary.json": audit,
        "manifest.json": {
            "run_id": request.run_id,
            "source_pas_db": str(request.source_pas_db),
            "source_pas_run_id": request.source_pas_run_id,
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
        zf.write(request.output_db_path, arcname="temp/signal_pas_alignment.duckdb")


def _create_tables(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        create table signal_pas_input_snapshot (
            candidate_id varchar, symbol varchar, timeframe varchar, setup_date date,
            signal_date date, setup_family varchar, candidate_state varchar,
            context_reason_code varchar, trigger_reason_code varchar,
            failure_reason_code varchar, confidence varchar, strength_score double,
            strength_bucket varchar, source_pas_run_id varchar,
            malf_wave_position_run_id varchar, source_alpha_pas_rule_version varchar,
            source_alpha_pas_schema_version varchar, source_concept_trace varchar,
            pas_lineage varchar, execution_hint varchar,
            execution_trade_date_policy varchar, execution_price_field varchar,
            source_db varchar, run_id varchar, created_at timestamp
        )
        """
    )
    con.execute(
        """
        create table signal_pas_formal_signal (
            signal_id varchar, symbol varchar, timeframe varchar, signal_date date,
            signal_type varchar, signal_state varchar, signal_strength double,
            signal_family varchar, source_run_id varchar, source_pas_run_id varchar,
            schema_version varchar, signal_rule_version varchar,
            source_alpha_pas_rule_version varchar, lineage varchar,
            execution_hint varchar, execution_trade_date_policy varchar,
            execution_price_field varchar, active_candidate_count bigint,
            created_at timestamp
        )
        """
    )
    con.execute(
        """
        create table signal_pas_component_ledger (
            component_id varchar, signal_id varchar, candidate_id varchar,
            symbol varchar, timeframe varchar, signal_date date, setup_family varchar,
            candidate_state varchar, component_role varchar, component_strength double,
            source_pas_run_id varchar, malf_wave_position_run_id varchar,
            source_concept_trace varchar, lineage varchar, created_at timestamp
        )
        """
    )
    con.execute(
        """
        create table signal_pas_audit (
            audit_id varchar, run_id varchar, check_name varchar, severity varchar,
            status varchar, failed_count bigint, sample_payload varchar,
            created_at timestamp
        )
        """
    )
