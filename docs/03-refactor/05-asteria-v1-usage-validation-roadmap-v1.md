# Asteria v1 使用验证 Roadmap v1

日期：2026-05-12

## 1. 定位

本路线图用于 `final-release-closeout-card` 通过后的 v1 使用验证。

它回答的问题不是“主线是否还有下一张 live card”，而是：

```text
Asteria 当前 v1 产出的结构、信号、组合和交易意图，对真实研究有没有使用价值。
```

当前主线 release 状态仍以以下事实为准：

| 项 | 当前状态 |
|---|---|
| final release closeout | `final-release-closeout-card` passed / v1 complete |
| 当前 live next card | none / terminal |
| 正式 DB manifest | `H:\Asteria-data` 25 个 DuckDB 已由 final release evidence 核对一致 |
| 本路线图性质 | v1 后使用验证路线；不改变 live gate |

本路线图不得被解释成：

```text
新的主线 live next card
Pipeline semantic repair
业务模块语义重定义
额外 System full build
实盘自动交易系统放行
```

## 2. 初衷复述

Asteria 的初衷不是把 roadmap 勾满，而是建立一个可解释、可审计、可复现、可增量维护的
系统化交易研究基础设施。

各层职责保持如下：

| 层 | 职责 |
|---|---|
| Data | 提供 source-fact 地基、行情、metadata 与可审计客观事实 |
| MALF | 解释市场结构、波段生命和 WavePosition |
| Alpha / Signal | 解释机会并形成正式信号 |
| Position / Portfolio Plan | 把信号转成持仓候选、组合准入和目标暴露 |
| Trade | 输出 order intent、execution plan、rejection，并保留 fill source caveat |
| System Readout / Pipeline | 只读全链路结论、审计、manifest 和运行读出 |

本路线图的目标是把 `v1 complete` 从“release 证据已闭环”推进到“真实研究使用价值已被验证”。

## 3. 使用验证边界

本路线图第一阶段只做只读使用验证。

允许：

- 读取 `H:\Asteria-data` 当前 25 个正式 DuckDB。
- 核对 schema、run ledger、row counts、source lineage、known limits。
- 产出 `H:\Asteria-report` 下的人读研究报告和 gap 分类。
- 将使用价值裁决登记到后续执行四件套。

禁止：

- 在使用验证卡中重建、补写或 promote `H:\Asteria-data`。
- 为了让报告好看而修历史 blocked 结论。
- 把 `fill_ledger` retained gap 伪装成真实成交闭环。
- 打开 week/month 下游全链路。
- 将使用验证结论替代策略收益证明或实盘生产放行。

如果只读验证发现正式库或链路缺口，只登记 gap；补库、补源、补 runner 必须另开
maintenance / hardening card。

## 4. 任务卡队列

| 顺序 | 卡 | 状态 | 独立目标 |
|---:|---|---|---|
| 1 | `v1-usage-validation-scope-card` | passed / scope frozen / 31-industry sample locked | 冻结股票池、日期范围、研究问题、报告格式与只读边界 |
| 2 | `v1-application-db-readiness-audit-card` | passed / application DB readiness audited | 只读核对 25 个正式 DB，确认 Data / MALF / Alpha / Signal 可作为应用输入 |
| 3 | `v1-usage-readout-report-card` | passed / usage readout report generated | 只读跑一次应用读出，产出人读研究报告 |
| 4 | `v1-usage-value-decision-card` | passed / research usable with caveats | 对报告做使用价值裁决，并分类 usage blocker / strategy quality issue / source caveat / future enhancement |
| 5 | `daily-incremental-production-scope-card` | prepared next route card | 在第 4 张通过后，冻结日更生产化范围和正式写库治理 |

第 5 张仍是 prepared route card，但在进入日更生产化范围冻结前，新增 Phase 2
战略边界裁决：先确认 Asteria 后续不再默认自研完整量化平台，而是收缩为
`Data source fact + MALF + Alpha + Signal` 自研核心，并把回测、组合绩效、成交模拟、
broker adapter、实盘接口和绩效报告优先交给成熟外部框架或 adapter。

第 4 张卡执行前允许加入只读 supplemental input，但该输入不得成为新的 live gate，也不得改变
`v1-usage-value-decision-card` 作为下一张路线卡的地位。

| supplemental run_id | 状态 | 用途 |
|---|---|---|
| `v1-downstream-reference-audit-20260513-01` | passed / downstream semantics benchmark input generated | 对照 Hikyuu / FinHack / easytrader 的 Position -> Portfolio Plan -> Trade -> System 同类边界，作为第 4 卡裁决输入 |

