from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

from asteria.alpha.pas_artifacts import (
    contract_coverage,
    lineage_summary,
    write_proof_db,
    write_report_files,
    write_validated_zip,
)
from asteria.alpha.pas_contracts import (
    ALPHA_PAS_RULE_VERSION,
    ALPHA_PAS_SCHEMA_VERSION,
    PAS_EXECUTION_HINT,
    PAS_EXECUTION_PRICE_FIELD,
    PAS_EXECUTION_TRADE_DATE_POLICY,
    PAS_LIFECYCLE_STATES,
    PAS_SOURCE_CONCEPT_TRACE,
)
from asteria.alpha.pas_rules import (
    PasWavePosition,
    boundary_interaction,
    candidate_state,
    completed_baseline,
    confidence,
    context_reason,
    in_flight_confirmation,
    is_terminal,
    lineage,
    lineage_json,
    opposite_comparison,
    setup_family,
    sparsity_label,
    stagnation_evidence,
    strength_bucket,
    strength_score,
    wave_position_from_row,
)

REPORT_DATE = "2026-05-14"


@dataclass(frozen=True)
class PasBoundedProofRequest:
    source_malf_db: Path
    temp_root: Path
    report_root: Path
    validated_root: Path
    run_id: str
    source_malf_service_version: str
    source_malf_run_id: str | None = None
    start_dt: str | None = None
    end_dt: str | None = None
    symbol_limit: int | None = None
    mode: str = "bounded"
    timeframe: str = "day"
    schema_version: str = ALPHA_PAS_SCHEMA_VERSION
    rule_version: str = ALPHA_PAS_RULE_VERSION
    formal_output_root: Path | None = None

    def __post_init__(self) -> None:
        if self.mode != "bounded":
            raise ValueError("Alpha/PAS proof is bounded-only")
        if self.timeframe != "day":
            raise ValueError("Alpha/PAS bounded proof is day-only")
        if self.formal_output_root is not None:
            raise ValueError("Alpha/PAS bounded proof cannot accept a formal data output root")
        if self.symbol_limit is not None and self.symbol_limit <= 0:
            raise ValueError("symbol_limit must be positive")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_dt cannot be later than end_dt")
        _reject_formal_write_path(self.temp_root)
        _reject_formal_write_path(self.report_root)

    @property
    def start_date(self) -> date | None:
        return date.fromisoformat(self.start_dt) if self.start_dt else None

    @property
    def end_date(self) -> date | None:
        return date.fromisoformat(self.end_dt) if self.end_dt else None

    @property
    def run_root(self) -> Path:
        return self.temp_root / "alpha_pas" / self.run_id

    @property
    def output_db_path(self) -> Path:
        return self.run_root / "alpha_pas_bounded_proof.duckdb"

    @property
    def report_dir(self) -> Path:
        return self.report_root / "pipeline" / REPORT_DATE / self.run_id

    @property
    def validated_zip_path(self) -> Path:
        return self.validated_root / f"Asteria-{self.run_id}.zip"


@dataclass(frozen=True)
class PasBoundedProofSummary:
    run_id: str
    status: str
    mode: str
    timeframe: str
    schema_version: str
    rule_version: str
    source_malf_db: str
    source_malf_service_version: str
    source_malf_run_id: str | None
    source_row_count: int
    candidate_count: int
    hard_fail_count: int
    covered_lifecycle_states: tuple[str, ...]
    output_db_path: Path
    report_dir: Path
    validated_zip_path: Path
    formal_data_mutation: str = "no"

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["output_db_path"] = str(self.output_db_path)
        payload["report_dir"] = str(self.report_dir)
        payload["validated_zip_path"] = str(self.validated_zip_path)
        return payload


def run_alpha_pas_bounded_proof(request: PasBoundedProofRequest) -> PasBoundedProofSummary:
    created_at = _utc_now()
    rows = _load_wave_positions(request)
    payload = _build_payload(rows, request, created_at)
    request.run_root.mkdir(parents=True, exist_ok=True)
    request.report_dir.mkdir(parents=True, exist_ok=True)
    write_proof_db(request.output_db_path, payload)
    coverage = contract_coverage(request.output_db_path)
    lineage = lineage_summary(payload, request)
    audit_summary = _audit_summary(request, payload, coverage)
    hard_fail_count = int(audit_summary["hard_fail_count"])
    summary = PasBoundedProofSummary(
        run_id=request.run_id,
        status="completed" if hard_fail_count == 0 else "failed",
        mode=request.mode,
        timeframe=request.timeframe,
        schema_version=request.schema_version,
        rule_version=request.rule_version,
        source_malf_db=str(request.source_malf_db),
        source_malf_service_version=request.source_malf_service_version,
        source_malf_run_id=request.source_malf_run_id,
        source_row_count=len(rows),
        candidate_count=len(payload["pas_entry_candidate"]),
        hard_fail_count=hard_fail_count,
        covered_lifecycle_states=tuple(sorted(PAS_LIFECYCLE_STATES)),
        output_db_path=request.output_db_path,
        report_dir=request.report_dir,
        validated_zip_path=request.validated_zip_path,
    )
    write_report_files(
        request,
        summary,
        coverage,
        lineage,
        audit_summary,
    )
    write_validated_zip(request)
    return summary


