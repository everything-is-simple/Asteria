# MALF Database Schema Spec v1

日期：2026-04-30

状态：frozen / v1.4 day runtime sync passed / v1.4 authority sync passed

## 1. 规格范围

第一阶段只冻结 day 级别三库：

```text
H:\Asteria-data\malf_core_day.duckdb
H:\Asteria-data\malf_lifespan_day.duckdb
H:\Asteria-data\malf_service_day.duckdb
```

week / month 在 day gate 通过后复用同一规格，但仍必须另走施工卡和 release
gate。MALF day、week 与 month bounded proof 已通过，不自动放行 full build。

## 2. 三库关系

```mermaid
flowchart TD
    A[market_base_day] --> B[malf_core_day]
    B --> C[malf_lifespan_day]
    C --> D[malf_service_day]
    B --> D
    D --> E[WavePosition]
```

Service 构建同时读取 Core 与 Lifespan：alive 行的 lifespan 字段来自 `malf_lifespan_snapshot`；transition 行的 `transition_span` 来自 `malf_transition_ledger`，不来自 `malf_lifespan_snapshot`。

当前 day Core 正式读取面固定为：

```text
market_base_day.market_base_bar
timeframe = day
price_line = analysis_price_line
adj_mode = backward
```

## 3. Core DB

| 表 | 自然键 | 说明 |
|---|---|---|
| `malf_core_run` | `run_id` | Core 构建审计 |
| `malf_schema_version` | `schema_version` | schema 版本 |
| `malf_pivot_ledger` | `symbol + timeframe + pivot_dt + pivot_type + pivot_seq_in_bar + core_rule_version` | pivot 事实 |
| `malf_structure_ledger` | `pivot_id + structure_context + reference_pivot_id + core_rule_version` | 结构原语 |
| `malf_wave_ledger` | `symbol + timeframe + wave_seq + core_rule_version` | wave 账本 |
| `malf_break_ledger` | `wave_id + break_dt + guard_pivot_id + core_rule_version` | break 账本 |
| `malf_transition_ledger` | `old_wave_id + break_id + core_rule_version` | transition 账本 |
| `malf_candidate_ledger` | `transition_id + candidate_guard_pivot_id + candidate_direction + core_rule_version` | candidate 账本 |
| `malf_core_state_snapshot` | `symbol + timeframe + bar_dt + run_id` | Core 每 bar 状态快照 |

Core 表必须带：

```text
run_id
schema_version
core_rule_version
created_at
```

v1.4 当前已同步字段：

| 表 | 字段 | 说明 |
|---|---|---|
| `malf_wave_ledger` | `current_effective_guard_pivot_id` | active wave 当前有效 guard |
| `malf_break_ledger` | `broken_guard_pivot_id` | 被击穿的 current effective guard |
| `malf_transition_ledger` | `transition_boundary_high` | transition 上边界 |
| `malf_transition_ledger` | `transition_boundary_low` | transition 下边界 |
| `malf_candidate_ledger` | `candidate_status` | active / invalidated / confirmed 候选状态 |
| `malf_candidate_ledger` | `confirmation_pivot_id` | 触发 new wave 的 progress confirmation pivot |
| `malf_candidate_ledger` | `new_wave_id` | confirmation 后创建的新 wave |
| `malf_candidate_ledger` | `candidate_event_type` | created / refresh / replacement / confirmed |
| `malf_core_run` | `pivot_detection_rule_version`, `core_event_ordering_version`, `price_compare_policy`, `epsilon_policy`, `source_market_base_run_id` | v1.4 runtime policy 元数据 |
| `malf_core_state_snapshot` | `wave_id`, `old_wave_id`, `progress_updated`, `transition_span`, `guard_boundary_price`, `transition_id`, `break_id`, `active_candidate_id`, `source_market_base_run_id` | Core 每 bar replay snapshot |

## 4. Lifespan DB

| 表 | 自然键 | 说明 |
|---|---|---|
| `malf_lifespan_run` | `run_id` | Lifespan 构建审计 |
| `malf_lifespan_snapshot` | `wave_id + bar_dt + lifespan_rule_version` | 每 bar lifespan 状态 |
| `malf_lifespan_profile` | `timeframe + direction + sample_version + metric_name + sample_cutoff` | rank 样本分布 |
| `malf_sample_version` | `sample_version` | 样本范围版本 |
| `malf_rule_version` | `lifespan_rule_version` | lifespan 规则版本 |

