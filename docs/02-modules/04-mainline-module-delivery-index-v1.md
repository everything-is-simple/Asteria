# Asteria 主线模块文档交付索引 v1

日期：2026-04-29

## 1. 目的

本索引用来回答：

```text
主线模块文档交付到哪里？
哪些模块已经冻结？
哪些模块只是占位？
哪些模块允许进入施工？
```

正式模块文档存放在：

```text
H:\Asteria\docs\02-modules\
```

正式可交付压缩包存放在：

```text
H:\Asteria-Validated\Asteria-mainline-module-docs-v1.zip
```

当前 docs/code 快照基线：

```text
H:\Asteria-Validated\Asteria-docs-code-20260428-214427.zip
```

该快照之后的 repo HEAD 事实由治理执行记录、commit history 和新的 Validated
归档补充，不得用旧 zip 覆盖当前仓库。

## 2. 权威来源

MALF 的语义权威来自：

```text
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2.zip
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2\
```

该资产包含：

| 文件 | Asteria 地位 |
|---|---|
| `MALF_00_Three_Documents_Bridge_v1_2.md` | 三文档关系桥接 |
| `MALF_01_Core_Definitions_Theorems_v1_3.md` | Core 结构真值 |
| `MALF_02_Lifespan_Stats_Definitions_Theorems_v1_2.md` | Lifespan 统计真值 |
| `MALF_03_System_Service_Interface_v1_2.md` | WavePosition 服务接口真值 |

当前执行权威补充：

| 资产 | 地位 |
|---|---|
| `docs/04-execution/records/malf/malf-day-bounded-proof-20260428-01.conclusion.md` | MALF day bounded proof 已通过 |
| `H:\Asteria-Validated\Asteria-malf-day-bounded-proof-20260428-01.zip` | MALF day release evidence |
| `H:\Asteria-Validated\Asteria-docs-authority-refresh-20260429-01.zip` | 文档权威链刷新归档 |

## 3. 交付状态表

| 顺序 | 模块 | 文档位置 | 文档状态 | 是否允许施工 | 等待条件 |
|---:|---|---|---|---:|---|
| 0 | Data Foundation | `docs/02-modules/data/` | foundation six-doc draft | 否 | 作为地基输入契约继续审阅，不占主线施工位 |
| 1 | MALF | `docs/02-modules/malf/` | frozen / day bounded proof passed | 否 | day 已通过；week/month 或 full build 另需新卡 |
| 2 | Alpha | `docs/02-modules/alpha/` | pre-gate six-doc draft / freeze review next | 否 | 只允许 Alpha freeze review，不允许代码施工 |
| 3 | Signal | `docs/02-modules/signal/` | pre-gate six-doc draft | 否 | 等 Alpha 放行后重新审阅并冻结 |
| 4 | Position | `docs/02-modules/position/` | pre-gate six-doc draft | 否 | 等 Signal 放行后重新审阅并冻结 |
| 5 | Portfolio Plan | `docs/02-modules/portfolio_plan/` | pre-gate six-doc draft | 否 | 等 Position 放行后重新审阅并冻结 |
| 6 | Trade | `docs/02-modules/trade/` | pre-gate six-doc draft | 否 | 等 Portfolio Plan 放行后重新审阅并冻结 |
| 7 | System Readout | `docs/02-modules/system_readout/` | pre-gate six-doc draft | 否 | 等 Trade 放行后重新审阅并冻结 |
| 8 | Pipeline | `docs/02-modules/pipeline/` | pre-gate six-doc draft | 否 | MALF gate 已过但当前不占主线卡位；不得建立全链路 |

## 4. 主线顺序

```mermaid
flowchart LR
    DF[Data Foundation] --> M[MALF]
    M --> A[Alpha]
    A --> S[Signal]
    S --> P[Position]
    P --> PP[Portfolio Plan]
    PP --> T[Trade]
    T --> SY[System Readout]
    PL[Pipeline] -.orchestrates.-> M
    PL -.orchestrates.-> A
    PL -.orchestrates.-> S
    PL -.orchestrates.-> P
    PL -.orchestrates.-> PP
    PL -.orchestrates.-> T
    PL -.orchestrates.-> SY
```

## 5. 交付裁决

已冻结并完成当前 proof：

```text
MALF day bounded proof
```

当前唯一允许推进：

```text
Alpha freeze review
```

除 MALF day proof 外，仍只保留 foundation draft 或 pre-gate draft，不冻结：

```text
Data Foundation
Alpha
Signal
Position
Portfolio Plan
Trade
System Readout
Pipeline
```

Data Foundation foundation draft 与 Alpha / Signal / Position / Portfolio Plan / Trade /
System Readout / Pipeline pre-gate draft 都不得被解释为语义冻结、schema 冻结或施工许可。

## 6. 硬边界

| 边界 | 裁决 |
|---|---|
| MALF 输出 | 只输出结构事实、lifespan 统计位置、WavePosition |
| Alpha 以后写回 MALF | 禁止 |
| `wave_core_state` 与 `system_state` | 必须分离 |
| Pipeline | 只编排和记录，不定义业务语义 |
| 正式 DB | 只能放在 `H:\Asteria-data` |
| 临时构建物 | 只能放在 `H:\Asteria-temp` |
