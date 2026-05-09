# Pipeline One-Year Strategy Behavior Replay Rerun Evidence Index

日期：2026-05-09

## 1. Execution Summary

| item | value |
|---|---|
| module | `pipeline` |
| run_id | `pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01` |
| target_year | `2024` |
| module_scope | `year_replay_rerun` |
| run_mode | `bounded` |
| status | `blocked` |

## 2. Blocking Audit

| check | result |
|---|---|
| `pipeline_year_replay_full_year_coverage` | `hard fail` |
| `pipeline_year_replay_rerun_malf_source_locked` | `hard fail` |
| required year window | `2024-01-01..2024-12-31` |
| observed year window | `2024-01-08..2024-12-31` |
| expected MALF source run | `malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001` |
| observed MALF source run | `malf-v1-4-core-runtime-sync-implementation-20260505-01` |

## 3. Released-Surface Facts

| layer | fact |
|---|---|
| MALF repaired run | `2024-01-02..2024-12-31` 已存在 |
| released Signal | 仍从 `2024-01-08` 开始 |
| released Position | 仍从 `2024-01-09` 开始 |
| Pipeline source selection | 如实读取 released `system_source_manifest`，未自行跳源 |

## 4. Behavior Summary

| item | value |
|---|---|
| readout_count | `4633` |
| signal_count | `5494` |
| position_candidate_count | `1158` |
| portfolio_admission_count | `1158` |
| order_intent_count | `3` |
| execution_plan_count | `3` |
| fill_count | `0` |
| rejection_count | `1155` |

## 5. External Assets

| asset | path |
|---|---|
| behavior summary | `H:\Asteria-report\pipeline\2026-05-09\pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01\behavior-summary.json` |
| closeout | `H:\Asteria-report\pipeline\2026-05-09\pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01\closeout.md` |
| manifest | `H:\Asteria-report\pipeline\2026-05-09\pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01\manifest.json` |
| audit summary | `H:\Asteria-report\pipeline\2026-05-09\pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01-audit-summary.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01.zip` |
