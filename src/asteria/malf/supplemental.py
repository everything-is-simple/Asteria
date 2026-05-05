from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import date
from pathlib import Path
from typing import Any

import duckdb

from asteria.build_orchestration import (
    BatchLedgerEntry,
    BuildManifest,
    BuildScope,
    SymbolBatch,
    append_batch_ledger,
    build_symbol_batches,
    completed_batch_ids,
    resolve_target_scope,
    write_checkpoint,
    write_manifest,
)
from asteria.build_orchestration.ledger import utc_now_iso
from asteria.malf.bootstrap import (
    run_malf_day_audit,
    run_malf_day_core_build,
    run_malf_day_lifespan_build,
    run_malf_day_service_build,
)
from asteria.malf.bootstrap_support import latest_run_id
from asteria.malf.contracts import MALF_SCHEMA_VERSION, MalfDayRequest
from asteria.malf.schema import (
    bootstrap_malf_core_day_database,
    bootstrap_malf_lifespan_day_database,
    bootstrap_malf_service_day_database,
)
from asteria.malf.source_contract import MALF_SOURCE_ADJ_MODE, MALF_SOURCE_PRICE_LINE


@dataclass(frozen=True)
class MalfSupplementalBuildRequest:
    source_db: Path
    core_db: Path
    lifespan_db: Path
    service_db: Path
    report_root: Path
    validated_root: Path
    temp_root: Path
    run_id: str
    mode: str
    scope: BuildScope
    batch_size: int = 100
    symbols: tuple[str, ...] = ()
    symbols_file: Path | None = None
    symbol_start: str | None = None
    symbol_end: str | None = None
    schema_version: str = MALF_SCHEMA_VERSION
    core_rule_version: str = "core-rule-fractal-1bar-v1"
    lifespan_rule_version: str = "lifespan-dense-bar-v1"
    sample_version: str = "malf-day-supplemental-v1"
    service_version: str = "malf-wave-position-dense-v1"
    source_market_base_run_id: str | None = None

    def __post_init__(self) -> None:
        if self.mode not in {"segmented", "resume", "audit-only"}:
            raise ValueError("MALF supplemental mode must be segmented, resume, or audit-only")

    @property
    def run_root(self) -> Path:
        return self.temp_root / "malf" / self.run_id


@dataclass(frozen=True)
class MalfSupplementalBuildSummary:
    run_id: str
    mode: str
    status: str
    batch_count: int
    promoted_batch_count: int
    skipped_batch_count: int
    manifest_path: str
    checkpoint_path: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def make_scope(
    *,
    year: int | None = None,
    month: int | None = None,
    day: str | None = None,
    start_dt: str | None = None,
    end_dt: str | None = None,
) -> BuildScope:
    return resolve_target_scope(
        timeframe="day",
        year=year,
        month=month,
        day=day,
        start_dt=start_dt,
        end_dt=end_dt,
    )


def run_malf_day_supplemental_build(
    request: MalfSupplementalBuildRequest,
) -> MalfSupplementalBuildSummary:
    if request.mode == "audit-only":
        return _run_formal_audit_only(request)

    universe = _load_symbol_universe(request.source_db, request.scope)
    batches = build_symbol_batches(
        universe,
        batch_size=request.batch_size,
        symbols=request.symbols or None,
        symbols_file=request.symbols_file,
        symbol_start=request.symbol_start,
        symbol_end=request.symbol_end,
    )
    manifest_path = request.run_root / "build-manifest.json"
    ledger_path = request.run_root / "batch-ledger.jsonl"
    checkpoint_path = request.run_root / "checkpoint.json"
    manifest = BuildManifest(
        run_id=request.run_id,
        module_id="malf",
        mode=request.mode,
        db_names=("malf_core_day.duckdb", "malf_lifespan_day.duckdb", "malf_service_day.duckdb"),
        scope=request.scope,
        schema_version=request.schema_version,
        rule_versions={
            "core_rule_version": request.core_rule_version,
            "lifespan_rule_version": request.lifespan_rule_version,
            "sample_version": request.sample_version,
            "service_version": request.service_version,
        },
        source_run_id=request.source_market_base_run_id,
        batches=batches,
    )
    write_manifest(manifest_path, manifest)

    skipped = completed_batch_ids(ledger_path) if request.mode == "resume" else set()
    promoted = 0
    for batch in batches:
        if batch.batch_id in skipped:
            continue
        _run_and_promote_batch(request, batch, ledger_path, checkpoint_path)
        promoted += 1

    summary = MalfSupplementalBuildSummary(
        run_id=request.run_id,
        mode=request.mode,
        status="completed",
        batch_count=len(batches),
        promoted_batch_count=promoted,
        skipped_batch_count=len(skipped),
        manifest_path=str(manifest_path),
        checkpoint_path=str(checkpoint_path),
    )
    write_checkpoint(checkpoint_path, {"status": summary.status, "summary": summary.as_dict()})
    return summary


