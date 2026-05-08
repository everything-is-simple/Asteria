# Pipeline Authority Design v1

日期：2026-04-29

状态：frozen / freeze review passed / single-module orchestration build passed / full-chain dry-run prepared

## 1. 模块定义

Pipeline 是 Asteria 的编排层与治理记录层，不是业务语义模块，也不属于策略主线。

Pipeline 当前只释放一层最小运行面：编排 `system_readout` 单模块样本，并记录运行、步骤、门禁快照、构建清单和审计结果。它不定义 MALF、Alpha、Signal、Position、Portfolio Plan、Trade 或 System Readout 的业务含义，不回写业务真值，不以自身状态代替模块 release 状态。

## 2. 当前放行事实

```text
pipeline-freeze-review-20260508-01 passed
pipeline-build-runtime-authorization-scope-freeze-20260508-01 passed
pipeline-single-module-orchestration-build-card-20260508-01 passed
pipeline-full-chain-dry-run-authorization-scope-freeze-20260508-01 passed
```

当前 Pipeline 已证明：

| 项 | 当前状态 |
|---|---|
| formal DB | `H:\Asteria-data\pipeline.duckdb` 已创建 |
| released module scope | `system_readout` only |
| released run modes | `bounded / resume / audit-only` |
| next prepared card | `pipeline-full-chain-dry-run-card-20260508-01` |
| full-chain dry-run | 已准备 / 未执行 |
| full-chain bounded proof | 未授权 |

## 3. 权威来源

Pipeline 输入只来自编排元数据：

```text
module gate registry
module run metadata
build manifest inputs
```

它不读取业务表来重新解释业务语义。

## 4. 只回答什么

| 问题 | Pipeline 是否回答 |
|---|---:|
| 某次编排运行了哪些步骤 | 是 |
| 当前门禁快照是什么 | 是 |
| source / target / artifact 清单是什么 | 是 |
| 审计是否通过 | 是 |
| 业务模块字段代表什么 | 否 |
| 是否买卖、是否持仓、是否分配资金 | 否 |

## 5. 当前输出

目标 DB：

```text
H:\Asteria-data\pipeline.duckdb
```

当前正式表族：

| 表 | 职责 |
|---|---|
| `pipeline_run` | 编排运行记录 |
| `pipeline_step_run` | 单步运行记录 |
| `module_gate_snapshot` | 门禁快照 |
| `build_manifest` | artifact 清单 |
| `pipeline_audit` | Pipeline 审计 |

## 6. 数据流

```mermaid
flowchart LR
    G[module gate registry] --> P[Pipeline]
    R[system_readout run metadata] --> P
    M[build manifest inputs] --> P
    P --> PR[pipeline_run]
    P --> PS[pipeline_step_run]
    P --> GS[module_gate_snapshot]
    P --> BM[build_manifest]
    P --> PA[pipeline_audit]
```

## 7. 边界

| 边界 | 裁决 |
|---|---|
| released module scope | `system_readout` only |
| business mutation | 禁止 |
| downstream writeback | 禁止 |
| full-chain pipeline | 仍需新卡 |

## 8. 下一步

当前已准备但未执行的下一张卡是 `pipeline-full-chain-dry-run-card-20260508-01`。
它只表示下一步可进入 full-chain dry-run card；并不等于 dry-run 已执行。
如需进入 full-chain bounded proof，仍必须另开明确授权卡。
