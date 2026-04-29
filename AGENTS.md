# Asteria Agent Rules

This repository is the new Asteria refactor workspace.

Before changing code, every agent must read:

1. `README.md`
2. `docs/00-governance/00-asteria-refactor-charter-v1.md`
3. `docs/01-architecture/00-mainline-authoritative-map-v1.md`
4. `docs/01-architecture/01-database-topology-v1.md`
5. `docs/03-refactor/00-module-gate-ledger-v1.md`
6. `docs/04-execution/00-conclusion-index-v1.md`

Current authority assets:

- `H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.md`
- `H:\Asteria-Validated\Asteria-docs-code-20260428-214427.zip`
- `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2`
- `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2.zip`

Current gate:

- `MALF day bounded proof passed`
- `Alpha freeze review passed`
- `Alpha bounded proof passed`
- `Signal freeze review passed`
- `Signal bounded proof passed`
- `Position freeze review blocked`
- Next allowed action: `MALF Lifespan dense bar snapshot resolution`
- Signal bounded proof only releases the bounded `signal.duckdb` surface; it does not authorize Signal full build, Position construction, downstream construction, or a full-chain pipeline.

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
- Run `ruff check . --cache-dir H:\Asteria-temp\ruff-cache`, `ruff format --check . --cache-dir H:\Asteria-temp\ruff-cache`, `mypy src --cache-dir H:\Asteria-temp\mypy-cache`, and pytest with run-scoped `H:\Asteria-temp` cache/temp paths before release gates.
- Python files should stay under 500 lines. Script wrappers should stay under 240 lines.
- Markdown design/spec files should stay under 1200 lines; split by module when they grow past that.
- Comments should explain intent, boundaries, and non-obvious invariants. Avoid comments that restate code.