Lifespan 表必须带：

```text
run_id
schema_version
lifespan_rule_version
sample_version
created_at
```

v1.4 当前已同步字段：

| 字段 | 说明 |
|---|---|
| `birth_type` | initial / same-direction / opposite-direction |
| `candidate_wait_span` | active candidate 到 confirmation 的等待跨度 |
| `candidate_replacement_count` | transition 内 candidate 替换次数 |
| `confirmation_distance_abs` | confirmation 越过 boundary 的绝对距离 |
| `confirmation_distance_pct` | confirmation 越过 boundary 的比例距离 |

## 5. Service DB

| 表 | 自然键 | 说明 |
|---|---|---|
| `malf_service_run` | `run_id` | Service 构建审计 |
| `malf_wave_position` | `symbol + timeframe + bar_dt + service_version` | Alpha-facing WavePosition |
| `malf_wave_position_latest` | `symbol + timeframe + service_version` | 最新 WavePosition |
| `malf_interface_audit` | `audit_id` | 接口完整性审计 |

首次 wave 尚未确认的 uninitialized bar 不写入 `malf_wave_position`。截至 service run 最新 bar 仍未初始化的 symbol 不写入 `malf_wave_position_latest`；下游缺行即视为 uninitialized。

Service 表必须带：

```text
run_id
schema_version
service_version
source_core_run_id
source_lifespan_run_id
created_at
```

## 6. WavePosition 最小字段

| 字段 | 要求 |
|---|---|
| `symbol` | 必填 |
| `timeframe` | 必填，第一阶段为 `day` |
| `bar_dt` | 必填 |
| `system_state` | `up_alive / down_alive / transition` |
| `wave_id` | alive 状态必填，transition 中为空 |
| `old_wave_id` | transition 中必填 |
| `wave_core_state` | `alive / terminated` |
| `direction` | 必填，transition 中为 old_direction |
| `new_count` | 必填 |
| `no_new_span` | 必填 |
| `transition_span` | 必填 |
| `update_rank` | 可空但字段必有 |
| `stagnation_rank` | 可空但字段必有 |
| `life_state` | 必填 |
| `position_quadrant` | 必填 |
| `guard_boundary_price` | 可空 |
| `transition_boundary_high` | 当前已同步字段 |
| `transition_boundary_low` | 当前已同步字段 |
| `active_candidate_guard_pivot_id` | 当前已同步字段 |
| `confirmation_pivot_id` | 当前已同步字段 |
| `new_wave_id` | 当前已同步字段 |
| `birth_type` | 当前已同步字段 |
| `candidate_wait_span` | 当前已同步字段 |
| `candidate_replacement_count` | 当前已同步字段 |
| `confirmation_distance_abs` | 当前已同步字段 |
| `confirmation_distance_pct` | 当前已同步字段 |
| `sample_scope` | 必填 |
| `sample_version` | 必填 |
| `lifespan_rule_version` | 必填 |
| `service_version` | 必填 |

## 7. ER 图

```mermaid
erDiagram
    malf_wave_ledger ||--o{ malf_break_ledger : terminated_by
    malf_break_ledger ||--|| malf_transition_ledger : opens
    malf_transition_ledger ||--o{ malf_candidate_ledger : owns
    malf_wave_ledger ||--o{ malf_lifespan_snapshot : measured_by
    malf_lifespan_snapshot ||--o{ malf_wave_position : published_as
    malf_transition_ledger ||--o{ malf_wave_position : publishes_transition_span
```

## 8. 写入裁决

| 规则 | 裁决 |
|---|---|
| 正式 DB 路径 | `H:\Asteria-data` |
| working DB 路径 | `H:\Asteria-temp\malf\<run_id>\` |
| 写入方式 | 批量写入 |
| 同库多写 | 禁止 |
| 旧数据替换 | staging 审计通过后 promote |
| `run_id` | 审计字段，不作为业务自然键 |
