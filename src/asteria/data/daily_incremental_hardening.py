from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb

from asteria.build_orchestration import BatchLedgerEntry, append_batch_ledger, write_checkpoint
from asteria.data.bootstrap import run_data_bootstrap
from asteria.data.contracts import DataBootstrapRequest, DataBootstrapSummary

DATA_DAILY_HARDENING_SCHEMA_VERSION = "data-daily-incremental-hardening-v1"
DATA_DAILY_HARDENING_CARD = "data-ledger-daily-incremental-hardening-card"
NEXT_ALLOWED_ACTION = "malf_daily_incremental_ledger_build_card"
REPORT_DATE = "2026-05-11"
BASE_LEDGER_DBS = (
    ("market_base_day.duckdb", "day"),
    ("market_base_week.duckdb", "week"),
    ("market_base_month.duckdb", "month"),
)


@dataclass(frozen=True)
class DataDailyIncrementalHardeningRequest:
    source_root: Path
    target_root: Path
    temp_root: Path
    report_root: Path
    run_id: str
    mode: str
    start_dt: str | None = None
    end_dt: str | None = None
    symbol_limit: int | None = None
    asset_type: str = "stock"
    adj_mode: str = "backward"

    def __post_init__(self) -> None:
        if self.mode not in {"daily_incremental", "resume", "audit-only"}:
            raise ValueError(f"Unsupported hardening mode: {self.mode}")

    @property
    def run_root(self) -> Path:
        return self.temp_root / "data" / self.run_id

    @property
    def report_dir(self) -> Path:
        return self.report_root / "data" / REPORT_DATE / self.run_id

    @property
    def checkpoint_path(self) -> Path:
        return self.run_root / "checkpoint.json"

    @property
    def source_manifest_path(self) -> Path:
        return self.run_root / "source-manifest.json"

    @property
    def daily_dirty_scope_path(self) -> Path:
        return self.run_root / "daily-dirty-scope.json"

    @property
    def batch_ledger_path(self) -> Path:
        return self.run_root / "batch-ledger.jsonl"

    @property
    def audit_summary_path(self) -> Path:
        return self.report_dir / "audit-summary.json"


@dataclass(frozen=True)
class DataLedgerAudit:
    db_name: str
    status: str
    read_only: bool
    checks: dict[str, str]
    row_counts: dict[str, int]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DataDailyIncrementalHardeningSummary:
    run_id: str
    status: str
    mode: str
    card_id: str
    next_allowed_action: str
    bootstrap: DataBootstrapSummary
    ledger_audit: dict[str, DataLedgerAudit]
    daily_dirty_scope_count: int
    source_manifest_path: str
    daily_dirty_scope_path: str
    batch_ledger_path: str
    checkpoint_path: str
    audit_summary_path: str

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["bootstrap"] = self.bootstrap.as_dict()
        payload["ledger_audit"] = {
            name: audit.as_dict() for name, audit in self.ledger_audit.items()
        }
        return payload


def run_data_daily_incremental_hardening(
    request: DataDailyIncrementalHardeningRequest,
) -> DataDailyIncrementalHardeningSummary:
    request.run_root.mkdir(parents=True, exist_ok=True)
    request.report_dir.mkdir(parents=True, exist_ok=True)
    append_batch_ledger(
        request.batch_ledger_path,
        BatchLedgerEntry(request.run_id, _batch_id(), "running", started_at=_utc_now_iso()),
    )
    try:
        bootstrap = run_data_bootstrap(_bootstrap_request(request))
        source_manifest = _write_source_manifest(request)
        dirty_scope = _write_daily_dirty_scope(request)
        ledger_audit = _audit_data_ledgers(request)
        status = _summary_status(bootstrap, ledger_audit)
        summary = DataDailyIncrementalHardeningSummary(
            run_id=request.run_id,
            status=status,
            mode=request.mode,
            card_id=DATA_DAILY_HARDENING_CARD,
            next_allowed_action=NEXT_ALLOWED_ACTION,
            bootstrap=bootstrap,
            ledger_audit=ledger_audit,
            daily_dirty_scope_count=int(dirty_scope["scope_count"]),
            source_manifest_path=str(request.source_manifest_path),
            daily_dirty_scope_path=str(request.daily_dirty_scope_path),
            batch_ledger_path=str(request.batch_ledger_path),
            checkpoint_path=str(request.checkpoint_path),
            audit_summary_path=str(request.audit_summary_path),
        )
        _write_audit_summary(request, summary, source_manifest, dirty_scope)
        _write_hardening_checkpoint(request, summary)
        append_batch_ledger(
            request.batch_ledger_path,
            BatchLedgerEntry(
                request.run_id,
                _batch_id(),
                "promoted" if status == "passed" else "failed",
                completed_at=_utc_now_iso(),
                promoted_at=_utc_now_iso() if status == "passed" else None,
                row_counts={
                    "source_manifest": int(source_manifest["source_count"]),
                    "daily_dirty_scope": int(dirty_scope["scope_count"]),
                },
                audit_summary_path=str(request.audit_summary_path),
            ),
        )
        return summary
    except Exception as exc:
        append_batch_ledger(
            request.batch_ledger_path,
            BatchLedgerEntry(
                request.run_id,
                _batch_id(),
                "failed",
                completed_at=_utc_now_iso(),
                error=str(exc),
            ),
        )
        raise


