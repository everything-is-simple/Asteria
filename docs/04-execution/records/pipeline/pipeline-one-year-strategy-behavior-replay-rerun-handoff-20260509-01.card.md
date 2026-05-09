# Pipeline One-Year Strategy Behavior Replay Rerun Handoff Card

日期：2026-05-09

状态：`passed / rerun prepared handoff`

## 1. 目标

在 `malf-2024-natural-year-coverage-repair-card-20260509-01` 已通过后，
把 Pipeline live next action 从 MALF repair handoff 切换到 year replay rerun prepared handoff。

## 2. 范围

| item | decision |
|---|---|
| module | `pipeline` |
| card type | `governance handoff / prepared next-card update` |
| upstream prerequisite | `malf-2024-natural-year-coverage-repair-card-20260509-01` |
| prepared next card | `pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01` |

## 3. 允许动作

- 更新 pipeline live next-card truth 到 `pipeline_one_year_strategy_behavior_replay_rerun_build_card`。
- 复核 MALF repair 已形成的 released run 是否明确可被 rerun 锁定。
- 同步 gate ledger、conclusion index、roadmap 与 registry。

## 4. 仍然禁止

| forbidden | decision |
|---|---|
| 直接执行 rerun | 禁止 |
| 改写 `system_source_manifest` | 禁止 |
| 新开 Data / Alpha / Signal / System semantic repair | 禁止 |
| full rebuild / daily incremental / v1 complete | 禁止 |
