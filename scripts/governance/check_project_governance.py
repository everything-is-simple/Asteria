from __future__ import annotations

import argparse
from pathlib import Path

from asteria.governance.checks import run_checks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Asteria project governance checks.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    findings = run_checks(repo_root)
    if findings:
        for finding in findings:
            print(f"FAIL {finding.path}: {finding.message}")
        return 1

    print("Asteria governance checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
