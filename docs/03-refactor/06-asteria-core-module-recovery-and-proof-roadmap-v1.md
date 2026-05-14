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

### 2.3 Alpha/PAS 必须先形成类似 MALF 的定义包

Alpha/PAS 恢复不走“直接迁移旧代码”路线，而是先形成类似
`H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4` 的权威定义包。

建议目标形态：

```text
H:\Asteria-Validated\Alpha_PAS_Design_Set_v1_0
```

定义包应至少包含：

| 文件 | 角色 |
|---|---|
| `AlphaPAS_00_Three_Documents_Bridge_v1_0.md` | 说明 Alpha/PAS 与 MALF v1.4、当前 Alpha 五族、历史系统和书籍来源的桥接关系 |
| `AlphaPAS_01_Core_Definitions_Theorems_v1_0.md` | 定义 PAS market context、strength/weakness、setup、trigger、candidate、failure |
| `AlphaPAS_01B_Operational_Boundary_Rules_v1_0.md` | 定义只读消费 MALF、不得重定义 MALF、不得输出订单/仓位/成交的边界 |
| `AlphaPAS_02_Trigger_Strength_Stats_Definitions_Theorems_v1_0.md` | 定义 PAS 触发、波段强弱比较、历史统计排名与样本约束 |
| `AlphaPAS_02A_Candidate_Lifecycle_Definitions_Theorems_v1_0.md` | 定义 setup 等待、触发、取消、修改、重入候选、失效、Signal 接受/拒绝 |
| `AlphaPAS_03_System_Service_Interface_v1_0.md` | 定义给 Signal / T+1 proof 消费的 Alpha/PAS service surface |
| `AlphaPAS_04_Context_Chart_View_v1_0.md` | 给出 market context 与 MALF 波段标尺的图示化读法 |
| `AlphaPAS_05_Trigger_Chart_View_v1_0.md` | 给出 TST / BOF / BPB / PB / CPB 的触发视图 |
| `AlphaPAS_06_Stats_Ranking_Chart_View_v1_0.md` | 给出历史统计排名、分位、样本量、稀疏性与解释限制 |
| `AlphaPAS_07_Definition_Theorem_Review_and_Implementation_Delta_v1_0.md` | 记录与当前 Asteria Alpha、历史 PAS、书籍语义的差异和取舍 |
| `MANIFEST.json` | 列明来源、hash、版本和适用范围 |

本定义包模仿 MALF 的治理形态，但不得复制 MALF 的业务层级：MALF 定义结构事实，
Alpha/PAS 只解释机会。

### 2.4 PAS 强弱比较必须以 MALF 已完成波段为基准

Lance Beggs / YTC 的 PAS 核心不是“看图感觉”，而是持续判断市场结构、趋势、强弱与未来路径。
在 Asteria 中，这一层必须落到 MALF v1.4 已发布的波段事实上：

| PAS 比较 | Asteria 落地口径 |
|---|---|
| 已完成同向基准 | `previous_completed_same_direction_wave` 与 `pre_previous_completed_same_direction_wave` 比较：推进距离、持续时间、速度、是否创新、是否更轻松越过边界 |
| 已完成正逆对比 | 最近已完成趋势推进波与最近已完成逆向波段比较：强势是否仍在趋势方向，逆向是否只是弱回撤，还是已经出现反向接管 |
| 当前进行中证据 | `current_wave`、candidate、transition、latest WavePosition 只能作为 `in_flight_confirmation`，用于判断预期是否被支持、削弱或失效；不得当作 completed baseline |
| setup 时点约束 | 只使用 setup bar 当时及之前 MALF 已确认或已发布的 facts，不使用未来数据，不用事后完成的波段回填当时判断 |
| S/R / boundary 交互 | 用 MALF guard boundary、transition boundary、candidate guard / confirmation facts 辅助判断测试、突破、突破失败、突破回撤 |
| 无力继续 | 用 no-new-span、stagnation-rank、candidate replacement、transition span 等事实标记无法延伸或延伸质量变差 |

因此，沙盘口径必须修正为：

```text
不是问“当前 up wave 比前一段 up wave 有没有更强”。
而是先问“上一段已完成 up wave 是否强于上上一段已完成 up wave”。
当前正在展开的 up wave / down pullback 只进入行进中确认、弱化、失效判断。
```

