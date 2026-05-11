# Alpha Signal Daily Incremental Ledger Build Card Evidence Index

日期：2026-05-11

## 1. Repo Evidence

| file | role |
|---|---|
| `src/asteria/alpha/daily_incremental_ledger.py` | Alpha day daily incremental sample runner |
| `src/asteria/signal/daily_incremental_ledger.py` | Signal day daily incremental sample runner |
| `scripts/pipeline/run_alpha_signal_daily_incremental_ledger.py` | pipeline orchestration entry |
| `src/asteria/alpha/contracts.py` | Alpha daily incremental contract surface |
| `src/asteria/signal/contracts.py` | Signal daily incremental contract surface |
| `tests/unit/alpha/test_daily_incremental_ledger.py` | Alpha sample / resume / idempotence coverage |
| `tests/unit/signal/test_signal_daily_incremental_ledger.py` | Signal sample / resume / idempotence coverage |
| `tests/unit/governance/test_alpha_signal_daily_incremental_ledger_gate_transition.py` | gate transition coverage |
| `governance/module_gate_registry.toml` | live next card truth after closure |
| `governance/module_api_contracts/pipeline.toml` | next allowed action truth |
| `docs/04-execution/records/pipeline/downstream-daily-impact-ledger-schema-card.card.md` | prepared follow-up card |

## 2. External Evidence

| asset | path |
|---|---|
| pipeline summary | `H:\Asteria-report\pipeline\2026-05-11\alpha-signal-daily-incremental-ledger-build-card\summary.json` |
| alpha audit summary | `H:\Asteria-report\alpha\2026-05-11\alpha-signal-daily-incremental-ledger-build-card\audit-summary.json` |
| signal audit summary | `H:\Asteria-report\signal\2026-05-11\alpha-signal-daily-incremental-ledger-build-card\audit-summary.json` |
| alpha replay scope | `H:\Asteria-temp\alpha\alpha-signal-daily-incremental-ledger-build-card\derived-replay-scope.json` |
| alpha impact scope | `H:\Asteria-temp\alpha\alpha-signal-daily-incremental-ledger-build-card\daily-impact-scope.json` |
| signal impact scope | `H:\Asteria-temp\signal\alpha-signal-daily-incremental-ledger-build-card\daily-impact-scope.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-alpha-signal-daily-incremental-ledger-build-card-20260511-01.zip` |

## 3. Boundary Statement

This evidence proves Alpha/Signal day-only daily incremental sample hardening. It does not prove
formal `H:\Asteria-data` mutation, downstream daily runtime, pipeline full daily chain, formal full
rebuild, or `v1 complete`.
