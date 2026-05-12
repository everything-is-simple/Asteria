from __future__ import annotations

import argparse
from pathlib import Path

from asteria.governance.workflow_protocol import run_workflow_checks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check Asteria 6A workflow wiring.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--codex-home", type=Path, default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--hook-event", default="", help="Optional Codex hook event name.")
    args = parser.parse_args(argv)

    findings = run_workflow_checks(args.repo_root, codex_home=args.codex_home)
    errors = [finding for finding in findings if finding.severity == "error"]
    warnings = [finding for finding in findings if finding.severity == "warning"]

    if args.hook_event:
        print(f"Asteria workflow hook: {args.hook_event}")
        print("Use A1-A6: Align, Architect, Act, Assert, Archive, Advance.")

    for finding in errors:
        print(f"FAIL {finding.path}: {finding.message}")
    for finding in warnings:
        print(f"WARN {finding.path}: {finding.message}")

    if errors or (args.strict and warnings):
        return 1
    print("Asteria workflow checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
