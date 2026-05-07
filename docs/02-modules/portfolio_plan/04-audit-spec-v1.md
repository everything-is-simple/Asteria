# Portfolio Plan Audit Spec v1

日期：2026-04-27

状态：frozen / freeze review passed / bounded proof passed / full build not executed

## 1. 审计目标

Portfolio Plan 审计用于证明 Portfolio Plan 只读消费 Position 输出，输出仅限组合准入、约束、目标暴露和裁剪账本，并且没有越界写入 Position、Signal、Alpha、MALF、Trade 或 System。

## 2. 前置审计

| 检查 | 失败裁决 |
|---|---|
| Position released | hard fail |
| Position candidate / entry / exit 可读取 | hard fail |
| Position hard audit 全通过 | hard fail |
| source Position release version 已记录 | hard fail |
| Portfolio Plan 不直接读取 Signal / Alpha / MALF 形成业务输出 | hard fail |

## 3. 输入边界硬审计

| 检查 | 失败裁决 |
|---|---|
| Portfolio Plan 不得修改 Position DB | hard fail |
| Portfolio Plan 输入必须能追溯到 Position candidate 自然键 | hard fail |
| Portfolio Plan 不得伪造 Position candidate | hard fail |
| Portfolio Plan 不得把 Position 缺行解释为 Signal / Alpha / MALF 错误 | hard fail |
| Portfolio Plan 输入必须记录 Position rule version | hard fail |

## 4. 输出语义硬审计

| 检查 | 失败裁决 |
|---|---|
| `portfolio_admission_ledger` 自然键唯一 | hard fail |
| `portfolio_target_exposure` 自然键唯一 | hard fail |
| `portfolio_trim_ledger` 自然键唯一 | hard fail |
| admitted plan 必须至少有一个 target exposure | hard fail |
| target exposure 必须可追溯到 portfolio admission | hard fail |
| trim 必须可追溯到 portfolio admission | hard fail |
| Portfolio Plan 输出不得包含 `order_intent_id` | hard fail |
| Portfolio Plan 输出不得包含 `fill_id` | hard fail |
| Portfolio Plan 输出不得写入 Trade DB | hard fail |

## 5. 组合规则硬审计

| 检查 | 失败裁决 |
|---|---|
| 每行 admission 必须有 `portfolio_plan_rule_version` | hard fail |
| portfolio plan rule version 必须能追溯到 `portfolio_plan_rule_version` 表 | hard fail |
| target exposure 不得解释为成交数量 | hard fail |
| rejected admission 必须记录 reason code 或审计样例 | hard fail |
| trim 必须记录 constraint_name | hard fail |

## 6. 软观察

| 检查 | 裁决 |
|---|---|
| admitted 占比异常 | observe |
| rejected 占比异常 | observe |
| 单一 constraint 过度主导 trim | observe |
| target exposure 分布异常集中 | observe |

软观察只形成报告，不自动放行或阻塞。是否阻塞由 Portfolio Plan release review 决定。

`portfolio_plan_audit` 已在 `portfolio-plan-bounded-proof-build-card-20260507-01` 的
bounded proof 范围内写入并通过 hard audit；full build 审计仍必须另开卡。

## 7. 审计输出

审计写入：

```text
portfolio_plan_audit
```

最小字段：

| 字段 | 说明 |
|---|---|
| `audit_id` | 审计 id |
| `run_id` | Portfolio Plan run |
| `check_name` | 检查项 |
| `severity` | `hard / soft` |
| `status` | `pass / fail / observe` |
| `failed_count` | 失败行数 |
| `sample_payload` | 样例 |

## 8. 审计裁决

| 结果 | 裁决 |
|---|---|
| hard fail > 0 | Portfolio Plan 不得放行 |
| hard 全 pass，soft 有 observe | 可进入人工复核 |
| hard 全 pass，soft 无阻塞 | 可形成 bounded proof evidence |

## 9. 验收样本

首轮 bounded proof 样本必须覆盖：

| 场景 | 要求 |
|---|---|
| admitted plan | 必须 |
| rejected plan | 必须 |
| trimmed plan | 必须 |
| target weight 或 target notional | 必须 |
| constraint triggered | 必须 |
| expired plan | 必须 |

若真实样本不足，必须补人工 fixture，但 fixture 不得改变 Position、Signal、Alpha 或 MALF 语义。
