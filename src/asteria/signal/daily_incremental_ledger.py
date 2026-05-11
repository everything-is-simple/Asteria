from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import duckdb

from asteria.build_orchestration import BatchLedgerEntry, build_symbol_batches, completed_batch_ids
from asteria.build_orchestration.ledger import append_batch_ledger, utc_now_iso, write_checkpoint
from asteria.signal.bootstrap import run_signal_build
from asteria.signal.contracts import (
    SignalBuildRequest,
    SignalDailyIncrementalLedgerRequest,
    SignalDailyIncrementalLedgerSummary,
)

SIGNAL_DAILY_INCREMENTAL_CARD = "alpha-signal-daily-incremental-ledger-build-card"


@dataclass(frozen=True)
class ReplayScopeEntry:
    symbol: str
    timeframe: str
    source_alpha_run_id: str
    target_start_dt: str
    target_end_dt: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def run_signal_daily_incremental_ledger(
    request: SignalDailyIncrementalLedgerRequest,
) -> SignalDailyIncrementalLedgerSummary:
    request.run_root.mkdir(parents=True, exist_ok=True)
    request.report_dir.mkdir(parents=True, exist_ok=True)

    completed = _load_completed_summary(request)
    if completed:
        return completed

    alpha_checkpoint = _load_json(request.alpha_checkpoint_path)
    if alpha_checkpoint.get("status") != "completed":
        raise ValueError("Signal daily incremental requires completed Alpha daily checkpoint")

    alpha_impact_scope = _load_json(request.alpha_daily_impact_scope_path)
    alpha_lineage = _load_json(request.alpha_lineage_path)
    replay_scopes = _derive_replay_scopes(alpha_impact_scope, alpha_lineage)
    _write_json(
        request.derived_replay_scope_path,
        {
            "run_id": request.run_id,
            "card_id": SIGNAL_DAILY_INCREMENTAL_CARD,
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
                "card_id": SIGNAL_DAILY_INCREMENTAL_CARD,
                "schema_version": request.schema_version,
                "scope_count": 0,
                "scopes": [],
            },
        )
        _write_json(
            request.lineage_path,
            {
                "run_id": request.run_id,
                "card_id": SIGNAL_DAILY_INCREMENTAL_CARD,
                "schema_version": request.schema_version,
                "lineage": [],
            },
        )
        audit_payload = _build_audit_summary(request, 0, [])
        _write_json(request.audit_summary_path, audit_payload)
        summary = SignalDailyIncrementalLedgerSummary(
            run_id=request.run_id,
            status=audit_payload["status"],
            mode=request.mode,
            timeframe=request.timeframe,
            schema_version=request.schema_version,
            batch_count=0,
            replay_scope_count=len(replay_scopes),
            impact_scope_count=0,
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
            raise ValueError("Signal daily incremental sample currently requires batch_size=1")
        scope = scope_by_symbol[batch.symbols[0]]
        append_batch_ledger(
            request.batch_ledger_path,
            BatchLedgerEntry(request.run_id, batch.batch_id, "running", started_at=utc_now_iso()),
        )
        try:
            build_summary = run_signal_build(
                SignalBuildRequest(
                    source_alpha_root=request.source_alpha_root,
                    target_signal_db=request.target_signal_db,
                    report_root=request.report_root,
                    validated_root=request.temp_root / "signal-validated-placeholder",
                    temp_root=request.temp_root,
                    run_id=request.run_id,
                    mode="resume" if request.mode == "resume" else "daily_incremental",
                    source_alpha_release_version=request.source_alpha_release_version,
                    source_alpha_run_id=scope.source_alpha_run_id,
                    schema_version=request.schema_version,
                    signal_rule_version=request.signal_rule_version,
                    timeframe=request.timeframe,
                    start_dt=scope.target_start_dt,
                    end_dt=scope.target_end_dt,
                    symbol_limit=1,
                )
            )
            impact_scope_rows.extend(
                _impact_scope_rows(request.target_signal_db, request.run_id, batch.symbols[0])
            )
            lineage_rows.append(
                {
                    "symbol": batch.symbols[0],
                    "timeframe": request.timeframe,
                    "source_run_id": scope.source_alpha_run_id,
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
                    audit_summary_path=build_summary.report_path,
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
            "card_id": SIGNAL_DAILY_INCREMENTAL_CARD,
            "schema_version": request.schema_version,
            "protocol_fields": [
                "symbol",
                "trade_date",
                "timeframe",
                "upstream_module",
                "source_run_id",
            ],
            "scope_count": len(impact_scope_rows),
            "scopes": impact_scope_rows,
        },
    )
    _write_json(
        request.lineage_path,
        {
            "run_id": request.run_id,
            "card_id": SIGNAL_DAILY_INCREMENTAL_CARD,
            "schema_version": request.schema_version,
            "lineage": lineage_rows,
        },
    )
    audit_payload = _build_audit_summary(request, len(impact_scope_rows), lineage_rows)
    _write_json(request.audit_summary_path, audit_payload)
    summary = SignalDailyIncrementalLedgerSummary(
        run_id=request.run_id,
        status=audit_payload["status"],
        mode=request.mode,
        timeframe=request.timeframe,
        schema_version=request.schema_version,
        batch_count=len(batches),
        replay_scope_count=len(replay_scopes),
        impact_scope_count=len(impact_scope_rows),
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
    alpha_run_ids = {
        str(item["target_run_id"])
        for item in lineage_payload.get("lineage", [])
        if str(item.get("target_run_id"))
    }
    if len(alpha_run_ids) != 1:
        raise ValueError("Signal daily incremental sample requires a single Alpha batch run_id")
    source_alpha_run_id = next(iter(alpha_run_ids))
    grouped: dict[str, dict[str, str]] = {}
    for item in impact_scope_payload.get("scopes", []):
        if str(item.get("timeframe")) != "day":
            continue
        symbol = str(item["symbol"])
        trade_date = str(item["trade_date"])
        current = grouped.get(symbol)
        if current is None:
            grouped[symbol] = {
                "symbol": symbol,
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
            source_alpha_run_id=source_alpha_run_id,
            target_start_dt=payload["target_start_dt"],
            target_end_dt=payload["target_end_dt"],
        )
        for symbol, payload in sorted(grouped.items())
    ]


def _impact_scope_rows(db_path: Path, run_id: str, symbol: str) -> list[dict[str, str]]:
    with duckdb.connect(str(db_path), read_only=True) as con:
        rows = con.execute(
            """
            select distinct signal_dt
            from formal_signal_ledger
            where run_id = ? and symbol = ? and timeframe = 'day'
            order by signal_dt
            """,
            [run_id, symbol],
        ).fetchall()
    return [
        {
            "symbol": symbol,
            "trade_date": row[0].isoformat(),
            "timeframe": "day",
            "upstream_module": "signal",
            "source_run_id": run_id,
        }
        for row in rows
    ]


def _build_audit_summary(
    request: SignalDailyIncrementalLedgerRequest,
    impact_scope_count: int,
    lineage_rows: list[dict[str, str]],
) -> dict[str, Any]:
    row_counts = _row_counts(request.target_signal_db)
    formal_signal_count = row_counts.get("formal_signal_ledger", 0)
    status = "passed" if request.target_signal_db.exists() and formal_signal_count > 0 else "failed"
    return {
        "run_id": request.run_id,
        "card_id": SIGNAL_DAILY_INCREMENTAL_CARD,
        "status": status,
        "impact_scope_count": impact_scope_count,
        "lineage_count": len(lineage_rows),
        "checks": {
            "signal_db_exists": request.target_signal_db.exists(),
            "formal_signal_rows_present": formal_signal_count > 0,
            "downstream_runtime_opened": False,
        },
        "row_counts": row_counts,
        "boundaries": {
            "day_only": True,
            "formal_data_mutation": False,
            "downstream_runtime_opened": False,
            "full_rebuild_opened": False,
        },
    }


def _row_counts(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}
    counts: dict[str, int] = {}
    with duckdb.connect(str(path), read_only=True) as con:
        for table in ("signal_run", "signal_input_snapshot", "formal_signal_ledger"):
            row = con.execute(f"select count(*) from {table}").fetchone()
            counts[table] = 0 if row is None else int(row[0])
    return counts


def _load_completed_summary(
    request: SignalDailyIncrementalLedgerRequest,
) -> SignalDailyIncrementalLedgerSummary | None:
    if request.mode != "resume" or not request.checkpoint_path.exists():
        return None
    payload = _load_json(request.checkpoint_path)
    if payload.get("status") != "completed":
        return None
    return SignalDailyIncrementalLedgerSummary(**{**payload["summary"], "resume_reused": True})


def _save_summary(
    request: SignalDailyIncrementalLedgerRequest,
    summary: SignalDailyIncrementalLedgerSummary,
) -> None:
    write_checkpoint(request.checkpoint_path, {"status": "completed", "summary": summary.as_dict()})


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
