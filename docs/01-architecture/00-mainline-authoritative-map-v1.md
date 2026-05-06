# Asteria 主线模块权威图 v1

日期：2026-04-30

## 1. 主线总图

```mermaid
flowchart LR
    DF[Data Foundation<br/>not strategy mainline] --> M[MALF]
    M --> A[Alpha]
    A --> S[Signal]
    S --> P[Position]
    P --> PP[Portfolio Plan]
    PP --> T[Trade]
    T --> SY[System Readout]
    PL[Pipeline] -.run order / status.-> M
    PL -.run order / status.-> A
    PL -.run order / status.-> S
    PL -.run order / status.-> P
    PL -.run order / status.-> PP
    PL -.run order / status.-> T
    PL -.run order / status.-> SY
```

## 1.1 当前门禁状态

截至 `malf-v1-4-core-runtime-sync-implementation-20260505-01`：

| 项 | 当前状态 |
|---|---|
| 当前已冻结主线模块 | `MALF`; `Alpha`; `Signal` |
| 当前已通过 bounded proof | `MALF day`; `Alpha day`; `Signal day`; `MALF v1.4 day runtime sync implementation` |
| 当前已准备执行卡 | `data reference target maintenance scope` plus seven-card upstream repair queue |
| 当前只允许施工 | `Data reference scope freeze / Position construction suspended` |
| 当前仍禁止 | Alpha full build、Signal full build、Position full build、Portfolio Plan/Trade/System/Pipeline 施工 |

`Signal bounded proof` 已基于已放行的 Alpha candidate 完成最小证明。Data Foundation
已补齐正式 `market_meta.duckdb` 的最小事实，并部分释放可匹配正式 Data 标的的申万
2021 当前行业快照。Data Foundation 已封为主线输入底座，后续只能通过明确
maintenance card 扩展；ST、停牌、真实上市/退市状态与历史行业沿革仍不覆盖。Position freeze
review reentry 已完成只读评审并通过；MALF v1.4 day runtime sync implementation 已通过并取代旧 v1.3
runtime evidence。随后 `upstream-pre-position-completeness-synthesis-20260506-01`
裁定：若按最终完整目标衡量，Data / MALF / Alpha / Signal 仍不能给出全部完成的肯定答复，
因此 Position bounded proof 施工暂时搁置。当前仍不授权 Alpha full build、Signal full build、
Position full build、下游施工或全链路 pipeline。
后续必须按七张卡顺序推进：Data reference scope、Data reference closeout、MALF week、
MALF month、Alpha production hardening、Signal production hardening、upstream release decision。

## 2. 主线模块

| 顺序 | 模块 | 是否主线 | 核心职责 |
|---:|---|---:|---|
| 0 | Data Foundation | 否 | 提供 source facts、market base、metadata |
| 1 | MALF | 是 | 结构事实、波段生命、WavePosition |
| 2 | Alpha | 是 | 解释机会，不处理资金和执行 |
| 3 | Signal | 是 | 聚合 Alpha 输出为正式信号账本 |
| 4 | Position | 是 | 把信号转为持仓候选和持仓计划 |
| 5 | Portfolio Plan | 是 | 资金、容量、组合约束、准入裁决 |
| 6 | Trade | 是 | 订单意图、执行价格线、成交账本 |
| 7 | System Readout | 是 | 全链路只读汇总、运行读出、审计快照 |
| 8 | Pipeline | 编排层 | 调度模块、记录步骤，不定义业务语义 |

## 3. 退役或降级模块

| 旧模块/概念 | 新地位 | 理由 |
|---|---|---|
| `structure` | 退役为 MALF Core 内部结构事实 | HH/HL/LL/LH 已归入 MALF-Core |
| `filter` | 降级为 Data/Universe 客观事实或 Alpha 前置 gate | 客观可交易性是地基事实，不是策略解释 |
| `reborn` | 退役 | Core 已定义 transition 后 new wave |
| 牛顺/牛逆/熊顺/熊逆 | 退役 | Core 已用结构推进/非推进完整替代 |

## 4. 模块边界

### MALF

MALF 只产出结构事实与统计位置。

```text
Input: market_base bars
Output: WavePosition
No output: buy/sell/weight/order
```

### Alpha

Alpha 读取 MALF 和可用辅助事实，解释机会。

```text
Input: WavePosition + alpha family facts
Output: alpha event / alpha score / alpha signal candidate
No output: position size / portfolio allocation / order
```

### Signal

Signal 只做信号账本聚合。

```text
Input: alpha outputs
Output: formal signal
No output: capital allocation / fill
```

