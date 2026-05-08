# Pipeline Authority Design v1

日期：2026-04-29

状态：frozen / freeze review passed / single-module orchestration build passed / full-chain dry-run passed / full-chain day bounded proof passed / one-year strategy behavior replay blocked

## 1. 模块定义

Pipeline 是 Asteria 的编排层与治理记录层，不是业务语义模块，也不属于策略主线。

Pipeline 当前已释放三层运行事实：`system_readout` 单模块 orchestration、`full_chain_day` dry-run、以及 `full_chain_day` bounded proof。另有一次 `year_replay` 已真实执行，但因完整自然年覆盖不足而 blocked。它只记录运行、步骤、门禁快照、构建清单和审计结果；不定义 MALF、Alpha、Signal、Position、Portfolio Plan、Trade 或 System Readout 的业务含义，不回写业务真值，不以自身状态代替模块 release 状态。

## 2. 当前放行事实

```text
pipeline-freeze-review-20260508-01 passed
pipeline-build-runtime-authorization-scope-freeze-20260508-01 passed
pipeline-single-module-orchestration-build-card-20260508-01 passed
pipeline-full-chain-dry-run-authorization-scope-freeze-20260508-01 passed
pipeline-full-chain-dry-run-card-20260508-01 passed
pipeline-full-chain-bounded-proof-build-card-20260508-01 passed
pipeline-full-chain-bounded-proof-closeout-20260508-01 passed
pipeline-one-year-strategy-behavior-replay-authorization-scope-freeze-20260508-01 passed
pipeline-one-year-strategy-behavior-replay-build-card-20260508-01 blocked
```

当前 Pipeline 已证明：

| 项 | 当前状态 |
|---|---|
| formal DB | `H:\Asteria-data\pipeline.duckdb` 已创建 |
| released module scope | `system_readout` single-module orchestration + `full_chain_day` dry-run + `full_chain_day` bounded proof |
| released run modes | `bounded / dry-run / resume / audit-only` |
| current next card | `none` |
| full-chain dry-run | 已执行 / 已通过 |
| full-chain bounded proof | 已执行 / 已通过 |
| one-year strategy behavior replay | 已执行 / `blocked`（完整自然年覆盖不足） |

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
| released module scope | `system_readout` single-module orchestration + `full_chain_day` dry-run + `full_chain_day` bounded proof |
| business mutation | 禁止 |
| downstream writeback | 禁止 |
| year replay release truth | 完整自然年不足时不得 passed |

## 8. 下一步

当前没有 live `current_allowed_next_card`。year replay 已执行过一次，但因为 `2024-01-01..2024-12-31`
未被完整覆盖，只能保持 `blocked`，等待后续新 repair / replay 决策卡。
