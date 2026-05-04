# MALF v1.4 Core Formal Rebuild Closeout Record

日期：2026-05-04

run_id：`malf-v1-4-core-formal-rebuild-closeout-20260504-01`

状态：`blocked at hard audit after rerun`

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

## 3. Rerun Path

1. `malf-v1-4-core-formal-rebuild-repair-20260504-01` 已先修复历史正式库列位兼容写入问题。
2. 在同一 `run_id` 下重新执行 `scripts/malf/run_malf_day_core_build.py`。
3. Core 不再在首个正式写入事务内失败，并继续完成 `lifespan`、`service`、`audit`。
4. 最终阻塞转移到 hard audit，而不是写入兼容层。

## 4. Current Failure Point

| check | failed_count |
|---|---:|
| `service_wave_position_natural_key_unique` | `4767` |
| `core_new_candidate_replaces_previous` | `3579` |
| `service_v13_trace_matches_lifespan` | `392` |
| `hard_fail_count total` | `8738` |

## 5. Formal Output Impact

| 项 | 结果 |
|---|---|
| core wave rows written | `744` |
| core state snapshot rows written | `9,534` |
| lifespan snapshot rows written | `9,534` |
| service wave position rows written | `9,534` |
| service latest rows written | `20` |
| interface audit rows written | `22` |
| current runtime evidence switched | `no` |
| current runtime evidence | `malf-v1-3-formal-rebuild-closeout-20260502-01 remains current` |
| allowed next action | `malf_v1_4_core_formal_rebuild_audit_repair` |

## 6. Boundary

本卡当前已进入 Lifespan / Service / hard audit，但未通过 hard audit，因此仍不纳入 week/month
proof，不打开 Position construction，不打开任何 downstream construction。
