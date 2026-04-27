from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


@dataclass(frozen=True)
class Finding:
    path: Path
    message: str


def _load_governance(repo_root: Path) -> dict:
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


def _check_file_sizes(repo_root: Path, governance: dict) -> list[Finding]:
    findings: list[Finding] = []
    limits = {
        ".py": int(governance["max_python_file_lines"]),
        ".md": int(governance["max_markdown_file_lines"]),
    }
    script_limit = int(governance["max_script_file_lines"])
    ignored_parts = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache"}

    for path in repo_root.rglob("*"):
        if not path.is_file() or ignored_parts.intersection(path.parts):
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


def run_checks(repo_root: Path) -> list[Finding]:
    governance = _load_governance(repo_root)
    findings: list[Finding] = []
    findings.extend(_check_required_docs(repo_root, list(governance["required_docs"])))
    findings.extend(_check_file_sizes(repo_root, governance))
    return findings


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
