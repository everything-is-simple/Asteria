# Pipeline System Readout 2024 Coverage Repair Handoff Card

日期：2026-05-10

状态：`passed / pipeline source-selection repair prepared handoff`

## 1. Objective

在 `system-readout-2024-coverage-repair-card-20260509-01` 已真实完成之后，接住
System Readout repair follow-up diagnosis 的只读结论，把 Pipeline live next action 切换到
`pipeline-year-replay-source-selection-repair-card-20260509-01`。

## 2. Scope

| item | decision |
|---|---|
| module | `pipeline` |
| card type | `governance handoff / prepared next-card update` |
| upstream prerequisite | `system-readout-2024-coverage-repair-card-20260509-01` |
| prepared next card | `pipeline-year-replay-source-selection-repair-card-20260509-01` |

## 3. Allowed Actions

- 更新 Pipeline live next-card truth 到 `pipeline_year_replay_source_selection_repair_card`。
- 复核 System Readout repair follow-up attribution 已唯一落在 `calendar_semantic_gap_only`。
- 同步 gate ledger、conclusion index、roadmap 与 registry。

## 4. Still Forbidden

| forbidden | decision |
|---|---|
| 直接执行 Pipeline year replay source-selection repair | 禁止 |
| 改写 `system.duckdb` | 禁止 |
| 新开 System full build | 禁止 |
| full rebuild / daily incremental / v1 complete | 禁止 |
