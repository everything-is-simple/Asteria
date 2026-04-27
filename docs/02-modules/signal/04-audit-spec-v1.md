# Signal Audit Spec v1

日期：2026-04-27

状态：draft / pre-gate / not frozen

## 1. 审计目标

Signal 审计用于证明 Signal 只读消费 Alpha 输出，输出仅限 formal signal ledger，并且没有越界写入 Alpha、MALF、Position、Portfolio Plan、Trade 或 System。

## 2. 前置审计

| 检查 | 失败裁决 |
|---|---|
| Alpha released | hard fail |
| alpha family 输出可读取 | hard fail |
| Alpha hard audit 全通过 | hard fail |
| source Alpha release version 已记录 | hard fail |
| Signal 不直接读取 MALF 形成业务输出 | hard fail |

## 3. 输入边界硬审计

| 检查 | 失败裁决 |
|---|---|
| Signal 不得修改 Alpha DB | hard fail |
| Signal 输入必须能追溯到 Alpha candidate 自然键 | hard fail |
| Signal 不得伪造 Alpha candidate | hard fail |
| Signal 不得把 Alpha 缺行解释为 MALF 错误 | hard fail |
| Signal 输入必须记录 Alpha rule version | hard fail |

## 4. 输出语义硬审计

| 检查 | 失败裁决 |
|---|---|
| `formal_signal_ledger` 自然键唯一 | hard fail |
| `signal_component_ledger` 自然键唯一 | hard fail |
| formal signal 必须至少有一个 component | hard fail |
| signal component 必须可追溯到 Alpha candidate | hard fail |
| formal signal 不得包含 `position_size` | hard fail |
| formal signal 不得包含 `target_weight` | hard fail |
| formal signal 不得包含 `order_intent_id` | hard fail |
| Signal 输出不得写入 Position DB | hard fail |

## 5. 聚合规则硬审计

| 检查 | 失败裁决 |
|---|---|
| 每行 formal signal 必须有 `signal_rule_version` | hard fail |
| signal rule version 必须能追溯到 `signal_rule_version` 表 | hard fail |
| component weight 不得解释为资金权重 | hard fail |
| conflicting components 必须记录 component role | hard fail |
| rejected signal 必须记录 reason code 或审计样例 | hard fail |

## 6. 软观察

| 检查 | 裁决 |
|---|---|
| signal 输出过少 | observe |
| rejected 占比异常 | observe |
| 单一 Alpha family 过度主导 | observe |
| conflict component 占比异常 | observe |

软观察只形成报告，不自动放行或阻塞。是否阻塞由 Signal release review 决定。

## 7. 审计输出

审计写入：

```text
signal_audit
```

最小字段：

| 字段 | 说明 |
|---|---|
| `audit_id` | 审计 id |
| `run_id` | Signal run |
| `check_name` | 检查项 |
| `severity` | `hard / soft` |
| `status` | `pass / fail / observe` |
| `failed_count` | 失败行数 |
| `sample_payload` | 样例 |

## 8. 审计裁决

| 结果 | 裁决 |
|---|---|
| hard fail > 0 | Signal 不得放行 |
| hard 全 pass，soft 有 observe | 可进入人工复核 |
| hard 全 pass，soft 无阻塞 | 可形成 bounded proof evidence |

## 9. 验收样本

首轮 bounded proof 样本必须覆盖：

| 场景 | 要求 |
|---|---|
| 单一 Alpha family 支持 signal | 必须 |
| 多个 Alpha family 同向支持 signal | 必须 |
| Alpha family 互相冲突 | 必须 |
| Alpha candidate 被过滤或拒绝 | 必须 |
| formal signal active | 必须 |
| formal signal rejected | 必须 |

若真实样本不足，必须补人工 fixture，但 fixture 不得改变 Alpha 或 MALF 语义。
