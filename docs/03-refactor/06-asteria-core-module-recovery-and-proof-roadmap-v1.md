# Asteria Core Module Recovery And Proof Roadmap v1

日期：2026-05-14

## 1. 定位

本路线图用于 `v1-vectorbt-portfolio-analytics-proof-card-20260514-01` 之后的
post-terminal 研究路线校正。

它回答的问题不是“下一步接哪个 broker”，而是：

```text
Asteria 哪些核心模块必须继续由我们自己掌握、梳理、证明，哪些能力必须等策略证明后再外接。
```

当前 live authority 仍以以下事实为准：

| 项 | 当前状态 |
|---|---|
| final release closeout | `final-release-closeout-card` passed / v1 complete |
| 当前 live next card | none / terminal |
| 本路线图性质 | post-terminal core recovery / proof roadmap |
| 正式 DB mutation | `no`，本路线图不授权写 `H:\Asteria-data` |
| broker / live trading | deferred，不进入近期执行队列 |

本路线图不得被解释成：

```text
新的 live gate
MALF 语义重定义
Alpha/PAS 代码立即迁移
Position / Portfolio Plan / Trade / System 删除
真实 broker 接入
实盘交易放行
```

## 2. 核心裁决

### 2.1 MALF v1.4 固定为长期不变量

`H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4` 是后续研究路线的
MALF authority anchor。

后续任何 Alpha / Signal / Position / Portfolio / Trade / System 工作都只能消费 MALF v1.4：

| 规则 | 裁决 |
|---|---|
| MALF v1.4 定义 | 长期固定，不随 Alpha/PAS 重做而漂移 |
| Alpha/PAS 与 MALF 的关系 | Alpha/PAS 解释机会，不反向修改 MALF |
| 下游与 MALF 的关系 | 下游消费 Signal / Position 语义，不重定义 MALF |
| 历史版本用途 | 只回收经验、样本、失败教训，不覆盖 MALF v1.4 |

### 2.2 Alpha/PAS 是当前需要重点恢复的模块

当前 Asteria 的 Alpha/PAS 已有 released / bounded proof / production hardening evidence，
但 Phase 2 的 `backtesting.py` 与 `vectorbt` proof 已暴露：

| 事实 | 含义 |
|---|---|
| 31 只代表股中只有 1 只有 active Signal | Alpha/PAS 与 Signal 覆盖不足 |
| T+1 proof 已能跑通，但收益为负 | 外部回测 adapter 可运行，不等于策略有效 |
| vectorbt 组合 proof 可运行，但暴露时间极低 | 当前信号稀疏，组合层研究价值仍需重证 |
| 当前没有正式 fill / account loop | 不适合进入实盘 broker |

因此下一阶段重心从 broker 选择前移到 Alpha/PAS 语义恢复与收益证明。

### 2.3 Broker feasibility 暂缓

`v1-broker-adapter-feasibility-card` 不取消，但必须延后。

执行前置条件：

| 前置条件 | 当前状态 |
|---|---|
| Alpha/PAS authority map 完成 | not started |
| 新版 Alpha/PAS contract 冻结 | not started |
| 新版 Alpha/PAS bounded proof 通过 | not started |
| T+1 open return proof 有研究价值 | not proven |
| portfolio analytics reproof 改善覆盖和收益解释 | not proven |

在这些前置条件满足前，不讨论真实 broker 接入、实盘账户、自动委托或成交闭环。

## 3. Roadmap Structure

本路线图按 `4 个执行 stage + Stage 0 路线冻结 / 10 张卡` 组织。

用户口径中的 `4 个 stage / 10 张卡` 指 Stage 1-4 的实质模块恢复与证明阶段；
Stage 0 只冻结路线与 no-live 边界。

| Stage | 目标 | 卡数 |
|---|---:|---:|
| Stage 0 | 路线冻结与 no-live 边界 | 1 |
| Stage 1 | MALF v1.4 不变量锚定 | 1 |
| Stage 2 | Alpha/PAS 历史权威恢复 | 3 |
| Stage 3 | Alpha/PAS 到 Signal 与收益证明 | 3 |
| Stage 4 | 组合复验与 broker 延后裁决 | 2 |

合计：

```text
10 cards
```

## 4. Card Sequence

