# v1-t-plus-one-open-backtesting-py-proof-card-20260514-01 Evidence Index

## Repo Evidence

| Evidence | Path | Purpose |
|---|---|---|
| Runner | `src/asteria/pipeline/v1_t_plus_one_open_backtesting_py_proof.py` | Executes the read-only T+1 open proof |
| Artifact IO | `src/asteria/pipeline/v1_t_plus_one_open_backtesting_py_proof_io.py` | Writes manifest, report, closeout, temp manifest, and validated archive |
| Contracts | `src/asteria/pipeline/v1_t_plus_one_open_backtesting_py_proof_contracts.py` | Freezes run id, request, summary, and next route constants |
| Renderer | `src/asteria/pipeline/v1_t_plus_one_open_backtesting_py_proof_render.py` | Renders manifest, report, and closeout |
| CLI | `scripts/pipeline/run_v1_t_plus_one_open_backtesting_py_proof.py` | Runs the proof from the command line |
| Dependency | `pyproject.toml` | Adds `backtesting>=0.6.5` |
| Runner allowlist | `src/asteria/governance/pipeline_runner_surface.py` | Allows the new post-terminal pipeline runner |
| Roadmap | `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md` | Records passed status and next route card |
| Gate ledger | `docs/03-refactor/00-module-gate-ledger-v1.md` | Preserves terminal live truth and records route status |
| Conclusion index | `docs/04-execution/00-conclusion-index-v1.md` | Registers this card conclusion |
| Unit test | `tests/unit/pipeline/test_v1_t_plus_one_open_backtesting_py_proof.py` | Verifies runner behavior and blocked predecessor path |
| Governance test | `tests/unit/governance/test_v1_t_plus_one_open_backtesting_py_proof_route.py` | Verifies route status, four-piece presence, and live next preservation |

## External Evidence

| Artifact | Path |
|---|---|
| Manifest | `H:\Asteria-report\pipeline\2026-05-14\v1-t-plus-one-open-backtesting-py-proof-card-20260514-01\t-plus-one-open-backtesting-py-manifest.json` |
| Report | `H:\Asteria-report\pipeline\2026-05-14\v1-t-plus-one-open-backtesting-py-proof-card-20260514-01\t-plus-one-open-backtesting-py-report.md` |
| Closeout | `H:\Asteria-report\pipeline\2026-05-14\v1-t-plus-one-open-backtesting-py-proof-card-20260514-01\closeout.md` |
| Temp manifest | `H:\Asteria-temp\pipeline\v1-t-plus-one-open-backtesting-py-proof-card-20260514-01\t-plus-one-open-backtesting-py-temp-manifest.json` |
| Validated archive | `H:\Asteria-Validated\Asteria-v1-t-plus-one-open-backtesting-py-proof-card-20260514-01.zip` |

## Verification Commands

```powershell
H:\Asteria\.venv\Scripts\python.exe -m pytest tests\unit\pipeline\test_v1_t_plus_one_open_backtesting_py_proof.py -q --basetemp=H:\Asteria-temp\pytest-tmp-v1-tplus1-proof -o cache_dir=H:\Asteria-temp\pytest-cache-v1-tplus1-proof
H:\Asteria\.venv\Scripts\python.exe scripts\pipeline\run_v1_t_plus_one_open_backtesting_py_proof.py
H:\Asteria\.venv\Scripts\python.exe -m pytest tests\unit\governance\test_v1_t_plus_one_open_backtesting_py_proof_route.py -q --basetemp=H:\Asteria-temp\pytest-tmp-v1-tplus1-route -o cache_dir=H:\Asteria-temp\pytest-cache-v1-tplus1-route
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_asteria_workflow.py --strict
H:\Asteria\.venv\Scripts\ruff.exe check src\asteria\pipeline\v1_t_plus_one_open_backtesting_py_proof.py src\asteria\pipeline\v1_t_plus_one_open_backtesting_py_proof_io.py src\asteria\pipeline\v1_t_plus_one_open_backtesting_py_proof_contracts.py src\asteria\pipeline\v1_t_plus_one_open_backtesting_py_proof_render.py scripts\pipeline\run_v1_t_plus_one_open_backtesting_py_proof.py tests\unit\pipeline\test_v1_t_plus_one_open_backtesting_py_proof.py tests\unit\governance\test_v1_t_plus_one_open_backtesting_py_proof_route.py --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\ruff.exe format --check src\asteria\pipeline\v1_t_plus_one_open_backtesting_py_proof.py src\asteria\pipeline\v1_t_plus_one_open_backtesting_py_proof_io.py src\asteria\pipeline\v1_t_plus_one_open_backtesting_py_proof_contracts.py src\asteria\pipeline\v1_t_plus_one_open_backtesting_py_proof_render.py scripts\pipeline\run_v1_t_plus_one_open_backtesting_py_proof.py tests\unit\pipeline\test_v1_t_plus_one_open_backtesting_py_proof.py tests\unit\governance\test_v1_t_plus_one_open_backtesting_py_proof_route.py --cache-dir H:\Asteria-temp\ruff-cache
```

## Evidence Boundary

This evidence proves only that a small external `backtesting.py` proof can consume Asteria
Signal with T+1 open execution semantics. It does not prove production portfolio quality,
real fills, account updates, broker integration, or live trading capability.
