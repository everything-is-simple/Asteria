# Trade Pending Module Gate v1

日期：2026-04-27

状态：pending / not frozen

## 1. 当前裁决

Trade 是 Portfolio Plan 之后的主线模块，本轮不冻结 Trade 设计，不允许进入施工。

## 2. 等待条件

Trade 必须等待：

```text
Portfolio Plan released
```

Portfolio Plan 放行前，Trade 不得定义订单意图、执行价格线、成交账本或拒单账本。

## 3. 上游依赖

Trade 只能消费正式 Portfolio Plan 输出，不得绕过组合裁决直接使用 Position、Signal 或 Alpha。

## 4. 禁止项

| 禁止项 | 原因 |
|---|---|
| 修改 Portfolio Plan 历史裁决 | 下游不得回写上游 |
| 重新定义目标暴露 | 归属 Portfolio Plan |
| 重新定义持仓计划 | 归属 Position |
| 修改 MALF / Alpha / Signal | 越过主线边界 |
| 输出系统级结论 | 归属 System Readout |

## 5. 未来必须补齐

Trade 进入设计冻结前必须补齐：

```text
00-authority-design-v1.md
01-semantic-contract-v1.md
02-database-schema-spec-v1.md
03-runner-contract-v1.md
04-audit-spec-v1.md
05-build-card-v1.md
```