| 顺序 | 卡 | 状态 | 目标 |
|---:|---|---|---|
| 1 | `v1-core-module-recovery-roadmap-freeze-card` | prepared next route card | 冻结本路线图、broker 暂缓、no-live 边界 |
| 2 | `v1-malf-v1-4-immutability-anchor-card` | planned | 只读锚定 MALF v1.4 不变量清单 |
| 3 | `v1-alpha-pas-source-inventory-card` | planned | 盘点当前 Alpha/PAS、历史版本、书籍和系统经验 |
| 4 | `v1-alpha-pas-authority-map-card` | planned | 映射 Lance Beggs / Bob Volman / 简简单单做股票 / 历史系统中的 PAS 语义 |
| 5 | `v1-alpha-pas-contract-redesign-card` | planned | 冻结新版 Alpha/PAS 合同，输入固定为 MALF v1.4 |
| 6 | `v1-alpha-pas-bounded-proof-build-card` | planned | 小范围实现/恢复新版 Alpha/PAS bounded proof |
| 7 | `v1-signal-contract-alignment-card` | planned | 让 Signal 对齐新版 Alpha/PAS 与 T+1 execution hint |
| 8 | `v1-alpha-pas-t-plus-one-return-proof-card` | planned | T 日信号、T+1 开盘执行，输出收益/回撤/交易数/跳过原因 |
| 9 | `v1-portfolio-analytics-reproof-card` | planned | 用新版 Alpha/PAS 信号重跑组合层 proof |
| 10 | `v1-broker-adapter-feasibility-card` | deferred | 仅在第 8、9 卡证明策略有研究收益价值后，只读评估 broker adapter |

每张卡执行前必须独立创建或更新自己的：

```text
card
record
evidence-index
conclusion
```

没有执行四件套和外部 evidence，就不得把 planned 卡声明为 passed。

## 5. 单卡定义

### 5.1 `v1-core-module-recovery-roadmap-freeze-card`

目标：冻结本路线图，正式把重心从 broker feasibility 前移到核心模块恢复与证明。

通过标准：

- 明确当前没有正式收益证明、真实成交闭环或实盘交易能力。
- 明确 `v1-broker-adapter-feasibility-card` 标记为 deferred。
- 明确 `current live next = none / terminal` 不变。
- 明确 `H:\Asteria-data` 不写入。

### 5.2 `v1-malf-v1-4-immutability-anchor-card`

目标：只读核对 `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4`，
输出后续所有 Alpha/PAS 工作必须遵守的 MALF 不变量清单。

通过标准：

- MALF v1.4 authority anchor 已列明。
- 明确后续 Alpha/PAS 只能消费 MALF，不得重定义 MALF。
- 明确历史版本不得覆盖 MALF v1.4。

### 5.3 `v1-alpha-pas-source-inventory-card`

目标：只读盘点 Alpha/PAS 的来源材料。

默认 source scope：

| 来源 | 用途 |
|---|---|
| 当前 Asteria Alpha docs / code / DB evidence | 当前实现事实 |
| `G:\malf-history\astock_lifespan-alpha` | T+0 signal -> T+1 open、filled / rejected runner 经验 |
| `G:\malf-history\EmotionQuant-alpha` | 早期 PAS / governance / 6A 经验 |
| `G:\malf-history\EmotionQuant-beta` | 外部回测选型与 Alpha/PAS 演进经验 |
| `G:\malf-history\EmotionQuant-gamma` | T+1 Open、Broker/Backtest 共用内核、A 股规则 |
| `G:\malf-history\lifespan-0.01` | data producer、market_base、dirty queue、checkpoint |
| `G:\malf-history\Lifespan-Validated` | MALF / System 历史证据资产 |
| `G:\malf-history\MarketLifespan-Quant` | PAS / risk unit / trailing stop / system readout |
| `H:\Asteria-Validated\MALF-system-history` | 历史系统经验锚点 |
| `G:\《股市浮沉二十载》\2020.(Au)LanceBeggs` | PAS 定义核心来源 |
| `G:\《股市浮沉二十载》\2021.Bob_Volman外汇超短线交易` | 价格行为与入场细节参考 |
| `G:\《股市浮沉二十载》\2018.(CHINA)简简单单做股票` | A 股实操经验参考 |

通过标准：

- 输出 source inventory。
- 不迁移历史代码。
- 不复制书籍内容到 repo，只记录可审计引用和概念索引。

### 5.4 `v1-alpha-pas-authority-map-card`

目标：把书籍、历史版本和当前实现中的 PAS / Alpha 语义映射成权威对照表。

通过标准：

- 标出当前 Alpha/PAS 简化版缺口。
- 区分必须保留、需要补强、历史弃用、不适合当前 Asteria 的概念。
- 明确哪些语义进入 contract redesign，哪些只保留为 future enhancement。

### 5.5 `v1-alpha-pas-contract-redesign-card`

目标：冻结新版 Alpha/PAS 合同。

边界：

