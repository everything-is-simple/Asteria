# MALF Audit Spec v1

日期：2026-04-27

状态：frozen

## 1. 审计目标

MALF 审计用于证明 Core、Lifespan、Service 三层没有破坏权威语义，并且 WavePosition 可被 Alpha 只读消费。

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

## 3. Lifespan 硬审计

| 检查 | 失败裁决 |
|---|---|
| new wave confirmation bar 的 `no_new_span = 0` | hard fail |
| `transition_span` 不并入 `no_new_span` | hard fail |
| transition 中 `direction` 必须为 old_direction | hard fail |
| rank 样本必须能追溯到 `sample_version` | hard fail |
| lifespan 规则必须能追溯到 `lifespan_rule_version` | hard fail |

## 4. Service 硬审计

| 检查 | 失败裁决 |
|---|---|
| `wave_core_state` 不得为 `transition` | hard fail |
| `system_state = transition` 时 `old_wave_id` 必填 | hard fail |
| `system_state = transition` 时 `wave_id` 为空 | hard fail |
| `system_state = transition` 时 `direction` 必须为 old_direction | hard fail |
| WavePosition 自然键唯一 | hard fail |
| `malf_wave_position_latest` 每个 `symbol + timeframe + service_version` 只有一行 | hard fail |

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
