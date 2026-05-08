from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import duckdb

from asteria.build_orchestration import BuildManifest, BuildScope
from asteria.pipeline.contracts import PipelineBuildRequest

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


AUTHORIZED_NEXT_CARD = "pipeline_single_module_orchestration_build_card"


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
    step_started_at = created_at
    step_rows = [
        [
            f"{request.run_id}|1",
            request.run_id,
            1,
            request.module_scope,
            "single_module_orchestration",
            "staged",
            str(request.source_system_db),
            source_run.run_id,
            request.source_chain_release_version,
            step_started_at,
            step_started_at,
            created_at,
        ]
    ]
    gate_rows = _build_gate_snapshot_rows(request, registry, gate_registry_version, created_at)
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
    manifest_rows = [
        _manifest_row(
            request,
            created_at,
            artifact_name="source_system_db",
            artifact_role="source_db",
            artifact_path=str(request.source_system_db),
            source_ref=request.source_chain_release_version,
            source_type="database",
        ),
        _manifest_row(
            request,
            created_at,
            artifact_name="target_pipeline_db",
            artifact_role="target_db",
            artifact_path=str(request.target_pipeline_db),
            source_ref=request.schema_version,
            source_type="database",
        ),
        _manifest_row(
            request,
            created_at,
            artifact_name="module_gate_registry",
            artifact_role="gate_registry",
            artifact_path=str(request.gate_registry_path),
            source_ref=gate_registry_version,
            source_type="toml",
        ),
        _manifest_row(
            request,
            created_at,
            artifact_name="runtime_manifest",
            artifact_role="runtime_manifest",
            artifact_path=str(request.runtime_manifest_path),
            source_ref=request.pipeline_version,
            source_type="json",
        ),
        _manifest_row(
            request,
            created_at,
            artifact_name="step_1_checkpoint",
            artifact_role="step_checkpoint",
            artifact_path=str(request.step_checkpoint_path(1)),
            source_ref=request.run_id,
            source_type="json",
        ),
    ]
    return PipelineRuntimeInputs(
        gate_registry_version=gate_registry_version,
        source_run=source_run,
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
    if registry.get("current_allowed_next_card") != AUTHORIZED_NEXT_CARD:
        raise ValueError("single-module orchestration build is not currently authorized")
    if registry.get("active_mainline_module") != "system_readout":
        raise ValueError(
            "single-module orchestration build requires active mainline system_readout"
        )
    if pipeline_module.get("status") != "freeze_review_passed":
        raise ValueError("pipeline status must remain freeze_review_passed before execution")
    if pipeline_module.get("next_card") != AUTHORIZED_NEXT_CARD:
        raise ValueError("pipeline next_card does not match single-module orchestration card")
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


def _build_gate_snapshot_rows(
    request: PipelineBuildRequest,
    registry: dict[str, Any],
    gate_registry_version: str,
    created_at: object,
) -> list[list[object]]:
    modules = {module["module_id"]: module for module in registry.get("modules", [])}
    pipeline_module = modules["pipeline"]
    system_module = modules["system_readout"]
    pairs = [
        ("registry", "active_mainline_module", str(registry.get("active_mainline_module", ""))),
        (
            "registry",
            "current_allowed_next_card",
            str(registry.get("current_allowed_next_card", "")),
        ),
        ("pipeline", "status", str(pipeline_module.get("status", ""))),
        ("pipeline", "next_card", str(pipeline_module.get("next_card", ""))),
        ("system_readout", "proof_status", str(system_module.get("proof_status", ""))),
        ("system_readout", "next_card", str(system_module.get("next_card", ""))),
    ]
    return [
        [
            f"{request.run_id}|{module_name}|{gate_name}",
            request.run_id,
            module_name,
            gate_name,
            gate_value,
            gate_registry_version,
            created_at,
        ]
        for module_name, gate_name, gate_value in pairs
    ]


def _manifest_row(
    request: PipelineBuildRequest,
    created_at: object,
    *,
    artifact_name: str,
    artifact_role: str,
    artifact_path: str,
    source_ref: str,
    source_type: str,
) -> list[object]:
    return [
        f"{request.run_id}|{artifact_name}|{artifact_role}",
        request.run_id,
        artifact_name,
        artifact_role,
        artifact_path,
        source_ref,
        source_type,
        "",
        created_at,
    ]


def _coerce_date(value: object) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise TypeError(f"unsupported date value: {value!r}")
