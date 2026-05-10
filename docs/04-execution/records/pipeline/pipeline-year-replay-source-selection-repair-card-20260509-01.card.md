# Pipeline Year Replay Source Selection Repair Card

日期：2026-05-10

状态：`prepared / not executed`

## 1. 目标

在 `system-readout-2024-coverage-repair-card-20260509-01` 已真实完成之后，只修 Pipeline 的
year replay source-selection 逻辑，让 `run_year_replay_coverage_gap_diagnosis` 和后续 rerun 只读消费
released System Readout truth，而不是继续留在旧的 routing / lock 语义上。

## 2. 触发事实

| item | value |
|---|---|
| released System Readout earliest day | `2024-01-02` |
| follow-up attribution | `calendar_semantic_gap_only` |
| prepared handoff | `pipeline-system-readout-2024-coverage-repair-handoff-20260510-01` |

## 3. 允许动作

- 只修 Pipeline source-selection 归因与读取路径。
- 不改写 `system.duckdb`。
- 不打开 System full build、Pipeline semantic repair、full rebuild 或 daily incremental。

## 4. 仍然禁止

| forbidden | decision |
|---|---|
| 回写上游模块 | 禁止 |
| 重新定义 year replay 的业务语义 | 禁止 |
| v1 complete | 禁止 |
