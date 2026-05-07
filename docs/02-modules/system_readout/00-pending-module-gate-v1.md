# System Readout Pending Module Gate v1

日期：2026-04-29

状态：freeze review prepared / not frozen

## 1. 当前裁决

System Readout 是 Trade 之后的只读主线读出模块。本目录已补齐 pre-gate 六件套 draft；当前已进入 freeze review prepared 状态，但本轮仍不执行 System Readout 正式施工。

截至 2026-05-07，Trade freeze review 与 Trade bounded proof 均已通过。System Readout
当前只允许准备 `system_readout_freeze_review`，不得触发全链路重算或重定义上游字段。

## 2. 等待条件

System Readout 必须等待：

```text
Trade released
```

Trade 放行前，System Readout 不得定义全链路 readout、summary 或 audit snapshot。Trade 已放行后，
仍仅允许 review-only 审阅，不允许创建 `system.duckdb` 或 System runner。

## 3. 上游依赖

System Readout 只能读取各模块正式账本，不得触发业务重算并改变上游语义。

## 4. 禁止项

| 禁止项 | 原因 |
|---|---|
| 写回 MALF / Alpha / Signal / Position / Portfolio / Trade | System 只读 |
| 触发重算并改变历史事实 | 破坏审计链 |
| 重新定义业务字段含义 | 上游模块已定义 |
| 输出交易执行事实 | 归属 Trade |
| 混合 `wave_core_state` 与 `system_state` | 破坏 MALF 状态边界 |

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

System Readout 进入设计冻结前必须在 Trade released 之后重新审阅这些文档。
