# MALF v1.4 Core Formal Rebuild Closeout Card

日期：2026-05-04

状态：`executed / blocked`

## 1. 目的

本卡是 `malf-v1-4-core-runtime-sync-code-20260504-01` 之后的第二张卡，只负责：

- 用正式 `market_base_day.duckdb` 输入重建 `malf_core_day / malf_lifespan_day / malf_service_day`。
- 运行 hard audit、接口审计与 sample 场景审计。
- 形成 repo 内 execution 四件套与 repo 外 validated closeout evidence。
- 在通过后，用新的 v1.4 day closeout 替代 `malf-v1-3-formal-rebuild-closeout-20260502-01`
  作为当前 MALF day runtime evidence。

## 2. 当前边界

- 本卡已执行到 Core formal rebuild 起步阶段，但在首个正式写入事务内阻塞。
- 阻塞根因：历史正式 DuckDB 采用旧列顺序，`created_at` 在前；v1.4 新增策略字段通过
  `ALTER TABLE` 追加到末尾。当前 build 仍使用 `insert into ... values (...)` 的位置写入，
  导致 `pivot_detection_rule_version` 被写入 timestamp 列位并触发 `Conversion Error`。
- 本卡未留下 `run_id = malf-v1-4-core-formal-rebuild-closeout-20260504-01` 的脏写行。
- 当前正式 runtime evidence 仍为 `malf-v1-3-formal-rebuild-closeout-20260502-01`。
- 当前允许下一张卡已切为 `malf_v1_4_core_formal_rebuild_repair`。
- week / month 不在本卡范围。
- Position / downstream 仍未打开。
