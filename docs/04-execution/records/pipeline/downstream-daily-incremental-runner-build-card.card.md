# Downstream Daily Incremental Runner Build Card

日期：2026-05-12

状态：`passed / downstream daily incremental sample hardened`

## 1. 目标

在 downstream daily impact schema 已冻结后，为 Position / Portfolio Plan / Trade /
System Readout 实现 `day`-only downstream daily incremental runner 样板，验证：

- 按 `daily_impact_scope` 重算
- `checkpoint / resume`
- `source_run_id -> target_run_id` lineage
- 幂等 promote 前的审计闭环

## 2. 触发事实

| item | value |
|---|---|
| prepared by | `downstream-daily-impact-ledger-schema-card` |
| live allowed next action | `pipeline_full_daily_incremental_chain_build_card` |
| current stage | `Stage 11 step 6` |

## 3. 允许动作

- 只做 downstream `day` daily incremental sample runner。
- 只在 `H:\Asteria-temp` / `H:\Asteria-report` 做 temp-only proof。
- 只消费已冻结的 downstream impact map / replay scope / lineage 协议。

## 4. 执行结果

- Position / Portfolio Plan / Trade / System Readout 的 `daily_incremental` wrapper 已全部落地。
- Pipeline 已新增 downstream day-only orchestration 入口，并显式串联 `source_run_id -> target_run_id`。
- 统一输出 `source-manifest.json`、`derived-replay-scope.json`、`daily-impact-scope.json`、`lineage.json`、`batch-ledger.jsonl`、`checkpoint.json` 与 `audit-summary.json`。
- 当前 live next 已前推到 `pipeline_full_daily_incremental_chain_build_card`。

## 5. 仍然禁止

| forbidden | decision |
|---|---|
| 直接把样板 promote 到正式 `H:\Asteria-data` | 禁止 |
| 越过下一张卡直接打开 release closeout / full rebuild | 禁止 |
| 宣称 full rebuild 或 `v1 complete` | 禁止 |