def _run_formal_audit_only(
    request: MalfSupplementalBuildRequest,
) -> MalfSupplementalBuildSummary:
    latest_service_run = latest_run_id(request.service_db, "malf_service_run")
    if latest_service_run is None:
        raise ValueError("audit-only requires an existing formal MALF service run")
    audit_request = _base_stage_request(
        request, SymbolBatch("audit-only", (), 1, 1), request.run_root
    )
    audit_request = replace(
        audit_request,
        core_db=request.core_db,
        lifespan_db=request.lifespan_db,
        service_db=request.service_db,
        run_id=latest_service_run,
        mode="audit-only",
    )
    run_malf_day_audit(audit_request)
    checkpoint_path = request.run_root / "checkpoint.json"
    manifest_path = request.run_root / "build-manifest.json"
    summary = MalfSupplementalBuildSummary(
        run_id=request.run_id,
        mode=request.mode,
        status="completed",
        batch_count=0,
        promoted_batch_count=0,
        skipped_batch_count=0,
        manifest_path=str(manifest_path),
        checkpoint_path=str(checkpoint_path),
    )
    write_checkpoint(checkpoint_path, {"status": summary.status, "summary": summary.as_dict()})
    return summary


def _run_and_promote_batch(
    request: MalfSupplementalBuildRequest,
    batch: SymbolBatch,
    ledger_path: Path,
    checkpoint_path: Path,
) -> None:
    started_at = utc_now_iso()
    append_batch_ledger(
        ledger_path,
        BatchLedgerEntry(request.run_id, batch.batch_id, "running", started_at=started_at),
    )
    try:
        batch_dir = request.run_root / batch.batch_id
        stage_request = _base_stage_request(request, batch, batch_dir)
        run_malf_day_core_build(stage_request)
        run_malf_day_lifespan_build(stage_request)
        service_summary = run_malf_day_service_build(stage_request)
        audit_summary = run_malf_day_audit(stage_request)
        hard_fail_count = _hard_fail_count(stage_request.service_db, stage_request.run_id)
        if hard_fail_count:
            raise ValueError(f"Batch {batch.batch_id} audit hard_fail_count={hard_fail_count}")
        _promote_batch(request, batch, stage_request)
        row_counts = {
            "published_row_count": service_summary.published_row_count,
            "hard_fail_count": hard_fail_count,
        }
        append_batch_ledger(
            ledger_path,
            BatchLedgerEntry(
                request.run_id,
                batch.batch_id,
                "promoted",
                started_at=started_at,
                completed_at=utc_now_iso(),
                promoted_at=utc_now_iso(),
                row_counts=row_counts,
                audit_summary_path=audit_summary.report_path,
            ),
        )
        write_checkpoint(
            checkpoint_path,
            {"status": "running", "last_promoted_batch_id": batch.batch_id},
        )
    except Exception as exc:
        append_batch_ledger(
            ledger_path,
            BatchLedgerEntry(
                request.run_id,
                batch.batch_id,
                "failed",
                started_at=started_at,
                completed_at=utc_now_iso(),
                error=str(exc),
            ),
        )
        write_checkpoint(checkpoint_path, {"status": "failed", "failed_batch_id": batch.batch_id})
        raise