这些卡均不是当前 live next card。每张卡执行前必须独立创建或更新自己的：

```text
card
record
evidence-index
conclusion
```

没有执行四件套和外部 evidence，就不得把 planned 卡声明为 passed。

## 5. 单卡定义

### 5.1 `v1-usage-validation-scope-card`

目标：冻结本轮真实使用验证的题目。

建议默认范围：

| 项 | 默认值 |
|---|---|
| 股票池 | 20-50 只代表性股票，或一个行业板块 |
| 日期范围 | `2024-01-02..2024-12-31` |
| 研究问题 | Asteria 当前链路能否给出可解释、可审计的结构-信号-持仓-交易意图读出 |
| 报告形态 | 人读报告 + machine-readable manifest |
| 正式 DB 权限 | read-only |

通过标准：

- 股票池、日期范围、研究问题、输出报告结构已冻结。
- 明确不写 `H:\Asteria-data`。
- 下一张只允许进入 `v1-application-db-readiness-audit-card`，不允许跳到日更生产化。

2026-05-12 freeze result：

| 项 | 冻结结果 |
|---|---|
| 执行 run_id | `v1-usage-validation-scope-card-20260512-01` |
| 股票池 | `31` 个申万一级行业各取 `1` 只代表股 |
| 选股规则 | `2024 年覆盖完整度优先；execution-line 平均 amount 次优先；可带理由人工 override` |
| 日期范围 | `2024-01-02..2024-12-31` |
| 研究问题 | `Asteria 当前链路能否给出可解释、可审计的结构-信号-持仓-交易意图读出` |
| 报告形态 | `双层输出：总报告 + 少量逐股 appendix` |
| 正式 DB 权限 | `read_only` |
| 当前 live next | `none / terminal`（保持不变） |
| 下一张路线卡 | `v1-application-db-readiness-audit-card` |

### 5.2 `v1-application-db-readiness-audit-card`

目标：确认现有正式库是否足以支撑应用验收。

检查范围：

| 层 | DB 数量 | 核心检查 |
|---|---:|---|
| Data | 5 | source manifest、market base、market meta、reference caveat |
| MALF | 9 | Core/Lifespan/Service run、WavePosition、schema/rule version |
| Alpha / Signal | 6 | Alpha 五族、Signal ledger、source run lineage |
| Downstream / Pipeline | 5 | Position/Portfolio/Trade/System/Pipeline readout surface 可读性 |

通过标准：

- 当前 25 个 DuckDB 可被只读打开。
- 上游 20 个 Data/MALF/Alpha/Signal DB 可作为应用输入。
- 缺口只分类登记，不在本卡补库。

2026-05-13 audit result：

| 项 | 审计结果 |
|---|---|
| 执行 run_id | `v1-application-db-readiness-audit-card-20260513-01` |
| 当前 live next | `none / terminal`（保持不变） |
| 正式 DB 只读打开 | `25 / 25` |
| 应用输入 DB ready | `20 / 20` |
| Downstream / Pipeline 可读 | `5 / 5` |
| issue_count | `0` |
| 正式 DB mutation | `no` |
| retained caveat | `fill_ledger source-bound gap`; `ST / 停牌 / 上市退市 / 历史行业沿革 source caveats` |
| 下一张路线卡 | `v1-usage-readout-report-card` |

### 5.3 `v1-usage-readout-report-card`

目标：用正式库产出第一份真实使用验收报告。

报告必须至少回答：

| 问题 | 输出 |
|---|---|
| 市场结构是什么 | MALF 结构、波段生命、WavePosition 摘要 |
| 机会在哪里 | Alpha / Signal 输出摘要 |
| 持仓和组合如何解释 | Position / Portfolio Plan 读出 |
| 交易意图是什么 | Trade order intent / execution plan / rejection 摘要 |
| 全链路是否自洽 | System Readout / Pipeline manifest 结论 |
| 哪些 caveat 保留 | fill source、reference facts、calendar semantic gap 等 |

通过标准：

- 报告落在 `H:\Asteria-report`。
- 临时产物落在 `H:\Asteria-temp`。
- 不修改正式 DB。
- 结论能被人读懂，并能追溯到正式 DB / run_id / source lineage。

2026-05-13 readout result：