因此 Alpha/PAS authority map 必须把“强势方向运动、弱势方向失败”的书籍语义，
翻译成基于 MALF wave / transition / lifespan / service facts 的可审计定义。

### 2.5 Source Sufficiency Verdict

对当前列出的历史系统与书籍材料，本路线图给出阶段性裁决：

```text
sufficient for Alpha/PAS authority definition.
not sufficient for direct legacy code migration.
not sufficient for profit proof or broker readiness.
```

可用于正式版 Alpha/PAS 定义包的材料分层如下：

| 来源层 | 可进入定义包的内容 | 不得直接进入 |
|---|---|---|
| YTC / Lance Beggs | market context、S/R、强弱、未来路径、TST / BOF / BPB / PB / CPB 语义 | 书籍正文复制、主观图感、不带 lineage 的人工判断 |
| Bob Volman | 触发、入场、临界点、假突破、区间/突破细节参考 | 外汇短线参数原样照搬到 A 股日线 |
| `MarketLifespan-Quant` | PAS 五触发器、16-cell readout、trigger ledger、formal signal、result reuse、table ownership 经验 | 旧 `research_lab` 临时链、一次性 backtest 输出、旧库表直接迁移 |
| `EmotionQuant-gamma` | T+1 Open、IRS ranking、MSS risk sidecar、BOF-only 主线经验 | broker 执行闭环、MSS 进入个股横截面总分 |
| `astock_lifespan-alpha` | 早期 MALF/PAS/Signal/Position 分解经验、T+0 signal -> T+1 open 桥接经验 | 历史代码和旧 schema 原样继承 |
| `lifespan-0.01` | data producer、runner、checkpoint、trade bridge 的工程经验 | 把 Data / Trade 事实反向混入 Alpha/PAS 定义 |

因此，第四卡必须回答“这些材料如何映射为 Asteria 自己的 PAS 语义层”，而不是问
“旧系统有没有一个现成 PAS 可以搬过来”。

### 2.6 Alpha/PAS Semantic Layers

正式版 Alpha/PAS 至少拆成七层：

| 层 | 职责 |
|---|---|
| `pas_market_context` | 解释价格当前处于 MALF 结构、S/R、timeframe 与 boundary 的哪个位置 |
| `pas_trigger_event` | 记录 TST / BOF / BPB / PB / CPB 是否在 setup 时点触发 |
| `pas_strength_profile` | 使用 MALF 已完成波段生成同向基准、正逆对比、回撤质量、无力继续 |
| `pas_in_flight_state` | 记录当前 wave / candidate / transition 对预期的支持、削弱或失效，不替代 completed baseline |
| `pas_candidate_lifecycle` | 记录 setup 等待、触发、取消、修改、重入候选、失效、被 Signal 接受或拒绝 |
| `pas_historical_rank_profile` | 记录同类 setup 在历史样本中的频率、稀疏性、forward readout、failure / cancellation ranking |
| `pas_formal_candidate` | 给 Signal / T+1 proof 的可消费候选，不生成订单、仓位或成交 |

### 2.7 Alpha/PAS 入门剑裁决

基于当前已实现系统与第 3 卡 source inventory，本路线图追加如下人话裁决：

```text
当前已实现的 MALF + Alpha + Signal 只是剑胚，不是已经能下场的剑。
MALF v1.4 + 新版 Alpha/PAS + Signal 按本路线图做完后，可以形成适合 A 股生存的入门剑。
```

这里的“入门剑”不得解释为盈利机器、自动交易系统或 broker-ready 系统。它只用于：

| 能力 | 允许解释 |
|---|---|
| 避坏位置 | 用 MALF 结构位置、completed-wave baseline 与 in-flight invalidation 过滤明显坏机会 |
| 选相对更优候选 | 用 PAS context、trigger、strength profile、candidate lifecycle 与 historical rank 识别候选 |
| 可审计信号 | 把 PAS 主观交易实例翻译成 Signal 可消费、T+1 proof 可验证的候选事实 |

第 4 卡必须把 YTC 卷 3 第 5 章交易实例纳入 authority map，尤其是：