def _bootstrap_request(request: DataDailyIncrementalHardeningRequest) -> DataBootstrapRequest:
    return DataBootstrapRequest(
        source_root=request.source_root,
        target_root=request.target_root,
        temp_root=request.temp_root,
        asset_type=request.asset_type,
        adj_mode=request.adj_mode,
        mode=request.mode,
        run_id=request.run_id,
        start_dt=request.start_dt,
        end_dt=request.end_dt,
        symbol_limit=request.symbol_limit,
    )


def _write_source_manifest(request: DataDailyIncrementalHardeningRequest) -> dict[str, Any]:
    raw_db = request.target_root / "raw_market.duckdb"
    sources: list[dict[str, Any]] = []
    if raw_db.exists():
        with duckdb.connect(str(raw_db), read_only=True) as con:
            rows = con.execute(
                """
                select source_file_key, source_vendor, asset_type, symbol, adj_mode,
                       source_path, source_size_bytes, source_content_hash, run_id
                from raw_market_source_file
                order by symbol, adj_mode, source_path
                """
            ).fetchall()
        sources = [
            {
                "source_file_key": row[0],
                "source_vendor": row[1],
                "asset_type": row[2],
                "symbol": row[3],
                "adj_mode": row[4],
                "source_path": row[5],
                "source_size_bytes": row[6],
                "source_content_hash": row[7],
                "run_id": row[8],
            }
            for row in rows
        ]
    payload = {
        "run_id": request.run_id,
        "schema_version": DATA_DAILY_HARDENING_SCHEMA_VERSION,
        "generated_at": _utc_now_iso(),
        "source_count": len(sources),
        "sources": sources,
    }
    _write_json(request.source_manifest_path, payload)
    return payload


def _write_daily_dirty_scope(request: DataDailyIncrementalHardeningRequest) -> dict[str, Any]:
    db_path = request.target_root / "market_base_day.duckdb"
    scopes: list[dict[str, Any]] = []
    if db_path.exists():
        with duckdb.connect(str(db_path), read_only=True) as con:
            rows = con.execute(
                """
                select dirty_key, symbol, asset_type, timeframe, adj_mode,
                       dirty_start_dt, dirty_end_dt, dirty_reason, dirty_status,
                       source_run_id, run_id
                from market_base_dirty_scope
                where run_id = ?
                order by symbol, timeframe, adj_mode
                """,
                [request.run_id],
            ).fetchall()
        scopes = [
            {
                "dirty_key": row[0],
                "symbol": row[1],
                "asset_type": row[2],
                "timeframe": row[3],
                "adj_mode": row[4],
                "dirty_start_dt": _stringify(row[5]),
                "dirty_end_dt": _stringify(row[6]),
                "dirty_reason": row[7],
                "dirty_status": row[8],
                "source_run_id": row[9],
                "run_id": row[10],
            }
            for row in rows
        ]
    payload = {
        "run_id": request.run_id,
        "schema_version": DATA_DAILY_HARDENING_SCHEMA_VERSION,
        "protocol_fields": ("symbol", "trade_date", "timeframe", "source_run_id"),
        "scope_count": len(scopes),
        "scopes": scopes,
    }
    _write_json(request.daily_dirty_scope_path, payload)
    return payload


def _audit_data_ledgers(
    request: DataDailyIncrementalHardeningRequest,
) -> dict[str, DataLedgerAudit]:
    audits = {"raw_market.duckdb": _audit_raw_market(request.target_root / "raw_market.duckdb")}
    for db_name, timeframe in BASE_LEDGER_DBS:
        audits[db_name] = _audit_market_base(request.target_root / db_name, db_name, timeframe)
    return audits


def _audit_raw_market(path: Path) -> DataLedgerAudit:
    checks: dict[str, str] = {"exists": "passed" if path.exists() else "failed"}
    row_counts: dict[str, int] = {}
    if path.exists():
        with duckdb.connect(str(path), read_only=True) as con:
            row_counts = {
                "raw_market_sync_run": _count(con, "raw_market_sync_run"),
                "raw_market_source_file": _count(con, "raw_market_source_file"),
                "raw_market_bar": _count(con, "raw_market_bar"),
            }
            duplicate_count = _scalar(
                con,
                """
                select count(*)
                from (
                    select source_vendor, symbol, timeframe, bar_dt, adj_mode, source_revision
                    from raw_market_bar
                    group by 1, 2, 3, 4, 5, 6
                    having count(*) > 1
                )
                """,
            )
        checks["run_ledger_present"] = _passed(row_counts["raw_market_sync_run"] > 0)
        checks["source_manifest_diff_ready"] = _passed(row_counts["raw_market_source_file"] > 0)
        checks["natural_key_uniqueness"] = _passed(duplicate_count == 0)
    return DataLedgerAudit(
        db_name="raw_market.duckdb",
        status=_audit_status(checks),
        read_only=True,
        checks=checks,
        row_counts=row_counts,
    )


