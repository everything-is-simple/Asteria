# <Execution Card Title>

日期：<YYYY-MM-DD>

## 1. 背景

<为什么开工，承接哪张门禁卡或冻结卡>

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `<module_id>` |
| run_id | `<run_id>` |
| stage | `<freeze-review / bounded-proof / release / ...>` |
| owner | `<owner>` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| source | `<source path or contract>` |
| scope | `<timeframe / date range / symbol scope>` |
| prerequisite docs | `<docs>` |
| authority assets | `<validated assets / authority directories>` |

## 4. 权威边界

| 项 | 值 |
|---|---|
| upstream semantics | `<read-only / redefined / not applicable>` |
| formal DB permission | `<allowed path / not allowed>` |
| allowed next action before card | `<current next action>` |

## 5. 允许动作

- <allowed action 1>
- <allowed action 2>

## 6. 禁止动作

- <forbidden action 1>
- <forbidden action 2>

## 7. 关联入口

- [gate ledger](../../03-refactor/00-module-gate-ledger-v1.md)
- [conclusion index](../00-conclusion-index-v1.md)
- [build card or checklist](<related doc>)
