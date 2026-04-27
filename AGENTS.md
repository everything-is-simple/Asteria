# Asteria Agent Rules

This repository is the new Asteria refactor workspace.

Before changing code, every agent must read:

1. `README.md`
2. `docs/00-governance/00-asteria-refactor-charter-v1.md`
3. `docs/01-architecture/00-mainline-authoritative-map-v1.md`
4. `docs/01-architecture/01-database-topology-v1.md`
5. `docs/03-refactor/00-module-gate-ledger-v1.md`

Hard rules:

- Do not migrate legacy code into the mainline before the target module has a frozen design document.
- Do not edit more than one mainline module in one construction turn.
- Do not let a downstream module redefine an upstream module's semantics.
- Do not treat `data` as a strategy module. It is foundation infrastructure and source-fact service.
- Do not merge `wave_core_state` and `system_state`.
- Do not let Alpha, Signal, Portfolio, Trade, or System write back to MALF.
- Put formal databases under `H:\Asteria-data`.
- Put temporary build artifacts under `H:\Asteria-temp`.
- Keep `H:\Asteria-Validated` as validated input/output assets, not as a casual scratch directory.

Python environment:

- Use `D:\miniconda\py310` as the base Python provider.
- Prefer repo-local virtualenv `H:\Asteria\.venv`.
- Install the project with `H:\Asteria\.venv\Scripts\python.exe -m pip install -e ".[dev]"`.
- Do not put pytest cache, temporary DBs, or report artifacts under the repo root.

Governance checks:

- Run `python scripts\governance\check_project_governance.py` before committing structural changes.
- Run `ruff check .`, `ruff format --check .`, `mypy src`, and `pytest` before release gates.
- Python files should stay under 500 lines. Script wrappers should stay under 240 lines.
- Markdown design/spec files should stay under 1200 lines; split by module when they grow past that.
- Comments should explain intent, boundaries, and non-obvious invariants. Avoid comments that restate code.
