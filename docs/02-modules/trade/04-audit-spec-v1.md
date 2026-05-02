# Trade Audit Spec v1

日期：2026-04-27

状态：draft / pre-gate / not frozen

## 1. 审计目标

Trade 审计用于证明 Trade 只读消费 Portfolio Plan 输出，输出仅限 order intent、execution plan、fill ledger 和 rejection ledger，并且没有越界写入 Portfolio Plan、Position、Signal、Alpha、MALF 或 System。

## 2. 前置审计

| 检查 | 失败裁决 |
|---|---|
| Portfolio Plan released | hard fail |
| admitted plan / target exposure 可读取 | hard fail |
| Portfolio Plan hard audit 全通过 | hard fail |
| source Portfolio Plan release version 已记录 | hard fail |
| Trade 不直接读取 Position / Signal / Alpha / MALF 形成业务输出 | hard fail |

## 3. 输入边界硬审计

| 检查 | 失败裁决 |
|---|---|
| Trade 不得修改 Portfolio Plan DB | hard fail |
| Trade 输入必须能追溯到 portfolio admission 自然键 | hard fail |
| Trade 不得伪造 admitted plan | hard fail |
| Trade 不得把 Portfolio Plan 缺行解释为上游错误 | hard fail |
| Trade 输入必须记录 Portfolio Plan rule version | hard fail |

## 4. 输出语义硬审计

| 检查 | 失败裁决 |
|---|---|
| `order_intent_ledger` 自然键唯一 | hard fail |
| `execution_plan_ledger` 自然键唯一 | hard fail |
| `fill_ledger` 自然键唯一 | hard fail |
| `order_rejection_ledger` 自然键唯一 | hard fail |
| executable order intent 必须至少有一个 execution plan | hard fail |
| fill 必须可追溯到 order intent | hard fail |
| rejection 必须可追溯到 order intent | hard fail |
| Trade 输出不得包含 `strategy_score` | hard fail |
| Trade 输出不得写入 System DB | hard fail |

## 5. 执行规则硬审计

| 检查 | 失败裁决 |
|---|---|
| 每行 order intent 必须有 `trade_rule_version` | hard fail |
| trade rule version 必须能追溯到 `trade_rule_version` 表 | hard fail |
| fill quantity 不得为负 | hard fail |
| fill amount 必须与 fill price / quantity 可审计 | hard fail |
| fill price / order price 必须来自 Data `execution_price_line` | hard fail |
| Trade 不得使用 Data `analysis_price_line` 作为真实成交价 | hard fail |
| rejected order 必须记录 rejection reason | hard fail |

## 6. 软观察

| 检查 | 裁决 |
|---|---|
| rejection 占比异常 | observe |
| partial fill 占比异常 | observe |
| fill price 偏离 execution price line | observe |
| expired order 占比异常 | observe |

软观察只形成报告，不自动放行或阻塞。是否阻塞由 Trade release review 决定。

## 7. 审计输出

审计写入：

```text
trade_audit
```

最小字段：

| 字段 | 说明 |
|---|---|
| `audit_id` | 审计 id |
| `run_id` | Trade run |
| `check_name` | 检查项 |
| `severity` | `hard / soft` |
| `status` | `pass / fail / observe` |
| `failed_count` | 失败行数 |
| `sample_payload` | 样例 |

## 8. 审计裁决

| 结果 | 裁决 |
|---|---|
| hard fail > 0 | Trade 不得放行 |
| hard 全 pass，soft 有 observe | 可进入人工复核 |
| hard 全 pass，soft 无阻塞 | 可形成 bounded proof evidence |

## 9. 验收样本

首轮 bounded proof 样本必须覆盖：

| 场景 | 要求 |
|---|---|
| order intent created | 必须 |
| execution plan created | 必须 |
| fill recorded | 必须 |
| partial fill 或 expired order | 必须 |
| rejection recorded | 必须 |
| source Portfolio Plan trace | 必须 |

若真实样本不足，必须补人工 fixture，但 fixture 不得改变 Portfolio Plan、Position、Signal、Alpha 或 MALF 语义。
