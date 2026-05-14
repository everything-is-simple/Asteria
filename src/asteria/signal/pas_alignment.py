from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, SupportsFloat

import duckdb

from asteria.signal.pas_artifacts import (
    contract_coverage,
    write_alignment_db,
    write_report_files,
    write_validated_zip,
)
from asteria.signal.pas_contracts import (
    SIGNAL_PAS_ACTIVE_STATES,
    SIGNAL_PAS_EXECUTION_HINT,
    SIGNAL_PAS_EXECUTION_PRICE_FIELD,
    SIGNAL_PAS_EXECUTION_TRADE_DATE_POLICY,
    SIGNAL_PAS_REQUIRED_INPUT_FIELDS,
    SIGNAL_PAS_REQUIRED_OUTPUT_FIELDS,
    SIGNAL_PAS_RULE_VERSION,
    SIGNAL_PAS_SCHEMA_VERSION,
)

REPORT_DATE = "2026-05-14"
FORMAL_DATA_ROOT = Path("H:/Asteria-data")


@dataclass(frozen=True)
class SignalPasAlignmentRequest:
    source_pas_db: Path
    temp_root: Path
    report_root: Path
    validated_root: Path
    run_id: str
    source_pas_run_id: str
    mode: str = "bounded"
    timeframe: str = "day"
    schema_version: str = SIGNAL_PAS_SCHEMA_VERSION
    signal_rule_version: str = SIGNAL_PAS_RULE_VERSION
    formal_output_root: Path | None = None

    def __post_init__(self) -> None:
        if self.mode != "bounded":
            raise ValueError("Signal/PAS alignment only allows bounded mode.")
        if self.timeframe != "day":
            raise ValueError("Signal/PAS alignment only allows day timeframe.")
        if not self.source_pas_run_id:
            raise ValueError("source_pas_run_id is required.")
        if self.formal_output_root is not None:
            raise ValueError("formal output root is not allowed for this card.")
        for name, path in (
            ("temp_root", self.temp_root),
            ("report_root", self.report_root),
            ("validated_root", self.validated_root),
        ):
            if _is_under_formal_data_root(path):
                raise ValueError(f"{name} must not be under H:/Asteria-data.")

    @property
    def run_root(self) -> Path:
        return self.temp_root / "signal_pas" / self.run_id

    @property
    def output_db_path(self) -> Path:
        return self.run_root / "signal_pas_alignment.duckdb"

    @property
    def report_dir(self) -> Path:
        return self.report_root / "pipeline" / REPORT_DATE / self.run_id

    @property
    def validated_zip_path(self) -> Path:
        return self.validated_root / f"Asteria-{self.run_id}.zip"


@dataclass(frozen=True)
class PasEntryCandidate:
    symbol: str
    timeframe: str
    setup_date: date
    signal_date: date
    setup_family: str
    candidate_state: str
    context_reason_code: str
    trigger_reason_code: str
    failure_reason_code: str
    confidence: str
    strength_score: float
    strength_bucket: str
    source_run_id: str
    malf_wave_position_run_id: str
    rule_version: str
    schema_version: str
    source_concept_trace: str
    lineage: str
    execution_hint: str
    execution_trade_date_policy: str
    execution_price_field: str
    candidate_id: str


@dataclass(frozen=True)
class SignalPasAlignmentSummary:
    run_id: str
    status: str
    mode: str
    timeframe: str
    schema_version: str
    signal_rule_version: str
    source_pas_db: str
    source_pas_run_id: str
    input_candidate_count: int
    active_candidate_count: int
    formal_signal_count: int
    component_count: int
    hard_fail_count: int
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


