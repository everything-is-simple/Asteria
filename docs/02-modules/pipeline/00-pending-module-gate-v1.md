# Pipeline Pending Module Gate v1

日期：2026-04-29

状态：historical pre-gate note / superseded by `pipeline-freeze-review-20260508-01`

## 1. 当前裁决

Pipeline 是编排层，不是业务语义模块。本说明记录的是 freeze review 之前的 pre-gate 裁决，
现已由 `pipeline-freeze-review-20260508-01` supersede。当前真实状态是 Pipeline freeze review、
`pipeline-build-runtime-authorization-scope-freeze-20260508-01`、
`pipeline-single-module-orchestration-build-card-20260508-01`、
`pipeline-full-chain-dry-run-authorization-scope-freeze-20260508-01` 与
`pipeline-full-chain-dry-run-card-20260508-01` 已通过；但仍不允许直接跳 bounded proof。

## 2. 等待条件

Pipeline 必须等待：

```text
MALF bounded proof gate passed
active card explicitly authorizes Pipeline freeze review
```

之后也只能在有明确 Pipeline 卡时记录模块运行，不得抢占 Alpha 以后模块的施工位，
也不得把 pre-gate 文档解释为施工许可。

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

## 5. 当前 pre-gate 文档集

本轮已补齐以下 pre-gate draft：

```text
00-authority-design-v1.md
01-semantic-contract-v1.md
02-database-schema-spec-v1.md
03-runner-contract-v1.md
04-audit-spec-v1.md
05-build-card-v1.md
```

这些文档用于锁定 Pipeline 的编排边界、记录边界和未来 runner 审计边界，不构成 frozen、schema gate 或施工许可。

## 6. 下一次重审条件

Pipeline 只有在以下条件满足后，才允许重新审阅是否进入冻结：

```text
MALF bounded proof gate passed
active card explicitly authorizes Pipeline freeze review
```

即便届时进入重审，Pipeline 也仍然只能负责编排与记录，不得定义任何主线业务语义。
