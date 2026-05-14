from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import duckdb
import pytest

from asteria.signal.pas_alignment import SignalPasAlignmentRequest, run_signal_pas_alignment
from asteria.signal.pas_contracts import (
    SIGNAL_PAS_EXECUTION_HINT,
    SIGNAL_PAS_EXECUTION_PRICE_FIELD,
    SIGNAL_PAS_EXECUTION_TRADE_DATE_POLICY,
    SIGNAL_PAS_FORBIDDEN_OUTPUT_FIELDS,
    SIGNAL_PAS_REQUIRED_OUTPUT_FIELDS,
)

RUN_ID = "signal-pas-alignment-unit-001"
SOURCE_PAS_RUN_ID = "alpha-pas-proof-unit-001"


def _request(tmp_path: Path, **overrides: object) -> SignalPasAlignmentRequest:
    kwargs: dict[str, object] = {
        "source_pas_db": tmp_path / "source" / "alpha_pas_bounded_proof.duckdb",
        "temp_root": tmp_path / "temp",
        "report_root": tmp_path / "report",
        "validated_root": tmp_path / "validated",
        "run_id": RUN_ID,
        "source_pas_run_id": SOURCE_PAS_RUN_ID,
    }
    kwargs.update(overrides)
    return SignalPasAlignmentRequest(**kwargs)


def _seed_pas_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute(
            """
            create table pas_entry_candidate (
                symbol varchar, timeframe varchar, setup_date date, signal_date date,
                setup_family varchar, candidate_state varchar,
                context_reason_code varchar, trigger_reason_code varchar,
                failure_reason_code varchar, confidence varchar, strength_score double,
                strength_bucket varchar, source_run_id varchar,
                malf_wave_position_run_id varchar, rule_version varchar,
                schema_version varchar, source_concept_trace varchar, lineage varchar,
                execution_hint varchar, execution_trade_date_policy varchar,
                execution_price_field varchar, pas_management_handoff_hint varchar,
                candidate_id varchar, created_at timestamp
            )
            """
        )
        rows = [
            (
                "000001.SZ",
                "day",
                "2024-01-02",
                "2024-01-03",
                "BOF",
                "triggered",
                "context_ok",
                "breakout",
                "none",
                "medium",
                0.42,
                "medium",
                SOURCE_PAS_RUN_ID,
                "malf-run-001",
                "alpha-pas-rule-v1",
                "alpha-pas-schema-v1",
                "trace-a",
                '{"pas":"lineage-a"}',
                SIGNAL_PAS_EXECUTION_HINT,
                SIGNAL_PAS_EXECUTION_TRADE_DATE_POLICY,
                SIGNAL_PAS_EXECUTION_PRICE_FIELD,
                "handoff_only",
                "candidate-001",
                "2026-05-14 00:00:00",
            ),
            (
                "000001.SZ",
                "day",
                "2024-01-02",
                "2024-01-03",
                "TST",
                "reentry_candidate",
                "context_ok",
                "reentry",
                "none",
                "high",
                0.84,
                "high",
                SOURCE_PAS_RUN_ID,
                "malf-run-002",
                "alpha-pas-rule-v1",
                "alpha-pas-schema-v1",
                "trace-b",
                '{"pas":"lineage-b"}',
                SIGNAL_PAS_EXECUTION_HINT,
                SIGNAL_PAS_EXECUTION_TRADE_DATE_POLICY,
                SIGNAL_PAS_EXECUTION_PRICE_FIELD,
                "handoff_only",
                "candidate-002",
                "2026-05-14 00:00:00",
            ),
            (
                "000002.SZ",
                "day",
                "2024-01-04",
                "2024-01-05",
                "PB",
                "invalidated",
                "context_ok",
                "none",
                "invalidated",
                "low",
                0.13,
                "low",
                SOURCE_PAS_RUN_ID,
                "malf-run-003",
                "alpha-pas-rule-v1",
                "alpha-pas-schema-v1",
                "trace-c",
                '{"pas":"lineage-c"}',
                SIGNAL_PAS_EXECUTION_HINT,
                SIGNAL_PAS_EXECUTION_TRADE_DATE_POLICY,
                SIGNAL_PAS_EXECUTION_PRICE_FIELD,
                "handoff_only",
                "candidate-003",
                "2026-05-14 00:00:00",
            ),
            (
                "000003.SZ",
                "day",
                "2024-01-04",
                "2024-01-05",
                "CPB",
                "waiting",
                "context_ok",
                "none",
                "waiting",
                "low",
                0.11,
                "low",
                SOURCE_PAS_RUN_ID,
                "malf-run-004",
                "alpha-pas-rule-v1",
                "alpha-pas-schema-v1",
                "trace-d",
                '{"pas":"lineage-d"}',
                SIGNAL_PAS_EXECUTION_HINT,
                SIGNAL_PAS_EXECUTION_TRADE_DATE_POLICY,
                SIGNAL_PAS_EXECUTION_PRICE_FIELD,
                "handoff_only",
                "candidate-004",
                "2026-05-14 00:00:00",
            ),
            (
                "000004.SZ",
                "day",
                "2024-01-04",
                "2024-01-05",
                "BPB",
                "cancelled",
                "context_ok",
                "none",
                "cancelled",
                "low",
                0.10,
                "low",
                SOURCE_PAS_RUN_ID,
                "malf-run-005",
                "alpha-pas-rule-v1",
                "alpha-pas-schema-v1",
                "trace-e",
                '{"pas":"lineage-e"}',
                SIGNAL_PAS_EXECUTION_HINT,
                SIGNAL_PAS_EXECUTION_TRADE_DATE_POLICY,
                SIGNAL_PAS_EXECUTION_PRICE_FIELD,
                "handoff_only",
                "candidate-005",
                "2026-05-14 00:00:00",
            ),
            (
                "000005.SZ",
                "day",
                "2024-01-04",
                "2024-01-05",
                "BOF",
                "modified",
                "context_ok",
                "none",
                "modified",
                "low",
                0.12,
                "low",
                SOURCE_PAS_RUN_ID,
                "malf-run-006",
                "alpha-pas-rule-v1",
                "alpha-pas-schema-v1",
                "trace-f",
                '{"pas":"lineage-f"}',
                SIGNAL_PAS_EXECUTION_HINT,
                SIGNAL_PAS_EXECUTION_TRADE_DATE_POLICY,
                SIGNAL_PAS_EXECUTION_PRICE_FIELD,
                "handoff_only",
                "candidate-006",
                "2026-05-14 00:00:00",
            ),
        ]
        placeholders = ", ".join(["?"] * 24)
        con.executemany(f"insert into pas_entry_candidate values ({placeholders})", rows)