| 交易实例语义 | Alpha/PAS 落地要求 |
|---|---|
| BPB / PB / BOF / TST / CPB 不只是标签 | 必须记录 setup 是否等待、触发、失败、取消、修改或重入候选 |
| T1 / T2、保本、跟踪止损 | 只作为后续 Position / Trade 管理语义或 proof annotation，不由 Alpha/PAS 生成订单 |
| 取消后重入 | 必须有新的 valid trigger 与当前 context / strength 支持，不允许机械重入 |
| 强势冲入阻力或弱势回撤 | 必须落到 `pas_strength_profile` 与 `pas_in_flight_state`，供 Signal 放行或拒绝 |
| 区间内的区间、复杂横向环境 | 必须记录 context nestedness 与 source caveat，不把复杂图感硬编码成确定信号 |

A 股第一版生存边界固定为：

| 边界 | 裁决 |
|---|---|
| 交易方向 | long-only / avoid-risk first；空头语义只用于回避或退出，不用于做空 |
| 执行语义 | T 日信号，T+1 open proof；不得假设日内同日灵活进出 |
| 频率 | day 为主，week/month 作为背景；不进入超短线或实盘 scalping |
| 风险事实 | ST、停牌、涨跌停、流动性不足与 source gaps 先作为 hard filter 或 caveat |
| 生存定义 | 降低坏交易暴露与提升候选可审计性，不等于收益 proof |

因此，第 4 卡的核心产出不是 runtime，也不是 contract freeze，而是：

```text
MALF 做尺。
Alpha/PAS 做机会与候选生命周期。
Signal 做汇聚裁决。
Position / Trade 以后才处理 T1/T2、分批、保本、跟踪、撤单和真实执行。
```

### 2.8 Broker feasibility 暂缓

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
| Stage 2 | Alpha/PAS 历史权威恢复与定义包冻结 | 3 |
| Stage 3 | Alpha/PAS 到 Signal 与收益证明 | 3 |
| Stage 4 | 组合复验与 broker 延后裁决 | 2 |

合计：

```text
10 cards
```

## 4. Card Sequence

| 顺序 | 卡 | 状态 | 目标 |
|---:|---|---|---|
| 1 | `v1-core-module-recovery-roadmap-freeze-card` | passed / roadmap frozen | 冻结本路线图、broker 暂缓、no-live 边界 |
| 2 | `v1-malf-v1-4-immutability-anchor-card` | passed / immutability anchored | 只读锚定 MALF v1.4 不变量清单 |
| 3 | `v1-alpha-pas-source-inventory-card` | passed / source inventory completed | 盘点当前 Alpha/PAS、历史版本、书籍和系统经验 |
| 4 | `v1-alpha-pas-authority-map-card` | passed / authority map completed | 映射书籍、历史系统和第 5 章交易实例，冻结 PAS 候选生命周期与 A 股入门剑边界 |
| 5 | `v1-alpha-pas-contract-redesign-card` | passed / contract redesigned | 冻结 Alpha/PAS v1.0 定义包与新版合同，输入固定为 MALF v1.4 |
| 6 | `v1-alpha-pas-bounded-proof-build-card` | passed / bounded proof built | 小范围实现/恢复新版 Alpha/PAS bounded proof |
| 7 | `v1-signal-contract-alignment-card` | prepared next route card | 让 Signal 对齐新版 Alpha/PAS 与 T+1 execution hint |
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

目标：把书籍、历史版本和当前实现中的 PAS / Alpha 语义映射成权威对照表，
并裁决 MALF + 新版 Alpha/PAS + Signal 如何形成 A 股 long-only / T+1 的入门级生存剑。

重点来源：

| 来源 | 用途 |
|---|---|
| YTC 卷 2 第 3 章 `市场分析` | market context、S/R、多重时间框架、市场结构、趋势、强弱、未来趋势方向 |
| YTC 卷 3 第 4 章 `交易策略` | YTC 架构、反弱势、被套交易者、TST / BOF / BPB / PB / CPB setup |
| YTC 卷 3 第 5 章 `交易示例` | BPB / PB / BOF / TST / CPB 的触发、取消、修改、重入、T1/T2、保本、跟踪止损与失败样例 |
| Bob Volman price action references | 入场、临界点、假突破、区间/突破细节参考 |
| `MarketLifespan-Quant` PAS runtime / docs | 五触发器、16-cell、trigger ledger、formal signal、历史统计与 result reuse 经验 |
| `EmotionQuant-gamma` | T+1 Open、IRS ranking、MSS sidecar 与 BOF-only 主线边界 |
| `astock_lifespan-alpha` | 早期 Alpha/PAS trigger、Signal、Position 桥接和 staged docs 经验 |
| 当前 Asteria Alpha 五族 | `BOF / TST / PB / CPB / BPB` 当前实现表面 |
| MALF v1.4 | wave / transition / candidate / lifespan / WavePosition 计量事实 |

