from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

import duckdb

from asteria.build_orchestration import BatchLedgerEntry, build_symbol_batches, completed_batch_ids
from asteria.build_orchestration.ledger import append_batch_ledger, utc_now_iso, write_checkpoint
from asteria.malf.supplemental import (
    MalfSupplementalBuildRequest,
    make_scope,
    run_malf_day_supplemental_build,
)

MALF_DAILY_INCREMENTAL_SCHEMA_VERSION = "malf-daily-incremental-ledger-v1"
MALF_DAILY_INCREMENTAL_CARD = "malf-daily-incremental-ledger-build-card"
NEXT_ALLOWED_ACTION = "alpha_signal_daily_incremental_ledger_build_card"
REPORT_DATE = "2026-05-11"


@dataclass(frozen=True)
class MalfDailyIncrementalLedgerRequest:
    source_db: Path
    target_root: Path
    temp_root: Path
    report_root: Path
    run_id: str
    mode: str
    data_source_manifest_path: Path
    data_daily_dirty_scope_path: Path
    data_checkpoint_path: Path
    batch_size: int = 1

    def __post_init__(self) -> None:
        if self.mode not in {"daily_incremental", "resume", "audit-only"}:
            raise ValueError(f"Unsupported MALF daily incremental mode: {self.mode}")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")

    @property
    def run_root(self) -> Path:
        return self.temp_root / "malf" / self.run_id

    @property
    def report_dir(self) -> Path:
        return self.report_root / "malf" / REPORT_DATE / self.run_id

    @property
    def source_manifest_path(self) -> Path:
        return self.run_root / "source-manifest.json"

    @property
    def derived_replay_scope_path(self) -> Path:
        return self.run_root / "derived-replay-scope.json"

    @property
    def daily_impact_scope_path(self) -> Path:
        return self.run_root / "daily-impact-scope.json"

    @property
    def lineage_path(self) -> Path:
        return self.run_root / "lineage.json"

    @property
    def batch_ledger_path(self) -> Path:
        return self.run_root / "batch-ledger.jsonl"

    @property
    def checkpoint_path(self) -> Path:
        return self.run_root / "checkpoint.json"

    @property
    def audit_summary_path(self) -> Path:
        return self.report_dir / "audit-summary.json"

    @property
    def core_db(self) -> Path:
        return self.target_root / "malf_core_day.duckdb"

    @property
    def lifespan_db(self) -> Path:
        return self.target_root / "malf_lifespan_day.duckdb"

    @property
    def service_db(self) -> Path:
        return self.target_root / "malf_service_day.duckdb"


