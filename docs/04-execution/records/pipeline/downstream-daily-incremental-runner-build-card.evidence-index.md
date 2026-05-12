# Downstream Daily Incremental Runner Build Card Evidence Index

日期：2026-05-12

## 1. Repo Evidence

| file | role |
|---|---|
| `src/asteria/position/daily_incremental_ledger.py` | Position day daily incremental sample runner |
| `src/asteria/portfolio_plan/daily_incremental_ledger.py` | Portfolio Plan day daily incremental sample runner |
| `src/asteria/trade/daily_incremental_ledger.py` | Trade day daily incremental sample runner |
| `src/asteria/system_readout/daily_incremental_ledger.py` | System Readout day daily incremental sample runner |
| `scripts/position/run_position_daily_incremental_ledger.py` | Position CLI wrapper |
| `scripts/portfolio_plan/run_portfolio_plan_daily_incremental_ledger.py` | Portfolio Plan CLI wrapper |
| `scripts/trade/run_trade_daily_incremental_ledger.py` | Trade CLI wrapper |
| `scripts/system_readout/run_system_readout_daily_incremental_ledger.py` | System Readout CLI wrapper |
| `scripts/pipeline/run_downstream_daily_incremental_ledger.py` | pipeline orchestration entry |
| `src/asteria/position/contracts.py` | Position daily incremental contract surface |
| `src/asteria/portfolio_plan/contracts.py` | Portfolio Plan daily incremental contract surface |
| `src/asteria/trade/contracts.py` | Trade daily incremental contract surface |
| `src/asteria/system_readout/contracts.py` | System Readout daily incremental contract surface |
| `tests/unit/position/test_position_daily_incremental_ledger.py` | Position sample / resume / audit-only coverage |
| `tests/unit/portfolio_plan/test_portfolio_plan_daily_incremental_ledger.py` | Portfolio Plan sample / resume / audit-only coverage |
| `tests/unit/trade/test_trade_daily_incremental_ledger.py` | Trade sample / resume / audit-only coverage |
| `tests/unit/system_readout/test_system_readout_daily_incremental_ledger.py` | System Readout sample / resume / audit-only coverage |
| `tests/unit/pipeline/test_downstream_daily_incremental_ledger.py` | downstream pipeline orchestration coverage |
| `tests/unit/governance/test_downstream_daily_incremental_runner_gate_transition.py` | gate transition coverage |
| `governance/module_gate_registry.toml` | live next card truth after closure |
| `governance/module_api_contracts/pipeline.toml` | pipeline next allowed action truth |
| `docs/04-execution/records/pipeline/pipeline-full-daily-incremental-chain-build-card.card.md` | prepared follow-up card |

## 2. External Evidence

| asset | path |
|---|---|
| pipeline summary | `H:\Asteria-report\pipeline\2026-05-12\downstream-daily-incremental-runner-build-card\summary.json` |
| pipeline closeout | `H:\Asteria-report\pipeline\2026-05-12\downstream-daily-incremental-runner-build-card\closeout.md` |
| position audit summary | `H:\Asteria-report\position\2026-05-12\downstream-daily-incremental-runner-build-card\audit-summary.json` |
| portfolio_plan audit summary | `H:\Asteria-report\portfolio_plan\2026-05-12\downstream-daily-incremental-runner-build-card\audit-summary.json` |
| trade audit summary | `H:\Asteria-report\trade\2026-05-12\downstream-daily-incremental-runner-build-card\audit-summary.json` |
| system_readout audit summary | `H:\Asteria-report\system_readout\2026-05-12\downstream-daily-incremental-runner-build-card\audit-summary.json` |
| lineage chain | `H:\Asteria-temp\system_readout\downstream-daily-incremental-runner-build-card\lineage.json` |

## 3. Boundary Statement

This evidence proves downstream day-only daily incremental sample hardening. It does not prove
formal `H:\Asteria-data` mutation, pipeline full daily incremental chain execution, release
closeout, formal full rebuild, or `v1 complete`.