def test_alignment_generates_active_signal_and_preserves_pas_snapshot(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path)
    _seed_pas_db(request.source_pas_db)

    summary = run_signal_pas_alignment(request)

    assert summary.input_candidate_count == 6
    assert summary.active_candidate_count == 2
    assert summary.formal_signal_count == 1
    assert summary.hard_fail_count == 0
    with duckdb.connect(str(request.output_db_path), read_only=True) as con:
        snapshot_count = con.execute("select count(*) from signal_pas_input_snapshot").fetchone()[0]
        formal_rows = con.execute(
            """
            select symbol, signal_date, signal_strength, signal_family,
                   source_run_id, source_pas_run_id, lineage, execution_hint,
                   execution_trade_date_policy, execution_price_field
            from signal_pas_formal_signal
            """
        ).fetchall()
        component_count = con.execute(
            "select count(*) from signal_pas_component_ledger"
        ).fetchone()[0]

    assert snapshot_count == 6
    assert component_count == 2
    assert len(formal_rows) == 1
    assert formal_rows[0][:6] == (
        "000001.SZ",
        date(2024, 1, 3),
        0.84,
        "BOF+TST",
        RUN_ID,
        SOURCE_PAS_RUN_ID,
    )
    assert formal_rows[0][7:] == (
        SIGNAL_PAS_EXECUTION_HINT,
        SIGNAL_PAS_EXECUTION_TRADE_DATE_POLICY,
        SIGNAL_PAS_EXECUTION_PRICE_FIELD,
    )
    lineage = json.loads(formal_rows[0][6])
    assert lineage["candidate_ids"] == ["candidate-001", "candidate-002"]
    assert lineage["malf_wave_position_run_ids"] == ["malf-run-001", "malf-run-002"]
    assert lineage["source_concept_trace"] == ["trace-a", "trace-b"]


def test_alignment_output_contract_fields_and_forbidden_fields(tmp_path: Path) -> None:
    request = _request(tmp_path)
    _seed_pas_db(request.source_pas_db)

    summary = run_signal_pas_alignment(request)

    assert summary.status == "completed"
    with duckdb.connect(str(request.output_db_path), read_only=True) as con:
        formal_columns = {
            str(row[1])
            for row in con.execute("pragma table_info(signal_pas_formal_signal)").fetchall()
        }
    assert formal_columns >= SIGNAL_PAS_REQUIRED_OUTPUT_FIELDS
    assert SIGNAL_PAS_FORBIDDEN_OUTPUT_FIELDS.isdisjoint(formal_columns)
    coverage = json.loads((request.report_dir / "contract-coverage.json").read_text())
    assert coverage["required_fields_missing"] == []
    assert coverage["forbidden_fields_present"] == []


def test_alignment_rejects_formal_output_root_and_non_day_timeframe(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="formal output"):
        _request(tmp_path, formal_output_root=Path("H:/Asteria-data"))

    with pytest.raises(ValueError, match="day"):
        _request(tmp_path, timeframe="week")
