# Downstream Daily Impact Ledger Schema Card

日期：2026-05-11

状态：`passed / downstream daily impact schema frozen`

## 1. 目标

在 Alpha/Signal daily incremental sample 已通过后，冻结 Position / Portfolio Plan / Trade /
System Readout 所需的 downstream daily impact ledger schema、impact map 与必要日期维字段。

## 2. 触发事实

| item | value |
|---|---|
| prepared by | `alpha-signal-daily-incremental-ledger-build-card` |
| live allowed next action | `downstream_daily_impact_ledger_schema_card` |
| current stage | `Stage 11 step 5` |

## 3. 允许动作

- 只冻结 downstream daily impact ledger schema 与 impact map。
- 只在 contract / governance / design 范围内收口 Position / Portfolio Plan / Trade / System Readout 的字段协议。
- 不直接打开 downstream daily runtime。

## 4. Freeze Result

| item | result |
|---|---|
| downstream contract role | `position / portfolio_plan / trade = writer`; `system_readout = read_only_consumer` |
| protocol replay scope | `symbol + trade_date + source_run_id` |
| formal `H:\Asteria-data` mutation | `no` |
| downstream daily runtime opened | `no` |
| next allowed action | `downstream_daily_incremental_runner_build_card` |

## 5. 仍然禁止

| forbidden | decision |
|---|---|
| 借 schema card 直接执行 downstream daily runtime | 禁止 |
| 借 schema card 打开 full rebuild 或宣称 `v1 complete` | 禁止 |
| 重定义上游 Data / MALF / Alpha / Signal 的 dirty scope 或 lineage 语义 | 禁止 |
