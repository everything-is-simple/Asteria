---
name: asteria-governance
description: Project-specific governance for Asteria refactor work. Use when Codex changes Asteria docs, Python code, module boundaries, DuckDB schema specs, runner contracts, execution cards, or release gates.
---

# Asteria Governance

## Overview

Use this skill to keep Asteria changes doc-first, module-scoped, and aligned with the MALF-led mainline.

Current authority chain:

- `H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.md`
- `H:\Asteria-Validated\Asteria-docs-code-20260428-214427.zip`
- `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2`
- `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2.zip`

Current gate state:

```text
MALF day bounded proof passed -> Alpha freeze review
```

`Alpha freeze review` is review-only. It does not authorize Alpha implementation,
formal Alpha DB creation, downstream construction, or a full-chain pipeline.

## Required Reading

Read these files before changing formal code, schemas, runner contracts, or module gates:

1. `README.md`
2. `AGENTS.md`
3. `docs/00-governance/00-asteria-refactor-charter-v1.md`
4. `docs/01-architecture/00-mainline-authoritative-map-v1.md`
5. `docs/01-architecture/01-database-topology-v1.md`
6. `docs/03-refactor/00-module-gate-ledger-v1.md`
7. `docs/04-execution/00-conclusion-index-v1.md`

## Workflow

1. Identify the active module from `docs/03-refactor/00-module-gate-ledger-v1.md`.
2. Confirm the target change stays inside that module, or update governance docs before implementation.
3. Ensure a design/spec/card exists before formal source or schema work.
4. Keep generated DBs, reports, and temporary artifacts outside the repo.
5. For release or proof work, create or update the execution four-pack:
   `card`, `evidence-index`, `record`, and `conclusion`.
6. Run the project checks before commit.

## Mainline Rules

- Treat `data` as foundation infrastructure, not as the strategy mainline.
- Keep the mainline order: `MALF -> Alpha -> Signal -> Position -> Portfolio Plan -> Trade -> System`.
- Let `Pipeline` orchestrate only; it must not define business semantics.
- Do not let downstream modules write back to MALF or redefine MALF fields.
- Do not merge `wave_core_state` and `system_state`.
- Only one mainline module may be under construction at a time.
- Keep `H:\Asteria-Validated` for validated assets only, not scratch work.

## Environment

Use `D:\miniconda\py310` as the Python provider and prefer `H:\Asteria\.venv`.

Run checks with the repo-local environment:

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\ruff.exe check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\ruff.exe format --check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\mypy.exe src --cache-dir H:\Asteria-temp\mypy-cache
H:\Asteria\.venv\Scripts\pytest.exe --basetemp=H:/Asteria-temp/pytest-tmp-<run_id> -o cache_dir=H:/Asteria-temp/pytest-cache-<run_id>
```

Do not leave tool caches in the repo root. Treat `H:\Asteria\.ruff_cache` and
`H:\Asteria\.mypy_cache` as accidental temporary artifacts: delete them if they
appear, never stage them, and rerun checks with the cache directories above.

## Style

- Keep Python files under 500 lines and script wrappers under 240 lines.
- Keep Markdown design/spec files under 1200 lines.
- Use comments for intent, boundaries, and non-obvious invariants.
- Avoid comments that merely restate assignments or function names.
- Prefer small module contracts over broad helper abstractions.