def _audit_market_base(path: Path, db_name: str, timeframe: str) -> DataLedgerAudit:
    checks: dict[str, str] = {"exists": "passed" if path.exists() else "failed"}
    row_counts: dict[str, int] = {}
    if path.exists():
        with duckdb.connect(str(path), read_only=True) as con:
            row_counts = {
                "market_base_run": _count(con, "market_base_run"),
                "market_base_bar": _count(con, "market_base_bar"),
                "market_base_latest": _count(con, "market_base_latest"),
                "market_base_dirty_scope": _count(con, "market_base_dirty_scope"),
            }
            natural_dups = _scalar(
                con,
                """
                select count(*)
                from (
                    select symbol, timeframe, bar_dt, price_line, adj_mode
                    from market_base_bar
                    group by 1, 2, 3, 4, 5
                    having count(*) > 1
                )
                """,
            )
            latest_dups = _scalar(
                con,
                """
                select count(*)
                from (
                    select symbol, timeframe, price_line, adj_mode
                    from market_base_latest
                    group by 1, 2, 3, 4
                    having count(*) > 1
                )
                """,
            )
            wrong_timeframe = _scalar(
                con,
                "select count(*) from market_base_bar where timeframe <> ?",
                [timeframe],
            )
        checks["run_ledger_present"] = _passed(row_counts["market_base_run"] > 0)
        checks["dirty_scope_present"] = _passed(row_counts["market_base_dirty_scope"] > 0)
        checks["natural_key_uniqueness"] = _passed(natural_dups == 0)
        checks["latest_pointer_uniqueness"] = _passed(latest_dups == 0)
        checks["timeframe_boundary"] = _passed(wrong_timeframe == 0)
    return DataLedgerAudit(
        db_name=db_name,
        status=_audit_status(checks),
        read_only=True,
        checks=checks,
        row_counts=row_counts,
    )


def _write_audit_summary(
    request: DataDailyIncrementalHardeningRequest,
    summary: DataDailyIncrementalHardeningSummary,
    source_manifest: dict[str, Any],
    dirty_scope: dict[str, Any],
) -> None:
    payload = {
        **summary.as_dict(),
        "source_manifest": {
            "path": str(request.source_manifest_path),
            "source_count": source_manifest["source_count"],
        },
        "daily_dirty_scope": {
            "path": str(request.daily_dirty_scope_path),
            "scope_count": dirty_scope["scope_count"],
        },
        "boundaries": {
            "data_foundation_only": True,
            "malf_or_downstream_runtime_opened": False,
            "full_rebuild_opened": False,
            "week_month_rebuilt_from_day": False,
        },
    }
    _write_json(request.audit_summary_path, payload)


def _write_hardening_checkpoint(
    request: DataDailyIncrementalHardeningRequest,
    summary: DataDailyIncrementalHardeningSummary,
) -> None:
    write_checkpoint(
        request.checkpoint_path,
        {
            "status": "completed" if summary.status == "passed" else "failed",
            "summary": summary.bootstrap.as_dict(),
            "hardening": {
                "card_id": DATA_DAILY_HARDENING_CARD,
                "status": summary.status,
                "daily_dirty_scope_count": summary.daily_dirty_scope_count,
                "audit_summary_path": summary.audit_summary_path,
            },
        },
    )


def _summary_status(
    bootstrap: DataBootstrapSummary,
    ledger_audit: dict[str, DataLedgerAudit],
) -> str:
    if bootstrap.status != "completed":
        return "failed"
    if any(audit.status != "passed" for audit in ledger_audit.values()):
        return "failed"
    return "passed"


def _audit_status(checks: dict[str, str]) -> str:
    return (
        "passed" if checks and all(status == "passed" for status in checks.values()) else "failed"
    )


def _passed(condition: bool) -> str:
    return "passed" if condition else "failed"


def _count(con: duckdb.DuckDBPyConnection, table: str) -> int:
    return _scalar(con, f"select count(*) from {table}")


def _scalar(
    con: duckdb.DuckDBPyConnection,
    query: str,
    params: list[object] | None = None,
) -> int:
    row = con.execute(query, params or []).fetchone()
    return 0 if row is None else int(row[0])


def _batch_id() -> str:
    return "data-daily-incremental-sample"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _stringify(value: object) -> str | None:
    return None if value is None else str(value)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