def run_signal_pas_alignment(
    request: SignalPasAlignmentRequest,
) -> SignalPasAlignmentSummary:
    created_at = _utc_now()
    rows = _load_pas_candidates(request)
    payload = _build_payload(rows, request, created_at)
    request.run_root.mkdir(parents=True, exist_ok=True)
    request.report_dir.mkdir(parents=True, exist_ok=True)
    write_alignment_db(request.output_db_path, payload)
    coverage = contract_coverage(request.output_db_path)
    audit = _audit_summary(request, rows, payload, coverage)
    hard_fail_count = int(audit["hard_fail_count"])
    summary = SignalPasAlignmentSummary(
        run_id=request.run_id,
        status="completed" if hard_fail_count == 0 else "failed",
        mode=request.mode,
        timeframe=request.timeframe,
        schema_version=request.schema_version,
        signal_rule_version=request.signal_rule_version,
        source_pas_db=str(request.source_pas_db),
        source_pas_run_id=request.source_pas_run_id,
        input_candidate_count=len(rows),
        active_candidate_count=len(_active_candidates(rows)),
        formal_signal_count=len(payload["signal_pas_formal_signal"]),
        component_count=len(payload["signal_pas_component_ledger"]),
        hard_fail_count=hard_fail_count,
        output_db_path=request.output_db_path,
        report_dir=request.report_dir,
        validated_zip_path=request.validated_zip_path,
    )
    write_report_files(
        request=request,
        summary=summary,
        coverage=coverage,
        lineage=_lineage_summary(request, payload),
        audit=audit,
    )
    write_validated_zip(request)
    return summary


def _load_pas_candidates(request: SignalPasAlignmentRequest) -> list[PasEntryCandidate]:
    if not request.source_pas_db.exists():
        raise FileNotFoundError(f"source PAS DB not found: {request.source_pas_db}")
    with duckdb.connect(str(request.source_pas_db), read_only=True) as con:
        tables = {str(row[0]) for row in con.execute("show tables").fetchall()}
        if "pas_entry_candidate" not in tables:
            raise ValueError("source PAS DB must contain pas_entry_candidate.")
        columns = {
            str(row[1]) for row in con.execute("pragma table_info(pas_entry_candidate)").fetchall()
        }
        missing = SIGNAL_PAS_REQUIRED_INPUT_FIELDS - columns
        if missing:
            raise ValueError(f"PAS source missing required fields: {sorted(missing)}")
        query = """
            select symbol, timeframe, setup_date, signal_date, setup_family,
                   candidate_state, context_reason_code, trigger_reason_code,
                   failure_reason_code, confidence, strength_score,
                   strength_bucket, source_run_id, malf_wave_position_run_id,
                   rule_version, schema_version, source_concept_trace, lineage,
                   execution_hint, execution_trade_date_policy,
                   execution_price_field, candidate_id
            from pas_entry_candidate
            where timeframe = ? and source_run_id = ?
            order by symbol, timeframe, signal_date, setup_family, candidate_id
        """
        raw_rows = con.execute(query, (request.timeframe, request.source_pas_run_id)).fetchall()
    return [_candidate_from_row(row) for row in raw_rows]


def _candidate_from_row(row: tuple[object, ...]) -> PasEntryCandidate:
    return PasEntryCandidate(
        symbol=str(row[0]),
        timeframe=str(row[1]),
        setup_date=_as_date(row[2]),
        signal_date=_as_date(row[3]),
        setup_family=str(row[4]),
        candidate_state=str(row[5]),
        context_reason_code=str(row[6]),
        trigger_reason_code=str(row[7]),
        failure_reason_code=str(row[8]),
        confidence=str(row[9]),
        strength_score=_as_float(row[10]),
        strength_bucket=str(row[11]),
        source_run_id=str(row[12]),
        malf_wave_position_run_id=str(row[13]),
        rule_version=str(row[14]),
        schema_version=str(row[15]),
        source_concept_trace=str(row[16]),
        lineage=str(row[17]),
        execution_hint=str(row[18]),
        execution_trade_date_policy=str(row[19]),
        execution_price_field=str(row[20]),
        candidate_id=str(row[21]),
    )


