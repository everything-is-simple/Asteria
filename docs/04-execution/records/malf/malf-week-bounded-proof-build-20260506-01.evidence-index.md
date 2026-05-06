# MALF Week Bounded Proof Build Evidence Index

日期：2026-05-06

run_id：`malf-week-bounded-proof-build-20260506-01`

## 1. Repo Records

| evidence | path |
|---|---|
| card | `docs/04-execution/records/malf/malf-week-bounded-proof-build-20260506-01.card.md` |
| record | `docs/04-execution/records/malf/malf-week-bounded-proof-build-20260506-01.record.md` |
| conclusion | `docs/04-execution/records/malf/malf-week-bounded-proof-build-20260506-01.conclusion.md` |
| conclusion index | `docs/04-execution/00-conclusion-index-v1.md` |
| gate ledger | `docs/03-refactor/00-module-gate-ledger-v1.md` |

## 2. Runtime Evidence

| evidence | path |
|---|---|
| source DB | `H:\Asteria-data\market_base_week.duckdb` |
| Core DB | `H:\Asteria-data\malf_core_week.duckdb` |
| Lifespan DB | `H:\Asteria-data\malf_lifespan_week.duckdb` |
| Service DB | `H:\Asteria-data\malf_service_week.duckdb` |
| audit summary | `H:\Asteria-report\malf\2026-05-06\malf-week-bounded-proof-build-20260506-01-audit-summary.json` |
| closeout | `H:\Asteria-report\malf\2026-05-06\malf-week-bounded-proof-build-20260506-01\closeout.md` |
| manifest | `H:\Asteria-report\malf\2026-05-06\malf-week-bounded-proof-build-20260506-01\manifest.json` |
| table counts | `H:\Asteria-report\malf\2026-05-06\malf-week-bounded-proof-build-20260506-01\table-counts.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-malf-week-bounded-proof-build-20260506-01.zip` |

## 3. Audit Result

| check | result |
|---|---|
| timeframe | `week` |
| source filter | `analysis_price_line / backward` |
| source scope | `2024-01-01..2024-12-31 / symbol_limit=20` |
| hard_fail_count | `0` |
| WavePosition natural key duplicate groups | `0` |
| allowed next action | `malf_month_bounded_proof_build` |

## 4. Boundary

本证据只放行 MALF week bounded Core/Lifespan/Service runtime proof，不声明 MALF month、
Alpha/Signal full build、Position construction、下游施工或 Pipeline runtime 已打开。
