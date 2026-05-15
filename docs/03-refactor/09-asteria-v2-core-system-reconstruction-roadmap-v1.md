# Asteria v2 Core System Reconstruction Roadmap v1

日期：2026-05-14

## 1. 定位

本路线图用于 `v1-signal-contract-alignment-card-20260514-01` 之后的
post-terminal 架构收敛裁决。它不打开新的 live gate，不改变
`current live next = none / terminal`，也不授权立即重写 runtime。

它回答的问题是：

```text
在 MALF v1.4 已定型、当前 Asteria v1 已 terminal、历史版本各有成熟经验、
外部开源生态已有成熟组件的情况下，Asteria 是否需要进入一次新的全链路收敛型再重构。
```

本路线图的裁决是：

```text
需要再重构。
但这是收敛型再重构，不是推倒重来。
```

## 2. 当前权威状态

| 项 | 当前状态 |
|---|---|
| final release closeout | `final-release-closeout-card` passed / v1 complete |
| 当前 live next card | none / terminal |
| 本路线图性质 | post-terminal / roadmap-only / v2 reconstruction planning |
| 正式 DB mutation | no，本路线图不授权写 `H:\Asteria-data` |
| broker / live trading | deferred，必须等待 Trade / System 研究与执行证据 |
| 第 8 卡 | 暂停扩大实现；只保留为后续 narrow research return proof 候选 |

本路线图不得被解释成：

```text
新的 live gate
MALF v1.4 重定义
直接迁移历史代码
立即替换当前 Asteria v1 正式 DB
立即接 broker / paper-live / 实盘
```

## 3. 核心裁决

### 3.1 MALF v1.4 继续做不可变核心

`H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4` 继续作为长期结构权威。
v2 再重构不得改动 MALF v1.4 的结构定义、WavePosition 语义和操作边界。

| 层 | 裁决 |
|---|---|
| MALF | 结构事实与波段生命，不输出交易动作 |
| Alpha/PAS | 解释机会与候选生命周期，不输出仓位、订单、成交 |
| Signal | 聚合候选并保留 T+1 open execution hint |
| Position | 持仓语义、entry/exit plan、生命周期管理 |
| Portfolio Plan | 资金、容量、组合约束、准入与裁剪 |
| Trade | order intent、execution、rejection、carry、fill boundary |
| System | 全链路只读 readout、归因、研究结论 |

### 3.2 当前 Asteria 的价值

当前 Asteria 不能丢。它的强项是：

| 强项 | 必须保留的原因 |
|---|---|
| 6A / execution records / conclusion index | 防止再回到口头裁决和不可追溯状态 |
| 多 DuckDB 拓扑 | 分离 Data、MALF、Alpha、Signal、Downstream 与 Pipeline 写入边界 |
| MALF v1.4 | 当前最稳定的结构尺 |
| post-terminal proof discipline | 能区分 research proof、bounded proof、formal release 与 broker readiness |
| final release closeout | v1 终态真相，不应被 v2 roadmap 改写 |

### 3.3 历史版本的价值

历史版本不直接继承，但必须系统吸收。

| 来源 | 可吸收能力 | 禁止方式 |
|---|---|---|
| `G:\malf-history\astock_lifespan-alpha` | runner、queue、checkpoint、DuckDB ledger、大规模 materialization、trade order intent/execution | 原样迁移 schema 或覆盖当前 MALF/PAS |
| `G:\malf-history\MarketLifespan-Quant` | PAS -> Position -> Trade -> System bridge、partial exit、carry、trailing stop、readout | 直接复活旧 research_lab 或旧临时 backtest 链 |
| `G:\malf-history\EmotionQuant-gamma` | Broker/Risk/Matcher、T+1 open、订单拒绝、lifecycle trace、A 股执行边界 | 提前接 broker 或让 broker 反向定义 Signal |
| `G:\malf-history\EmotionQuant-alpha/beta` | paper trade、T+1 guard、limit/suspension/retry 测试 | 用早期 demo 逻辑替代正式合同 |
| `G:\malf-history\lifespan-0.01` | 早期 data -> system 合同、position/funding/exit/trade readout 文档 | 继承旧复杂度或混写 position/trade/system |

### 3.4 外部成熟项目的边界

