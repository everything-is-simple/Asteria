from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import duckdb

from asteria.build_orchestration import BuildManifest, BuildScope
from asteria.pipeline.contracts import PipelineBuildRequest
from asteria.pipeline.runtime_records import (
    FullChainSourceEntry,
    PipelineStep,
    build_gate_snapshot_rows,
    build_manifest_rows,
)

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


AUTHORIZED_SINGLE_MODULE_NEXT_CARD = "pipeline_single_module_orchestration_build_card"
AUTHORIZED_FULL_CHAIN_NEXT_CARD = "pipeline_full_chain_dry_run_card"
ALPHA_SOURCE_MODULES = ("alpha_bof", "alpha_tst", "alpha_pb", "alpha_cpb", "alpha_bpb")


@dataclass(frozen=True)
class SourceSystemRun:
    run_id: str
    schema_version: str
    system_readout_version: str
    readout_count: int
    source_manifest_count: int
    module_status_count: int
    min_readout_dt: date
    max_readout_dt: date


@dataclass(frozen=True)
class PipelineRuntimeInputs:
    gate_registry_version: str
    source_run: SourceSystemRun
    steps: list[PipelineStep]
    step_rows: list[list[object]]
    gate_rows: list[list[object]]
    manifest_rows: list[list[object]]
    manifest: BuildManifest


def load_runtime_inputs(
    request: PipelineBuildRequest,
    *,
    created_at: object,
) -> PipelineRuntimeInputs:
    registry = _load_gate_registry(request)
    source_run = _load_source_system_run(request)
    gate_registry_version = str(registry.get("registry_version", "unknown"))
    full_chain_sources = (
        _load_full_chain_sources(request, source_run.run_id)
        if request.module_scope == "full_chain_day"
        else []
    )
    steps = _build_steps(request, created_at, source_run, full_chain_sources)
    gate_rows = build_gate_snapshot_rows(
        request,
        registry,
        gate_registry_version=gate_registry_version,
        created_at=created_at,
    )
    manifest = BuildManifest(
        run_id=request.run_id,
        module_id="pipeline",
        mode=request.mode,
        db_names=("pipeline.duckdb",),
        scope=BuildScope(
            timeframe="day",
            target_start_dt=source_run.min_readout_dt,
            target_end_dt=source_run.max_readout_dt,
            compute_start_dt=source_run.min_readout_dt,
            compute_end_dt=source_run.max_readout_dt,
        ),
        schema_version=request.schema_version,
        rule_versions={
            "pipeline_version": request.pipeline_version,
            "source_system_readout_version": source_run.system_readout_version,
        },
        source_run_id=request.source_chain_release_version,
        batches=(),
    )
    manifest_rows = build_manifest_rows(
        request,
        created_at=created_at,
        gate_registry_version=gate_registry_version,
        steps=steps,
        full_chain_sources=full_chain_sources,
    )
    step_rows = [
        [
            f"{request.run_id}|{step.step_seq}",
            request.run_id,
            step.step_seq,
            step.module_name,
            step.step_name,
            "staged",
            step.source_db,
            step.source_run_id,
            step.source_release_version,
            created_at,
            created_at,
            created_at,
        ]
        for step in steps
    ]
    return PipelineRuntimeInputs(
        gate_registry_version=gate_registry_version,
        source_run=source_run,
        steps=steps,
        step_rows=step_rows,
        gate_rows=gate_rows,
        manifest_rows=manifest_rows,
        manifest=manifest,
    )


def _load_gate_registry(request: PipelineBuildRequest) -> dict[str, Any]:
    with request.gate_registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    modules = {module["module_id"]: module for module in registry.get("modules", [])}
    pipeline_module = modules.get("pipeline", {})
    system_module = modules.get("system_readout", {})
    if (
        request.mode in {"audit-only", "resume"}
        and pipeline_module.get("status") == "released"
        and pipeline_module.get("proof_run_id") == request.run_id
    ):
        return registry

    if request.module_scope == "system_readout":
        if registry.get("current_allowed_next_card") != AUTHORIZED_SINGLE_MODULE_NEXT_CARD:
            raise ValueError("single-module orchestration build is not currently authorized")
        if pipeline_module.get("status") != "freeze_review_passed":
            raise ValueError("pipeline status must remain freeze_review_passed before execution")
        if pipeline_module.get("next_card") != AUTHORIZED_SINGLE_MODULE_NEXT_CARD:
            raise ValueError("pipeline next_card does not match single-module orchestration card")
    else:
        if registry.get("current_allowed_next_card") != AUTHORIZED_FULL_CHAIN_NEXT_CARD:
            raise ValueError("full-chain dry-run is not currently authorized")
        if pipeline_module.get("status") != "released":
            raise ValueError("pipeline status must remain released before full-chain dry-run")
        if pipeline_module.get("next_card") != AUTHORIZED_FULL_CHAIN_NEXT_CARD:
            raise ValueError("pipeline next_card does not match full-chain dry-run card")
        if pipeline_module.get("proof_run_id") != (
            "pipeline-single-module-orchestration-build-card-20260508-01"
        ):
            raise ValueError("full-chain dry-run requires single-module orchestration proof first")

    if registry.get("active_mainline_module") != "system_readout":
        raise ValueError("pipeline orchestration requires active mainline system_readout")
    if system_module.get("status") != "released":
        raise ValueError("system_readout must remain released for pipeline orchestration sample")
    return registry


