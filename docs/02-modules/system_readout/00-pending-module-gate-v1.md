# System Readout Pending Module Gate v1

日期：2026-04-29

状态：superseded by freeze review passed / bounded proof passed

## 1. 当前裁决

System Readout 是 Trade 之后的只读主线读出模块。本目录曾用于登记 pre-gate 六件套 draft；
当前 `system-readout-freeze-review-20260507-01` 与
`system-readout-bounded-proof-build-card-20260508-01` 已通过，下一步只允许进入
`pipeline_freeze_review`。

截至 2026-05-08，Trade freeze review 与 Trade bounded proof 均已通过，System Readout
freeze review 也已通过。System Readout 六件套现已冻结为文档合同表面，但仍不得触发全链路
重算或重定义上游字段。

## 2. 等待条件

System Readout 必须等待：

```text
Trade released
```

Trade 放行前，System Readout 不得定义全链路 readout、summary 或 audit snapshot。当前 Trade 已放行，
且 bounded proof 已闭环，因此 `system.duckdb` 与 System runner 已形成 day bounded proof 表面；
但 System full build 与 Pipeline runtime 仍须等待新卡。

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

以下文档已通过 freeze review，但仍不表示 full build 或 release 许可：

| 文档 | 状态 |
|---|---|
| `00-authority-design-v1.md` | frozen / freeze review passed / bounded proof passed / full build not executed |
| `01-semantic-contract-v1.md` | frozen / freeze review passed / bounded proof passed / full build not executed |
| `02-database-schema-spec-v1.md` | frozen / freeze review passed / bounded proof passed / full build not executed |
| `03-runner-contract-v1.md` | frozen / freeze review passed / bounded proof passed / full build not executed |
| `04-audit-spec-v1.md` | frozen / freeze review passed / bounded proof passed / full build not executed |
| `05-build-card-v1.md` | frozen / freeze review passed / bounded proof passed / full build not executed |

下一步只能进入 Pipeline freeze review。任何 System full build、Pipeline runtime 或上游写回，
都仍必须等待新的执行卡与后续门禁。
