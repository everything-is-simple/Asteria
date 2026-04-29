# Portfolio Plan Pending Module Gate v1

日期：2026-04-29

状态：pre-gate draft / not frozen

## 1. 当前裁决

Portfolio Plan 是 Position 之后的主线模块。本目录已补齐 pre-gate 六件套 draft，但本轮不冻结 Portfolio Plan 设计，不允许进入施工。

截至 2026-04-29，当前唯一允许推进的是 `Alpha freeze review`。Portfolio Plan
仍必须等待 Position release，不得绕过 Position 定义组合资金或目标暴露。

## 2. 等待条件

Portfolio Plan 必须等待：

```text
Position released
```

Position 放行前，Portfolio Plan 不得定义组合准入、资金分配或目标暴露。

## 3. 上游依赖

Portfolio Plan 只能消费正式 Position 输出，不得绕过 Position 直接消费 Signal 或 Alpha 草案。

## 4. 禁止项

| 禁止项 | 原因 |
|---|---|
| 修改 Position 历史计划 | 下游不得回写上游 |
| 重新定义 Signal 强弱 | 归属 Signal |
| 重新解释 MALF 结构位置 | 归属 MALF |
| 生成成交事实 | 归属 Trade |
| 输出全链路系统读出 | 归属 System Readout |

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

Portfolio Plan 进入设计冻结前必须在 Position released 之后重新审阅这些文档。
