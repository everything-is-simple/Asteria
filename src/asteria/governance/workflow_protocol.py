from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


Severity = Literal["error", "warning"]


@dataclass(frozen=True)
class WorkflowFinding:
    path: Path
    message: str
    severity: Severity = "error"


AUTHORITY_DOCS = (
    "README.md",
    "AGENTS.md",
    "docs/00-governance/00-asteria-refactor-charter-v1.md",
    "docs/00-governance/06-asteria-6a-workflow-protocol-v1.md",
    "docs/01-architecture/00-mainline-authoritative-map-v1.md",
    "docs/01-architecture/01-database-topology-v1.md",
    "governance/module_gate_registry.toml",
    "docs/03-refactor/00-module-gate-ledger-v1.md",
    "docs/03-refactor/04-asteria-full-system-roadmap-v1.md",
    "docs/04-execution/00-conclusion-index-v1.md",
)
MCP_SERVERS = ("codebase-retrieval", "context7", "fetch", "sequential-thinking")
PLUGIN_MANIFEST = Path("plugins/asteria-workflow/.codex-plugin/plugin.json")
HOOKS_CONFIG = Path("plugins/asteria-workflow/hooks.json")
MARKETPLACE = Path(".agents/plugins/marketplace.json")
AUTOMATION_ID = "asteria-daily-workflow-drift-scan"


def run_workflow_checks(
    repo_root: Path,
    *,
    codex_home: Path | None = None,
    include_user_tools: bool = True,
) -> list[WorkflowFinding]:
    repo_root = repo_root.resolve()
    findings: list[WorkflowFinding] = []
    findings.extend(_check_authority_docs(repo_root))
    findings.extend(_check_terminal_truth(repo_root))
    findings.extend(_check_local_hook_bundle(repo_root))
    if include_user_tools:
        findings.extend(_check_codex_tools(codex_home or _default_codex_home()))
    return findings


def _check_authority_docs(repo_root: Path) -> list[WorkflowFinding]:
    findings: list[WorkflowFinding] = []
    for raw_path in AUTHORITY_DOCS:
        path = repo_root / raw_path
        if not path.exists():
            findings.append(WorkflowFinding(path, "Asteria workflow authority file is missing"))
    protocol = repo_root / "docs/00-governance/06-asteria-6a-workflow-protocol-v1.md"
    if protocol.exists():
        text = protocol.read_text(encoding="utf-8")
        for token in (
            "A1 Align",
            "A2 Architect",
            "A3 Act",
            "A4 Assert",
            "A5 Archive",
            "A6 Advance",
        ):
            if token not in text:
                findings.append(
                    WorkflowFinding(protocol, f"workflow protocol missing phase: {token}")
                )
    return findings


def _check_terminal_truth(repo_root: Path) -> list[WorkflowFinding]:
    findings: list[WorkflowFinding] = []
    registry_path = repo_root / "governance/module_gate_registry.toml"
    ledger_path = repo_root / "docs/03-refactor/00-module-gate-ledger-v1.md"
    conclusion_index = repo_root / "docs/04-execution/00-conclusion-index-v1.md"
    if not registry_path.exists() or not ledger_path.exists() or not conclusion_index.exists():
        return findings

    with registry_path.open("rb") as handle:
        registry = tomllib.load(handle)
    latest_release = registry.get("latest_mainline_release_run_id")
    next_card = registry.get("current_allowed_next_card", "")
    if latest_release != "final-release-closeout-card":
        findings.append(
            WorkflowFinding(registry_path, "latest_mainline_release_run_id is not final closeout")
        )
    if next_card not in {"", "none"}:
        findings.append(
            WorkflowFinding(registry_path, "terminal workflow must not expose live next card")
        )

    ledger_text = ledger_path.read_text(encoding="utf-8")
    index_text = conclusion_index.read_text(encoding="utf-8")
    for path, text in ((ledger_path, ledger_text), (conclusion_index, index_text)):
        if "final-release-closeout-card" not in text:
            findings.append(WorkflowFinding(path, "final release closeout is not recorded"))
        if "terminal" not in text:
            findings.append(WorkflowFinding(path, "terminal state is not explicit"))
    return findings


def _check_local_hook_bundle(repo_root: Path) -> list[WorkflowFinding]:
    findings: list[WorkflowFinding] = []
    for raw_path in (PLUGIN_MANIFEST, HOOKS_CONFIG, MARKETPLACE):
        path = repo_root / raw_path
        if not path.exists():
            findings.append(
                WorkflowFinding(path, "local Asteria workflow hook/plugin config is missing")
            )
    hooks_path = repo_root / HOOKS_CONFIG
    if hooks_path.exists():
        text = hooks_path.read_text(encoding="utf-8")
        for hook in ("SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop"):
            if hook not in text:
                findings.append(WorkflowFinding(hooks_path, f"hooks config missing {hook}"))
    return findings


def _check_codex_tools(codex_home: Path) -> list[WorkflowFinding]:
    findings: list[WorkflowFinding] = []
    config = codex_home / "config.toml"
    if not config.exists():
        return [
            WorkflowFinding(
                config, "Codex config is unavailable; MCP tool check skipped", "warning"
            )
        ]
    text = config.read_text(encoding="utf-8")
    for server in MCP_SERVERS:
        if f"mcp_servers.{server}" not in text:
            findings.append(WorkflowFinding(config, f"Codex MCP server not configured: {server}"))
    for token in (
        'plugins."asteria-workflow@asteria-local"',
        "marketplaces.asteria-local",
        "source = 'H:\\Asteria'",
    ):
        if token not in text:
            findings.append(
                WorkflowFinding(config, f"Codex workflow plugin config missing: {token}")
            )

    automation = codex_home / "automations" / AUTOMATION_ID / "automation.toml"
    if not automation.exists():
        findings.append(
            WorkflowFinding(automation, "Asteria daily workflow drift automation is not installed")
        )
    return findings


def _default_codex_home() -> Path:
    return Path.home() / ".codex"