必须输出的 authority map 维度：

| 维度 | 要求 |
|---|---|
| PAS market context | 如何由 MALF WavePosition、S/R、timeframe context 定义 |
| strength / weakness | 已完成同向基准、已完成正逆对比、当前进行中确认/失效分层 |
| setup family | TST / BOF / BPB / PB / CPB 是否对应并如何补强当前 Alpha 五族 |
| trigger event | 什么叫 PAS 触发、什么叫未触发、取消、失败、等待 |
| candidate lifecycle | 如何表达 `waiting / triggered / cancelled / modified / reentry_candidate / invalidated / accepted_by_signal / rejected_by_signal` |
| historical rank profile | 同类 setup 的历史统计排名、样本量、稀疏性、forward readout 与失败排名如何表达 |
| entry candidate | 只定义候选与执行 hint，不生成订单 |
| failure / invalidation | 如何表达 setup 失败、取消、重新评估 |
| A 股生存边界 | long-only、T+1 open、日线优先、source gaps、ST / 停牌 / 涨跌停 / 流动性 caveat 如何进入 hard filter 或 retained gap |
| source lineage | 每个概念来自当前实现、历史系统、YTC 章节或 retained reference |

通过标准：

- 标出当前 Alpha/PAS 简化版缺口。
- 区分必须保留、需要补强、历史弃用、不适合当前 Asteria 的概念。
- 明确哪些语义进入 contract redesign，哪些只保留为 future enhancement。
- 明确 PAS 强弱比较必须基于 MALF 已完成波段基准，不得把当前进行中波段当作 completed baseline。
- 明确当前已实现 MALF + Alpha + Signal 是 `sword_blank / 剑胚`，不是可下场交易系统。
- 明确 MALF v1.4 + 新版 Alpha/PAS + Signal 完成后只能裁决为 `entry_level_a_share_survival_sword_candidate`，
  不得宣称收益、实盘、broker-ready 或自动交易能力。
- 明确 `pas_candidate_lifecycle` 必须消费 YTC 卷 3 第 5 章交易实例中的等待、触发、取消、修改、重入、失败与 Signal 拒绝/接受语义。
- 明确 T1 / T2、保本、跟踪止损、分批退出属于后续 Position / Trade 管理面；
  Alpha/PAS 只能输出候选生命周期、risk/reward viability hint 或 proof annotation，不生成管理动作。
- 给出 `source_sufficiency = sufficient_for_definition / insufficient_for_migration_or_profit_proof` 裁决。
- 给出 `Alpha_PAS_Design_Set_v1_0` 的文件清单、必须定义项、retained gaps。

执行结果：

| 项 | 结果 |
|---|---|
| 执行 run_id | `v1-alpha-pas-authority-map-card-20260514-01` |
| 输出 | `docs/03-refactor/08-alpha-pas-authority-map-v1.md` |
| 当前 live next | `none / terminal`（保持不变） |
| 正式 DB mutation | `no` |
| source sufficiency | `sufficient_for_definition / insufficient_for_migration_or_profit_proof` |
| 当前链路状态 | `sword_blank / 剑胚` |
| 新版链路上限 | `entry_level_a_share_survival_sword_candidate` |
| 下一张路线卡 | `v1-alpha-pas-contract-redesign-card` |

### 5.5 `v1-alpha-pas-contract-redesign-card`

目标：冻结 `Alpha_PAS_Design_Set_v1_0` 与新版 Alpha/PAS 合同。

边界：

| 项 | 裁决 |
|---|---|
| 输入 | MALF v1.4 WavePosition / service facts |
| 输出 | Alpha/PAS context、setup、strength profile、event、score、reason、candidate、T+1 open execution hint |
| 不输出 | position size、portfolio allocation、broker order |
| 下游对象 | Signal 与 T+1 回测 |
| 禁止 | 写回 MALF、直接生成实盘订单 |

