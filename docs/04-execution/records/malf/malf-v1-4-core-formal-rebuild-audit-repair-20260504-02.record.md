# MALF v1.4 Core Formal Rebuild Audit Repair Record

日期：2026-05-04

run_id：`malf-v1-4-core-formal-rebuild-audit-repair-20260504-02`

状态：`passed`

## 1. Repair Scope

- 只修复 MALF day formal rebuild 在正式 `market_base_day.duckdb` 上暴露出的 hard audit 阻塞。
- 不回退 `malf-v1-4-core-formal-rebuild-repair-20260504-01` 的显式列名写入契约。
- 不扩大到 week/month proof，不打开 Position construction 或 downstream construction。

## 2. Root Cause

根因不是 Core / Lifespan / Service 各自独立新增了三类语义 bug，而是 MALF day rebuild 在
正式 `market_base_day` 上同时读入了两条价格线：

- `analysis_price_line / backward`
- `execution_price_line / none`

这导致相同 `symbol + timeframe + bar_dt` 的 bar 被 Core 事件流重复消费，进而连锁放大为：

- candidate 替换链重复记账；
- Lifespan / Service transition bar 重复发布；
- v1.3 trace 字段与 lifespan snapshot 对不上。

## 3. Execution Sequence

1. 在 `src/asteria/malf/bootstrap_support.py` 统一固化 MALF day rebuild 的
   `market_base_source_filters()`。
2. 在 `src/asteria/malf/core_engine.py` 把 Core bar 读取改为只消费
   `analysis_price_line / backward`。
3. 在 `src/asteria/malf/birth_descriptors.py` 把 `candidate_wait_span` 的 source bar 计数
   对齐到相同输入边界。
4. 在 `src/asteria/malf/audit_support.py` 把 audit source-bar binding 对齐到相同输入边界。
5. 在 `tests/unit/malf/test_v14_runtime_sync_code.py` 增加 mixed-price-line regression tests，
   固定 Core、Service 与 audit 三类回归面。
6. 重跑正式 closeout，同范围验证 hard audit 真正回到 `0`。

## 4. Verification

| check | result |
|---|---|
| mixed-price-line Core regression | `passed` |
| mixed-price-line Service regression | `passed` |
| mixed-price-line audit regression | `passed` |
| official formal rerun | `passed` |
| `service_wave_position_natural_key_unique` | `0` |
| `core_new_candidate_replaces_previous` | `0` |
| `service_v13_trace_matches_lifespan` | `0` |

## 5. Boundary Outcome

- 本卡不单独宣称 runtime proof passed；它的通过条件是 closeout rerun 真正通过。
- closeout 已在同一 turn 内重跑通过，因此 MALF day runtime evidence 已切换到
  `malf-v1-4-core-formal-rebuild-closeout-20260504-01`。
- Position 只恢复到 `freeze review reentry / review-only`，没有提前打开 construction。