v2 可以使用成熟开源项目，但只能作为 adapter 或 engine，不能作为 Asteria 业务语义真值。

| 能力 | 推荐策略 |
|---|---|
| 本地数据底座 | 继续优先使用本地正式数据与 DuckDB；Data Foundation 是 source-fact service |
| Baostock | 可作为受控 source adapter / refresh source；不得直接替代正式真值 |
| AKShare | 不作为正式依赖候选；稳定性不足，只能作为临时探索参考 |
| DuckDB / Arrow / Polars | 可作为核心数据处理底座 |
| vectorbt / backtesting.py | 可作为 research return readout adapter，不拥有 Trade ledger |
| Qlib | 可作为模型研究或因子实验隔离区，不定义 MALF/PAS |
| LEAN / 其他 broker 框架 | 仅在 broker feasibility 阶段研究，不进入当前核心重构 |
| Dagster / Prefect 类编排 | 可评估为 Pipeline 外层调度工具，但不得定义业务模块语义 |

裁决：

```text
外部项目可以帮我们跑得更稳、更快、更标准。
但 Asteria 的合同、字段、状态机、证据链和模块边界必须由 Asteria 自己定义。
```

## 4. 第 8 卡处置

`v1-alpha-pas-t-plus-one-return-proof-card` 不取消，但暂停扩大为 Trade/System 方案。

保留的窄边界：

| 项 | 裁决 |
|---|---|
| 目标 | 只回答 PAS-aligned Signal 在 T+1 open 语义下是否有研究收益读数 |
| 输入 | 第 7 卡 temp Signal/PAS alignment DB + 本地正式 `market_base_day.duckdb` |
| 输出 | event-level research return readout、skip reason、coverage、drawdown |
| 禁止 | order intent、fill、position leg、account state、broker order、实盘可执行宣称 |

执行前置：

```text
必须先完成 v2-card-01，
明确第 8 卡仍只是 research readout，
并确认它不会抢先定义 Trade / Position / System 合同。
```

## 5. v2 目标架构

v2 目标不是多做几个 runner，而是把全链路拆成三个可证明层级：

| 层级 | 目标 |
|---|---|
| Semantic Core | MALF v1.4 + Alpha/PAS v1 + Signal contract，解释机会与候选 |
| Execution Research | Position / Portfolio / Trade 的研究级执行、退出、carry、风险与 readout |
| Production Boundary | Data maintenance、full rebuild、daily incremental、broker feasibility、paper/live 边界 |

v2 的全链路目标：

```text
local Data
-> MALF v1.4
-> Alpha/PAS v1
-> Signal
-> Position
-> Portfolio Plan
-> Trade Research Execution
-> System Readout
-> Pipeline Orchestration
```

其中 Trade Research Execution 不等于 broker。

## 6. Roadmap Structure

本路线图按 `7 个阶段 / 18 张卡` 组织。

| Stage | 目标 | 卡数 |
|---|---:|---:|
| Stage 0 | v2 路线冻结与 no-live 边界 | 1 |
| Stage 1 | 当前权威与历史合同对账 | 3 |
| Stage 2 | Data source 与外部项目边界冻结 | 2 |
| Stage 3 | Semantic Core 合同收敛 | 3 |
| Stage 4 | Position / Portfolio / Trade 合同恢复 | 4 |
| Stage 5 | System / Pipeline 全链路 proof | 3 |
| Stage 6 | 生产边界与 broker 延后裁决 | 2 |

合计：

```text
18 cards
```

## 7. Card Sequence