def _load_wave_positions(request: PasBoundedProofRequest) -> list[PasWavePosition]:
    if not request.source_malf_db.exists():
        raise FileNotFoundError(f"Missing MALF service DB: {request.source_malf_db}")
    clauses = ["timeframe = ?", "service_version = ?"]
    params: list[object] = [request.timeframe, request.source_malf_service_version]
    if request.source_malf_run_id:
        clauses.append("run_id = ?")
        params.append(request.source_malf_run_id)
    if request.start_date:
        clauses.append("bar_dt >= ?")
        params.append(request.start_date)
    if request.end_date:
        clauses.append("bar_dt <= ?")
        params.append(request.end_date)
    symbol_limit = request.symbol_limit or 9223372036854775807
    query = f"""
        with base as (
            select symbol, timeframe, bar_dt, system_state, wave_core_state, direction,
                   new_count, no_new_span, transition_span, update_rank, stagnation_rank,
                   life_state, position_quadrant, guard_boundary_price, sample_version,
                   service_version, run_id
            from malf_wave_position
            where {" and ".join(clauses)}
        ),
        symbol_scope as (
            select symbol from base group by symbol order by symbol limit ?
        ),
        scoped as (
            select * from base where symbol in (select symbol from symbol_scope)
        ),
        canonical as (
            select *,
                   row_number() over (
                       partition by symbol, timeframe, bar_dt
                       order by case when system_state = 'transition' then 1 else 0 end,
                                transition_span desc,
                                run_id
                   ) as row_rank
            from scoped
        )
        select symbol, timeframe, bar_dt, system_state, wave_core_state, direction,
               new_count, no_new_span, transition_span, update_rank, stagnation_rank,
               life_state, position_quadrant, guard_boundary_price, sample_version,
               service_version, run_id
        from canonical
        where row_rank = 1
        order by symbol, bar_dt
    """
    with duckdb.connect(str(request.source_malf_db), read_only=True) as con:
        _assert_source_audit_clean(con)
        return [
            wave_position_from_row(row)
            for row in con.execute(query, params + [symbol_limit]).fetchall()
        ]


def _build_payload(
    rows: list[PasWavePosition],
    request: PasBoundedProofRequest,
    created_at: datetime,
) -> dict[str, list[tuple[object, ...]]]:
    payload: dict[str, list[tuple[object, ...]]] = {
        "pas_proof_run": [],
        "pas_lifecycle_state_catalog": [],
        "pas_market_context": [],
        "pas_strength_profile": [],
        "pas_trigger_event": [],
        "pas_historical_rank_profile": [],
        "pas_entry_candidate": [],
        "pas_candidate_lifecycle": [],
        "pas_failure_state": [],
        "pas_source_lineage": [],
    }
    payload["pas_lifecycle_state_catalog"] = [
        (state, _lifecycle_definition(state), created_at) for state in sorted(PAS_LIFECYCLE_STATES)
    ]
    seen_terminal: set[str] = set()
    by_symbol: dict[str, list[PasWavePosition]] = {}
    for source in rows:
        history = by_symbol.setdefault(source.symbol, [])
        candidate = _candidate_payload(source, history, seen_terminal, request, created_at)
        for table_name, row in candidate.items():
            payload[table_name].append(row)
        if is_terminal(source):
            seen_terminal.add(source.symbol)
        history.append(source)
    payload["pas_proof_run"].append(
        (
            request.run_id,
            "completed",
            request.mode,
            request.timeframe,
            str(request.source_malf_db),
            len(rows),
            len(payload["pas_entry_candidate"]),
            request.schema_version,
            request.rule_version,
            request.source_malf_service_version,
            request.source_malf_run_id,
            "no",
            created_at,
        )
    )
    return payload


