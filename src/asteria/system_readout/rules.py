from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime

from asteria.system_readout.contracts import SystemReadoutBuildRequest


@dataclass(frozen=True)
class SourceManifestInput:
    module_name: str
    source_db: str
    source_run_id: str
    source_release_version: str
    source_schema_version: str
    source_audit_ref: str
    source_audit_status: str


@dataclass(frozen=True)
class ModuleStatusInput:
    module_name: str
    module_release_version: str
    module_run_id: str
    module_status: str
    source_audit_ref: str
    source_audit_status: str


@dataclass(frozen=True)
class ReadoutRefs:
    malf_ref: str | None
    alpha_ref: str | None
    signal_ref: str | None
    position_ref: str | None
    portfolio_plan_ref: str | None
    trade_ref: str | None


@dataclass(frozen=True)
class ReadoutInput:
    symbol: str
    timeframe: str
    readout_dt: date
    refs: ReadoutRefs
    wave_core_state: str | None
    system_state: str | None
    has_upstream_audit_gap: bool = False


@dataclass(frozen=True)
class SystemReadoutRows:
    source_manifests: list[tuple[object, ...]]
    module_statuses: list[tuple[object, ...]]
    chain_readouts: list[tuple[object, ...]]
    summary_snapshots: list[tuple[object, ...]]
    audit_snapshots: list[tuple[object, ...]]


def classify_readout_status(refs: ReadoutRefs, has_upstream_audit_gap: bool = False) -> str:
    if has_upstream_audit_gap:
        return "audit_gap"
    if (
        refs.signal_ref
        and refs.alpha_ref is None
        or refs.position_ref
        and refs.signal_ref is None
        or refs.portfolio_plan_ref
        and refs.position_ref is None
        or refs.trade_ref
        and refs.portfolio_plan_ref is None
    ):
        return "source_gap"
    if all(
        [
            refs.malf_ref,
            refs.alpha_ref,
            refs.signal_ref,
            refs.position_ref,
            refs.portfolio_plan_ref,
            refs.trade_ref,
        ]
    ):
        return "complete"
    if any(
        [
            refs.malf_ref,
            refs.alpha_ref,
            refs.signal_ref,
            refs.position_ref,
            refs.portfolio_plan_ref,
            refs.trade_ref,
        ]
    ):
        return "partial"
    return "source_gap"


def build_system_readout_rows(
    source_manifests: list[SourceManifestInput],
    module_statuses: list[ModuleStatusInput],
    readouts: list[ReadoutInput],
    request: SystemReadoutBuildRequest,
    created_at: datetime,
) -> SystemReadoutRows:
    manifest_rows: list[tuple[object, ...]] = [
        (
            _manifest_id(request.run_id, item.module_name),
            request.run_id,
            item.module_name,
            item.source_db,
            item.source_run_id,
            item.source_release_version,
            item.source_schema_version,
            item.source_audit_ref,
            item.source_audit_status,
            created_at,
        )
        for item in source_manifests
    ]
    module_rows: list[tuple[object, ...]] = []
    for item in module_statuses:
        module_rows.append(
            (
                f"{request.run_id}|{item.module_name}|{item.module_release_version}",
                request.run_id,
                item.module_name,
                item.module_release_version,
                item.module_run_id,
                item.module_status,
                _manifest_id(request.run_id, item.module_name),
                item.source_audit_ref,
                item.source_audit_status,
                created_at,
            )
        )
    ordered_readouts = sorted(readouts, key=lambda row: (row.symbol, row.readout_dt))
    chain_rows: list[tuple[object, ...]] = []
    summary_rows: list[tuple[object, ...]] = []
    for row in ordered_readouts:
        status = classify_readout_status(row.refs, row.has_upstream_audit_gap)
        chain_rows.append(
            (
                _readout_id(
                    request.run_id,
                    row.symbol,
                    row.readout_dt,
                    request.system_readout_version,
                ),
                request.run_id,
                row.symbol,
                row.timeframe,
                row.readout_dt,
                status,
                row.refs.malf_ref,
                row.refs.alpha_ref,
                row.refs.signal_ref,
                row.refs.position_ref,
                row.refs.portfolio_plan_ref,
                row.refs.trade_ref,
                row.wave_core_state,
                row.system_state,
                request.source_chain_release_version,
                request.system_readout_version,
                created_at,
            )
        )
        summary_rows.append(
            (
                f"{request.run_id}|summary|{row.symbol}|{row.readout_dt.isoformat()}",
                request.run_id,
                row.symbol,
                row.readout_dt,
                json.dumps(
                    {
                        "symbol": row.symbol,
                        "readout_dt": row.readout_dt.isoformat(),
                        "readout_status": status,
                        "has_trade_ref": row.refs.trade_ref is not None,
                    },
                    ensure_ascii=False,
                ),
                status,
                request.source_chain_release_version,
                request.system_readout_version,
                created_at,
            )
        )
    audit_rows: list[tuple[object, ...]] = [
        (
            f"{request.run_id}|audit_snapshot|{item.module_name}",
            request.run_id,
            "module_release",
            ordered_readouts[0].readout_dt if ordered_readouts else date.today(),
            item.module_name,
            item.source_audit_ref,
            item.source_audit_status,
            request.system_readout_version,
            created_at,
        )
        for item in module_statuses
    ]
    return SystemReadoutRows(
        source_manifests=manifest_rows,
        module_statuses=module_rows,
        chain_readouts=chain_rows,
        summary_snapshots=summary_rows,
        audit_snapshots=audit_rows,
    )


def _manifest_id(run_id: str, module_name: str) -> str:
    return f"{run_id}|{module_name}"


def _readout_id(run_id: str, symbol: str, readout_dt: date, version: str) -> str:
    return f"{run_id}|{symbol}|{readout_dt.isoformat()}|{version}"
