# MALF Daily Incremental Ledger Build Card

日期：2026-05-11

状态：`prepared / not executed`

## 1. 目标

在 Data daily incremental sample hardening 已通过后，准备下一张 MALF 卡：让 MALF 正式消费
Data dirty scope，并生成 MALF 自身 daily impact scope / checkpoint / audit evidence。

## 2. 触发事实

| item | value |
|---|---|
| prepared by | `data-ledger-daily-incremental-hardening-card` |
| live allowed next action | `malf_daily_incremental_ledger_build_card` |
| current stage | `Stage 11 step 3` |

## 3. 允许动作

- 只在后续 MALF 卡内实现 MALF daily incremental ledger build。
- 只消费 Data 卡放行的 `source_manifest` / `daily_dirty_scope` / `checkpoint` 样板边界。
- 输出 MALF 自身 `daily_impact_scope` 与 source_run_id -> target_run_id lineage。

## 4. 仍然禁止

| forbidden | decision |
|---|---|
| 借 prepared card 直接执行 MALF runtime | 禁止 |
| 打开 Alpha/Signal 或 downstream daily runtime | 禁止 |
| 执行 full rebuild 或声明 `v1 complete` | 禁止 |