| 项 | 读出结果 |
|---|---|
| 执行 run_id | `v1-usage-readout-report-card-20260513-01` |
| 当前 live next | `none / terminal`（保持不变） |
| 股票池 | `31` 个申万一级行业代表股 |
| 日期范围 | `2024-01-02..2024-12-31` |
| issue_count | `0` |
| 正式 DB mutation | `no` |
| 人读报告 | `H:\Asteria-report\pipeline\2026-05-13\v1-usage-readout-report-card-20260513-01\usage-readout-report.md` |
| machine-readable manifest | `H:\Asteria-report\pipeline\2026-05-13\v1-usage-readout-report-card-20260513-01\usage-readout-manifest.json` |
| retained caveat | `fill_ledger source-bound gap`; `ST / 停牌 / 上市退市 / 历史行业沿革 source caveats`; `calendar semantic gap` |
| 下一张路线卡 | `v1-usage-value-decision-card` |

第 4 卡前置 supplemental input：

| 项 | 结果 |
|---|---|
| 执行 run_id | `v1-downstream-reference-audit-20260513-01` |
| 性质 | `roadmap_only_read_only_post_terminal_supplement` |
| 当前 live next | `none / terminal`（保持不变） |
| 外部参考 | Hikyuu / FinHack / easytrader |
| 对照结论 | 已覆盖 `4`；表达风险 `2`；真实缺口 `1`；不适用外部参考 `1` |
| 第 4 卡输入 | `order_intent_ledger = 1`; `order_rejection_ledger = 1158`; `fill_ledger row_count = 0` |
| 正式 DB mutation | `no` |

### 5.4 `v1-usage-value-decision-card`

目标：裁决当前 v1 是否具备真实研究使用价值。

裁决分类：

| 分类 | 含义 | 后续动作 |
|---|---|---|
| usage blocker | 阻止真实使用的问题 | 先开修复 / maintenance card |
| strategy quality issue | 策略质量、解释力或收益风险问题 | 进入策略评估路线 |
| source caveat | 数据源、reference fact、fill source 缺口 | 进入数据源补强路线 |
| future enhancement | 不阻塞当前研究使用的增强项 | 进入 backlog |

通过标准：

- 明确回答：当前 v1 对真实研究是否有使用价值。
- 只有通过后，才允许进入日更生产化范围冻结。
- 若未通过，不得直接打开 production daily incremental activation。

2026-05-13 decision result：

| 项 | 裁决结果 |
|---|---|
| 执行 run_id | `v1-usage-value-decision-card-20260513-01` |
| 当前 live next | `none / terminal`（保持不变） |
| value_decision | `research_usable_with_caveats` |
| 人话结论 | `Asteria 当前 v1 有研究使用价值，但带有明确 caveat` |
| usage_blocker | `0` |
| strategy_quality_issue | `2` |
| source_caveat | `3` |
| future_enhancement | `4` |
| 正式 DB mutation | `no` |
| 下一张路线卡 | `daily-incremental-production-scope-card` |

### 5.5 `daily-incremental-production-scope-card`

目标：在使用价值通过后，冻结日更生产化的治理范围。

本卡只冻结范围，不直接激活生产日更。

必须裁决：

| 项 | 需要冻结 |
|---|---|
| timeframe | 默认 `day`，不得偷开 week/month 下游全链路 |
| formal write permission | 是否允许写 `H:\Asteria-data`，以及显式 allow flag |
| source manifest | 每日源批次与 dirty scope 生成方式 |
| checkpoint/resume | 中断恢复、幂等重跑和 run ledger |
| audit/promote | hard audit、backup、staging、promote、rollback |
| reporting | 每日报告、manifest、known limits |

通过标准：

- 生产日更范围已冻结。
- 正式写库路径和失败回滚已定义。
- 下一张才能考虑 `daily-incremental-production-activation-card`。

## 6. Phase 2：Core Retention And Outsourcing Boundary

第 4 卡已经证明当前 v1 有研究使用价值，但也明确保留 caveat：不能宣称收益回测、
真实成交闭环或实盘交易能力。因此下一阶段不直接把 Asteria 推向“全平台自研”，
而是先冻结核心保留与外包边界。

Phase 2 不改变 live gate；当前 live next 仍保持 `none / terminal`。

### 6.1 任务卡队列

| 顺序 | 卡 | 状态 | 独立目标 |
|---:|---|---|---|
| 1 | `v1-core-retention-and-outsourcing-boundary-card` | passed / core retention and outsourcing boundary frozen | 冻结哪些自研、哪些外包、哪些历史资产回收、哪些 GitHub 项目只参考 |
| 2 | `v1-signal-export-contract-card` | passed / signal export contract frozen | 冻结 Asteria 对外输出给回测框架的最小信号合同 |
| 3 | `v1-t-plus-one-open-backtesting-py-proof-card` | prepared next route card | 用 `backtesting.py` 跑 T 日 signal -> T+1 open 的极小收益 proof |
| 4 | `v1-vectorbt-portfolio-analytics-proof-card` | planned / after backtesting.py proof | 用 `vectorbt` 做矩阵化组合级绩效、暴露、换手和回撤分析 |
| 5 | `v1-broker-adapter-feasibility-card` | planned / after backtest semantics stable | 只读评估 easytrader / vn.py / 自研 broker kernel 的 adapter 可行性 |

