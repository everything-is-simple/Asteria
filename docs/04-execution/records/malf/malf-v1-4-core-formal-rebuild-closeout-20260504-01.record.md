# MALF v1.4 Core Formal Rebuild Closeout Record

日期：2026-05-04

run_id：`malf-v1-4-core-formal-rebuild-closeout-20260504-01`

状态：`passed`

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

1. `malf-v1-4-core-formal-rebuild-audit-repair-20260504-02` 先修复 MALF day rebuild
   对 `market_base_day` 混合价格线的重复消费问题。
2. 在 `src/asteria/malf/bootstrap_support.py` 固化 MALF day rebuild 只读取
   `analysis_price_line / backward` 的 source filter。
3. 在同一 `run_id` 下重新执行 `scripts/malf/run_malf_day_core_build.py`、
   `scripts/malf/run_malf_day_lifespan_build.py`、
   `scripts/malf/run_malf_day_service_build.py` 与 `scripts/malf/run_malf_day_audit.py`。
4. Core / Lifespan / Service / Audit 全部完成，hard audit 从 `8738` 收敛到 `0`。

## 4. Repaired Audit Checks

| check | failed_count |
|---|---:|
| `service_wave_position_natural_key_unique` | `0` |
| `core_new_candidate_replaces_previous` | `0` |
| `service_v13_trace_matches_lifespan` | `0` |
| `hard_fail_count total` | `0` |

## 5. Formal Output Impact

| 项 | 结果 |
|---|---|
| source rows consumed | `1,280,703` |
| core wave rows written | `314` |
| core state snapshot rows written | `4,613` |
| lifespan snapshot rows written | `4,613` |
| service wave position rows written | `4,613` |
| service latest rows written | `20` |
| interface audit rows written | `22` |
| current runtime evidence switched | `yes` |
| current runtime evidence | `malf-v1-4-core-formal-rebuild-closeout-20260504-01` |
| allowed next action | `Position freeze review reentry / review-only` |

## 6. Boundary

本卡通过后只放行 MALF v1.4 day runtime proof，不纳入 week/month proof，不打开
Position construction，不打开任何 downstream construction；下一步只恢复
`Position freeze review reentry` 的 review-only 入口。
