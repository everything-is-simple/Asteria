# Position Audit Spec v1

日期：2026-04-27

状态：draft / pre-gate / not frozen

## 1. 审计目标

Position 审计用于证明 Position 只读消费 Signal 输出，输出仅限 position candidate / entry plan / exit plan，并且没有越界写入 Signal、Alpha、MALF、Portfolio Plan、Trade 或 System。

## 2. 前置审计

| 检查 | 失败裁决 |
|---|---|
| Signal released | hard fail |
| `formal_signal_ledger` 可读取 | hard fail |
| Signal hard audit 全通过 | hard fail |
| source Signal release version 已记录 | hard fail |
| Position 不直接读取 Alpha 或 MALF 形成业务输出 | hard fail |

## 3. 输入边界硬审计

| 检查 | 失败裁决 |
|---|---|
| Position 不得修改 Signal DB | hard fail |
| Position 输入必须能追溯到 formal signal 自然键 | hard fail |
| Position 不得伪造 formal signal | hard fail |
| Position 不得把 Signal 缺行解释为 Alpha 或 MALF 错误 | hard fail |
| Position 输入必须记录 Signal rule version | hard fail |

## 4. 输出语义硬审计

| 检查 | 失败裁决 |
|---|---|
| `position_candidate_ledger` 自然键唯一 | hard fail |
| `position_entry_plan` 自然键唯一 | hard fail |
| `position_exit_plan` 自然键唯一 | hard fail |
| planned candidate 必须至少有一个 entry plan | hard fail |
| planned candidate 必须至少有一个 exit plan | hard fail |
| entry / exit plan 必须可追溯到 position candidate | hard fail |
| Position 输出不得包含 `target_weight` | hard fail |
| Position 输出不得包含 `order_intent_id` | hard fail |
| Position 输出不得写入 Portfolio Plan DB | hard fail |

## 5. 持仓规则硬审计

| 检查 | 失败裁决 |
|---|---|
| 每行 candidate 必须有 `position_rule_version` | hard fail |
| position rule version 必须能追溯到 `position_rule_version` 表 | hard fail |
| entry plan 有效期不得早于 candidate_dt | hard fail |
| exit plan 有效期不得早于 candidate_dt | hard fail |
| rejected candidate 必须记录 reason code 或审计样例 | hard fail |

## 6. 软观察

| 检查 | 裁决 |
|---|---|
| candidate 输出过少 | observe |
| rejected 占比异常 | observe |
| planned 但 entry / exit 类型过度单一 | observe |
| expired 占比异常 | observe |

软观察只形成报告，不自动放行或阻塞。是否阻塞由 Position release review 决定。

## 7. 审计输出

审计写入：

```text
position_audit
```

最小字段：

| 字段 | 说明 |
|---|---|
| `audit_id` | 审计 id |
| `run_id` | Position run |
| `check_name` | 检查项 |
| `severity` | `hard / soft` |
| `status` | `pass / fail / observe` |
| `failed_count` | 失败行数 |
| `sample_payload` | 样例 |

## 8. 审计裁决

| 结果 | 裁决 |
|---|---|
| hard fail > 0 | Position 不得放行 |
| hard 全 pass，soft 有 observe | 可进入人工复核 |
| hard 全 pass，soft 无阻塞 | 可形成 bounded proof evidence |

## 9. 验收样本

首轮 bounded proof 样本必须覆盖：

| 场景 | 要求 |
|---|---|
| long candidate | 必须 |
| short 或 neutral candidate | 必须 |
| candidate rejected | 必须 |
| candidate planned | 必须 |
| entry plan expired 或 invalidated | 必须 |
| exit plan planned | 必须 |

若真实样本不足，必须补人工 fixture，但 fixture 不得改变 Signal、Alpha 或 MALF 语义。