### 6.2 `v1-core-retention-and-outsourcing-boundary-card`

目标：把 Asteria 后续工程方向从“继续自研完整量化平台”切换为“核心研究引擎自研，
外围能力外包或 adapter 化”。

冻结裁决：

| 分类 | 模块 / 能力 | 裁决 |
|---|---|---|
| retain_self_built | Data source fact / MALF / Alpha / Signal | 继续作为 Asteria 自研核心 |
| freeze_self_build_expansion | Position / Portfolio Plan / Trade / System Readout | 保留现有 v1 readout 证据，但停止按完整平台化方向扩张 |
| outsource_or_adapter | Backtest / Portfolio Analytics / Fill Simulation / Broker / Report | 优先由成熟外部框架承接 |

通过标准：

- 明确写出 `MALF + Alpha` 是研究灵魂，`Data + Signal` 是外部消费契约层。
- 明确写出当前 Asteria 没有正式收益回测、真实成交闭环或实盘交易能力。
- 明确写出 `T+0 signal -> T+1 open execution` 是下一阶段回测 adapter 的硬语义。
- 明确写出历史版本只回收语义和经验，不直接复制运行时代码。
- 明确写出外部项目差异不自动升级为 blocker。

2026-05-13 boundary result：

| 项 | 裁决结果 |
|---|---|
| 执行 run_id | `v1-core-retention-and-outsourcing-boundary-card-20260513-01` |
| 当前 live next | `none / terminal`（保持不变） |
| route type | `roadmap-only / read-only / post-terminal / strategic boundary` |
| core retention | `Data source fact + MALF + Alpha + Signal` |
| self-build expansion freeze | `Position / Portfolio Plan / Trade / System Readout` |
| first external proof target | `backtesting.py` for T+1 open PnL proof |
| second external proof target | `vectorbt` for matrix portfolio analytics |
| future broker adapter | `easytrader` / `vn.py` feasibility only after backtest semantics stabilize |
| 正式 DB mutation | `no` |
| 下一张路线卡 | `v1-signal-export-contract-card` |

### 6.3 `v1-signal-export-contract-card`

目标：冻结 Asteria Core 向外部回测框架输出的最小信号合同，让后续 `backtesting.py`
proof 可以只消费 `Data + MALF + Alpha + Signal` 的研究结果，而不是继续扩张
Position / Portfolio Plan / Trade / System 平台。

本卡只冻结 contract，不导出正式文件，不运行收益回测，不写 `H:\Asteria-data`，不安装外部依赖。

最小外部信号合同：

| 字段 | 来源 / 规则 | 语义 |
|---|---|---|
| `symbol` | `signal.duckdb::formal_signal_ledger.symbol` | Asteria 正式标的代码 |
| `timeframe` | `formal_signal_ledger.timeframe` | 第一版外部 proof 只消费 `day` |
| `signal_date` | `formal_signal_ledger.signal_dt` | T 日信号日期，对外统一命名为 `signal_date` |
| `signal_type` | `formal_signal_ledger.signal_type` | Asteria 已冻结的信号类型 |
| `signal_strength` | `formal_signal_ledger.signal_strength` | 信号强度，不直接等价于仓位或订单量 |
| `signal_family` | derived from `signal_type` unless a later mapping card freezes a richer table | 给外部框架分组用的轻量 family 标签，不新增 Alpha 语义 |
| `source_run_id` | `formal_signal_ledger.run_id` | 产生该信号的正式 Signal run |
| `schema_version` | `formal_signal_ledger.schema_version` | Signal schema version |
| `signal_rule_version` | `formal_signal_ledger.signal_rule_version` | Signal rule version |
| `source_alpha_release_version` | `formal_signal_ledger.source_alpha_release_version` | 上游 Alpha release lineage |
| `lineage` | machine-readable object from Signal ledger fields and optional `signal_component_ledger` rows | 至少包含 `signal_id`、`source_run_id`、`signal_rule_version`、`source_alpha_release_version`；若可用，附带 `alpha_candidate_ids` |
| `execution_hint` | fixed literal `T_PLUS_1_OPEN` | 明确提示后续 proof 使用 T+1 开盘执行 |
| `execution_signal_date` | same as `signal_date` | 记录信号发生日，不得改写为成交日 |
| `execution_trade_date_policy` | fixed literal `next_trading_day_after_signal_date` | 下一交易日执行策略，由后续 backtest card 解析交易日历 |
| `execution_price_field` | fixed literal `open` | 后续 proof 使用 T+1 open 作为模拟成交价 |

