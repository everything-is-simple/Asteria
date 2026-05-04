# MALF v1.4 Core Formal Rebuild Repair Card

日期：2026-05-04

状态：`passed`

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

## 3. 执行结果

- `src/asteria/malf/bootstrap.py`、`src/asteria/malf/bootstrap_support.py` 已切到显式列名写入。
- `src/asteria/malf/insert_contracts.py` 已成为 MALF day 写入契约单一来源。
- `tests/unit/malf/test_v14_legacy_promoted_tables.py` 已覆盖“历史 promoted DB + v1.4 runner”回归。
- 正式 rerun 已证明历史列位兼容写入问题被修复，但 `malf-v1-4-core-formal-rebuild-closeout-20260504-01`
  随后在 hard audit 处发现新的、超出本卡边界的阻塞，需转入后续 audit repair card。
