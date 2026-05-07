# Trade Pending Module Gate v1

日期：2026-04-29

状态：superseded by freeze review and bounded proof / retained for pre-gate history

## 1. 当前裁决

Trade 是 Portfolio Plan 之后的主线模块。本目录已补齐 pre-gate 六件套 draft；`trade-freeze-review-20260507-01` 已完成 review-only 审查并冻结六件套合同表面。

截至 2026-05-07，Portfolio Plan bounded proof 已通过，Trade freeze review 已通过，
Trade bounded proof 也已通过。当前只允许准备 `system_readout_freeze_review`；不得绕过
该 review 创建 System DB、System runner 或 full-chain Pipeline。

## 2. 等待条件

Trade 必须等待：

```text
Portfolio Plan released
```

Portfolio Plan 已放行 day bounded surface；Trade 已冻结订单意图、执行价格线、成交账本和拒单账本的合同表面。真实成交事实仍不得伪造：没有 evidence-backed execution / fill source 前，`fill_ledger` 只能作为 schema 或 retained gap。

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

Trade 进入设计冻结前必须在 Portfolio Plan released 之后重新审阅这些文档；本页仅保留
pre-gate 到 bounded proof 的历史门禁迁移。
