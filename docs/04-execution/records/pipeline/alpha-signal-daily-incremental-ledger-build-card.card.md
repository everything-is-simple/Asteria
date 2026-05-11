# Alpha Signal Daily Incremental Ledger Build Card

日期：2026-05-11

状态：`prepared / not executed`

## 1. 目标

在 MALF daily incremental sample hardening 已通过后，准备下一张 Stage 11 卡：让 Alpha/Signal
正式接住 MALF 的 `daily_impact_scope` 与 run lineage，并把 `symbol + trade_date + source_run_id`
脏域传播到 Signal。

## 2. 触发事实

| item | value |
|---|---|
| prepared by | `malf-daily-incremental-ledger-build-card` |
| live allowed next action | `alpha_signal_daily_incremental_ledger_build_card` |
| current stage | `Stage 11 step 4` |

## 3. 允许动作

- 只在 Alpha/Signal 范围内接入 `day` daily incremental sample ledger。
- 只消费 MALF 放行的 `daily_impact_scope` 与 `source_run_id -> target_run_id` lineage。
- 不提前打开 Position/Portfolio Plan/Trade/System/Pipeline full daily chain。

## 4. 仍然禁止

| forbidden | decision |
|---|---|
| 借 prepared card 直接执行 downstream daily runtime | 禁止 |
| 打开 full rebuild 或声明 `v1 complete` | 禁止 |
| 重定义 MALF dirty scope / impact scope 语义 | 禁止 |
