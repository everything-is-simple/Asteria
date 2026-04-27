# Alpha Audit Spec v1

日期：2026-04-27

状态：draft / pre-gate / not frozen

## 1. 审计目标

Alpha 审计用于证明 Alpha 只读消费 MALF WavePosition，输出仅限 opportunity event / score / candidate，并且没有越界写入 MALF、Signal、Position、Portfolio Plan、Trade 或 System。

## 2. 前置审计

| 检查 | 失败裁决 |
|---|---|
| MALF WavePosition service 已 release | hard fail |
| `malf_wave_position` 可读取 | hard fail |
| `malf_interface_audit` 硬规则通过 | hard fail |
| source MALF service version 已记录 | hard fail |
| source MALF run id 已记录 | hard fail |

## 3. 输入边界硬审计

| 检查 | 失败裁决 |
|---|---|
| Alpha 不得修改 MALF DB | hard fail |
| Alpha 不得自定义 `system_state` | hard fail |
| Alpha 不得自定义 `wave_core_state` | hard fail |
| Alpha 输入行必须能追溯到 WavePosition 自然键 | hard fail |
| 缺少 WavePosition 的 symbol/bar 不得伪造输入 | hard fail |

## 4. 输出语义硬审计

| 检查 | 失败裁决 |
|---|---|
| `alpha_event_ledger` 自然键唯一 | hard fail |
| `alpha_score_ledger` 自然键唯一 | hard fail |
| `alpha_signal_candidate` 自然键唯一 | hard fail |
| candidate 不得包含 `position_size` | hard fail |
| candidate 不得包含 `target_weight` | hard fail |
| candidate 不得包含 `order_intent_id` | hard fail |
| Alpha 输出不得写入 Signal DB | hard fail |

## 5. Family 规则硬审计

| 检查 | 失败裁决 |
|---|---|
| 每行必须有 `alpha_family` | hard fail |
| `alpha_family` 必须匹配目标 DB | hard fail |
| 每行必须有 `alpha_rule_version` | hard fail |
| 规则版本必须能追溯到 `alpha_rule_version` 表 | hard fail |
| family 输出不得混入其他 family | hard fail |

## 6. 软观察

| 检查 | 裁决 |
|---|---|
| family 输出过少 | observe |
| rejected 占比异常 | observe |
| score 分布异常集中 | observe |
| candidate 与 source WavePosition 状态组合稀疏 | observe |

软观察只形成报告，不自动放行或阻塞。是否阻塞由 Alpha release review 决定。

## 7. 审计输出

审计写入：

```text
alpha_source_audit
```

最小字段：

| 字段 | 说明 |
|---|---|
| `audit_id` | 审计 id |
| `run_id` | Alpha run |
| `alpha_family` | family |
| `check_name` | 检查项 |
| `severity` | `hard / soft` |
| `status` | `pass / fail / observe` |
| `failed_count` | 失败行数 |
| `sample_payload` | 样例 |

## 8. 审计裁决

| 结果 | 裁决 |
|---|---|
| hard fail > 0 | Alpha 不得放行 |
| hard 全 pass，soft 有 observe | 可进入人工复核 |
| hard 全 pass，soft 无阻塞 | 可形成 bounded proof evidence |

## 9. 验收样本

首轮 bounded proof 样本必须覆盖：

| 场景 | 要求 |
|---|---|
| `system_state = up_alive` | 必须 |
| `system_state = down_alive` | 必须 |
| `system_state = transition` | 必须 |
| `life_state` 不同状态 | 必须 |
| `position_quadrant` 不同象限 | 必须 |
| 至少一个 family 输出 qualified event | 必须 |
| 至少一个 family 输出 rejected event | 必须 |

若真实样本不足，必须补人工 fixture，但 fixture 不得改变 MALF 语义。