| 项 | 裁决 |
|---|---|
| 输入 | MALF v1.4 WavePosition / service facts |
| 输出 | Alpha/PAS event、score、reason、candidate |
| 不输出 | position size、portfolio allocation、broker order |
| 下游对象 | Signal 与 T+1 回测 |
| 禁止 | 写回 MALF、直接生成实盘订单 |

通过标准：

- 新合同可被 Signal 消费。
- 合同包含 source lineage、rule version、confidence / strength、reason code。
- 合同明确面向 T+1 open proof，不面向 broker。

### 5.6 `v1-alpha-pas-bounded-proof-build-card`

目标：在小范围内实现或恢复新版 Alpha/PAS 的 bounded proof。

通过标准：

- 只跑 bounded proof。
- 不写正式 DB，除非后续独立卡明确授权 guarded formal write。
- 证明新版 PAS 语义能从 MALF v1.4 输入落到可审计输出。

### 5.7 `v1-signal-contract-alignment-card`

目标：让 Signal 对齐新版 Alpha/PAS。

通过标准：

- Signal 保留 `symbol`、`signal_date`、`source_run_id`、`lineage`。
- Signal 保留 `T+1 open execution hint`。
- 不要求收益，不进入 broker。

### 5.8 `v1-alpha-pas-t-plus-one-return-proof-card`

目标：证明新版 Alpha/PAS 生成的 Signal 在 T+1 open 语义下是否有研究收益价值。

固定语义：

| 项 | 语义 |
|---|---|
| signal timing | `T+0 signal` |
| execution timing | `T+1 open` |
| price field | `open` |
| scope | 31 只申万一级行业代表股，`2024-01-02..2024-12-31` |
| output | PnL、drawdown、trade count、skip/rejection reason |

通过标准：

- 输出收益、回撤、交易数、跳过/拒绝原因。
- 明确是否比当前 Phase 2 proof 有改善。
- 仍不得宣称实盘能力。

### 5.9 `v1-portfolio-analytics-reproof-card`

目标：用新版 Alpha/PAS 信号重跑组合层 proof。

通过标准：

- 对比 `v1-vectorbt-portfolio-analytics-proof-card-20260514-01` 的负收益与低覆盖问题。
- 输出组合收益、最大回撤、暴露、换手、持仓分布。
- 判断新版 Alpha/PAS 是否具备继续投入价值。

### 5.10 `v1-broker-adapter-feasibility-card`

目标：仅在第 8、9 卡证明策略有研究收益价值后，才只读评估 broker adapter。

候选：

| 候选 | 角色 |
|---|---|
| `easytrader` | A 股真实 broker adapter 候选 |
| `vn.py` | 更完整的交易平台 / gateway 候选 |
| 自研 broker kernel | 只保留统一订单、回测成交和实盘 adapter 边界 |

通过标准：

- 只做 feasibility，不接真实账户。
- 不发送真实委托。
- 不打开自动交易。
- 若第 8、9 卡未证明收益价值，本卡继续保持 deferred。

## 6. 与 Phase 2 的关系

`docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md` 的 Phase 2 已证明：

| 已证明 | 未证明 |
|---|---|
| Signal export contract 可冻结 | Alpha/PAS 足够有效 |
| `backtesting.py` adapter 可运行 | 策略收益有效 |
| `vectorbt` portfolio analytics adapter 可运行 | 真实成交闭环 |
| T+0 signal -> T+1 open 语义可执行 | 账户更新与实盘交易能力 |

因此本路线图不是推翻 Phase 2，而是消费 Phase 2 暴露的问题：

```text
外部 adapter 已能工作，但当前 Alpha/PAS 信号覆盖和收益读数不足。
```

下一步必须先修核心机会解释层，而不是把不成熟信号接到 broker。

## 7. 退出标准

本路线图完成时，必须能回答四个问题：

| 问题 | 预期回答形式 |
|---|---|
| MALF v1.4 是否继续固定 | 是，作为长期不变量 |
| Alpha/PAS 是否恢复到足够可信的语义层 | passed / blocked with gap |
| T+1 open return proof 是否有研究价值 | passed / blocked with evidence |
| broker feasibility 是否可以重新进入队列 | allowed / deferred |

人话结论必须保持：

```text
策略收益未证明前，不适合接入实盘。
```

## 8. 当前主线边界

当前主线仍保持：

```text
final-release-closeout-card = passed / v1 complete
current live next = none / terminal
```

本路线图只新增 post-terminal core recovery / proof route，不修改
`governance/module_gate_registry.toml` 的 `current_allowed_next_card`，也不改变
`docs/04-execution/00-conclusion-index-v1.md` 当前 live 下一卡结论。
