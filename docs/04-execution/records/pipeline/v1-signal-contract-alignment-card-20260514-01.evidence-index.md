# Signal/PAS Contract Alignment Evidence Index

日期：2026-05-14

run_id：`v1-signal-contract-alignment-card-20260514-01`

## 1. Repo Evidence

| asset | role |
|---|---|
| `src/asteria/signal/pas_contracts.py` | Signal/PAS alignment constants, required fields, forbidden fields |
| `src/asteria/signal/pas_alignment.py` | Signal/PAS alignment runner and deterministic aggregation |
| `src/asteria/signal/pas_artifacts.py` | temp DuckDB, report, and validated archive writer |
| `scripts/signal/run_signal_pas_alignment.py` | CLI entrypoint |
| `tests/unit/signal/test_signal_pas_alignment.py` | PAS input, active state, lineage, T+1 hint, and temp-only tests |
| `tests/unit/signal/test_signal_bounded_proof_runner.py` | existing Signal bounded proof regression guard |
| `docs/03-refactor/06-asteria-core-module-recovery-and-proof-roadmap-v1.md` | route authority and card order |
| `docs/03-refactor/00-module-gate-ledger-v1.md` | post-terminal route status sync |
| `docs/04-execution/00-conclusion-index-v1.md` | conclusion registration |
| `governance/module_gate_registry.toml` | live terminal truth, unchanged |

## 2. Runtime Evidence

| asset | role |
|---|---|
| `H:\Asteria-temp\signal_pas\v1-signal-contract-alignment-card-20260514-01\signal_pas_alignment.duckdb` | temp-only Signal/PAS alignment DB |
| `H:\Asteria-report\pipeline\2026-05-14\v1-signal-contract-alignment-card-20260514-01\alignment-summary.json` | alignment summary |
| `H:\Asteria-report\pipeline\2026-05-14\v1-signal-contract-alignment-card-20260514-01\contract-coverage.json` | required / forbidden field coverage |
| `H:\Asteria-report\pipeline\2026-05-14\v1-signal-contract-alignment-card-20260514-01\lineage-summary.json` | source lineage summary |
| `H:\Asteria-report\pipeline\2026-05-14\v1-signal-contract-alignment-card-20260514-01\audit-summary.json` | hard audit summary |
| `H:\Asteria-report\pipeline\2026-05-14\v1-signal-contract-alignment-card-20260514-01\manifest.json` | report manifest |

## 3. Validated Evidence

| asset | role |
|---|---|
| `H:\Asteria-Validated\Asteria-v1-signal-contract-alignment-card-20260514-01.zip` | card evidence archive |

## 4. Boundary Evidence

| boundary | evidence |
|---|---|
| formal DB mutation | `no`; output DB is under `H:\Asteria-temp` |
| source PAS mutation | `no`; source opened read-only |
| required fields | `contract-coverage.json` shows no missing required fields |
| forbidden fields | `contract-coverage.json` shows no forbidden fields present |
| T+1 open hint | `signal_pas_formal_signal` includes `T_PLUS_1_OPEN / next_trading_day_after_signal_date / open` |
| broker / profit proof | `not executed`; no broker, fill, account, PnL, or return surface |
| live next changed | `no`; `current live next` remains `none / terminal` |
