# Position Pending Module Gate v1

日期：2026-04-29

状态：pre-gate draft / not frozen

## 1. 当前裁决

Position 是 Signal 之后的主线模块。本目录已补齐 pre-gate 六件套 draft，但本轮不冻结 Position 设计，不允许进入施工。

截至 2026-04-29，当前唯一允许推进的是 `Alpha freeze review`。Position 仍必须等待
Signal release，不得绕过 Signal 直接消费 Alpha 草案或 MALF WavePosition。

## 2. 等待条件

Position 必须等待：

```text
Signal released
```

Signal 放行前，Position 不得定义持仓候选、入场计划或退出计划。

## 3. 上游依赖

Position 只能消费正式 Signal 账本，不得直接用 Alpha 草案或 MALF 字段绕过 Signal。

## 4. 禁止项

| 禁止项 | 原因 |
|---|---|
| 修改 Signal | 下游不得回写上游 |
| 重新计算 Alpha 机会 | 归属 Alpha |
| 重新解释 WavePosition | 归属 MALF |
| 决定组合资金分配 | 归属 Portfolio Plan |
| 生成实际订单 | 归属 Trade |

## 5. 已补齐的 pre-gate draft

以下文档只表示预门禁草案，不表示设计冻结或施工许可：

| 文档 | 状态 |
|---|---|
| `00-authority-design-v1.md` | draft / pre-gate / not frozen |
| `01-semantic-contract-v1.md` | draft / pre-gate / not frozen |
| `02-database-schema-spec-v1.md` | draft / pre-gate / not frozen |
| `03-runner-contract-v1.md` | draft / pre-gate / not frozen |
| `04-audit-spec-v1.md` | draft / pre-gate / not frozen |
| `05-build-card-v1.md` | draft / pre-gate / not frozen |

Position 进入设计冻结前必须在 Signal released 之后重新审阅这些文档。