def _base_stage_request(
    request: MalfSupplementalBuildRequest,
    batch: SymbolBatch,
    batch_dir: Path,
) -> MalfDayRequest:
    compute_start = _compute_start_dt(request.source_db, batch.symbols, request.scope.target_end_dt)
    return MalfDayRequest(
        source_db=request.source_db,
        core_db=batch_dir / "malf_core_day.duckdb",
        lifespan_db=batch_dir / "malf_lifespan_day.duckdb",
        service_db=batch_dir / "malf_service_day.duckdb",
        report_root=request.report_root,
        validated_root=request.validated_root,
        temp_root=request.temp_root,
        run_id=f"{request.run_id}-{batch.batch_id}",
        mode="resume" if request.mode == "resume" else "segmented",
        schema_version=request.schema_version,
        core_rule_version=request.core_rule_version,
        lifespan_rule_version=request.lifespan_rule_version,
        sample_version=request.sample_version,
        service_version=request.service_version,
        source_market_base_run_id=request.source_market_base_run_id,
        start_dt=compute_start.isoformat() if compute_start else None,
        end_dt=request.scope.target_end_dt.isoformat(),
        symbols=batch.symbols,
    )


def _load_symbol_universe(source_db: Path, scope: BuildScope) -> tuple[str, ...]:
    if not source_db.exists():
        raise FileNotFoundError(f"Missing MALF source DB: {source_db}")
    with duckdb.connect(str(source_db), read_only=True) as con:
        return tuple(
            str(row[0])
            for row in con.execute(
                """
                select distinct symbol
                from market_base_bar
                where timeframe = ?
                  and price_line = ?
                  and adj_mode = ?
                  and bar_dt between ? and ?
                order by symbol
                """,
                [
                    scope.timeframe,
                    MALF_SOURCE_PRICE_LINE,
                    MALF_SOURCE_ADJ_MODE,
                    scope.target_start_dt,
                    scope.target_end_dt,
                ],
            ).fetchall()
        )


def _compute_start_dt(
    source_db: Path, symbols: tuple[str, ...], target_end_dt: date
) -> date | None:
    if not symbols:
        return target_end_dt
    placeholders = ", ".join(["?"] * len(symbols))
    with duckdb.connect(str(source_db), read_only=True) as con:
        row = con.execute(
            f"""
            select min(bar_dt)
            from market_base_bar
            where timeframe = 'day'
              and price_line = ?
              and adj_mode = ?
              and symbol in ({placeholders})
              and bar_dt <= ?
            """,
            [MALF_SOURCE_PRICE_LINE, MALF_SOURCE_ADJ_MODE, *symbols, target_end_dt],
        ).fetchone()
    return None if row is None or row[0] is None else row[0]


def _hard_fail_count(service_db: Path, run_id: str) -> int:
    with duckdb.connect(str(service_db), read_only=True) as con:
        row = con.execute(
            """
            select coalesce(sum(failed_count), 0)
            from malf_interface_audit
            where run_id = ? and severity = 'hard' and status <> 'pass'
            """,
            [run_id],
        ).fetchone()
    return 0 if row is None else int(row[0])


def _promote_batch(
    request: MalfSupplementalBuildRequest,
    batch: SymbolBatch,
    stage_request: MalfDayRequest,
) -> None:
    bootstrap_malf_core_day_database(request.core_db)
    bootstrap_malf_lifespan_day_database(request.lifespan_db)
    bootstrap_malf_service_day_database(request.service_db)
    _promote_core(request.core_db, stage_request.core_db, batch.symbols)
    _promote_lifespan(request.lifespan_db, stage_request.lifespan_db, batch.symbols)
    _promote_service(request, stage_request.service_db, batch.symbols)


def _promote_core(formal_db: Path, stage_db: Path, symbols: tuple[str, ...]) -> None:
    symbol_filter = _symbol_filter(symbols)
    with duckdb.connect(str(formal_db)) as con:
        _attach_stage(con, stage_db)
        con.execute("begin transaction")
        con.execute(
            f"""
            delete from malf_candidate_ledger
            where transition_id in (
                select transition_id from malf_transition_ledger
                where old_wave_id in (select wave_id from malf_wave_ledger where {symbol_filter})
            )
            """,
            list(symbols),
        )
        con.execute(
            f"""
            delete from malf_transition_ledger
            where old_wave_id in (select wave_id from malf_wave_ledger where {symbol_filter})
            """,
            list(symbols),
        )
        con.execute(
            f"""
            delete from malf_break_ledger
            where wave_id in (select wave_id from malf_wave_ledger where {symbol_filter})
            """,
            list(symbols),
        )
        for table in ("malf_core_state_snapshot", "malf_structure_ledger", "malf_pivot_ledger"):
            con.execute(f"delete from {table} where {symbol_filter}", list(symbols))
        con.execute(f"delete from malf_wave_ledger where {symbol_filter}", list(symbols))
        _replace_run_table(con, "malf_core_run")
        _replace_schema_table(con, "malf_schema_version", "schema_version")
        for table in (
            "malf_pivot_ledger",
            "malf_structure_ledger",
            "malf_wave_ledger",
            "malf_break_ledger",
            "malf_transition_ledger",
            "malf_candidate_ledger",
            "malf_core_state_snapshot",
        ):
            _insert_all_from_stage(con, table)
        con.execute("commit")


