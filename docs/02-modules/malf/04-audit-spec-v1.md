# MALF Audit Spec v1

日期：2026-04-30

状态：frozen / v1.4 day runtime sync passed / week/month bounded proof passed / hard audit source-bound / v1.4 authority sync passed

## 1. 审计目标

MALF 审计用于证明 Core、Lifespan、Service 三层没有破坏权威语义，并且 WavePosition 可被 Alpha 只读消费。

`malf-v1-4-core-runtime-sync-implementation-20260505-01` 已按本审计规格形成
`hard_fail_count = 0` 的 passed 结论。该结论是当前 MALF day runtime evidence，
不是下游施工许可。

## 2. Core 硬审计

| 检查 | 失败裁决 |
|---|---|
| terminated wave 不得重新 alive | hard fail |
| break 后不得延伸旧 wave | hard fail |
| transition 必须有关联 `old_wave_id` | hard fail |
| confirmed transition 必须有 `new_wave_id` | hard fail |
| 同一 transition 同一时刻只能一个 active candidate | hard fail |
| new wave 必须由 active candidate 和 progress confirmation 创建 | hard fail |
| candidate up confirmation 必须高于 old final HH | hard fail |
| candidate down confirmation 必须低于 old final LL | hard fail |
| candidate reference 必须等于 transition old progress extreme | hard fail |

v1.4 当前 Core hard audit：

| 检查 | 失败裁决 |
|---|---|
| break(up wave) 必须击穿 `current_effective_HL`，不是任意历史 HL | hard fail |
| break(down wave) 必须击穿 `current_effective_LH`，不是任意历史 LH | hard fail |
| transition 必须同时具备 `transition_boundary_high` 与 `transition_boundary_low` | hard fail |
| same-direction / opposite-direction new wave confirmation 必须使用 transition boundary | hard fail |
| active candidate 必须等于最新有效 candidate guard | hard fail |
| 被相反方向 candidate guard 替代的旧 candidate 不得继续确认 new wave | hard fail |

## 3. Lifespan 硬审计

| 检查 | 失败裁决 |
|---|---|
| new wave confirmation bar 的 `no_new_span = 0` | hard fail |
| `transition_span` 不并入 `no_new_span` | hard fail |
| transition 中 `direction` 必须为 old_direction | hard fail |
| rank 样本必须能追溯到 `sample_version` | hard fail |
| lifespan 规则必须能追溯到 `lifespan_rule_version` | hard fail |
| audit 必须能解析 `source_lifespan_run_id` 且查到 source rows | hard fail |

v1.4 当前 Lifespan hard audit：

| 检查 | 失败裁决 |
|---|---|
| birth descriptor 字段必须与 Core transition / candidate / confirmation 事实一致 | hard fail |
| `candidate_wait_span` 必须从 active candidate guard 后开始计数 | hard fail |
| `candidate_replacement_count` 必须等于 transition 内 candidate 替换事实 | hard fail |
| `confirmation_distance_abs/pct` 必须使用 transition boundary 计算 | hard fail |

## 4. Service 硬审计

| 检查 | 失败裁决 |
|---|---|
| `wave_core_state` 不得为 `transition` | hard fail |
| `system_state = transition` 时 `old_wave_id` 必填 | hard fail |
| `system_state = transition` 时 `wave_id` 为空 | hard fail |
| `system_state = transition` 时 `direction` 必须为 old_direction | hard fail |
| WavePosition 自然键唯一 | hard fail |
| `malf_wave_position_latest` 每个 `symbol + timeframe + service_version` 只有一行 | hard fail |
| audit 必须能解析 `source_core_run_id` 且查到 source rows | hard fail |

v1.4 当前 Service hard audit：

| 检查 | 失败裁决 |
|---|---|
| WavePosition transition trace 字段必须能回溯 Core break / transition / candidate ledger | hard fail |
| WavePosition 不得发布未确认 new wave 为 alive | hard fail |
| Service 发布的 `new_wave_id` 必须来自 Core confirmed new wave | hard fail |
| Service 不得发明 Core / Lifespan 中不存在的 birth descriptor | hard fail |

## 5. 接口审计输出

接口审计写入：

```text
malf_interface_audit
```

最小字段：

| 字段 | 说明 |
|---|---|
| `audit_id` | 审计 id |
| `run_id` | service run |
| `check_name` | 检查项 |
| `severity` | `hard / soft` |
| `status` | `pass / fail / observe` |
| `failed_count` | 失败行数 |
| `sample_payload` | 样例 |

## 6. 审计裁决

| 结果 | 裁决 |
|---|---|
| hard fail > 0 | MALF 不得放行 |
| hard 全 pass，soft 有 observe | 可进入人工复核 |
| hard 全 pass，soft 无阻塞 | 可形成 release evidence |

## 7. 验收样本

首轮 bounded proof 样本必须覆盖：

| 场景 | 要求 |
|---|---|
| alive wave 持续推进 | 必须 |
| alive wave 停滞 | 必须 |
| break 后进入 transition | 必须 |
| same-direction new wave | 必须 |
| opposite-direction new wave | 必须 |

若真实样本不足，必须补人工 fixture。
