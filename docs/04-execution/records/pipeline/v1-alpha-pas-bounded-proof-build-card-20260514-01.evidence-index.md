# Alpha/PAS Bounded Proof Build Evidence Index

日期：2026-05-14

run_id：`v1-alpha-pas-bounded-proof-build-card-20260514-01`

## 1. Repo Evidence

| asset | role |
|---|---|
| `src/asteria/alpha/pas_contracts.py` | PAS v1.0 proof constants and forbidden fields |
| `src/asteria/alpha/pas_rules.py` | setup family, lifecycle, strength and lineage rules |
| `src/asteria/alpha/pas_artifacts.py` | temp DuckDB, report, and validated archive writer |
| `src/asteria/alpha/pas_bounded_proof.py` | Alpha/PAS bounded proof runner |
| `scripts/alpha/run_alpha_pas_bounded_proof.py` | CLI entrypoint |
| `tests/unit/alpha/test_alpha_pas_bounded_proof.py` | contract, lifecycle, visibility, and temp-only tests |
| `tests/unit/alpha/test_alpha_bounded_proof_runner.py` | existing Alpha bounded proof regression guard |
| `docs/03-refactor/06-asteria-core-module-recovery-and-proof-roadmap-v1.md` | route authority and card order |
| `docs/03-refactor/00-module-gate-ledger-v1.md` | post-terminal route status sync |
| `docs/04-execution/00-conclusion-index-v1.md` | conclusion registration |
| `governance/module_gate_registry.toml` | live terminal truth, unchanged |

## 2. Runtime Evidence

| asset | role |
|---|---|
| `H:\Asteria-temp\alpha_pas\v1-alpha-pas-bounded-proof-build-card-20260514-01\alpha_pas_bounded_proof.duckdb` | temp-only Alpha/PAS proof DB |
| `H:\Asteria-report\pipeline\2026-05-14\v1-alpha-pas-bounded-proof-build-card-20260514-01\proof-summary.json` | proof summary |
| `H:\Asteria-report\pipeline\2026-05-14\v1-alpha-pas-bounded-proof-build-card-20260514-01\contract-coverage.json` | required / forbidden field coverage |
| `H:\Asteria-report\pipeline\2026-05-14\v1-alpha-pas-bounded-proof-build-card-20260514-01\lineage-summary.json` | source and lifecycle lineage summary |
| `H:\Asteria-report\pipeline\2026-05-14\v1-alpha-pas-bounded-proof-build-card-20260514-01\audit-summary.json` | hard audit summary |
| `H:\Asteria-report\pipeline\2026-05-14\v1-alpha-pas-bounded-proof-build-card-20260514-01\manifest.json` | report manifest |

## 3. Validated Evidence

| asset | role |
|---|---|
| `H:\Asteria-Validated\Asteria-v1-alpha-pas-bounded-proof-build-card-20260514-01.zip` | card evidence archive |

## 4. Boundary Evidence

| boundary | evidence |
|---|---|
| formal DB mutation | `no`; output DB is under `H:\Asteria-temp` |
| source MALF mutation | `no`; source opened read-only |
| lifecycle completeness | `pas_lifecycle_state_catalog = 8` |
| required fields | `contract-coverage.json` shows no missing required fields |
| forbidden fields | `contract-coverage.json` shows no forbidden fields present |
| broker / profit proof | `not executed`; no broker, fill, account, PnL, or return surface |
| live next changed | `no`; `current live next` remains `none / terminal` |