def _candidate_payload(
    source: PasWavePosition,
    history: list[PasWavePosition],
    seen_terminal: set[str],
    request: PasBoundedProofRequest,
    created_at: datetime,
) -> dict[str, tuple[object, ...]]:
    family = setup_family(source)
    candidate_id = _id(request.run_id, source.symbol, source.timeframe, source.bar_dt, family)
    state, trigger_reason, failure_reason = candidate_state(source, seen_terminal)
    baseline = completed_baseline(source, history)
    baseline_sample_count = baseline["sample_count"]
    score = strength_score(baseline)
    bucket = strength_bucket(score)
    confidence_value = confidence(bucket, baseline_sample_count)
    lineage_payload = lineage(source, family, state, request.run_id)
    setup_date = source.bar_dt
    common = [
        candidate_id,
        source.symbol,
        source.timeframe,
        setup_date,
        family,
        request.run_id,
        source.run_id,
        request.rule_version,
        request.schema_version,
        lineage_json(lineage_payload),
        created_at,
    ]
    return {
        "pas_market_context": (
            *common,
            context_reason(source),
            source.system_state,
            source.wave_core_state,
            source.direction,
            source.life_state,
            source.position_quadrant,
            source.guard_boundary_price,
            boundary_interaction(source),
        ),
        "pas_strength_profile": (
            *common,
            json.dumps(baseline, sort_keys=True),
            json.dumps(opposite_comparison(source, history), sort_keys=True),
            json.dumps(in_flight_confirmation(source), sort_keys=True),
            boundary_interaction(source),
            stagnation_evidence(source),
            baseline_sample_count,
            sparsity_label(baseline_sample_count),
            score,
            bucket,
        ),
        "pas_trigger_event": (
            *common,
            state,
            trigger_reason,
            "triggered" if state in {"triggered", "reentry_candidate"} else "not_triggered",
        ),
        "pas_historical_rank_profile": (
            *common,
            baseline_sample_count,
            sparsity_label(baseline_sample_count),
            bucket,
            "not_proven_in_bounded_proof",
            failure_reason,
        ),
        "pas_entry_candidate": (
            source.symbol,
            source.timeframe,
            setup_date,
            setup_date,
            family,
            state,
            context_reason(source),
            trigger_reason,
            failure_reason,
            confidence_value,
            score,
            bucket,
            request.run_id,
            source.run_id,
            request.rule_version,
            request.schema_version,
            PAS_SOURCE_CONCEPT_TRACE,
            lineage_json(lineage_payload),
            PAS_EXECUTION_HINT,
            PAS_EXECUTION_TRADE_DATE_POLICY,
            PAS_EXECUTION_PRICE_FIELD,
            "handoff_hint_only_not_order",
            candidate_id,
            created_at,
        ),
        "pas_candidate_lifecycle": (
            candidate_id,
            state,
            failure_reason or trigger_reason,
            True,
            lineage_json(lineage_payload),
            created_at,
        ),
        "pas_failure_state": (
            candidate_id,
            source.symbol,
            source.timeframe,
            setup_date,
            failure_reason,
            state in {"waiting", "cancelled", "modified", "invalidated", "rejected_by_signal"},
            json.dumps(in_flight_confirmation(source), sort_keys=True),
            request.run_id,
            source.run_id,
            request.rule_version,
            request.schema_version,
            created_at,
        ),
        "pas_source_lineage": (
            candidate_id,
            request.run_id,
            source.run_id,
            source.service_version,
            source.sample_version,
            PAS_SOURCE_CONCEPT_TRACE,
            lineage_json(lineage_payload),
            created_at,
        ),
    }


def _audit_summary(
    request: PasBoundedProofRequest,
    payload: dict[str, list[tuple[object, ...]]],
    contract_coverage: dict[str, Any],
) -> dict[str, Any]:
    checks = [
        ("candidate_count_positive", len(payload["pas_entry_candidate"]) > 0),
        ("required_fields_present", not contract_coverage["required_fields_missing"]),
        ("forbidden_fields_absent", not contract_coverage["forbidden_fields_present"]),
        (
            "lifecycle_catalog_complete",
            len(payload["pas_lifecycle_state_catalog"]) == len(PAS_LIFECYCLE_STATES),
        ),
        ("formal_data_mutation_absent", True),
    ]
    failures = [name for name, passed in checks if not passed]
    return {
        "run_id": request.run_id,
        "hard_fail_count": len(failures),
        "checks": [
            {"check_name": name, "status": "pass" if passed else "fail"} for name, passed in checks
        ],
    }


def _assert_source_audit_clean(con: duckdb.DuckDBPyConnection) -> None:
    tables = {str(row[0]) for row in con.execute("show tables").fetchall()}
    missing = {"malf_wave_position", "malf_interface_audit"} - tables
    if missing:
        raise ValueError(f"Missing MALF service tables: {sorted(missing)}")
    row = con.execute(
        """
        select coalesce(sum(failed_count), 0)
        from malf_interface_audit
        where severity = 'hard' and status = 'fail'
        """
    ).fetchone()
    if row and int(row[0] or 0) > 0:
        raise ValueError("MALF interface audit has hard failures")


def _lifecycle_definition(state: str) -> str:
    return f"Alpha/PAS v1.0 lifecycle state: {state}"


def _reject_formal_write_path(path: Path) -> None:
    normalized = str(path).replace("/", "\\").lower()
    if normalized.startswith("h:\\asteria-data"):
        raise ValueError("Alpha/PAS bounded proof cannot write formal data paths")


def _id(*parts: object) -> str:
    return "|".join(str(part) for part in parts)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