def _promote_lifespan(formal_db: Path, stage_db: Path, symbols: tuple[str, ...]) -> None:
    symbol_filter = _symbol_filter(symbols)
    with duckdb.connect(str(formal_db)) as con:
        _attach_stage(con, stage_db)
        con.execute("begin transaction")
        con.execute(f"delete from malf_lifespan_snapshot where {symbol_filter}", list(symbols))
        _replace_run_table(con, "malf_lifespan_run")
        _replace_schema_table(con, "malf_lifespan_profile", "run_id")
        _replace_schema_table(con, "malf_sample_version", "sample_version")
        _replace_schema_table(con, "malf_rule_version", "lifespan_rule_version")
        for table in (
            "malf_lifespan_snapshot",
            "malf_lifespan_profile",
            "malf_sample_version",
            "malf_rule_version",
        ):
            _insert_all_from_stage(con, table)
        con.execute("commit")


def _promote_service(
    request: MalfSupplementalBuildRequest,
    stage_db: Path,
    symbols: tuple[str, ...],
) -> None:
    symbol_filter = _symbol_filter(symbols)
    with duckdb.connect(str(request.service_db)) as con:
        _attach_stage(con, stage_db)
        con.execute("begin transaction")
        con.execute(
            f"""
            delete from malf_wave_position
            where {symbol_filter} and bar_dt between ? and ?
            """,
            [*symbols, request.scope.target_start_dt, request.scope.target_end_dt],
        )
        con.execute(f"delete from malf_wave_position_latest where {symbol_filter}", list(symbols))
        _replace_run_table(con, "malf_service_run")
        _replace_schema_table(con, "malf_interface_audit", "run_id")
        _insert_filtered_from_stage(
            con,
            "malf_wave_position",
            f"symbol in ({', '.join(['?'] * len(symbols))}) and bar_dt between ? and ?",
            [*symbols, request.scope.target_start_dt, request.scope.target_end_dt],
        )
        _insert_filtered_from_stage(
            con,
            "malf_wave_position_latest",
            f"symbol in ({', '.join(['?'] * len(symbols))})",
            list(symbols),
        )
        _insert_all_from_stage(con, "malf_service_run")
        _insert_all_from_stage(con, "malf_interface_audit")
        con.execute("commit")


def _attach_stage(con: duckdb.DuckDBPyConnection, stage_db: Path) -> None:
    con.execute(f"attach '{str(stage_db).replace(chr(39), chr(39) * 2)}' as stage")


def _symbol_filter(symbols: tuple[str, ...]) -> str:
    if not symbols:
        raise ValueError("Promote requires at least one symbol")
    return f"symbol in ({', '.join(['?'] * len(symbols))})"


def _replace_run_table(con: duckdb.DuckDBPyConnection, table: str) -> None:
    con.execute(f"delete from {table} where run_id in (select run_id from stage.{table})")


def _replace_schema_table(con: duckdb.DuckDBPyConnection, table: str, key: str) -> None:
    con.execute(f"delete from {table} where {key} in (select {key} from stage.{table})")


def _insert_all_from_stage(con: duckdb.DuckDBPyConnection, table: str) -> None:
    columns = _columns(con, table)
    con.execute(f"insert into {table} ({columns}) select {columns} from stage.{table}")


def _insert_filtered_from_stage(
    con: duckdb.DuckDBPyConnection,
    table: str,
    where_sql: str,
    params: list[object],
) -> None:
    columns = _columns(con, table)
    con.execute(
        f"insert into {table} ({columns}) select {columns} from stage.{table} where {where_sql}",
        params,
    )


def _columns(con: duckdb.DuckDBPyConnection, table: str) -> str:
    names = [str(row[1]) for row in con.execute(f"pragma table_info('{table}')").fetchall()]
    return ", ".join(names)
