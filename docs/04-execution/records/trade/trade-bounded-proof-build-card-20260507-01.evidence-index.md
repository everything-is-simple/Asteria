# Trade Bounded Proof Build Evidence Index

日期：2026-05-07

## 1. Execution Summary

| item | value |
|---|---|
| module | `trade` |
| run_id | `trade-bounded-proof-build-card-20260507-01` |
| source DB | `H:\Asteria-data\portfolio_plan.duckdb` |
| target DB | `H:\Asteria-data\trade.duckdb` |
| source release | `portfolio-plan-bounded-proof-build-card-20260507-01` |

## 2. Audit Result

| check | result |
|---|---|
| input_portfolio_plan_count | `1158` |
| order_intent_count | `3` |
| execution_plan_count | `3` |
| fill_count | `0` |
| rejection_count | `1155` |
| hard_fail_count | `0` |
| retained gap | `fill_ledger` empty; no evidence-backed execution / fill source available |

## 3. Report Assets

| asset | path |
|---|---|
| closeout | `H:\Asteria-report\trade\2026-05-07\trade-bounded-proof-build-card-20260507-01\closeout.md` |
| manifest | `H:\Asteria-report\trade\2026-05-07\trade-bounded-proof-build-card-20260507-01\manifest.json` |
| audit summary | `H:\Asteria-report\trade\2026-05-07\trade-bounded-proof-build-card-20260507-01-day-audit-summary.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-trade-bounded-proof-build-card-20260507-01.zip` |

## 4. Boundary

本证据只放行 Trade day bounded proof。它不授权 Trade full build、System Readout
正式 DB 或 full-chain Pipeline runtime。
