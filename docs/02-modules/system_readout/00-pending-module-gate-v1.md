# System Readout Pending Module Gate v1

日期：2026-04-27

状态：pending / not frozen

## 1. 当前裁决

System Readout 是 Trade 之后的只读主线读出模块，本轮不冻结 System Readout 设计，不允许进入施工。

## 2. 等待条件

System Readout 必须等待：

```text
Trade released
```

Trade 放行前，System Readout 不得定义全链路 readout、summary 或 audit snapshot。

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

## 5. 未来必须补齐

System Readout 进入设计冻结前必须补齐：

```text
00-authority-design-v1.md
01-semantic-contract-v1.md
02-database-schema-spec-v1.md
03-runner-contract-v1.md
04-audit-spec-v1.md
05-build-card-v1.md
```