定义包必须至少冻结：

| 定义 | 说明 |
|---|---|
| `pas_market_context` | 当前价格在 MALF 结构、S/R、timeframe context 中的位置 |
| `pas_strength_profile` | completed-wave baseline、in-flight confirmation、正逆波段对比、无力继续、boundary interaction |
| `pas_setup_family` | `TST / BOF / BPB / PB / CPB` 的 Asteria 定义 |
| `pas_trigger_event` | setup 触发、未触发、取消、失败、等待、重新评估 |
| `pas_candidate_lifecycle` | `waiting / triggered / cancelled / modified / reentry_candidate / invalidated / accepted_by_signal / rejected_by_signal` |
| `pas_historical_rank_profile` | setup 频率、样本量、历史分位、forward return readout、failure/cancellation rank |
| `pas_entry_candidate` | 面向 Signal / T+1 proof 的候选，不是订单 |
| `pas_management_handoff_hint` | T1/T2、保本、跟踪、分批只作为 Position / Trade handoff hint 或 proof annotation |
| `pas_failure_state` | setup 取消、失败、重新评估、需要等待 |
| `pas_source_lineage` | MALF run / WavePosition / rule version / source concept trace |

通过标准：

- `Alpha_PAS_Design_Set_v1_0` 形成 manifest 和版本锚点。
- 新合同可被 Signal 消费。
- 合同包含 source lineage、rule version、confidence / strength、reason code。
- 合同明确面向 T+1 open proof，不面向 broker。

执行结果：

| 项 | 结果 |
|---|---|
| 执行 run_id | `v1-alpha-pas-contract-redesign-card-20260514-01` |
| 定义包目录 | `H:\Asteria-Validated\Alpha_PAS_Design_Set_v1_0` |
| 定义包 zip | `H:\Asteria-Validated\Alpha_PAS_Design_Set_v1_0.zip` |
| 当前 live next | `none / terminal`（保持不变） |
| 正式 DB mutation | `no` |
| runtime proof | `no` |
| broker feasibility | `deferred` |
| 下一张路线卡 | `v1-alpha-pas-bounded-proof-build-card` |

### 5.6 `v1-alpha-pas-bounded-proof-build-card`

目标：在小范围内实现或恢复新版 Alpha/PAS 的 bounded proof。

通过标准：

- 只跑 bounded proof。
- 不写正式 DB，除非后续独立卡明确授权 guarded formal write。
- 证明新版 PAS 语义能从 MALF v1.4 输入落到可审计输出。
- 至少证明 `pas_strength_profile` 可从 setup 之前 MALF 已完成波段生成 completed baseline，不使用未来数据。
- 至少证明当前进行中波段只作为 in-flight confirmation / invalidation，不被写成 completed baseline。
- 至少证明 `pas_candidate_lifecycle` 能表达等待、触发、取消、修改、重入候选、失效、Signal 接受/拒绝。
- T1 / T2、保本、跟踪止损只能落为 handoff hint 或 proof annotation，不得由 Alpha/PAS 输出订单、仓位或成交。

执行结果：

| 项 | 结果 |
|---|---|
| 执行 run_id | `v1-alpha-pas-bounded-proof-build-card-20260514-01` |
| source DB | `H:\Asteria-data\malf_service_day.duckdb`（read-only） |
| source MALF run | `malf-v1-4-core-runtime-sync-implementation-20260505-01` |
| requested scope | `day / 2024-01-02..2024-12-31 / symbol_limit=31` |
| observed rows | `4395` |
| PAS candidates | `4395` |
| lifecycle catalog states | `8` |
| hard_fail_count | `0` |
| temp proof DB | `H:\Asteria-temp\alpha_pas\v1-alpha-pas-bounded-proof-build-card-20260514-01\alpha_pas_bounded_proof.duckdb` |
| report dir | `H:\Asteria-report\pipeline\2026-05-14\v1-alpha-pas-bounded-proof-build-card-20260514-01` |
| validated zip | `H:\Asteria-Validated\Asteria-v1-alpha-pas-bounded-proof-build-card-20260514-01.zip` |
| 当前 live next | `none / terminal`（保持不变） |
| 正式 DB mutation | `no` |
| return / broker proof | `no` |
| 下一张路线卡 | `v1-signal-contract-alignment-card` |

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
