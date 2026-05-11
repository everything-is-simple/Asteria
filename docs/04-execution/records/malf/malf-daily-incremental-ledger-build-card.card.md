# MALF Daily Incremental Ledger Build Card

日期：2026-05-11

状态：`passed / malf daily incremental sample hardened`

## 1. 目标

在 Data daily incremental sample hardening 已通过后，让 MALF 在 `day` 三库样板边界内正式消费
Data dirty scope，并生成 MALF 自身 daily impact scope / lineage / checkpoint / audit evidence。

## 2. 触发事实

| item | value |
|---|---|
| prepared by | `data-ledger-daily-incremental-hardening-card` |
| live allowed next action | `malf_daily_incremental_ledger_build_card` |
| current stage | `Stage 11 step 3` |

## 3. 允许动作

- 只在 MALF `day` 三库样板边界内实现 `daily_incremental` / `resume` / `audit-only`。
- 只消费 Data 卡放行的 `source_manifest` / `daily_dirty_scope` / `checkpoint` 样板边界。
- 输出 MALF 自身 `daily_impact_scope`、`source_run_id -> target_run_id` lineage、checkpoint 与 batch ledger。

## 4. 执行结果

| item | result |
|---|---|
| sample surface | `malf_core_day.duckdb`; `malf_lifespan_day.duckdb`; `malf_service_day.duckdb` |
| replay rule | `replay forward from earliest dirty date per symbol` |
| formal `H:\Asteria-data` mutation | `no` |
| next allowed action | `alpha_signal_daily_incremental_ledger_build_card` |

## 5. 仍然禁止

| forbidden | decision |
|---|---|
| 把本卡样板结果宣称为正式 MALF daily runtime | 禁止 |
| 打开 week/month daily incremental | 禁止 |
| 打开 Alpha/Signal 或 downstream daily runtime | 禁止 |
| 执行 full rebuild 或声明 `v1 complete` | 禁止 |