def _build_payload(
    rows: list[PasEntryCandidate],
    request: SignalPasAlignmentRequest,
    created_at: datetime,
) -> dict[str, list[tuple[object, ...]]]:
    active_rows = _active_candidates(rows)
    groups: dict[tuple[str, str, date], list[PasEntryCandidate]] = defaultdict(list)
    for row in active_rows:
        groups[(row.symbol, row.timeframe, row.signal_date)].append(row)

    formal_rows: list[tuple[object, ...]] = []
    component_rows: list[tuple[object, ...]] = []
    for (symbol, timeframe, signal_date), candidates in sorted(groups.items()):
        families = sorted({candidate.setup_family for candidate in candidates})
        signal_family = "+".join(families)
        signal_id = "|".join(
            [
                request.run_id,
                symbol,
                timeframe,
                signal_date.isoformat(),
                signal_family,
                request.signal_rule_version,
            ]
        )
        lineage = _signal_lineage(candidates, request)
        rule_versions = sorted({candidate.rule_version for candidate in candidates})
        formal_rows.append(
            (
                signal_id,
                symbol,
                timeframe,
                signal_date,
                "pas_aligned_opportunity",
                "active",
                max(candidate.strength_score for candidate in candidates),
                signal_family,
                request.run_id,
                request.source_pas_run_id,
                request.schema_version,
                request.signal_rule_version,
                "+".join(rule_versions),
                json.dumps(lineage, ensure_ascii=False, sort_keys=True),
                SIGNAL_PAS_EXECUTION_HINT,
                SIGNAL_PAS_EXECUTION_TRADE_DATE_POLICY,
                SIGNAL_PAS_EXECUTION_PRICE_FIELD,
                len(candidates),
                created_at,
            )
        )
        for index, candidate in enumerate(candidates, start=1):
            component_rows.append(
                (
                    f"{signal_id}|component|{index}",
                    signal_id,
                    candidate.candidate_id,
                    candidate.symbol,
                    candidate.timeframe,
                    candidate.signal_date,
                    candidate.setup_family,
                    candidate.candidate_state,
                    "support",
                    candidate.strength_score,
                    candidate.source_run_id,
                    candidate.malf_wave_position_run_id,
                    candidate.source_concept_trace,
                    candidate.lineage,
                    created_at,
                )
            )

    return {
        "signal_pas_input_snapshot": [
            _input_snapshot_row(row, request, created_at) for row in rows
        ],
        "signal_pas_formal_signal": formal_rows,
        "signal_pas_component_ledger": component_rows,
        "signal_pas_audit": _audit_rows(rows, formal_rows, request, created_at),
    }


def _input_snapshot_row(
    row: PasEntryCandidate,
    request: SignalPasAlignmentRequest,
    created_at: datetime,
) -> tuple[object, ...]:
    return (
        row.candidate_id,
        row.symbol,
        row.timeframe,
        row.setup_date,
        row.signal_date,
        row.setup_family,
        row.candidate_state,
        row.context_reason_code,
        row.trigger_reason_code,
        row.failure_reason_code,
        row.confidence,
        row.strength_score,
        row.strength_bucket,
        row.source_run_id,
        row.malf_wave_position_run_id,
        row.rule_version,
        row.schema_version,
        row.source_concept_trace,
        row.lineage,
        row.execution_hint,
        row.execution_trade_date_policy,
        row.execution_price_field,
        str(request.source_pas_db),
        request.run_id,
        created_at,
    )


def _active_candidates(rows: list[PasEntryCandidate]) -> list[PasEntryCandidate]:
    return [row for row in rows if row.candidate_state in SIGNAL_PAS_ACTIVE_STATES]


def _signal_lineage(
    candidates: list[PasEntryCandidate],
    request: SignalPasAlignmentRequest,
) -> dict[str, object]:
    return {
        "source": "Alpha/PAS v1.0 bounded proof",
        "source_pas_run_id": request.source_pas_run_id,
        "candidate_ids": [candidate.candidate_id for candidate in candidates],
        "pas_source_run_ids": sorted({candidate.source_run_id for candidate in candidates}),
        "malf_wave_position_run_ids": [
            candidate.malf_wave_position_run_id for candidate in candidates
        ],
        "source_concept_trace": [candidate.source_concept_trace for candidate in candidates],
        "pas_lineage": [candidate.lineage for candidate in candidates],
    }


