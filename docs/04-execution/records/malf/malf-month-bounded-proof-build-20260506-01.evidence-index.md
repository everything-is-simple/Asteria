# MALF Month Bounded Proof Build Evidence Index

日期：2026-05-06

run_id：`malf-month-bounded-proof-build-20260506-01`

## 1. Repo Records

| evidence | path |
|---|---|
| card | `docs/04-execution/records/malf/malf-month-bounded-proof-build-20260506-01.card.md` |
| record | `docs/04-execution/records/malf/malf-month-bounded-proof-build-20260506-01.record.md` |
| conclusion | `docs/04-execution/records/malf/malf-month-bounded-proof-build-20260506-01.conclusion.md` |
| conclusion index | `docs/04-execution/00-conclusion-index-v1.md` |
| gate ledger | `docs/03-refactor/00-module-gate-ledger-v1.md` |

## 2. Runtime Evidence

| evidence | path |
|---|---|
| source DB | `H:\Asteria-data\market_base_month.duckdb` |
| Core DB | `H:\Asteria-data\malf_core_month.duckdb` |
| Lifespan DB | `H:\Asteria-data\malf_lifespan_month.duckdb` |
| Service DB | `H:\Asteria-data\malf_service_month.duckdb` |
| audit summary | `H:\Asteria-report\malf\2026-05-06\malf-month-bounded-proof-build-20260506-01-audit-summary.json` |
| closeout | `H:\Asteria-report\malf\2026-05-06\malf-month-bounded-proof-build-20260506-01\closeout.md` |
| manifest | `H:\Asteria-report\malf\2026-05-06\malf-month-bounded-proof-build-20260506-01\manifest.json` |
| table counts | `H:\Asteria-report\malf\2026-05-06\malf-month-bounded-proof-build-20260506-01\table-counts.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-malf-month-bounded-proof-build-20260506-01.zip` |

## 3. Audit Result

| check | result |
|---|---|
| timeframe | `month` |
| source filter | `analysis_price_line / backward` |
| source scope | `2024-01-01..2024-12-31 / symbol_limit=20` |
| hard_fail_count | `0` |
| WavePosition natural key duplicate groups | `0` |
| allowed next action | `alpha_production_builder_hardening` |

## 4. Boundary

本证据只放行 MALF month bounded Core/Lifespan/Service runtime proof，不声明 MALF full build、
Alpha/Signal production builder 已完成、Position construction、下游施工或 Pipeline runtime 已打开。
