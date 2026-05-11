from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import duckdb

from asteria.alpha.bootstrap import ALPHA_FAMILIES, ALPHA_FAMILY_DATABASES, run_alpha_family_build
from asteria.alpha.contracts import (
    AlphaDailyIncrementalLedgerRequest,
    AlphaDailyIncrementalLedgerSummary,
    AlphaFamilyRequest,
)
from asteria.build_orchestration import BatchLedgerEntry, build_symbol_batches, completed_batch_ids
from asteria.build_orchestration.ledger import append_batch_ledger, utc_now_iso, write_checkpoint

ALPHA_DAILY_INCREMENTAL_CARD = "alpha-signal-daily-incremental-ledger-build-card"


@dataclass(frozen=True)
class ReplayScopeEntry:
    symbol: str
    timeframe: str
    source_run_id: str
    source_malf_run_id: str
    target_start_dt: str
    target_end_dt: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def run_alpha_daily_incremental_ledger(
    request: AlphaDailyIncrementalLedgerRequest,
) -> AlphaDailyIncrementalLedgerSummary:
    request.run_root.mkdir(parents=True, exist_ok=True)
    request.report_dir.mkdir(parents=True, exist_ok=True)

    completed = _load_completed_summary(request)
    if completed:
        return completed

    malf_checkpoint = _load_json(request.malf_checkpoint_path)
    if malf_checkpoint.get("status") != "completed":
        raise ValueError("Alpha daily incremental requires completed MALF daily checkpoint")

    malf_impact_scope = _load_json(request.malf_daily_impact_scope_path)
    malf_lineage = _load_json(request.malf_lineage_path)
    replay_scopes = _derive_replay_scopes(malf_impact_scope, malf_lineage)
    _write_source_manifest(request, malf_impact_scope, malf_checkpoint)
    _write_json(
        request.derived_replay_scope_path,
        {
            "run_id": request.run_id,
            "card_id": ALPHA_DAILY_INCREMENTAL_CARD,
            "schema_version": request.schema_version,
            "scope_count": len(replay_scopes),
            "scopes": [scope.as_dict() for scope in replay_scopes],
        },
    )

    if request.mode == "audit-only":
        _write_json(
            request.daily_impact_scope_path,
            {
                "run_id": request.run_id,
                "card_id": ALPHA_DAILY_INCREMENTAL_CARD,
                "schema_version": request.schema_version,
                "scope_count": 0,
                "scopes": [],
            },
        )
        _write_json(
            request.lineage_path,
            {
                "run_id": request.run_id,
                "card_id": ALPHA_DAILY_INCREMENTAL_CARD,
                "schema_version": request.schema_version,
                "lineage": [],
            },
        )
        audit_payload = _build_audit_summary(request, 0, [])
        _write_json(request.audit_summary_path, audit_payload)
        summary = AlphaDailyIncrementalLedgerSummary(
            run_id=request.run_id,
            status=audit_payload["status"],
            mode=request.mode,
            timeframe=request.timeframe,
            schema_version=request.schema_version,
            batch_count=0,
            replay_scope_count=len(replay_scopes),
            impact_scope_count=0,
            source_manifest_path=str(request.source_manifest_path),
            derived_replay_scope_path=str(request.derived_replay_scope_path),
            daily_impact_scope_path=str(request.daily_impact_scope_path),
            lineage_path=str(request.lineage_path),
            batch_ledger_path=str(request.batch_ledger_path),
            checkpoint_path=str(request.checkpoint_path),
            audit_summary_path=str(request.audit_summary_path),
        )
        _save_summary(request, summary)
        return summary

    scope_by_symbol = {scope.symbol: scope for scope in replay_scopes}
    batches = build_symbol_batches(tuple(sorted(scope_by_symbol)), batch_size=request.batch_size)
    promoted_batches = (
        completed_batch_ids(request.batch_ledger_path) if request.mode == "resume" else set()
    )
    impact_scope_rows: list[dict[str, str]] = []
    lineage_rows: list[dict[str, str]] = []

    for batch in batches:
        if batch.batch_id in promoted_batches:
            continue
        if len(batch.symbols) != 1:
            raise ValueError("Alpha daily incremental sample currently requires batch_size=1")
        scope = scope_by_symbol[batch.symbols[0]]
        append_batch_ledger(
            request.batch_ledger_path,
            BatchLedgerEntry(request.run_id, batch.batch_id, "running", started_at=utc_now_iso()),
        )
        try:
            family_summaries = []
            for family in ALPHA_FAMILIES:
                family_summary = run_alpha_family_build(
                    AlphaFamilyRequest(
                        source_malf_db=request.source_malf_root / "malf_service_day.duckdb",
                        target_alpha_db=request.target_root / ALPHA_FAMILY_DATABASES[family],
                        report_root=request.report_root,
                        validated_root=request.temp_root / "alpha-validated-placeholder",
                        temp_root=request.temp_root,
                        run_id=request.run_id,
                        mode="resume" if request.mode == "resume" else "daily_incremental",
                        alpha_family=family,
                        source_malf_service_version=_service_version_for_run(
                            request.source_malf_root / "malf_service_day.duckdb",
                            scope.source_malf_run_id,
                        ),
                        source_malf_run_id=scope.source_malf_run_id,
                        schema_version=request.schema_version,
                        alpha_rule_version=request.alpha_rule_version,
                        timeframe=request.timeframe,
                        start_dt=scope.target_start_dt,
                        end_dt=scope.target_end_dt,
                        symbol_limit=1,
                    )
                )
                family_summaries.append(family_summary)
                impact_scope_rows.extend(
                    _impact_scope_rows(
                        request.target_root / ALPHA_FAMILY_DATABASES[family],
                        request.run_id,
                        family,
                        scope.symbol,
                    )
                )
                lineage_rows.append(
                    {
                        "alpha_family": family,
                        "symbol": scope.symbol,
                        "timeframe": request.timeframe,
                        "source_run_id": request.run_id,
                        "source_malf_run_id": scope.source_malf_run_id,
                        "upstream_source_run_id": scope.source_run_id,
                        "target_run_id": request.run_id,
                    }
                )
            append_batch_ledger(
                request.batch_ledger_path,
                BatchLedgerEntry(
                    request.run_id,
                    batch.batch_id,
                    "promoted",
                    completed_at=utc_now_iso(),
                    promoted_at=utc_now_iso(),
                    row_counts={"impact_scope_count": len(impact_scope_rows)},
                    audit_summary_path=(
                        family_summaries[-1].report_path if family_summaries else None
                    ),
                ),
            )
        except Exception as exc:
            append_batch_ledger(
                request.batch_ledger_path,
                BatchLedgerEntry(
                    request.run_id,
                    batch.batch_id,
                    "failed",
                    completed_at=utc_now_iso(),
                    error=str(exc),
                ),
            )
            raise

    _write_json(
        request.daily_impact_scope_path,
        {
            "run_id": request.run_id,
            "card_id": ALPHA_DAILY_INCREMENTAL_CARD,
            "schema_version": request.schema_version,
            "protocol_fields": [
                "symbol",
                "trade_date",
                "timeframe",
                "upstream_module",
                "source_run_id",
                "alpha_family",
            ],
            "scope_count": len(impact_scope_rows),
            "scopes": impact_scope_rows,
        },
    )
    _write_json(
        request.lineage_path,
        {
            "run_id": request.run_id,
            "card_id": ALPHA_DAILY_INCREMENTAL_CARD,
            "schema_version": request.schema_version,
            "lineage": lineage_rows,
        },
    )
    audit_payload = _build_audit_summary(request, len(impact_scope_rows), lineage_rows)
    _write_json(request.audit_summary_path, audit_payload)
    summary = AlphaDailyIncrementalLedgerSummary(
        run_id=request.run_id,
        status=audit_payload["status"],
        mode=request.mode,
        timeframe=request.timeframe,
        schema_version=request.schema_version,
        batch_count=len(batches),
        replay_scope_count=len(replay_scopes),
        impact_scope_count=len(impact_scope_rows),
        source_manifest_path=str(request.source_manifest_path),
        derived_replay_scope_path=str(request.derived_replay_scope_path),
        daily_impact_scope_path=str(request.daily_impact_scope_path),
        lineage_path=str(request.lineage_path),
        batch_ledger_path=str(request.batch_ledger_path),
        checkpoint_path=str(request.checkpoint_path),
        audit_summary_path=str(request.audit_summary_path),
    )
    _save_summary(request, summary)
    return summary


