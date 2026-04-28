from __future__ import annotations

import argparse
from pathlib import Path

from asteria.governance.docs_sync import apply_safe_sync, plan_docs_sync


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check or safely sync Asteria docs state.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Check docs sync state without edits.")
    mode.add_argument("--plan", action="store_true", help="Print safe sync actions without edits.")
    mode.add_argument(
        "--apply-safe",
        action="store_true",
        help="Apply evidence-backed mechanical docs sync actions.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    if args.apply_safe:
        report = apply_safe_sync(repo_root)
        for action in report.actions:
            print(f"APPLY {action.path}: {action.message}")
    else:
        report = plan_docs_sync(repo_root)
        if args.plan:
            for action in report.actions:
                print(f"PLAN {action.path}: {action.message}")

    if report.findings:
        for finding in report.findings:
            print(f"FAIL {finding.path}: {finding.message}")
        return 1

    print("Asteria docs sync checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
