# Pipeline Pending Module Gate v1

日期：2026-04-27

状态：pending / not frozen

## 1. 当前裁决

Pipeline 是编排层，不是业务语义模块。本轮不冻结 Pipeline 设计，不允许建立全链路施工。

## 2. 等待条件

Pipeline 必须等待：

```text
MALF bounded proof gate
```

之后只能先记录 MALF 单模块运行，不得抢占 Alpha 以后模块的施工位。

## 3. 允许的未来职责

Pipeline 未来只能负责：

```text
pipeline_run
pipeline_step_run
module_gate_snapshot
build_manifest
```

## 4. 禁止项

| 禁止项 | 原因 |
|---|---|
| 定义业务语义 | Pipeline 只编排 |
| 修改 MALF / Alpha / Signal 等模块输出 | 下游和编排层不得回写业务真值 |
| 把 gate 状态当作策略信号 | gate 是治理状态 |
| 合并模块 DB | 违反多库拓扑 |
| 绕过模块冻结直接运行全链路 | 违反单模块施工门禁 |

## 5. 未来必须补齐

Pipeline 进入设计冻结前必须补齐：

```text
00-authority-design-v1.md
01-semantic-contract-v1.md
02-database-schema-spec-v1.md
03-runner-contract-v1.md
04-audit-spec-v1.md
05-build-card-v1.md
```
