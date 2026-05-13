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
| 3 | `v1-usage-readout-report-card` | prepared next route card | 只读跑一次应用读出，产出人读研究报告 |
| 4 | `v1-usage-value-decision-card` | planned | 对报告做使用价值裁决，并分类 usage blocker / strategy quality issue / source caveat / future enhancement |
| 5 | `daily-incremental-production-scope-card` | gated | 仅在第 4 张通过后，冻结日更生产化范围和正式写库治理 |

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

## 6. 退出标准

本使用验证阶段完成时，必须给出一句人话结论：

```text
Asteria 当前 v1 产出的结构、信号、组合和交易意图，对真实研究是否有价值。
```

若答案是“有”，进入日更生产化范围冻结。

若答案是“不够”，按 gap 分类补强；不得盲目日更化，也不得把使用验证失败改写成 release 失败。

## 7. 与当前主线的关系

当前主线仍保持：

```text
final-release-closeout-card = passed / v1 complete
current live next = none / terminal
```

本路线图是 v1 后使用验证路线，不修改 `governance/module_gate_registry.toml` 的
`current_allowed_next_card`，也不改变 `docs/04-execution/00-conclusion-index-v1.md`
当前 live 下一卡结论。