边界：

- 该 contract 是 `Signal -> external backtest adapter` 的消费合同，不是订单合同。
- `signal_strength` 不等于 position size，也不等于 broker order quantity。
- `execution_hint = T_PLUS_1_OPEN` 是下一阶段硬语义，但本卡不证明成交、不计算收益、不更新账户。
- 当前 Asteria 仍不能宣称正式收益回测、真实成交闭环或实盘交易能力。
- `lineage` 用于把外部 proof 追溯回正式 Signal / Alpha 证据，不允许回写 MALF、Alpha、Signal 或正式 DB。

2026-05-13 contract result：

| 项 | 裁决结果 |
|---|---|
| 执行 run_id | `v1-signal-export-contract-card-20260513-01` |
| 当前 live next | `none / terminal`（保持不变） |
| route type | `roadmap-only / read-only / post-terminal / contract freeze` |
| formal source | `H:\Asteria-data\signal.duckdb::formal_signal_ledger` |
| optional lineage source | `signal_component_ledger` |
| required execution hint | `T_PLUS_1_OPEN` |
| required trade date policy | `next_trading_day_after_signal_date` |
| required price field | `open` |
| 正式 DB mutation | `no` |
| 下一张路线卡 | `v1-t-plus-one-open-backtesting-py-proof-card` |

### 6.4 历史版本回收边界

| 历史版本 | 回收内容 | 边界 |
|---|---|---|
| `G:\malf-history\lifespan-0.01` | Data producer、TDX ingest、market_base、dirty queue、checkpoint | 回收 Data 生产者经验，不直接迁入主线 |
| `G:\malf-history\astock_lifespan-alpha` | T+0 signal -> T+1 open execution、`filled / rejected` trade runner | 回收交易时序和状态语义，不直接覆盖当前 Trade |
| `G:\malf-history\EmotionQuant-gamma` | T+1 Open、Broker/Backtest 共用交易内核、A 股规则 | 回收 broker kernel 分层经验 |
| `G:\malf-history\MarketLifespan-Quant` | risk unit、trailing stop、system backtest/readout | 回收风控与系统读出经验 |
| `G:\malf-history\Lifespan-Validated` | MALF / System 证据资产 | 只作为权威锚点，不作为运行时代码 |

### 6.5 外部项目分工

| 外部项目 | 分工 | 裁决 |
|---|---|---|
| `backtesting.py` | 第一版 T+1 open PnL proof | 先接，目标是可读、可审计、少魔法 |
| `vectorbt` | 矩阵化组合回测、参数扫描、绩效分析 | 第二步接，用于组合层研究 |
| `qlib` | Alpha / Signal benchmark、因子/模型工作流参考 | 不替代 MALF |
| `Hikyuu` | SYS / MM / PF / Slippage 架构参考 | 不直接嵌入主线 |
| `FinHack` | A 股 T+1、涨跌停、投研到实盘流程参考 | 近期不作为工程依赖 |
| `easytrader` | 未来 broker adapter 候选 | 回测语义稳定前不接真实 broker |
| `backtrader` | 事件驱动模型参考 | 不作为第一主线 |

## 7. 退出标准

本使用验证阶段完成时，必须给出一句人话结论：

```text
Asteria 当前 v1 产出的结构、信号、组合和交易意图，对真实研究是否有价值。
```

若答案是“有”，进入日更生产化范围冻结。

若答案是“不够”，按 gap 分类补强；不得盲目日更化，也不得把使用验证失败改写成 release 失败。

Phase 2 完成时，必须给出另一句人话结论：

```text
Asteria 后续是否继续自研完整量化平台，还是保留核心研究引擎并把外围能力外包。
```

当前答案是：保留核心研究引擎，外围优先外包或 adapter 化。

## 8. 与当前主线的关系

当前主线仍保持：

```text
final-release-closeout-card = passed / v1 complete
current live next = none / terminal
```

本路线图是 v1 后使用验证路线，不修改 `governance/module_gate_registry.toml` 的
`current_allowed_next_card`，也不改变 `docs/04-execution/00-conclusion-index-v1.md`
当前 live 下一卡结论。
