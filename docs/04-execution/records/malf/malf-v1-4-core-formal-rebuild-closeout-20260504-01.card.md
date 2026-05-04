# MALF v1.4 Core Formal Rebuild Closeout Card

日期：2026-05-04

状态：`executed / passed`

## 1. 目的

本卡是 `malf-v1-4-core-runtime-sync-code-20260504-01` 之后的第二张卡，只负责：

- 用正式 `market_base_day.duckdb` 输入重建 `malf_core_day / malf_lifespan_day / malf_service_day`。
- 运行 hard audit、接口审计与 sample 场景审计。
- 形成 repo 内 execution 四件套与 repo 外 validated closeout evidence。
- 在通过后，用新的 v1.4 day closeout 替代 `malf-v1-3-formal-rebuild-closeout-20260502-01`
  作为当前 MALF day runtime evidence。

## 2. 当前边界

- 本卡在 `malf-v1-4-core-formal-rebuild-repair-20260504-01` 完成后已重新执行。
- 历史正式 DuckDB 列位兼容写入问题已被 repair 解开，不再是当前阻塞根因。
- 当前 rerun 已完成 Core / Lifespan / Service / Audit，且 hard audit 已通过。
- 当前正式 runtime evidence 已切换为 `malf-v1-4-core-formal-rebuild-closeout-20260504-01`。
- 当前允许下一张卡已恢复为 `Position freeze review reentry / review-only`。
- week / month 不在本卡范围。
- Position / downstream 仍未打开。