### Position

Position 把信号变成持仓语义。

```text
Input: formal signal
Output: position candidate / entry plan / exit plan
No output: portfolio-wide capital allocation
```

### Portfolio Plan

Portfolio Plan 做组合层裁决。

```text
Input: position candidates
Output: portfolio plan / target exposure / admitted and trimmed plans
No output: actual fill
```

### Trade

Trade 是执行事实层。

```text
Input: portfolio plan
Output: order intent / execution / fill ledger
No output: strategy score
```

### System Readout

System 只读全链路。

```text
Input: all downstream official ledgers
Output: readout / summary / audit
No output: business mutation
```

## 5. 依赖方向

```mermaid
flowchart TD
    A[MALF] --> B[Alpha]
    B --> C[Signal]
    C --> D[Position]
    D --> E[Portfolio Plan]
    E --> F[Trade]
    F --> G[System]

    B -.must not write back.-> A
    C -.must not write back.-> B
    D -.must not write back.-> C
    E -.must not write back.-> D
    F -.must not write back.-> E
    G -.must not write back.-> F
```

禁止反向依赖：

| 禁止依赖 | 裁决 |
|---|---|
| Alpha 修改 MALF | 禁止 |
| Position 回写 Signal | 禁止 |
| Portfolio Plan 修改 Alpha | 禁止 |
| Trade 影响 Portfolio Plan 历史裁决 | 禁止 |
| System 触发业务重算并改变上游语义 | 禁止 |

## 6. 构建模式

Asteria 采用模块化账本构建：

```text
design freeze
-> schema freeze
-> runner implementation
-> bounded proof
-> full build or segmented build
-> audit
-> release gate
-> downstream integration proof
```

每个模块必须支持：

| 能力 | 要求 |
|---|---|
| 一次性批量建仓 | 必须 |
| 增量更新 | 必须 |
| checkpoint | 必须 |
| dirty queue 或 replay scope | 必须 |
| run ledger | 必须 |
| schema version | 必须 |
| rule version | 语义模块必须 |
| sample version | 统计模块必须 |

## 7. 权威来源与状态更新

主线语义权威与工程治理权威分开：

| 权威输入 | 回答的问题 | 当前用途 |
|---|---|---|
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4.zip` | MALF v1.4 语义与操作边界：v1.3 semantic baseline + Core operational boundary rules | 当前 MALF 语义/操作边界权威；day runtime evidence 已升级到 v1.4 day runtime sync closeout |
| `H:\Asteria-Validated\Asteria-docs-code-20260502-104932.zip` | 最新仓库 docs/code 快照 | Data formal promotion 与 MALF v1.3 closeout 后的系统备份 |
| `H:\Asteria-Validated\Asteria-data-market-meta-formalization-20260502-01.zip` | Data market_meta 最小正式证据 | 证明 Data metadata fact 最小表面已落地，reference gaps retained |
| `H:\Asteria-Validated\Asteria-data-market-meta-sw-industry-snapshot-20260502-01.zip` | Data 申万行业快照证据 | 证明 `industry_classification` 已部分释放申万 2021 当前快照 |
| `H:\Asteria-Validated\Asteria-data-foundation-production-baseline-seal-20260502-01.zip` | Data baseline seal 证据 | 证明 Data 已封为主线输入底座，后续只走 maintenance card |
| `H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.*` | 多 DuckDB、日更、pipeline ledger、release evidence 如何治理 | 支撑逻辑历史总账和增量构建协议 |
| `docs/04-execution/00-conclusion-index-v1.md` | 哪些执行卡已经正式落档 | 当前放行状态入口 |

当前主线图不是“全系统已上线图”。它是模块依赖和施工顺序的法律图：

```text
MALF day 已通过 -> Alpha freeze review 已通过 -> Alpha bounded proof 已通过 -> Signal freeze review 已通过 -> Signal bounded proof 已通过 -> Position freeze review 已阻塞 -> Data formal promotion 已通过 -> MALF v1.4 day runtime sync implementation 已通过 -> Position freeze review reentry 已通过 -> upstream pre-position completeness synthesis 已完成 -> data reference target maintenance scope prepared
```

任何下游实现都必须等前置模块完成 freeze / proof / release evidence。

MALF v1.4 authority package 已形成，并已落实到 day runtime sync implementation；
当前 day runtime 证据由 MALF v1.4 runtime sync closeout 承接。week/month proof 与
full build 仍需另开执行卡，不授权 Alpha full build、Signal full build、Position
construction 或 Pipeline 扩权。