def _derive_replay_scopes(
    impact_scope_payload: dict[str, Any],
    lineage_payload: dict[str, Any],
) -> list[ReplayScopeEntry]:
    lineage_by_source = {
        str(item["source_run_id"]): str(item["target_run_id"])
        for item in lineage_payload.get("lineage", [])
    }
    grouped: dict[str, dict[str, str]] = {}
    for item in impact_scope_payload.get("scopes", []):
        if str(item.get("timeframe")) != "day":
            continue
        symbol = str(item["symbol"])
        source_run_id = str(item["source_run_id"])
        source_malf_run_id = lineage_by_source.get(source_run_id)
        if source_malf_run_id is None:
            raise ValueError(f"Missing MALF lineage mapping for source run {source_run_id}")
        trade_date = str(item["trade_date"])
        current = grouped.get(symbol)
        if current is None:
            grouped[symbol] = {
                "symbol": symbol,
                "source_run_id": source_run_id,
                "source_malf_run_id": source_malf_run_id,
                "target_start_dt": trade_date,
                "target_end_dt": trade_date,
            }
            continue
        if trade_date < current["target_start_dt"]:
            current["target_start_dt"] = trade_date
        if trade_date > current["target_end_dt"]:
            current["target_end_dt"] = trade_date
    return [
        ReplayScopeEntry(
            symbol=symbol,
            timeframe="day",
            source_run_id=payload["source_run_id"],
            source_malf_run_id=payload["source_malf_run_id"],
            target_start_dt=payload["target_start_dt"],
            target_end_dt=payload["target_end_dt"],
        )
        for symbol, payload in sorted(grouped.items())
    ]


