# v1-signal-export-contract-card-20260513-01 Evidence Index

## Repo Evidence

| Evidence | Path | Purpose |
|---|---|---|
| Roadmap update | `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md` | Records Phase 2 card status, frozen signal export contract, and next route card |
| Gate ledger sync | `docs/03-refactor/00-module-gate-ledger-v1.md` | Records post-terminal route status while preserving `none / terminal` live truth |
| Conclusion index sync | `docs/04-execution/00-conclusion-index-v1.md` | Registers the passed card and links this evidence set |
| Card | `docs/04-execution/records/pipeline/v1-signal-export-contract-card-20260513-01.card.md` | Freezes scope, inputs, boundaries, and pass criteria |
| Record | `docs/04-execution/records/pipeline/v1-signal-export-contract-card-20260513-01.record.md` | Records executed work and explicit non-claims |
| Conclusion | `docs/04-execution/records/pipeline/v1-signal-export-contract-card-20260513-01.conclusion.md` | Gives the final human-readable route conclusion |
| Governance test | `tests/unit/governance/test_v1_signal_export_contract_route.py` | Verifies route status, required contract fields, and four-piece presence |
| Phase 2 regression test | `tests/unit/governance/test_v1_core_retention_outsourcing_boundary_route.py` | Verifies the prior Phase 2 boundary card remains passed after the next route card advances |

## Contract Anchors

| Anchor | Path | Detail |
|---|---|---|
| Signal module API contract | `governance/module_api_contracts/signal.toml` | Formal source table and public/version fields |
| Signal authority design | `docs/02-modules/signal/00-authority-design-v1.md` | Formal Signal ledger natural key and schema authority |
| Future formal source | `H:\Asteria-data\signal.duckdb::formal_signal_ledger` | Future export input only; not mutated by this card |

## Archive Evidence

| Artifact | Path |
|---|---|
| Validated archive | `H:\Asteria-Validated\Asteria-v1-signal-export-contract-card-20260513-01.zip` |

## Verification Commands

```powershell
H:\Asteria\.venv\Scripts\python.exe -m pytest tests\unit\governance\test_v1_signal_export_contract_route.py -q --basetemp=H:\Asteria-temp\pytest-tmp-v1-signal-export-contract -o cache_dir=H:\Asteria-temp\pytest-cache-v1-signal-export-contract
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_asteria_workflow.py --strict
H:\Asteria\.venv\Scripts\ruff.exe check tests\unit\governance\test_v1_signal_export_contract_route.py --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\ruff.exe format --check tests\unit\governance\test_v1_signal_export_contract_route.py --cache-dir H:\Asteria-temp\ruff-cache
```

## Evidence Boundary

This evidence proves only the export contract freeze. It does not prove PnL, fills,
account updates, broker execution, or live trading.
