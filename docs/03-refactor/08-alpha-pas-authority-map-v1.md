# Alpha/PAS Authority Map v1

日期：2026-05-14

状态：frozen / authority map completed

执行卡：`v1-alpha-pas-authority-map-card-20260514-01`

## 1. 定位

本文件是 `docs/03-refactor/06-asteria-core-module-recovery-and-proof-roadmap-v1.md`
第四卡的只读 authority map 输出。

它回答：

```text
当前 Alpha、历史 PAS、书籍经验与 MALF v1.4 如何映射成 Asteria 自己的 Alpha/PAS 语义权威。
```

它不回答：

```text
新版 Alpha/PAS schema 怎么冻结。
历史代码怎么迁移。
新版策略是否有收益。
是否可以接 broker 或实盘。
```

## 2. 本卡边界

| 项 | 裁决 |
|---|---|
| card type | `post-terminal / roadmap-only / read-only / authority-map` |
| live next | `none / terminal` |
| formal DB mutation | `no` |
| historical code migration | `no` |
| book content copied into repo | `no` |
| Alpha/PAS contract frozen | `no`，进入第 5 卡 |
| broker feasibility | `deferred` |
| next route card | `v1-alpha-pas-contract-redesign-card` |

## 3. Source Classification

| source class | source anchor | authority use | decision |
|---|---|---|---|
| MALF v1.4 | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4` | 结构事实、WavePosition、transition、candidate、lifespan 与 boundary | `must_keep` |
| current Asteria Alpha | `docs/02-modules/alpha`; `src/asteria/alpha`; `H:\Asteria-data\alpha_*.duckdb` | 当前五族 Alpha released surface 与 source audit 事实 | `must_keep_and_strengthen` |
| MarketLifespan-Quant PAS | `G:\malf-history\MarketLifespan-Quant` | 五触发器、trigger ledger、formal signal、16-cell readout 与历史统计经验 | `contract_redesign_input` |
| EmotionQuant-gamma | `G:\malf-history\EmotionQuant-gamma` | T+1 Open、IRS ranking、MSS sidecar、BOF-only 主线经验 | `contract_redesign_input` |
| astock_lifespan-alpha | `G:\malf-history\astock_lifespan-alpha` | 早期 Alpha/PAS trigger、Signal、Position 桥接经验 | `reference_input` |
| YTC chapter anchors | 卷 2 第 3 章；卷 3 第 4 / 5 章 | market context、strength/weakness、setup family、示例生命周期 | `concept_index_only` |
| Bob Volman references | price action / false breakout / entry detail references | 入场临界点、假突破、区间与突破细节 | `reference_input` |
| A 股实操参考 | `简简单单做股票` 与历史 A 股系统经验 | long-only、T+1、日线优先、source caveat | `boundary_input` |

## 4. Disposition Buckets

| bucket | 含义 |
|---|---|
| `must_keep` | 必须继承为新版 Alpha/PAS authority 的不变量 |
| `needs_strengthening` | 当前已有表面，但不足以表达正式 PAS 语义 |
| `contract_redesign_input` | 进入第 5 卡定义包与合同重设 |
| `future_enhancement` | 不阻塞第 5 卡，但后续可扩展 |
| `retained_gap` | 当前没有 approved source 或正式证据，不得伪装为已解决 |
| `rejected_or_not_applicable` | 不适合当前 Asteria v1 或越过模块边界 |

## 5. Authority Map

| 维度 | authority mapping | disposition |
|---|---|---|
| PAS market context | 由 MALF v1.4 WavePosition、guard boundary、transition boundary、timeframe 与 S/R interaction 定义；Alpha/PAS 只解释机会位置，不重写结构事实 | `contract_redesign_input` |
| strength / weakness | 先比较 MALF 已完成波段：同向完成波段、正逆完成波段、距离、持续时间、速度、创新能力与边界穿越质量 | `contract_redesign_input` |
| in-flight confirmation | `current_wave`、candidate、transition、latest WavePosition 只能支持、削弱或失效预期，不得写成 completed baseline | `must_keep` |
| setup family | TST / BOF / BPB / PB / CPB 继续作为 Alpha/PAS 五族入口，但当前 `waveposition_only` 表面必须补强 context、trigger、lifecycle 与 rank | `needs_strengthening` |
| trigger event | 触发必须区分 `waiting`、`triggered`、`not_triggered`、`cancelled`、`failed` 与 `invalidated`，不得把 family hit 简化为可交易信号 | `contract_redesign_input` |
| candidate lifecycle | 生命周期必须表达 `waiting / triggered / cancelled / modified / reentry_candidate / invalidated / accepted_by_signal / rejected_by_signal` | `contract_redesign_input` |
| historical rank profile | 同类 setup 的频率、样本量、分位、forward readout、失败/取消 ranking 与稀疏性必须显式输出 | `contract_redesign_input` |
| entry candidate | Alpha/PAS 只能输出候选、reason、confidence / strength、T+1 open hint 与 proof annotation，不生成订单、仓位或成交 | `must_keep` |
| failure / invalidation | setup 取消、失败、重新评估、等待必须成为一等语义，供 Signal 接受/拒绝裁决消费 | `contract_redesign_input` |
| A 股生存边界 | long-only、T+1 open、日线优先进入第 5 卡合同；ST、停牌、涨跌停、流动性、真实上市退市与行业沿革不足继续登记为 source caveat 或 hard filter gap | `retained_gap` |
| source lineage | 每个候选必须记录 MALF run、WavePosition source、rule version、source concept trace、source family 与 reason code | `must_keep` |

## 6. Core Decisions

| 裁决项 | 结果 |
|---|---|
| MALF role | MALF v1.4 继续做结构尺 |
| Alpha/PAS role | 解释机会与候选生命周期 |
| Signal role | 聚合 Alpha/PAS 候选并做接受 / 拒绝裁决 |
| completed-wave baseline | 必须基于 setup 时点可见的 MALF 已完成波段 |
| in-flight facts | 只能作为 confirmation / weakening / invalidation |
| management actions | T1 / T2、保本、跟踪止损、分批退出属于后续 Position / Trade 管理面 |
| current system status | `sword_blank / 剑胚` |
| future candidate status | `entry_level_a_share_survival_sword_candidate` |
| source sufficiency | `sufficient_for_definition / insufficient_for_migration_or_profit_proof` |

人话版：

```text
MALF 做尺，Alpha/PAS 判断机会，Signal 做汇聚裁决。
现在只是剑胚；即使新版 Alpha/PAS 完成，也只能先成为 A 股 long-only / T+1 的入门级生存剑候选。
策略收益未证明前，不适合接入实盘。
```

## 7. Candidate Lifecycle Boundary

`pas_candidate_lifecycle` 在第 5 卡必须至少冻结以下状态：

| state | 含义 | 下游关系 |
|---|---|---|
| `waiting` | setup 条件形成但未触发 | Signal 不得当作 active intent |
| `triggered` | setup 触发条件在当时可见事实下成立 | 可进入 Signal 候选池 |
| `cancelled` | setup 前提被破坏或等待条件取消 | 进入 rejected / cancelled lineage |
| `modified` | 市场上下文改变，需要修正候选解释 | 必须保留原候选 lineage |
| `reentry_candidate` | 失败或取消后重新出现可审计候选 | 不得覆盖原失败记录 |
| `invalidated` | 当前结构事实使候选失效 | Signal 必须可拒绝 |
| `accepted_by_signal` | Signal 聚合后接受 | 只形成 signal intent，不形成订单 |
| `rejected_by_signal` | Signal 聚合后拒绝 | 必须保留 reason code |

## 8. Alpha_PAS_Design_Set_v1_0 Shape

第 5 卡应冻结 `Alpha_PAS_Design_Set_v1_0`，建议文件清单保持：

| file | must define |
|---|---|
| `AlphaPAS_00_Three_Documents_Bridge_v1_0.md` | MALF v1.4、当前 Alpha、历史系统、书籍概念的桥接边界 |
| `AlphaPAS_01_Core_Definitions_Theorems_v1_0.md` | market context、strength/weakness、setup、trigger、candidate、failure |
| `AlphaPAS_01B_Operational_Boundary_Rules_v1_0.md` | 只读消费 MALF、不得重定义 MALF、不得输出订单 / 仓位 / 成交 |
| `AlphaPAS_02_Trigger_Strength_Stats_Definitions_Theorems_v1_0.md` | 触发、完成波段强弱比较、历史统计排名与样本约束 |
| `AlphaPAS_02A_Candidate_Lifecycle_Definitions_Theorems_v1_0.md` | 候选生命周期、取消、修改、重入、失效、Signal 接受 / 拒绝 |
| `AlphaPAS_03_System_Service_Interface_v1_0.md` | 给 Signal / T+1 proof 消费的 service surface |
| `AlphaPAS_04_Context_Chart_View_v1_0.md` | context 与 MALF 波段标尺的图示读法 |
| `AlphaPAS_05_Trigger_Chart_View_v1_0.md` | TST / BOF / BPB / PB / CPB 的触发视图 |
| `AlphaPAS_06_Stats_Ranking_Chart_View_v1_0.md` | ranking、分位、样本量、稀疏性与解释限制 |
| `AlphaPAS_07_Definition_Theorem_Review_and_Implementation_Delta_v1_0.md` | 当前 Asteria、历史 PAS、书籍语义的差异和取舍 |
| `MANIFEST.json` | source anchors、hash、version、scope、retained gaps |

第 5 卡可以冻结合同；本卡只冻结上表作为合同重设输入。

## 9. Retained Gaps

| gap | retained reason |
|---|---|
| profit proof | 第 8 / 第 9 卡前不得宣称 |
| broker readiness | broker feasibility 仍 deferred |
| formal write path | 本路线不授权写 `H:\Asteria-data` |
| ST / 停牌 / 涨跌停 / 流动性 hard filters | 需 approved source manifest 或后续 hard-filter card |
| historical industry / index / block membership | 当前仍是 Data reference retained gap |
| direct legacy code migration | source sufficiency 只够 definition，不够 migration |
| book text as contract | 只保留章节锚点和概念索引，不复制正文 |

## 10. Next Route Input

`v1-alpha-pas-contract-redesign-card` 应消费本 authority map，并只做以下事情：

| target | decision |
|---|---|
| design package | 冻结 `Alpha_PAS_Design_Set_v1_0` |
| service contract | 定义 Signal / T+1 proof 可消费的 Alpha/PAS surface |
| source lineage | 固定 MALF run、WavePosition、rule version、source concept trace |
| candidate lifecycle | 固定等待、触发、取消、修改、重入、失效、接受 / 拒绝 |
| non-goals | 不证明收益、不接 broker、不输出订单 / 仓位 / 成交 |