def _write_source_manifest(
    request: AlphaDailyIncrementalLedgerRequest,
    malf_impact_scope: dict[str, Any],
    malf_checkpoint: dict[str, Any],
) -> None:
    _write_json(
        request.source_manifest_path,
        {
            "run_id": request.run_id,
            "card_id": ALPHA_DAILY_INCREMENTAL_CARD,
            "schema_version": request.schema_version,
            "mode": request.mode,
            "source_module": "malf",
            "source_root": str(request.source_malf_root),
            "source_scope_count": int(malf_impact_scope.get("scope_count", 0)),
            "source_checkpoint_status": str(malf_checkpoint.get("status")),
            "source_daily_impact_scope_path": str(request.malf_daily_impact_scope_path),
            "source_lineage_path": str(request.malf_lineage_path),
        },
    )


def _impact_scope_rows(
    db_path: Path,
    run_id: str,
    family: str,
    symbol: str,
) -> list[dict[str, str]]:
    with duckdb.connect(str(db_path), read_only=True) as con:
        rows = con.execute(
            """
            select distinct bar_dt
            from alpha_signal_candidate
            where run_id = ? and alpha_family = ? and symbol = ? and timeframe = 'day'
            order by bar_dt
            """,
            [run_id, family, symbol],
        ).fetchall()
    return [
        {
            "symbol": symbol,
            "trade_date": row[0].isoformat(),
            "timeframe": "day",
            "upstream_module": "alpha",
            "source_run_id": run_id,
            "alpha_family": family,
        }
        for row in rows
    ]


def _build_audit_summary(
    request: AlphaDailyIncrementalLedgerRequest,
    impact_scope_count: int,
    lineage_rows: list[dict[str, str]],
) -> dict[str, Any]:
    family_checks: dict[str, dict[str, Any]] = {}
    status = "passed"
    for family in ALPHA_FAMILIES:
        db_path = request.target_root / ALPHA_FAMILY_DATABASES[family]
        row_counts = _row_counts(db_path)
        candidate_count = row_counts.get("alpha_signal_candidate", 0)
        family_checks[family] = {
            "db_path": str(db_path),
            "exists": db_path.exists(),
            "row_counts": row_counts,
            "candidate_rows_present": candidate_count > 0,
        }
        if not db_path.exists() or candidate_count == 0:
            status = "failed"
    return {
        "run_id": request.run_id,
        "card_id": ALPHA_DAILY_INCREMENTAL_CARD,
        "status": status,
        "impact_scope_count": impact_scope_count,
        "lineage_count": len(lineage_rows),
        "checks": family_checks,
        "week_month_opened": False,
        "formal_data_mutation": False,
        "boundaries": {
            "day_only": True,
            "downstream_runtime_opened": False,
            "full_rebuild_opened": False,
        },
    }


def _row_counts(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}
    counts: dict[str, int] = {}
    with duckdb.connect(str(path), read_only=True) as con:
        for table in ("alpha_family_run", "alpha_event_ledger", "alpha_signal_candidate"):
            row = con.execute(f"select count(*) from {table}").fetchone()
            counts[table] = 0 if row is None else int(row[0])
    return counts


def _service_version_for_run(service_db: Path, run_id: str) -> str:
    with duckdb.connect(str(service_db), read_only=True) as con:
        row = con.execute(
            """
            select service_version
            from malf_wave_position
            where run_id = ?
            order by service_version
            limit 1
            """,
            [run_id],
        ).fetchone()
    if row is None or row[0] is None:
        raise ValueError(f"Missing MALF service_version for run_id {run_id}")
    return str(row[0])


def _load_completed_summary(
    request: AlphaDailyIncrementalLedgerRequest,
) -> AlphaDailyIncrementalLedgerSummary | None:
    if request.mode != "resume" or not request.checkpoint_path.exists():
        return None
    payload = _load_json(request.checkpoint_path)
    if payload.get("status") != "completed":
        return None
    return AlphaDailyIncrementalLedgerSummary(**{**payload["summary"], "resume_reused": True})


def _save_summary(
    request: AlphaDailyIncrementalLedgerRequest,
    summary: AlphaDailyIncrementalLedgerSummary,
) -> None:
    write_checkpoint(request.checkpoint_path, {"status": "completed", "summary": summary.as_dict()})


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
