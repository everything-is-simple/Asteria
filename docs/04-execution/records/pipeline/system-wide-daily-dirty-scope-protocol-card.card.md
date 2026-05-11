# System-Wide Daily Dirty Scope Protocol Card

日期：2026-05-11

状态：`prepared / not executed`

## 1. 目标

冻结 Stage 11 的第一张跨模块协议卡，明确：

- `daily_dirty_scope`
- `daily_impact_scope`
- `checkpoint / resume`
- `source_run_id -> target_run_id` lineage
- writer / read-only 边界

## 2. 触发事实

| item | value |
|---|---|
| prepared by | `pipeline-year-replay-disposition-decision-card-20260510-01` |
| live allowed next action | `system_wide_daily_dirty_scope_protocol_card` |
| current stage | `Stage 11 entry` |

## 3. 允许动作

- 只冻结跨模块 dirty scope / impact scope / lineage 协议。
- 只定义 Stage 11 的 writer/read-only 规则，不改任何既有业务语义。
- 为后续 daily incremental / full rebuild cards 建立统一入口。

## 4. 仍然禁止

| forbidden | decision |
|---|---|
| 直接打开 full rebuild / daily incremental | 禁止 |
| 在本卡内改 year replay 审计语义 | 禁止 |
| 重新定义主线业务字段 | 禁止 |
