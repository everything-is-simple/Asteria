from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import duckdb

from asteria.build_orchestration import BatchLedgerEntry, build_symbol_batches, completed_batch_ids
from asteria.build_orchestration.ledger import append_batch_ledger, utc_now_iso, write_checkpoint
from asteria.portfolio_plan.bootstrap import run_portfolio_plan_build
from asteria.portfolio_plan.contracts import (
    PortfolioPlanBuildRequest,
    PortfolioPlanDailyIncrementalLedgerRequest,
    PortfolioPlanDailyIncrementalLedgerSummary,
)

PORTFOLIO_PLAN_DAILY_INCREMENTAL_CARD = "downstream-daily-incremental-runner-build-card"


@dataclass(frozen=True)
class ReplayScopeEntry:
    symbol: str
    timeframe: str
    source_position_run_id: str
    target_start_dt: str
    target_end_dt: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def run_portfolio_plan_daily_incremental_ledger(
    request: PortfolioPlanDailyIncrementalLedgerRequest,
) -> PortfolioPlanDailyIncrementalLedgerSummary:
    request.run_root.mkdir(parents=True, exist_ok=True)
    request.report_dir.mkdir(parents=True, exist_ok=True)

    completed = _load_completed_summary(request)
    if completed:
        return completed

    position_checkpoint = _load_json(request.position_checkpoint_path)
    if position_checkpoint.get("status") != "completed":
        raise ValueError(
            "Portfolio Plan daily incremental requires completed Position daily checkpoint"
        )

    position_impact_scope = _load_json(request.position_daily_impact_scope_path)
    position_lineage = _load_json(request.position_lineage_path)
    replay_scopes = _derive_replay_scopes(position_impact_scope, position_lineage)
    _write_json(
        request.source_manifest_path,
        {
            "run_id": request.run_id,
            "card_id": PORTFOLIO_PLAN_DAILY_INCREMENTAL_CARD,
            "schema_version": request.schema_version,
            "source_position_db": str(request.source_position_db),
            "source_position_release_version": request.source_position_release_version,
            "source_position_scope_path": str(request.position_daily_impact_scope_path),
            "source_position_lineage_path": str(request.position_lineage_path),
            "source_position_checkpoint_path": str(request.position_checkpoint_path),
            "source_checkpoint_status": str(position_checkpoint.get("status")),
        },
    )
    _write_json(
        request.derived_replay_scope_path,
        {
            "run_id": request.run_id,
            "card_id": PORTFOLIO_PLAN_DAILY_INCREMENTAL_CARD,
            "schema_version": request.schema_version,
            "scope_count": len(replay_scopes),
            "scopes": [scope.as_dict() for scope in replay_scopes],
        },
    )

    if request.mode == "audit-only":
        summary = _finalize_audit_only(request, replay_scopes)
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
            raise ValueError(
                "Portfolio Plan daily incremental sample currently requires batch_size=1"
            )
        scope = scope_by_symbol[batch.symbols[0]]
        sub_run_id = f"{request.run_id}-{batch.batch_id}"
        append_batch_ledger(
            request.batch_ledger_path,
            BatchLedgerEntry(sub_run_id, batch.batch_id, "running", started_at=utc_now_iso()),
        )
        try:
            build_summary = run_portfolio_plan_build(
                PortfolioPlanBuildRequest(
                    source_position_db=request.source_position_db,
                    target_portfolio_plan_db=request.target_portfolio_plan_db,
                    report_root=request.report_root,
                    validated_root=request.temp_root / "portfolio-plan-validated-placeholder",
                    temp_root=request.temp_root,
                    run_id=sub_run_id,
                    mode="resume" if request.mode == "resume" else "daily_incremental",
                    source_position_release_version=request.source_position_release_version,
                    source_position_run_id=scope.source_position_run_id,
                    schema_version=request.schema_version,
                    portfolio_plan_rule_version=request.portfolio_plan_rule_version,
                    timeframe=request.timeframe,
                    start_dt=scope.target_start_dt,
                    end_dt=scope.target_end_dt,
                    symbol_limit=1,
                    symbols=(scope.symbol,),
                    max_active_symbols=request.max_active_symbols,
                )
            )
            impact_scope_rows.extend(
                _impact_scope_rows(request.target_portfolio_plan_db, sub_run_id, scope.symbol)
            )
            lineage_rows.append(
                {
                    "symbol": scope.symbol,
                    "timeframe": request.timeframe,
                    "source_run_id": scope.source_position_run_id,
                    "target_run_id": sub_run_id,
                }
            )
            append_batch_ledger(
                request.batch_ledger_path,
                BatchLedgerEntry(
                    sub_run_id,
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
                    sub_run_id,
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
            "card_id": PORTFOLIO_PLAN_DAILY_INCREMENTAL_CARD,
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
            "card_id": PORTFOLIO_PLAN_DAILY_INCREMENTAL_CARD,
            "schema_version": request.schema_version,
            "lineage": lineage_rows,
        },
    )
    _write_json(
        request.audit_summary_path, _build_audit_summary(request, impact_scope_rows, lineage_rows)
    )
    summary = PortfolioPlanDailyIncrementalLedgerSummary(
        run_id=request.run_id,
        status="passed" if impact_scope_rows else "failed",
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


def _finalize_audit_only(
    request: PortfolioPlanDailyIncrementalLedgerRequest,
    replay_scopes: list[ReplayScopeEntry],
) -> PortfolioPlanDailyIncrementalLedgerSummary:
    _write_json(
        request.daily_impact_scope_path,
        {
            "run_id": request.run_id,
            "card_id": PORTFOLIO_PLAN_DAILY_INCREMENTAL_CARD,
            "schema_version": request.schema_version,
            "scope_count": 0,
            "scopes": [],
        },
    )
    _write_json(
        request.lineage_path,
        {
            "run_id": request.run_id,
            "card_id": PORTFOLIO_PLAN_DAILY_INCREMENTAL_CARD,
            "schema_version": request.schema_version,
            "lineage": [],
        },
    )
    _write_json(request.audit_summary_path, _build_audit_summary(request, [], []))
    return PortfolioPlanDailyIncrementalLedgerSummary(
        run_id=request.run_id,
        status="passed",
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


def _derive_replay_scopes(
    impact_scope_payload: dict[str, Any],
    lineage_payload: dict[str, Any],
) -> list[ReplayScopeEntry]:
    source_run_by_symbol = {
        str(item["symbol"]): str(item["target_run_id"])
        for item in lineage_payload.get("lineage", [])
        if item.get("symbol") and item.get("target_run_id")
    }
    fallback_run_ids = {
        str(item["target_run_id"])
        for item in lineage_payload.get("lineage", [])
        if str(item.get("target_run_id"))
    }
    fallback_run_id = next(iter(fallback_run_ids)) if len(fallback_run_ids) == 1 else None
    grouped: dict[str, dict[str, str]] = {}
    for item in impact_scope_payload.get("scopes", []):
        if str(item.get("timeframe")) != "day":
            continue
        symbol = str(item["symbol"])
        trade_date = str(item["trade_date"])
        current = grouped.get(symbol)
        if current is None:
            grouped[symbol] = {
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
            source_position_run_id=source_run_by_symbol.get(symbol)
            or _missing_symbol_run_id(
                symbol,
                "Portfolio Plan",
                fallback_run_id,
            ),
            target_start_dt=payload["target_start_dt"],
            target_end_dt=payload["target_end_dt"],
        )
        for symbol, payload in sorted(grouped.items())
    ]


def _missing_symbol_run_id(symbol: str, module_name: str, fallback_run_id: str | None) -> str:
    if fallback_run_id:
        return fallback_run_id
    raise ValueError(f"{module_name} daily incremental sample missing upstream run_id for {symbol}")


def _impact_scope_rows(db_path: Path, run_id: str, symbol: str) -> list[dict[str, str]]:
    if not db_path.exists():
        return []
    with duckdb.connect(str(db_path), read_only=True) as con:
        rows = con.execute(
            """
                select distinct impact_dt
                from (
                    select candidate_dt as impact_dt
                    from portfolio_position_snapshot
                    where portfolio_run_id = ? and symbol = ? and timeframe = 'day'
                    union all
                    select plan_dt as impact_dt
                    from portfolio_admission_ledger
                where run_id = ? and symbol = ? and timeframe = 'day'
                union all
                select e.exposure_valid_from as impact_dt
                from portfolio_target_exposure e
                join portfolio_admission_ledger a
                  on a.portfolio_admission_id = e.portfolio_admission_id
                 and a.run_id = e.run_id
                where e.run_id = ? and a.symbol = ? and a.timeframe = 'day'
                union all
                select e.exposure_valid_until as impact_dt
                from portfolio_target_exposure e
                join portfolio_admission_ledger a
                  on a.portfolio_admission_id = e.portfolio_admission_id
                 and a.run_id = e.run_id
                where e.run_id = ? and a.symbol = ? and a.timeframe = 'day'
            )
            where impact_dt is not null
            order by impact_dt
            """,
            [run_id, symbol, run_id, symbol, run_id, symbol, run_id, symbol],
        ).fetchall()
    return [
        {
            "symbol": symbol,
            "trade_date": row[0].isoformat(),
            "timeframe": "day",
            "upstream_module": "portfolio_plan",
            "source_run_id": run_id,
        }
        for row in rows
    ]


def _build_audit_summary(
    request: PortfolioPlanDailyIncrementalLedgerRequest,
    impact_scope_rows: list[dict[str, str]],
    lineage_rows: list[dict[str, str]],
) -> dict[str, Any]:
    row_counts = _row_counts(request.target_portfolio_plan_db)
    return {
        "run_id": request.run_id,
        "card_id": PORTFOLIO_PLAN_DAILY_INCREMENTAL_CARD,
        "status": "passed"
        if request.mode == "audit-only" or row_counts["portfolio_admission_ledger"] > 0
        else "failed",
        "impact_scope_count": len(impact_scope_rows),
        "lineage_count": len(lineage_rows),
        "checks": {
            "portfolio_plan_db_exists": request.target_portfolio_plan_db.exists(),
            "portfolio_admission_rows_present": row_counts["portfolio_admission_ledger"] > 0,
            "downstream_runtime_opened": False,
        },
        "row_counts": row_counts,
        "boundaries": {
            "day_only": True,
            "formal_data_mutation": False,
            "system_readout_read_only_consumer": False,
            "full_daily_chain_opened": False,
        },
    }


def _row_counts(path: Path) -> dict[str, int]:
    if not path.exists():
        return {
            "portfolio_position_snapshot": 0,
            "portfolio_admission_ledger": 0,
            "portfolio_target_exposure": 0,
            "portfolio_trim_ledger": 0,
        }
    with duckdb.connect(str(path), read_only=True) as con:

        def count_rows(table_name: str) -> int:
            row = con.execute(f"select count(*) from {table_name}").fetchone()
            return 0 if row is None else int(row[0])

        return {
            "portfolio_position_snapshot": count_rows("portfolio_position_snapshot"),
            "portfolio_admission_ledger": count_rows("portfolio_admission_ledger"),
            "portfolio_target_exposure": count_rows("portfolio_target_exposure"),
            "portfolio_trim_ledger": count_rows("portfolio_trim_ledger"),
        }


def _load_completed_summary(
    request: PortfolioPlanDailyIncrementalLedgerRequest,
) -> PortfolioPlanDailyIncrementalLedgerSummary | None:
    if request.mode != "resume" or not request.checkpoint_path.exists():
        return None
    payload = _load_json(request.checkpoint_path)
    if payload.get("status") != "completed":
        return None
    return PortfolioPlanDailyIncrementalLedgerSummary(
        **{**payload["summary"], "resume_reused": True}
    )


def _save_summary(
    request: PortfolioPlanDailyIncrementalLedgerRequest,
    summary: PortfolioPlanDailyIncrementalLedgerSummary,
) -> None:
    write_checkpoint(request.checkpoint_path, {"status": "completed", "summary": summary.as_dict()})


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
