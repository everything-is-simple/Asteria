# Alpha/PAS Source Inventory v1

日期：2026-05-14

状态：frozen / source inventory completed

执行卡：`v1-alpha-pas-source-inventory-card-20260514-01`

## 1. 定位

本文件是 `docs/03-refactor/06-asteria-core-module-recovery-and-proof-roadmap-v1.md`
第三卡的只读 source inventory 输出。

它只回答：

```text
后续 Alpha/PAS authority map 可以从哪些来源取材。
```

它不回答：

```text
新版 Alpha/PAS 合同是什么。
哪些历史代码可以迁入。
哪些书籍概念已经成为 Asteria 权威语义。
```

## 2. 本卡边界

| 项 | 裁决 |
|---|---|
| card type | `post-terminal / source-inventory / read-only` |
| live next | `none / terminal` |
| formal DB mutation | `no` |
| historical code migration | `no` |
| book content copied into repo | `no` |
| next route card | `v1-alpha-pas-authority-map-card` |

## 3. Current Asteria Alpha Surface

| source | current fact | use in next card |
|---|---|---|
| `docs/02-modules/alpha/` | Alpha 六件套已冻结，定义 Alpha 为 MALF 之后、Signal 之前的机会解释层 | 当前权威基线 |
| `src/asteria/alpha/` | 当前实现为五个 Alpha family 的 bounded / production builder surface | 当前实现事实 |
| `scripts/alpha/` | Alpha family build / audit / bounded proof / production builder runner | runner 行为事实 |
| `tests/unit/alpha/` | Alpha bounded proof 与 daily incremental ledger 单元测试 | 回归约束入口 |
| `docs/04-execution/records/alpha/` | Alpha freeze review、bounded proof、target completeness、production hardening 记录 | 已通过证据链 |
| `H:\Asteria-data\alpha_bof.duckdb` | BOF formal Alpha DB exists | 当前 release surface |
| `H:\Asteria-data\alpha_tst.duckdb` | TST formal Alpha DB exists | 当前 release surface |
| `H:\Asteria-data\alpha_pb.duckdb` | PB formal Alpha DB exists | 当前 release surface |
| `H:\Asteria-data\alpha_cpb.duckdb` | CPB formal Alpha DB exists | 当前 release surface |
| `H:\Asteria-data\alpha_bpb.duckdb` | BPB formal Alpha DB exists | 当前 release surface |

当前 Alpha 已证明可只读消费 MALF WavePosition / Service facts，并输出
`alpha_event_ledger`、`alpha_score_ledger`、`alpha_signal_candidate` 与
`alpha_source_audit`。但当前规则版本仍是 `waveposition_only` / family bounded
surface，不等于完整 PAS 语义恢复。

## 4. Current Concept Index

| concept | current location | current status |
|---|---|---|
| Alpha family | `BOF / TST / PB / CPB / BPB` | frozen current implementation surface |
| opportunity event | `alpha_event_ledger` | current Asteria output |
| opportunity score | `alpha_score_ledger` | current Asteria output |
| signal candidate | `alpha_signal_candidate` | current Signal input, not order / position |
| source audit | `alpha_source_audit` | current traceability surface |
| PAS | roadmap / historical / book source term | not yet remapped into Asteria contract |
| T+1 open | post-terminal proof route and history roots | not yet proven with restored PAS semantics |
| broker adapter | deferred route card | not allowed before proof value is established |
| completed-wave baseline | MALF v1.4 completed wave facts + YTC strength/weakness analysis | required split for next authority map |
| in-flight confirmation | MALF latest WavePosition / candidate / transition facts + YTC ongoing market analysis | provisional only, not completed baseline |

## 5. Historical Source Roots

| source root | exists | inventory role |
|---|---:|---|
| `G:\malf-history\astock_lifespan-alpha` | yes | T+0 signal -> T+1 open、filled / rejected runner 经验 |
| `G:\malf-history\EmotionQuant-alpha` | yes | 早期 PAS / governance / 6A 经验 |
| `G:\malf-history\EmotionQuant-beta` | yes | 外部回测选型与 Alpha/PAS 演进经验 |
| `G:\malf-history\EmotionQuant-gamma` | yes | T+1 Open、Broker/Backtest 共用内核、A 股规则 |
| `G:\malf-history\lifespan-0.01` | yes | data producer、market_base、dirty queue、checkpoint |
| `G:\malf-history\Lifespan-Validated` | yes | MALF / System 历史证据资产 |
| `G:\malf-history\MarketLifespan-Quant` | yes | PAS / risk unit / trailing stop / system readout |
| `H:\Asteria-Validated\MALF-system-history` | yes | 历史系统经验锚点 |

这些目录只作为 source inventory 与后续 authority map 的只读输入。任何历史代码迁移、
runner 行为继承、字段语义继承，都必须等待独立卡明确授权。

## 6. Book / Reference Roots

| source root | exists | inventory role |
|---|---:|---|
| `G:\《股市浮沉二十载》\2020.(Au)LanceBeggs` | yes | PAS 定义核心来源 |
| `G:\《股市浮沉二十载》\2021.Bob_Volman外汇超短线交易` | yes | 价格行为与入场细节参考 |
| `G:\《股市浮沉二十载》\2018.(CHINA)简简单单做股票` | yes | A 股实操经验参考 |

本卡不复制书籍正文、不摘录受版权保护内容、不把任何书籍术语直接提升为 Asteria
contract。下一张 `v1-alpha-pas-authority-map-card` 只能产出概念对照和取舍裁决。

### 6.1 YTC Chapter Anchors

| source | chapter / section anchor | next-card use |
|---|---|---|
| `YTC卷2：市场和市场分析` | 第 3 章：市场分析；尤其 3.3 强弱、3.5 / 3.6 行进中的市场分析 | 把 strength / weakness 拆成 completed-wave baseline 与 in-flight confirmation |
| `YTC卷3：交易策略` | 第 4 章：架构、反弱势、TST / BOF / BPB / PB / CPB | 映射 PAS setup family 与弱势失败后的机会解释 |
| `YTC卷3：交易策略` | 第 5 章：交易示例 | 保留为样例语料来源，不直接复制正文，不直接成为 contract |

下一卡必须特别处理一个口径：MALF 已发布 facts 主要是已经发生并可审计的结构事实；
因此 PAS 的强弱基准应优先比较已完成波段，例如
`previous_completed_same_direction_wave` vs `pre_previous_completed_same_direction_wave`。
当前正在发生的 up wave / down pullback 只能作为行进中证据，不能替代 completed baseline。

## 7. Next-Card Input

`v1-alpha-pas-authority-map-card` 应消费本 inventory，并输出：

| mapping target | required decision |
|---|---|
| current Alpha family surface | 保留 / 补强 / 弃用 / future enhancement |
| historical PAS concepts | 可进入 contract redesign / 只作为参考 / 不适合当前 Asteria |
| book-derived PAS concepts | 可映射概念索引，不复制正文 |
| MALF completed-wave baseline | 必须定义同向完成波段、正逆完成波段与 setup 时点可见性 |
| MALF in-flight confirmation | 必须定义 current wave / candidate / transition 只能如何支持、削弱或失效预期 |
| T+1 open execution hint | 是否进入新版 Alpha/PAS contract |
| broker / fill / account loop | 继续 deferred，除非收益 proof 与组合 reproof 后续放行 |

核心不变量保持：

```text
MALF v1.4 defines structure.
Alpha/PAS interprets opportunity.
Signal aggregates intent.
No Alpha/PAS source may redefine MALF or authorize broker execution.
```
