from __future__ import annotations

from pathlib import Path

from asteria.governance.workflow_protocol import run_workflow_checks


def _write(path: Path, text: str = "ok") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_workflow_protocol_accepts_terminal_authority_and_tooling(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    codex_home = tmp_path / ".codex"
    for raw_path in [
        "README.md",
        "AGENTS.md",
        "docs/00-governance/00-asteria-refactor-charter-v1.md",
        "docs/01-architecture/00-mainline-authoritative-map-v1.md",
        "docs/01-architecture/01-database-topology-v1.md",
        "docs/03-refactor/04-asteria-full-system-roadmap-v1.md",
    ]:
        _write(repo / raw_path)
    _write(
        repo / "docs/00-governance/06-asteria-6a-workflow-protocol-v1.md",
        "A1 Align\nA2 Architect\nA3 Act\nA4 Assert\nA5 Archive\nA6 Advance\n",
    )
    _write(
        repo / "governance/module_gate_registry.toml",
        'latest_mainline_release_run_id = "final-release-closeout-card"\n'
        'current_allowed_next_card = ""\n',
    )
    _write(
        repo / "docs/03-refactor/00-module-gate-ledger-v1.md",
        "final-release-closeout-card\nterminal / no next card\n",
    )
    _write(
        repo / "docs/04-execution/00-conclusion-index-v1.md",
        "final-release-closeout-card\nnone / terminal\n",
    )
    _write(repo / "plugins/asteria-workflow/.codex-plugin/plugin.json", "{}")
    _write(
        repo / "plugins/asteria-workflow/hooks.json",
        "SessionStart UserPromptSubmit PreToolUse PostToolUse Stop",
    )
    _write(repo / ".agents/plugins/marketplace.json", "{}")
    _write(
        codex_home / "config.toml",
        "[mcp_servers.codebase-retrieval]\n"
        "[mcp_servers.context7]\n"
        "[mcp_servers.fetch]\n"
        "[mcp_servers.sequential-thinking]\n"
        '[plugins."asteria-workflow@asteria-local"]\n'
        "[marketplaces.asteria-local]\n"
        "source = 'H:\\Asteria'\n",
    )
    _write(codex_home / "automations/asteria-daily-workflow-drift-scan/automation.toml")

    assert run_workflow_checks(repo, codex_home=codex_home) == []


def test_workflow_protocol_flags_stale_live_next(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    codex_home = tmp_path / ".codex"
    for raw_path in [
        "README.md",
        "AGENTS.md",
        "docs/00-governance/00-asteria-refactor-charter-v1.md",
        "docs/00-governance/06-asteria-6a-workflow-protocol-v1.md",
        "docs/01-architecture/00-mainline-authoritative-map-v1.md",
        "docs/01-architecture/01-database-topology-v1.md",
        "docs/03-refactor/04-asteria-full-system-roadmap-v1.md",
        "plugins/asteria-workflow/.codex-plugin/plugin.json",
        "plugins/asteria-workflow/hooks.json",
        ".agents/plugins/marketplace.json",
    ]:
        _write(repo / raw_path, "A1 Align A2 Architect A3 Act A4 Assert A5 Archive A6 Advance")
    _write(
        repo / "governance/module_gate_registry.toml",
        'latest_mainline_release_run_id = "final-release-closeout-card"\n'
        'current_allowed_next_card = "final_release_closeout_card"\n',
    )
    _write(
        repo / "docs/03-refactor/00-module-gate-ledger-v1.md",
        "final-release-closeout-card\nterminal\n",
    )
    _write(
        repo / "docs/04-execution/00-conclusion-index-v1.md",
        "final-release-closeout-card\nterminal\n",
    )
    _write(codex_home / "config.toml", "")

    findings = run_workflow_checks(repo, codex_home=codex_home)

    assert any("terminal workflow must not expose live next card" in f.message for f in findings)
