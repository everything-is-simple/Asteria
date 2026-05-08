from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from asteria.pipeline.contracts import PipelineBuildRequest

FULL_CHAIN_GATE_MODULES = (
    "malf",
    "alpha",
    "signal",
    "position",
    "portfolio_plan",
    "trade",
    "system_readout",
)


@dataclass(frozen=True)
class FullChainSourceEntry:
    module_name: str
    source_db: str
    source_run_id: str
    source_release_version: str
    source_schema_version: str
    source_audit_ref: str
    source_audit_status: str


@dataclass(frozen=True)
class PipelineStep:
    step_seq: int
    module_name: str
    step_name: str
    source_db: str
    source_run_id: str
    source_release_version: str

    @property
    def batch_id(self) -> str:
        return f"step-{self.step_seq}-{self.module_name}"


def build_gate_snapshot_rows(
    request: PipelineBuildRequest,
    registry: dict[str, Any],
    *,
    gate_registry_version: str,
    created_at: object,
) -> list[list[object]]:
    modules = {module["module_id"]: module for module in registry.get("modules", [])}
    pairs = [
        ("registry", "active_mainline_module", str(registry.get("active_mainline_module", ""))),
        (
            "registry",
            "current_allowed_next_card",
            str(registry.get("current_allowed_next_card", "")),
        ),
        ("pipeline", "status", str(modules["pipeline"].get("status", ""))),
        ("pipeline", "next_card", str(modules["pipeline"].get("next_card", ""))),
    ]
    if request.module_scope == "system_readout":
        pairs.extend(
            [
                (
                    "system_readout",
                    "proof_status",
                    str(modules["system_readout"].get("proof_status", "")),
                ),
                (
                    "system_readout",
                    "next_card",
                    str(modules["system_readout"].get("next_card", "")),
                ),
            ]
        )
    else:
        for module_name in FULL_CHAIN_GATE_MODULES:
            pairs.append(
                (
                    module_name,
                    "proof_status",
                    str(modules[module_name].get("proof_status", "")),
                )
            )
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


def build_manifest_rows(
    request: PipelineBuildRequest,
    *,
    created_at: object,
    gate_registry_version: str,
    steps: list[PipelineStep],
    full_chain_sources: list[FullChainSourceEntry],
) -> list[list[object]]:
    rows = [
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
    ]
    if request.module_scope == "system_readout":
        rows.insert(
            0,
            _manifest_row(
                request,
                created_at,
                artifact_name="source_system_db",
                artifact_role="source_db",
                artifact_path=str(request.source_system_db),
                source_ref=request.source_chain_release_version,
                source_type="database",
            ),
        )
    else:
        rows.extend(
            _manifest_row(
                request,
                created_at,
                artifact_name=f"source_{entry.module_name}_db",
                artifact_role="source_db",
                artifact_path=entry.source_db,
                source_ref=entry.source_release_version,
                source_type="database",
            )
            for entry in full_chain_sources
        )
        rows.append(
            _manifest_row(
                request,
                created_at,
                artifact_name="source_system_db",
                artifact_role="source_db",
                artifact_path=str(request.source_system_db),
                source_ref=request.source_chain_release_version,
                source_type="database",
            )
        )
    rows.extend(
        _manifest_row(
            request,
            created_at,
            artifact_name=f"step_{step.step_seq}_checkpoint",
            artifact_role="step_checkpoint",
            artifact_path=str(request.step_checkpoint_path(step.step_seq)),
            source_ref=step.module_name,
            source_type="json",
        )
        for step in steps
    )
    return rows


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