@dataclass(frozen=True)
class MalfDailyIncrementalLedgerSummary:
    run_id: str
    status: str
    mode: str
    card_id: str
    next_allowed_action: str
    batch_count: int
    replay_scope_count: int
    impact_scope_count: int
    source_manifest_path: str
    derived_replay_scope_path: str
    daily_impact_scope_path: str
    lineage_path: str
    batch_ledger_path: str
    checkpoint_path: str
    audit_summary_path: str
    resume_reused: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReplayScopeEntry:
    symbol: str
    timeframe: str
    source_run_id: str
    target_start_dt: str
    target_end_dt: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def run_malf_daily_incremental_ledger(
    request: MalfDailyIncrementalLedgerRequest,
) -> MalfDailyIncrementalLedgerSummary:
    request.run_root.mkdir(parents=True, exist_ok=True)
    request.report_dir.mkdir(parents=True, exist_ok=True)

    completed = _load_completed_summary(request)
    if completed:
        return completed

    source_manifest = _load_json(request.data_source_manifest_path)
    dirty_scope = _load_json(request.data_daily_dirty_scope_path)
    data_checkpoint = _load_json(request.data_checkpoint_path)
    if data_checkpoint.get("status") != "completed":
        raise ValueError("MALF daily incremental requires completed Data hardening checkpoint")

    _write_json(
        request.source_manifest_path,
        {
            "run_id": request.run_id,
            "schema_version": MALF_DAILY_INCREMENTAL_SCHEMA_VERSION,
            "source_data_run_id": str(source_manifest["run_id"]),
            "source_manifest_path": str(request.data_source_manifest_path),
            "source_scope_count": int(dirty_scope.get("scope_count", 0)),
            "source_checkpoint_status": str(data_checkpoint.get("status")),
            "mode": request.mode,
        },
    )
    replay_scopes = _derive_replay_scopes(request, dirty_scope)
    _write_json(
        request.derived_replay_scope_path,
        {
            "run_id": request.run_id,
            "schema_version": MALF_DAILY_INCREMENTAL_SCHEMA_VERSION,
            "scope_count": len(replay_scopes),
            "scopes": [item.as_dict() for item in replay_scopes],
        },
    )

    if request.mode == "audit-only":
        _write_json(
            request.daily_impact_scope_path,
            {
                "run_id": request.run_id,
                "schema_version": MALF_DAILY_INCREMENTAL_SCHEMA_VERSION,
                "scope_count": 0,
                "scopes": [],
            },
        )
        _write_json(
            request.lineage_path,
            {
                "run_id": request.run_id,
                "schema_version": MALF_DAILY_INCREMENTAL_SCHEMA_VERSION,
                "lineage": [],
            },
        )
        audit_payload = _build_audit_summary(request, 0)
        _write_json(request.audit_summary_path, audit_payload)
        summary = MalfDailyIncrementalLedgerSummary(
            run_id=request.run_id,
            status=audit_payload["status"],
            mode=request.mode,
            card_id=MALF_DAILY_INCREMENTAL_CARD,
            next_allowed_action=NEXT_ALLOWED_ACTION,
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

    scope_by_symbol = {entry.symbol: entry for entry in replay_scopes}
    batches = build_symbol_batches(
        tuple(sorted(scope_by_symbol)),
        batch_size=request.batch_size,
    )
    promoted_batches = (
        completed_batch_ids(request.batch_ledger_path) if request.mode == "resume" else set()
    )
    impact_scope_rows: list[dict[str, str]] = []
    lineage_rows: list[dict[str, str]] = []

    for batch in batches:
        if batch.batch_id in promoted_batches:
            continue
        symbols = batch.symbols
        if len(symbols) != 1:
            raise ValueError("MALF daily incremental sample currently requires batch_size=1")
        scope_entry = scope_by_symbol[symbols[0]]
        sub_run_id = f"{request.run_id}-{batch.batch_id}"
        started_entry = BatchLedgerEntry(request.run_id, batch.batch_id, "running")
        append_batch_ledger(request.batch_ledger_path, started_entry)
        try:
            supplemental_summary = run_malf_day_supplemental_build(
                MalfSupplementalBuildRequest(
                    source_db=request.source_db,
                    core_db=request.core_db,
                    lifespan_db=request.lifespan_db,
                    service_db=request.service_db,
                    report_root=request.report_root,
                    validated_root=request.temp_root / "malf-validated-placeholder",
                    temp_root=request.temp_root,
                    run_id=sub_run_id,
                    mode="resume" if request.mode == "resume" else "segmented",
                    scope=make_scope(
                        start_dt=scope_entry.target_start_dt,
                        end_dt=scope_entry.target_end_dt,
                    ),
                    batch_size=1,
                    symbols=(scope_entry.symbol,),
                    source_market_base_run_id=scope_entry.source_run_id,
                )
            )
            stage_run_id = f"{sub_run_id}-batch-0001"
            impact_scope_rows.extend(
                _impact_scope_rows(
                    request.service_db,
                    stage_run_id,
                    scope_entry.symbol,
                    scope_entry.source_run_id,
                )
            )
            lineage_rows.append(
                {
                    "symbol": scope_entry.symbol,
                    "source_run_id": scope_entry.source_run_id,
                    "target_run_id": stage_run_id,
                    "core_run_id": stage_run_id,
                    "lifespan_run_id": stage_run_id,
                    "service_run_id": stage_run_id,
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
                    audit_summary_path=supplemental_summary.checkpoint_path,
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

    impact_scope_payload = {
        "run_id": request.run_id,
        "schema_version": MALF_DAILY_INCREMENTAL_SCHEMA_VERSION,
        "protocol_fields": [
            "symbol",
            "trade_date",
            "timeframe",
            "upstream_module",
            "source_run_id",
        ],
        "scope_count": len(impact_scope_rows),
        "scopes": impact_scope_rows,
    }
    lineage_payload = {
        "run_id": request.run_id,
        "schema_version": MALF_DAILY_INCREMENTAL_SCHEMA_VERSION,
        "lineage": lineage_rows,
    }
    _write_json(request.daily_impact_scope_path, impact_scope_payload)
    _write_json(request.lineage_path, lineage_payload)
    audit_payload = _build_audit_summary(request, len(impact_scope_rows))
    _write_json(request.audit_summary_path, audit_payload)
    summary = MalfDailyIncrementalLedgerSummary(
        run_id=request.run_id,
        status=audit_payload["status"],
        mode=request.mode,
        card_id=MALF_DAILY_INCREMENTAL_CARD,
        next_allowed_action=NEXT_ALLOWED_ACTION,
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
    request: MalfDailyIncrementalLedgerRequest,
    dirty_scope_payload: dict[str, Any],
) -> list[ReplayScopeEntry]:
    grouped: dict[str, dict[str, str]] = {}
    for item in dirty_scope_payload.get("scopes", []):
        if str(item.get("timeframe")) != "day":
            continue
        symbol = str(item["symbol"])
        source_run_id = str(item["source_run_id"])
        dirty_start_dt = str(item["dirty_start_dt"])
        current = grouped.get(symbol)
        if current is None or dirty_start_dt < current["target_start_dt"]:
            grouped[symbol] = {
                "symbol": symbol,
                "source_run_id": source_run_id,
                "target_start_dt": dirty_start_dt,
            }
    scopes: list[ReplayScopeEntry] = []
    for symbol in sorted(grouped):
        target_end = _max_bar_dt(request.source_db, symbol)
        scopes.append(
            ReplayScopeEntry(
                symbol=symbol,
                timeframe="day",
                source_run_id=grouped[symbol]["source_run_id"],
                target_start_dt=grouped[symbol]["target_start_dt"],
                target_end_dt=target_end.isoformat(),
            )
        )
    return scopes


def _impact_scope_rows(
    service_db: Path,
    run_id: str,
    symbol: str,
    source_run_id: str,
) -> list[dict[str, str]]:
    with duckdb.connect(str(service_db), read_only=True) as con:
        rows = con.execute(
            """
            select distinct bar_dt
            from malf_wave_position
            where run_id = ? and symbol = ?
            order by bar_dt
            """,
            [run_id, symbol],
        ).fetchall()
    return [
        {
            "symbol": symbol,
            "trade_date": row[0].isoformat(),
            "timeframe": "day",
            "upstream_module": "malf",
            "source_run_id": source_run_id,
        }
        for row in rows
    ]


def _build_audit_summary(
    request: MalfDailyIncrementalLedgerRequest,
    impact_scope_count: int,
) -> dict[str, Any]:
    dbs = {
        "malf_core_day.duckdb": request.core_db,
        "malf_lifespan_day.duckdb": request.lifespan_db,
        "malf_service_day.duckdb": request.service_db,
    }
    checks: dict[str, dict[str, Any]] = {}
    status = "passed"
    for db_name, path in dbs.items():
        exists = path.exists()
        row_counts = _row_counts(path)
        checks[db_name] = {"exists": exists, "row_counts": row_counts}
        if not exists:
            status = "failed"
    return {
        "run_id": request.run_id,
        "status": status,
        "impact_scope_count": impact_scope_count,
        "checks": checks,
        "week_month_opened": False,
        "formal_data_mutation": False,
    }


def _row_counts(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}
    table_map = {
        "malf_core_day.duckdb": ("malf_core_run", "malf_wave_ledger"),
        "malf_lifespan_day.duckdb": ("malf_lifespan_run", "malf_lifespan_snapshot"),
        "malf_service_day.duckdb": ("malf_service_run", "malf_wave_position"),
    }
    counts: dict[str, int] = {}
    with duckdb.connect(str(path), read_only=True) as con:
        for table in table_map.get(path.name, ()):
            row = con.execute(f"select count(*) from {table}").fetchone()
            counts[table] = 0 if row is None else int(row[0])
    return counts


def _max_bar_dt(source_db: Path, symbol: str) -> date:
    with duckdb.connect(str(source_db), read_only=True) as con:
        row = con.execute(
            """
            select max(bar_dt)
            from market_base_bar
            where symbol = ?
              and timeframe = 'day'
              and price_line = 'analysis_price_line'
              and adj_mode = 'backward'
            """,
            [symbol],
        ).fetchone()
    if row is None or row[0] is None:
        raise ValueError(f"No day source bars found for {symbol}")
    return row[0]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_completed_summary(
    request: MalfDailyIncrementalLedgerRequest,
) -> MalfDailyIncrementalLedgerSummary | None:
    if request.mode != "resume" or not request.checkpoint_path.exists():
        return None
    payload = _load_json(request.checkpoint_path)
    if payload.get("status") != "completed":
        return None
    return MalfDailyIncrementalLedgerSummary(
        **{**payload["summary"], "resume_reused": True},
    )


def _save_summary(
    request: MalfDailyIncrementalLedgerRequest,
    summary: MalfDailyIncrementalLedgerSummary,
) -> None:
    write_checkpoint(
        request.checkpoint_path,
        {
            "status": "completed",
            "summary": summary.as_dict(),
        },
    )
