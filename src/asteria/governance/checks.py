from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from asteria.governance.docs_sync import run_docs_sync_checks

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


@dataclass(frozen=True)
class Finding:
    path: Path
    message: str


REQUIRED_MODULE_DOCS = [
    "00-authority-design-v1.md",
    "01-semantic-contract-v1.md",
    "02-database-schema-spec-v1.md",
    "03-runner-contract-v1.md",
    "04-audit-spec-v1.md",
    "05-build-card-v1.md",
]
MAINLINE_MODULES = {
    "malf",
    "alpha",
    "signal",
    "position",
    "portfolio_plan",
    "trade",
    "system_readout",
}
REGISTRY_PATHS = [
    "governance/module_gate_registry.toml",
    "governance/database_topology_registry.toml",
    "governance/historical_ledger_registry.toml",
]
BAD_OFFICIAL_SOURCE_ROLES = {"mock", "legacy_downstream"}
IGNORED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}


def _load_toml(path: Path, findings: list[Finding]) -> dict[str, Any] | None:
    if not path.exists():
        findings.append(Finding(path, "required governance registry is missing"))
        return None
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _load_governance(repo_root: Path) -> dict[str, Any]:
    with (repo_root / "pyproject.toml").open("rb") as handle:
        data = tomllib.load(handle)
    return data["tool"]["asteria"]["governance"]


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for _ in handle)


