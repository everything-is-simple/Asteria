# MALF v1.4 Core Formal Rebuild Closeout Record

日期：2026-05-04

run_id：`malf-v1-4-core-formal-rebuild-closeout-20260504-01`

状态：`blocked at core formal rebuild`

## 1. Inputs

- `H:\Asteria-data\market_base_day.duckdb`
- `docs/04-execution/records/data/data-foundation-production-baseline-seal-20260502-01.conclusion.md`
- `docs/04-execution/records/malf/malf-v1-4-core-runtime-sync-code-20260504-01.conclusion.md`
- `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4`

## 2. Attempted Scope

| 项 | 值 |
|---|---|
| mode | `bounded formal-data proof` |
| timeframe | `day` |
| start_dt | `2024-01-01` |
| end_dt | `2024-12-31` |
| symbol_limit | `20` |
| schema_version | `malf-v1-4-runtime-sync-v1` |
| core_rule_version | `core-rule-fractal-1bar-v1` |
| pivot_detection_rule_version | `pivot-rule-fractal-1bar-v1` |
| core_event_ordering_version | `core-event-order-v1` |
| price_compare_policy | `strict` |
| epsilon_policy | `none_after_price_normalization` |
| lifespan_rule_version | `lifespan-rule-v1` |
| sample_version | `sample-v1` |
| service_version | `service-v1` |

## 3. Failure Point

- 阻塞阶段：`core`
- 触发命令：`scripts/malf/run_malf_day_core_build.py`
- 错误类型：`ConversionException`
- 关键报错：`invalid timestamp field format: "pivot-rule-fractal-1bar-v1"`

## 4. Root Cause

- `H:\Asteria-data\malf_core_day.duckdb` 中历史正式表是按 v1.3 列顺序建成，`created_at` 位于
  v1.4 新策略字段之前。
- v1.4 代码通过 `_ensure_columns` 给历史表追加
  `pivot_detection_rule_version / core_event_ordering_version / price_compare_policy / epsilon_policy`，
  这些列被追加到表尾，而不是插入到 `created_at` 之前。
- `run_malf_day_core_build()` 仍使用 `insert into ... values (...)`，按“新建表理想顺序”写入。
- 因此对历史正式库执行 rebuild 时，`pivot_detection_rule_version` 落到了 `created_at` 列位，
  在第一笔 Core 写入时即失败。

## 5. Formal Output Impact

| 项 | 结果 |
|---|---|
| core run rows written | `0` |
| pivot rows written | `0` |
| lifespan rows written | `0` |
| service rows written | `0` |
| audit rows written | `0` |
| current runtime evidence switched | `no` |
| current runtime evidence | `malf-v1-3-formal-rebuild-closeout-20260502-01 remains current` |
| allowed next action | `malf_v1_4_core_formal_rebuild_repair` |

## 6. Boundary

本卡未进入 Lifespan / Service / hard audit，不纳入 week/month proof，不打开 Position
construction，不打开任何 downstream construction。