def _load_source_system_run(request: PipelineBuildRequest) -> SourceSystemRun:
    if not request.source_system_db.exists():
        raise FileNotFoundError(f"Missing source system DB: {request.source_system_db}")
    with duckdb.connect(str(request.source_system_db), read_only=True) as con:
        run_row = con.execute(
            """
            select run_id, schema_version, system_readout_version, readout_count,
                   source_manifest_count, module_status_count
            from system_readout_run
            where status = 'completed'
            order by created_at desc
            limit 1
            """
        ).fetchone()
        if run_row is None:
            raise ValueError("missing completed system_readout_run row")
        if str(run_row[0]) != request.source_chain_release_version:
            raise ValueError("source system release version does not match latest completed run")
        date_row = con.execute(
            """
            select min(readout_dt), max(readout_dt)
            from system_chain_readout
            where system_readout_run_id = ?
            """,
            [request.source_chain_release_version],
        ).fetchone()
    if date_row is None or date_row[0] is None or date_row[1] is None:
        raise ValueError("system readout source run is missing bounded readout rows")
    return SourceSystemRun(
        run_id=str(run_row[0]),
        schema_version=str(run_row[1]),
        system_readout_version=str(run_row[2]),
        readout_count=int(run_row[3]),
        source_manifest_count=int(run_row[4]),
        module_status_count=int(run_row[5]),
        min_readout_dt=_coerce_date(date_row[0]),
        max_readout_dt=_coerce_date(date_row[1]),
    )


def _load_full_chain_sources(
    request: PipelineBuildRequest,
    source_run_id: str,
) -> list[FullChainSourceEntry]:
    with duckdb.connect(str(request.source_system_db), read_only=True) as con:
        rows = con.execute(
            """
            select module_name, source_db, source_run_id, source_release_version,
                   source_schema_version, source_audit_ref, source_audit_status
            from system_source_manifest
            where system_readout_run_id = ?
            order by module_name
            """,
            [source_run_id],
        ).fetchall()
    if not rows:
        raise ValueError("system readout source manifest is missing full-chain inputs")
    return [
        FullChainSourceEntry(
            module_name=str(row[0]),
            source_db=str(row[1]),
            source_run_id=str(row[2]),
            source_release_version=str(row[3]),
            source_schema_version=str(row[4]),
            source_audit_ref="" if row[5] is None else str(row[5]),
            source_audit_status=str(row[6]),
        )
        for row in rows
    ]


def _build_steps(
    request: PipelineBuildRequest,
    created_at: object,
    source_run: SourceSystemRun,
    full_chain_sources: list[FullChainSourceEntry],
) -> list[PipelineStep]:
    if request.module_scope == "system_readout":
        return [
            PipelineStep(
                step_seq=1,
                module_name="system_readout",
                step_name="single_module_orchestration",
                source_db=str(request.source_system_db),
                source_run_id=source_run.run_id,
                source_release_version=request.source_chain_release_version,
            )
        ]

    source_map = {entry.module_name: entry for entry in full_chain_sources}
    alpha_entries = [source_map[name] for name in ALPHA_SOURCE_MODULES if name in source_map]
    if len(alpha_entries) != len(ALPHA_SOURCE_MODULES):
        raise ValueError("system source manifest is missing one or more alpha family inputs")
    required_entries = ["malf", "signal", "position", "portfolio_plan", "trade"]
    for module_name in required_entries:
        if module_name not in source_map:
            raise ValueError(f"system source manifest is missing {module_name} input")

    alpha_run_id = alpha_entries[0].source_run_id
    alpha_release_version = alpha_entries[0].source_release_version
    return [
        PipelineStep(
            step_seq=1,
            module_name="malf",
            step_name="full_chain_dry_run",
            source_db=source_map["malf"].source_db,
            source_run_id=source_map["malf"].source_run_id,
            source_release_version=source_map["malf"].source_release_version,
        ),
        PipelineStep(
            step_seq=2,
            module_name="alpha",
            step_name="full_chain_dry_run",
            source_db=str(request.source_system_db.parent / "alpha_*.duckdb"),
            source_run_id=alpha_run_id,
            source_release_version=alpha_release_version,
        ),
        PipelineStep(
            step_seq=3,
            module_name="signal",
            step_name="full_chain_dry_run",
            source_db=source_map["signal"].source_db,
            source_run_id=source_map["signal"].source_run_id,
            source_release_version=source_map["signal"].source_release_version,
        ),
        PipelineStep(
            step_seq=4,
            module_name="position",
            step_name="full_chain_dry_run",
            source_db=source_map["position"].source_db,
            source_run_id=source_map["position"].source_run_id,
            source_release_version=source_map["position"].source_release_version,
        ),
        PipelineStep(
            step_seq=5,
            module_name="portfolio_plan",
            step_name="full_chain_dry_run",
            source_db=source_map["portfolio_plan"].source_db,
            source_run_id=source_map["portfolio_plan"].source_run_id,
            source_release_version=source_map["portfolio_plan"].source_release_version,
        ),
        PipelineStep(
            step_seq=6,
            module_name="trade",
            step_name="full_chain_dry_run",
            source_db=source_map["trade"].source_db,
            source_run_id=source_map["trade"].source_run_id,
            source_release_version=source_map["trade"].source_release_version,
        ),
        PipelineStep(
            step_seq=7,
            module_name="system_readout",
            step_name="full_chain_dry_run",
            source_db=str(request.source_system_db),
            source_run_id=source_run.run_id,
            source_release_version=request.source_chain_release_version,
        ),
    ]


def _coerce_date(value: object) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise TypeError(f"unsupported date value: {value!r}")
