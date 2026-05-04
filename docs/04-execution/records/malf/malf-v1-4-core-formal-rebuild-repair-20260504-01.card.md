# MALF v1.4 Core Formal Rebuild Repair Card

日期：2026-05-04

状态：`prepared / not executed`

## 1. 目的

本卡是 `malf-v1-4-core-formal-rebuild-closeout-20260504-01` 的修复前置卡，只负责：

- 修复 MALF day formal rebuild runner 与历史正式 DuckDB 列顺序不兼容的问题。
- 保证 v1.4 policy 字段可写入既有正式 `malf_core_day / malf_lifespan_day / malf_service_day`。
- 增加针对“历史 promoted DB + v1.4 runner”路径的回归验证。
- 修复后重新放行回到 `malf_v1_4_core_formal_rebuild_closeout`。

## 2. 当前边界

- 只允许修改 MALF day build / schema 兼容写入路径。
- 不允许扩大到 week/month proof。
- 不允许切换当前 runtime evidence。
- 不允许打开 Position / downstream construction。