def _check_required_docs(repo_root: Path, required_docs: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for raw_path in required_docs:
        path = repo_root / raw_path
        if not path.exists():
            findings.append(Finding(path, "required governance document is missing"))
    return findings


def _check_file_sizes(repo_root: Path, governance: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    limits = {
        ".py": int(governance["max_python_file_lines"]),
        ".md": int(governance["max_markdown_file_lines"]),
    }
    script_limit = int(governance["max_script_file_lines"])

    for path in repo_root.rglob("*"):
        if not path.is_file() or IGNORED_PARTS.intersection(path.parts):
            continue
        if path.suffix not in limits:
            continue
        limit = (
            script_limit
            if path.suffix == ".py" and "scripts" in path.parts
            else limits[path.suffix]
        )
        count = _line_count(path)
        if count > limit:
            findings.append(Finding(path, f"file has {count} lines, limit is {limit}"))
    return findings


def _module_map(gate_registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {module["module_id"]: module for module in gate_registry.get("modules", [])}


def _check_gate_registry(repo_root: Path, gate_registry: dict[str, Any]) -> list[Finding]:
    path = repo_root / "governance" / "module_gate_registry.toml"
    findings: list[Finding] = []
    modules = _module_map(gate_registry)
    active = gate_registry.get("active_mainline_module")
    build_allowed = [
        module_id
        for module_id, module in modules.items()
        if module_id in MAINLINE_MODULES and bool(module.get("allow_build"))
    ]

    if len(build_allowed) != 1:
        findings.append(Finding(path, "only one mainline module may allow build"))
    if active not in build_allowed:
        findings.append(
            Finding(path, "active_mainline_module must be the build-allowed mainline module")
        )
    if "system" in modules or "system_readout" not in modules:
        findings.append(
            Finding(path, "module_id must be system_readout; system is only a DB display shorthand")
        )

    for module_id, module in modules.items():
        for field in ["display_name", "status", "doc_path", "allow_build"]:
            if field not in module:
                findings.append(
                    Finding(path, f"module {module_id} missing required gate field: {field}")
                )
        doc_path = repo_root / str(module.get("doc_path", ""))
        if not doc_path.exists():
            findings.append(Finding(path, f"module {module_id} doc_path does not exist"))
            continue
        for doc_name in REQUIRED_MODULE_DOCS:
            if not (doc_path / doc_name).exists():
                findings.append(
                    Finding(path, f"module {module_id} missing required six-doc file: {doc_name}")
                )
    return findings


def _check_database_topology(
    repo_root: Path,
    gate_registry: dict[str, Any],
    topology_registry: dict[str, Any],
) -> list[Finding]:
    path = repo_root / "governance" / "database_topology_registry.toml"
    findings: list[Finding] = []
    modules = _module_map(gate_registry)
    databases = topology_registry.get("databases", [])
    registered_names: set[str] = set()
    required_fields = {
        "db_name",
        "module_id",
        "grain",
        "ledger_role",
        "writer",
        "allowed_modes",
        "checkpoint_policy",
        "checkpoint_key",
        "replay_scope",
        "promote_rule",
    }

    for database in databases:
        db_name = str(database.get("db_name", ""))
        missing = sorted(required_fields - database.keys())
        for field in missing:
            findings.append(
                Finding(path, f"database {db_name or '<unknown>'} missing required field: {field}")
            )
        if not db_name.endswith(".duckdb"):
            findings.append(Finding(path, f"database name must end with .duckdb: {db_name}"))
        if db_name in registered_names:
            findings.append(Finding(path, f"database registered more than once: {db_name}"))
        registered_names.add(db_name)
        module_id = database.get("module_id")
        if module_id not in modules:
            findings.append(
                Finding(path, f"database {db_name} references unknown module: {module_id}")
            )
        for list_field in ["allowed_modes", "checkpoint_key", "replay_scope"]:
            if not isinstance(database.get(list_field), list) or not database[list_field]:
                findings.append(
                    Finding(path, f"database {db_name} requires non-empty {list_field}")
                )

    topology_doc = repo_root / "docs" / "01-architecture" / "01-database-topology-v1.md"
    if topology_doc.exists():
        doc_names = _extract_duckdb_names(topology_doc)
        for db_name in sorted(doc_names - registered_names):
            findings.append(
                Finding(topology_doc, f"database topology doc mentions unregistered DB: {db_name}")
            )
    return findings


def _extract_duckdb_names(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    names: set[str] = set()
    for match in re.finditer(r"\b([A-Za-z0-9_]+\.duckdb)\b", text):
        if match.start() > 0 and text[match.start() - 1] == "<":
            continue
        name = match.group(1)
        if name != "name.duckdb":
            names.add(name)
    return names


def _check_historical_ledger(
    repo_root: Path,
    gate_registry: dict[str, Any],
    historical_registry: dict[str, Any],
) -> list[Finding]:
    path = repo_root / "governance" / "historical_ledger_registry.toml"
    findings: list[Finding] = []
    expected = {
        "source_authority": "tdx",
        "legacy_raw_base_role": "read_only_audit",
        "legacy_downstream_role": "evidence_only",
        "mock_role": "tests_only",
        "initial_batch_strategy": "time_window_first",
    }
    for key, value in expected.items():
        if historical_registry.get(key) != value:
            findings.append(Finding(path, f"historical ledger {key} must be {value}"))

    for key, required in {
        "initialization_modes": {"bounded", "segmented", "full", "resume", "audit-only"},
        "incremental_modes": {"daily_incremental", "resume", "audit-only"},
        "logical_ledger_required": {
            "source_manifest",
            "run_ledger",
            "checkpoint",
            "replay_scope",
            "audit_summary",
        },
    }.items():
        actual = set(historical_registry.get(key, []))
        if not required.issubset(actual):
            findings.append(Finding(path, f"historical ledger {key} missing required values"))

    modules = _module_map(gate_registry)
    for step in historical_registry.get("daily_incremental_chain", []):
        module_id = step.get("module_id")
        module = modules.get(module_id)
        if module is None:
            findings.append(
                Finding(path, f"daily incremental chain references unknown module: {module_id}")
            )
            continue
        if _daily_chain_module_allowed(module, bool(step.get("protocol_only"))):
            continue
        findings.append(
            Finding(
                path,
                "daily incremental chain references module that is not released or active-allowed",
            )
        )
    return findings


def _daily_chain_module_allowed(module: dict[str, Any], protocol_only: bool) -> bool:
    status = module.get("status")
    if status in {"released", "integrated"} or bool(module.get("allow_build")):
        return True
    if module.get("module_id") == "data" and status == "foundation_contract":
        return True
    return protocol_only and module.get("module_id") == "pipeline"


def _check_module_api_contracts(
    repo_root: Path,
    gate_registry: dict[str, Any],
    topology_registry: dict[str, Any],
) -> list[Finding]:
    findings: list[Finding] = []
    contract_root = repo_root / "governance" / "module_api_contracts"
    modules = _module_map(gate_registry)
    registered_dbs = {database["db_name"] for database in topology_registry.get("databases", [])}

    for module_id in modules:
        contract_path = contract_root / f"{module_id}.toml"
        contract = _load_toml(contract_path, findings)
        if contract is None:
            continue
        findings.extend(_check_one_contract(contract_path, contract, module_id, registered_dbs))
    return findings


def _check_one_contract(
    path: Path,
    contract: dict[str, Any],
    expected_module_id: str,
    registered_dbs: set[str],
) -> list[Finding]:
    findings: list[Finding] = []
    for field in [
        "module_id",
        "display_name",
        "contract_version",
        "status",
        "run_modes",
        "resume_behavior",
        "source_manifest_fields",
        "forbidden_inputs",
        "forbidden_outputs",
    ]:
        if field not in contract:
            findings.append(Finding(path, f"module API contract missing required field: {field}"))
    if contract.get("module_id") != expected_module_id:
        findings.append(Finding(path, "module API contract module_id does not match registry"))
    if contract.get("module_id") == "system":
        findings.append(
            Finding(path, "module_id must be system_readout; system.duckdb is the DB name")
        )

    for input_item in contract.get("official_inputs", []):
        if input_item.get("source_role") in BAD_OFFICIAL_SOURCE_ROLES:
            findings.append(
                Finding(path, "official input cannot use mock or legacy downstream source")
            )
        if (
            input_item.get("input_type") == "database"
            and input_item.get("db_name") not in registered_dbs
        ):
            findings.append(
                Finding(path, f"official input DB is not registered: {input_item.get('db_name')}")
            )
        for field in ["source_role", "required_fields"]:
            if field not in input_item:
                findings.append(Finding(path, f"official input missing required field: {field}"))

    for output_item in contract.get("official_outputs", []):
        db_name = output_item.get("db_name")
        if db_name not in registered_dbs:
            findings.append(Finding(path, f"official output DB is not registered: {db_name}"))
        for field in ["table", "natural_key", "public_fields", "version_fields"]:
            if not output_item.get(field):
                findings.append(Finding(path, f"official output missing required field: {field}"))
    return findings


def _check_forbidden_repo_artifacts(repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in repo_root.rglob("*"):
        if not path.is_file() or IGNORED_PARTS.intersection(path.parts):
            continue
        if path.name.endswith((".duckdb", ".duckdb.wal", ".duckdb.tmp")):
            findings.append(Finding(path, "generated database artifact is inside repo"))

    for name in [
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "reports",
        "artifacts",
        "tmp",
        "temp",
    ]:
        path = repo_root / name
        if path.exists():
            findings.append(Finding(path, "generated cache/report artifact is inside repo root"))
    return findings


def _check_forbidden_pre_gate_sources(
    repo_root: Path, gate_registry: dict[str, Any]
) -> list[Finding]:
    findings: list[Finding] = []
    for module_id, module in _module_map(gate_registry).items():
        if (
            bool(module.get("allow_build"))
            or module.get("exception") == "bounded_bootstrap_support"
        ):
            continue
        script_dir = repo_root / "scripts" / module_id
        if not script_dir.exists():
            continue
        for script_path in script_dir.glob("run_*.py"):
            findings.append(Finding(script_path, "pre-gate module has forbidden formal runner"))
        db_create_scripts = set(script_dir.glob("create_*.py")) | set(
            script_dir.glob("*_schema.py")
        )
        for script_path in sorted(db_create_scripts):
            findings.append(
                Finding(script_path, "pre-gate module has forbidden formal DB create script")
            )
    return findings


def run_checks(repo_root: Path) -> list[Finding]:
    governance = _load_governance(repo_root)
    findings: list[Finding] = []
    findings.extend(_check_required_docs(repo_root, list(governance["required_docs"])))
    findings.extend(_check_file_sizes(repo_root, governance))

    registries: dict[str, dict[str, Any]] = {}
    for raw_path in REGISTRY_PATHS:
        registry = _load_toml(repo_root / raw_path, findings)
        if registry is not None:
            registries[raw_path] = registry
    if len(registries) != len(REGISTRY_PATHS):
        return findings

    gate_registry = registries["governance/module_gate_registry.toml"]
    topology_registry = registries["governance/database_topology_registry.toml"]
    historical_registry = registries["governance/historical_ledger_registry.toml"]
    findings.extend(_check_gate_registry(repo_root, gate_registry))
    findings.extend(_check_database_topology(repo_root, gate_registry, topology_registry))
    findings.extend(_check_historical_ledger(repo_root, gate_registry, historical_registry))
    findings.extend(_check_module_api_contracts(repo_root, gate_registry, topology_registry))
    findings.extend(_check_forbidden_pre_gate_sources(repo_root, gate_registry))
    findings.extend(
        Finding(finding.path, finding.message) for finding in run_docs_sync_checks(repo_root)
    )
    findings.extend(_check_forbidden_repo_artifacts(repo_root))
    return findings
