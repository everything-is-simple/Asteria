# MALF v1.4 Core Formal Rebuild Closeout Card

日期：2026-05-04

状态：`prepared / not executed`

## 1. 目的

本卡是 `malf-v1-4-core-runtime-sync-code-20260504-01` 之后的第二张卡，只负责：

- 用正式 `market_base_day.duckdb` 输入重建 `malf_core_day / malf_lifespan_day / malf_service_day`。
- 运行 hard audit、接口审计与 sample 场景审计。
- 形成 repo 内 execution 四件套与 repo 外 validated closeout evidence。
- 在通过后，用新的 v1.4 day closeout 替代 `malf-v1-3-formal-rebuild-closeout-20260502-01`
  作为当前 MALF day runtime evidence。

## 2. 当前边界

- 本卡尚未执行。
- week / month 不在本卡范围。
- Position / downstream 仍未打开。