def _audit_rows(
    rows: list[PasEntryCandidate],
    formal_rows: list[tuple[object, ...]],
    request: SignalPasAlignmentRequest,
    created_at: datetime,
) -> list[tuple[object, ...]]:
    checks = [
        ("input_candidate_count", len(rows) > 0, {"count": len(rows)}),
        (
            "formal_signal_count",
            len(formal_rows) > 0,
            {"count": len(formal_rows), "active_states": sorted(SIGNAL_PAS_ACTIVE_STATES)},
        ),
        (
            "execution_hint_locked",
            all(row.execution_hint == SIGNAL_PAS_EXECUTION_HINT for row in rows),
            {"expected": SIGNAL_PAS_EXECUTION_HINT},
        ),
        (
            "source_pas_run_locked",
            all(row.source_run_id == request.source_pas_run_id for row in rows),
            {"source_pas_run_id": request.source_pas_run_id},
        ),
        (
            "formal_output_fields_planned",
            True,
            {"required_fields": sorted(SIGNAL_PAS_REQUIRED_OUTPUT_FIELDS)},
        ),
    ]
    return [
        (
            f"{request.run_id}|audit|{index}",
            request.run_id,
            name,
            "hard" if not passed else "info",
            "passed" if passed else "failed",
            0 if passed else 1,
            json.dumps(payload, ensure_ascii=False, sort_keys=True),
            created_at,
        )
        for index, (name, passed, payload) in enumerate(checks, start=1)
    ]


def _audit_summary(
    request: SignalPasAlignmentRequest,
    rows: list[PasEntryCandidate],
    payload: dict[str, list[tuple[object, ...]]],
    coverage: dict[str, Any],
) -> dict[str, Any]:
    table_failures = sum(
        _as_int(row[5]) for row in payload["signal_pas_audit"] if str(row[3]) == "hard"
    )
    coverage_failures = len(coverage["required_fields_missing"]) + len(
        coverage["forbidden_fields_present"]
    )
    return {
        "run_id": request.run_id,
        "source_pas_run_id": request.source_pas_run_id,
        "input_candidate_count": len(rows),
        "active_candidate_count": len(_active_candidates(rows)),
        "formal_signal_count": len(payload["signal_pas_formal_signal"]),
        "component_count": len(payload["signal_pas_component_ledger"]),
        "formal_data_mutation": "no",
        "required_fields_missing": coverage["required_fields_missing"],
        "forbidden_fields_present": coverage["forbidden_fields_present"],
        "hard_fail_count": table_failures + coverage_failures,
    }


def _lineage_summary(
    request: SignalPasAlignmentRequest,
    payload: dict[str, list[tuple[object, ...]]],
) -> dict[str, Any]:
    lineage_payloads = [json.loads(str(row[13])) for row in payload["signal_pas_formal_signal"]]
    candidate_ids = sorted(
        {candidate_id for lineage in lineage_payloads for candidate_id in lineage["candidate_ids"]}
    )
    malf_run_ids = sorted(
        {
            malf_run_id
            for lineage in lineage_payloads
            for malf_run_id in lineage["malf_wave_position_run_ids"]
        }
    )
    return {
        "run_id": request.run_id,
        "source_pas_db": str(request.source_pas_db),
        "source_pas_run_id": request.source_pas_run_id,
        "formal_signal_count": len(lineage_payloads),
        "candidate_ids_traced": candidate_ids,
        "malf_wave_position_run_ids_traced": malf_run_ids,
    }


def _as_date(value: object) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _as_float(value: object) -> float:
    if value is None:
        return 0.0
    if isinstance(value, SupportsFloat):
        return float(value)
    return float(str(value))


def _as_int(value: object) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    return int(str(value))


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _is_under_formal_data_root(path: Path) -> bool:
    try:
        resolved = path.resolve()
        formal_root = FORMAL_DATA_ROOT.resolve()
    except OSError:
        resolved = path.absolute()
        formal_root = FORMAL_DATA_ROOT.absolute()
    resolved_text = str(resolved).replace("\\", "/").lower()
    formal_text = str(formal_root).replace("\\", "/").lower()
    return resolved_text == formal_text or resolved_text.startswith(f"{formal_text}/")
