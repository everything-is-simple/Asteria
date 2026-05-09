# MALF 2024 Natural-Year Coverage Repair Evidence Index

日期：2026-05-09

run_id：`malf-2024-natural-year-coverage-repair-card-20260509-01`

## 1. Repo Records

| evidence | path |
|---|---|
| card | `docs/04-execution/records/malf/malf-2024-natural-year-coverage-repair-card-20260509-01.card.md` |
| record | `docs/04-execution/records/malf/malf-2024-natural-year-coverage-repair-card-20260509-01.record.md` |
| conclusion | `docs/04-execution/records/malf/malf-2024-natural-year-coverage-repair-card-20260509-01.conclusion.md` |
| next prepared card | `docs/04-execution/records/pipeline/pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01.card.md` |
| conclusion index | `docs/04-execution/00-conclusion-index-v1.md` |
| gate ledger | `docs/03-refactor/00-module-gate-ledger-v1.md` |

## 2. Runtime Evidence

| evidence | path |
|---|---|
| source DB | `H:\Asteria-data\market_base_day.duckdb` |
| Core DB | `H:\Asteria-data\malf_core_day.duckdb` |
| Lifespan DB | `H:\Asteria-data\malf_lifespan_day.duckdb` |
| Service DB | `H:\Asteria-data\malf_service_day.duckdb` |
| system manifest lock truth | `H:\Asteria-data\system.duckdb` |
| batch ledger | `H:\Asteria-temp\malf\malf-2024-natural-year-coverage-repair-card-20260509-01\batch-ledger.jsonl` |
| build manifest | `H:\Asteria-temp\malf\malf-2024-natural-year-coverage-repair-card-20260509-01\build-manifest.json` |
| audit summary | `H:\Asteria-report\malf\2026-05-09\malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001-audit-summary.json` |
| closeout | `H:\Asteria-report\malf\2026-05-09\malf-2024-natural-year-coverage-repair-card-20260509-01\closeout.md` |
| manifest | `H:\Asteria-report\malf\2026-05-09\malf-2024-natural-year-coverage-repair-card-20260509-01\manifest.json` |
| table counts | `H:\Asteria-report\malf\2026-05-09\malf-2024-natural-year-coverage-repair-card-20260509-01\table-counts.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-malf-2024-natural-year-coverage-repair-card-20260509-01.zip` |

## 3. Audit Result

| check | result |
|---|---|
| repaired symbol set | `000020.SZ` |
| released service run | `malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001` |
| focus trading dates | `2024-01-02..2024-01-05 all present` |
| hard_fail_count | `0` |
| WavePosition natural key duplicate groups | `0` |
| allowed next action | `pipeline_one_year_strategy_behavior_replay_rerun_build_card` |

## 4. Boundary

本证据只证明 MALF released day surface 的最小 natural-year coverage gap 已被修到足以覆盖
`2024-01-02..2024-01-05`。它不声明 MALF full build、20-symbol current universe 全量重修、
Alpha/Signal/downstream repair、year replay rerun passed、full rebuild、daily incremental 或
`v1 complete`。