| 顺序 | 卡 | 状态 | 目标 |
|---:|---|---|---|
| 1 | `v2-core-system-reconstruction-roadmap-freeze-card` | prepared first route card | 冻结本路线图、no-live 边界、第 8 卡暂停扩大实现 |
| 2 | `v2-current-authority-map-card` | planned | 对齐 `00-governance`、`01-architecture`、`02-modules`、registry、conclusion、formal DB |
| 3 | `v2-history-version-strength-map-card` | planned | 重新盘点历史版本各自成熟模块、可吸收合同和迁移风险 |
| 4 | `v2-contract-conflict-resolution-card` | planned | 裁决当前合同、历史合同、v2 目标合同的冲突优先级 |
| 5 | `v2-local-data-source-boundary-card` | planned | 冻结本地数据优先、Baostock adapter 可选、AKShare 不进正式依赖 |
| 6 | `v2-open-source-adapter-boundary-card` | planned | 裁决 DuckDB/Polars/vectorbt/Qlib/LEAN/Dagster 等工具的 adapter 边界 |
| 7 | `v2-malf-v1-4-service-contract-reconfirmation-card` | planned | 只读重确认 MALF v1.4 service surface 不变 |
| 8 | `v2-alpha-pas-signal-semantic-core-card` | planned | 把第 5-7 卡 Alpha/PAS + Signal proof 收敛为 v2 semantic core |
| 9 | `v2-t-plus-one-return-readout-card` | planned | 执行窄版第 8 卡，输出研究收益读数，不触碰 Trade |
| 10 | `v2-position-management-contract-card` | planned | 恢复 entry / exit / invalidation / reentry / holding lifecycle 合同 |
| 11 | `v2-portfolio-plan-capital-contract-card` | planned | 恢复资金、容量、组合约束、准入与裁剪合同 |
| 12 | `v2-trade-research-execution-contract-card` | planned | 冻结 order intent、execution plan、rejection、carry、fill retained gap |
| 13 | `v2-trade-a-share-guard-and-exit-contract-card` | planned | 冻结 T+1、涨跌停、停牌、撤单/重试、分腿、保本、trailing、time stop |
| 14 | `v2-system-readout-contract-card` | planned | 冻结全链路 readout、归因、研究结论与禁止业务写入 |
| 15 | `v2-full-chain-bounded-proof-card` | planned | 从 local Data 到 System 的 bounded proof，不接 broker |
| 16 | `v2-year-replay-research-readout-card` | planned | 只读或 temp-first 年度研究 replay，给出收益/回撤/覆盖/跳过原因 |
| 17 | `v2-production-hardening-scope-card` | planned | 裁决是否进入正式 full rebuild / daily incremental hardening |
| 18 | `v2-broker-feasibility-decision-card` | deferred | 只有研究价值、Trade 合同和 execution evidence 足够后，才评估 broker |

## 8. Throughput And Confidence

当前把握必须分层表达：

| 目标 | 当前把握 | 原因 |
|---|---:|---|
| 研究级全链路打通 | 80% - 85% | Asteria v1 已有 terminal proof，历史版本有可吸收 Trade/System 经验 |
| 全市场正式构建 + daily incremental | 60% - 70% | 数据质量、full rebuild 时间、resume/idempotence 与合同冲突仍需证明 |
| broker / paper-live / 实盘 | 25% - 35% | fill source、真实账户状态、撮合与风控仍未形成当前 Asteria 证据 |

本路线图的成功标准不是马上证明能赚钱，而是先证明：

```text
我们知道每一层在干什么。
每一层只说自己能证明的话。
每一层都能被审计、重放、归因。
```

## 9. Hard Boundaries

| 禁止项 | 原因 |
|---|---|
| 修改 MALF v1.4 定义 | MALF 已是长期结构尺 |
| 外部项目定义 Asteria 合同 | 会让语义被工具绑架 |
| AKShare 进入正式 source truth | 稳定性不足 |
| 第 8 卡直接扩成 Trade card | 会混淆 research return 与 execution ledger |
| 迁移历史代码先于合同冻结 | 会复活旧系统混乱边界 |
| broker feasibility 前置 | 策略价值、Trade 合同、fill boundary 都未证明 |
| 写 `H:\Asteria-data` | 本路线图只冻结路线，不执行 formal mutation |

## 10. Immediate Next

当前 immediate next 是：

```text
v2-core-system-reconstruction-roadmap-freeze-card
```

该卡只做四件事：

1. 把本路线图登记为 post-terminal 独立路线。
2. 明确第 8 卡暂停扩大实现，只保留 narrow research return proof 候选。
3. 冻结 local data first、Baostock optional adapter、AKShare not formal dependency。
4. 保持 `current live next = none / terminal`。

## 11. One Sentence

```text
Asteria v2 不是重写一个新玩具，而是把当前 MALF v1.4 定型版、历史版本成熟交易执行经验、
以及外部成熟工程工具，收敛成一条可证明、可重放、可审计、暂不接 broker 的 data -> system 新主线。
```
