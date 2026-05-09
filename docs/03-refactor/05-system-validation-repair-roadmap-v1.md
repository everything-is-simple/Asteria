# Asteria System Validation and Repair Roadmap v1

日期：2026-05-09

状态：planned / post-year-replay-blocked roadmap

适用阶段：系统级验证、数据补洞、综合调试

## 1. Roadmap 定位

Asteria 已完成原主干模块施工 roadmap 的关键短线目标：

```text
full-chain day bounded proof passed
one-year strategy behavior replay executed but blocked
```

当前系统不再处于“继续顺序开发下一个主线模块”的阶段，而是进入：

```text
系统级验证 + 数据补洞 + 综合调试阶段
```

这一阶段的核心问题不再是单模块是否能写出来，而是：

| 问题类型 | 说明 |
|---|---|
| 数据覆盖 | released surfaces 是否覆盖目标时间窗 |
| 时间口径 | natural year、UTC/local report bucket 是否一致 |
| DB 完整性 | 下游 proof surface 是否只是 bounded surface，还是 full build surface |
| 跨模块联动 | MALF -> Alpha -> Signal -> Position -> Portfolio -> Trade -> System 是否连续 |
| 证据落账 | repo record、report manifest、validated zip 是否互相引用 |
| 行为质量 | 一年下来信号、持仓、订单、拒单是否像样 |

因此，本 roadmap 不再追求“一次开很多张执行卡”，而是固定采用：

```text
诊断归因 -> 最小化修复 -> 重跑验证 -> closeout/decision
```

本 roadmap 是人读作战图，不替代 `module_gate_registry.toml`、gate ledger 或 conclusion index。
只有当前一张 conclusion 明确授权的卡，才允许进入 live authority。

## 2. 当前 Live Truth

截至 2026-05-09，当前权威状态为：

| 项 | 状态 |
|---|---|
| card 1 | `pipeline-full-chain-bounded-proof-build-card-20260508-01` passed |
| card 2 | `pipeline-full-chain-bounded-proof-closeout-20260508-01` passed |
| card 3 | `pipeline-one-year-strategy-behavior-replay-authorization-scope-freeze-20260508-01` passed |
| card 4 | `pipeline-one-year-strategy-behavior-replay-build-card-20260508-01` blocked |
| current allowed next card | `pipeline_year_replay_coverage_gap_diagnosis_and_repair_scope_freeze` |
| Pipeline next card | `pipeline_year_replay_coverage_gap_diagnosis_and_repair_scope_freeze` |
| blocked reason | `2024-01-01..2024-01-07` coverage gap |
| full rebuild | not authorized |
| daily incremental | not authorized |
| resume/idempotence hardening | not authorized |
| v1 complete | not authorized |

卡 4 的 blocked 是 truthful blocked，不是 pipeline runner 崩溃，也不是系统证明失败。它说明：

```text
year replay runner 能产出行为观察证据，
但 released System Readout coverage 未满足完整自然年 2024。
```

## 3. 阶段方法论

后续每张卡必须遵循同一节奏。

| 阶段 | 卡类型 | 目标 |
|---|---|---|
| 1 | diagnosis / scope freeze | 判定问题归属和修复边界 |
| 2 | minimal repair | 只修被授权的最小缺口 |
| 3 | rerun verification | 回到原验证目标重跑 |
| 4 | closeout / decision | 封存证据，决定下一卡或停住 |

禁止跳步：

| 禁止行为 | 原因 |
|---|---|
| 未诊断就修库 | 容易修错层 |
| repair card 里顺手重跑 year replay | 授权边界变脏 |
| replay blocked 后直接开 full build | 证据链不够 |
| 把 bounded surface 说成 full build surface | 结论失真 |
| 把 fill gap 包装成 PnL truth | 交易真实性不足 |
| 同时开很多 live card | 绕过门禁设计 |

## 4. 第一张下一卡

当前唯一 live candidate：

```text
pipeline-year-replay-coverage-gap-diagnosis-and-repair-scope-freeze-20260509-01
```

性质：

```text
diagnosis / repair scope freeze
```

目标：

```text
判定 2024-01-01..2024-01-07 缺口到底断在哪一层，
并只授权一张最小 repair card。
```

本卡只允许 read-only audit，不允许：

| 禁止项 | 裁决 |
|---|---|
| 写 `H:\Asteria-data` | 禁止 |
| rebuild Data | 禁止 |
| rebuild MALF/Alpha/Signal/System | 禁止 |
| rerun year replay | 禁止 |
| 修改 Pipeline 业务语义 | 禁止 |
| 宣称 full build passed | 禁止 |
| 开 v1 complete | 禁止 |

必须输出 coverage matrix：

| 层 | 必查内容 |
|---|---|
| Data | `raw_market`、`market_base_day`、`market_meta` 是否覆盖 2024-01-01..01-07 |
| MALF | released MALF day surface 是否覆盖 2024-01-01..01-07 |
| Alpha | released Alpha day/week/month production surface 是否覆盖目标窗口 |
| Signal | released signal surface 是否覆盖目标窗口 |
| Position | position candidate / entry / exit surface 是否覆盖目标窗口 |
| Portfolio Plan | admission / target exposure / trim surface 是否覆盖目标窗口 |
| Trade | order intent / execution plan / rejection surface 是否覆盖目标窗口 |
| System Readout | `system_chain_readout` 为什么从 2024-01-08 开始 |
| Pipeline | replay source selection 是否正确读取 released System Readout |

本卡 conclusion 必须只给出一个下一步：

| 诊断结果 | 下一张卡 |
|---|---|
| Data 缺覆盖 | `data-2024-natural-year-coverage-maintenance-card-20260509-01` |
| Data 有、MALF 缺 | `malf-2024-natural-year-coverage-repair-card-20260509-01` |
| MALF 有、Alpha/Signal 缺 | `alpha-signal-2024-coverage-repair-card-20260509-01` |
| 上游都有、System Readout 缺 | `system-readout-2024-coverage-repair-card-20260509-01` |
| System 有、Pipeline 取数错 | `pipeline-year-replay-source-selection-repair-card-20260509-01` |
| 证据不足无法归因 | `coverage-gap-evidence-incomplete-closeout-card-20260509-01` |

## 5. Candidate Card Queue

以下全部是 backlog candidate，不是 live card。只有当前一张 conclusion 明确授权，才能进入 live authority。

| 优先级 | 候选卡 | 目的 |
|---|---|---|
| P0 | `pipeline-year-replay-coverage-gap-diagnosis-and-repair-scope-freeze-20260509-01` | 判定 coverage gap 归属 |
| P1 | `data-2024-natural-year-coverage-maintenance-card-20260509-01` | 修 Data 层 2024 自然年覆盖 |
| P1 | `malf-2024-natural-year-coverage-repair-card-20260509-01` | 修 MALF released day surface 覆盖 |
| P1 | `alpha-signal-2024-coverage-repair-card-20260509-01` | 修 Alpha/Signal released surface 覆盖 |
| P1 | `system-readout-2024-coverage-repair-card-20260509-01` | 修 System Readout coverage |
| P1 | `pipeline-year-replay-source-selection-repair-card-20260509-01` | 修 replay source selection |
| P2 | `pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01` | coverage repair 后重跑 2024 replay |
| P2 | `pipeline-one-year-strategy-behavior-replay-rerun-closeout-20260509-01` | 封存 rerun evidence |
| P2 | `pipeline-report-date-bucket-utc-local-test-repair-card-20260509-01` | 单独修 UTC/local 日期分桶测试 |
| P3 | `pipeline-one-year-strategy-behavior-quality-review-card-20260509-01` | 审查一年行为是否合理 |
| P4 | `full-build-readiness-decision-card-20260509-01` | 决定是否进入 full build |
| P4 | `trade-fill-source-authority-decision-card-20260509-01` | 决定 fill/cash/PnL 真实来源 |
| P5 | `daily-incremental-readiness-decision-card-20260509-01` | 决定 daily incremental 是否开工 |
| P5 | `system-resume-idempotence-hardening-card-20260509-01` | 决定 resume/idempotence hardening |
| P6 | `asteria-v1-release-evidence-closeout-card-20260509-01` | 最终 v1 release evidence closeout |

## 6. 第一轮建议路线

第一轮只打穿 coverage gap 和 year replay rerun。

```text
coverage-gap diagnosis
-> one minimal repair card
-> year replay rerun
-> year replay closeout
-> behavior quality review
```

推荐顺序：

| 顺序 | 卡 | 状态 |
|---|---|---|
| 1 | `pipeline-year-replay-coverage-gap-diagnosis-and-repair-scope-freeze-20260509-01` | 立即准备 |
| 2 | repair card | 由第 1 张 conclusion 决定 |
| 3 | `pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01` | repair passed 后准备 |
| 4 | `pipeline-one-year-strategy-behavior-replay-rerun-closeout-20260509-01` | rerun 有结论后准备 |
| 5 | `pipeline-one-year-strategy-behavior-quality-review-card-20260509-01` | replay passed 后准备 |

## 7. 单独小修队列

UTC/local 日期分桶测试失败单独处理，不并入 coverage gap。

候选卡：

```text
pipeline-report-date-bucket-utc-local-test-repair-card-20260509-01
```

原因：

| 项 | coverage gap | UTC/local test repair |
|---|---|---|
| 性质 | released surface 覆盖问题 | 测试/报告路径日期口径问题 |
| 是否影响 year replay truth | 是 | 否 |
| 是否需要修数据 | 可能 | 否 |
| 是否应合并 | 否 | 否 |

该卡只能修：

```text
report date bucket expectation
test date source
UTC/local date assertion
```

不得顺手改 replay coverage gate。

## 8. 行为质量审查阶段

当 year replay rerun passed 后，不直接进入 v1 release，而是先审查行为质量。

候选卡：

```text
pipeline-one-year-strategy-behavior-quality-review-card-20260509-01
```

审查对象：

| 指标 | 目的 |
|---|---|
| signal count | 信号频率是否合理 |
| position candidate count | 候选持仓是否过稀或过密 |
| portfolio admission count | 组合准入是否过度裁剪 |
| order intent count | 订单意图是否异常偏少 |
| execution plan count | 执行计划是否和订单意图一致 |
| rejection count | 拒单是否集中在少数规则 |
| readout timeline | 关键阶段是否连续 |
| fill count | 只能记录 retained gap，不得解释为真实成交 |

审查结论只能是：

| 结论 | 下一步 |
|---|---|
| behavior acceptable | 准备 full build readiness decision |
| behavior distorted | 准备对应诊断/修补卡 |
| evidence insufficient | 停住，补 evidence |
| fill gap blocks interpretation | 准备 fill source authority decision |

## 9. 长线候选方向

以下方向必须等 year replay rerun 和 behavior review 之后再排序。

| 方向 | 什么时候开 |
|---|---|
| full build | 行为质量基本可信后 |
| fill source | 需要讨论真实成交、现金账本、PnL 前 |
| daily incremental | full build 证明稳定后 |
| resume/idempotence | runner 进入长周期运行前 |
| v1 release evidence | full build、incremental、fill/cash 口径都有结论后 |

禁止把 year replay passed 解释成：

```text
full rebuild passed
daily incremental passed
production release
v1 complete
real PnL validated
```

## 10. Governance Sync 要求

实施本 roadmap 时，应同步更新：

| 文件 | 目的 |
|---|---|
| `docs/03-refactor/05-system-validation-repair-roadmap-v1.md` | 新增本 roadmap |
| `docs/03-refactor/04-asteria-full-system-roadmap-v1.md` | 增加交接说明 |
| `governance/module_gate_registry.toml` | 设置唯一下一卡 |
| `docs/03-refactor/00-module-gate-ledger-v1.md` | 登记阶段切换 |
| `docs/04-execution/00-conclusion-index-v1.md` | 登记 roadmap handoff 和下一卡 |
| `governance/module_api_contracts/pipeline.toml` | 登记 diagnosis-only scope |
| `docs/01-architecture/00-mainline-authoritative-map-v1.md` | 同步当前 next-card 与禁止扩权项 |

第一张 diagnosis card 准备完成后，允许的 live authority 应变为：

```text
current_allowed_next_card = "pipeline_year_replay_coverage_gap_diagnosis_and_repair_scope_freeze"
```

Pipeline module 应保持：

```text
status = "released"
allow_build = false
next_card = "pipeline_year_replay_coverage_gap_diagnosis_and_repair_scope_freeze"
proof_status includes "one_year_strategy_behavior_replay_blocked"
```

## 11. Evidence 要求

每张正式执行卡在 closeout 前都必须具备 repo 四件套：

```text
card
evidence-index
record
conclusion
```

需要 release/closeout 的卡还必须具备：

```text
H:\Asteria-report\<module>\<date>\<run_id>\manifest.json
H:\Asteria-report\<module>\<date>\<run_id>\closeout.md
H:\Asteria-Validated\<zip>
```

diagnosis card 的 evidence 可以是 read-only audit summary，但必须能回答：

```text
检查了哪些 DB/table
检查了哪些 run_id
每层 min/max date 是什么
断点归因是什么
下一张 repair card 为什么只应该是这一张
```

## 12. 验收标准

本 roadmap 本身通过标准：

| 检查 | 标准 |
|---|---|
| governance consistency | registry、gate ledger、roadmap、conclusion index 一致 |
| next-card clarity | 只有一张 immediate live candidate |
| backlog clarity | 第 2 张以后只是 candidate，不是 live |
| no overclaim | 不宣称 full build、daily incremental、v1 complete |
| phase clarity | 明确系统验证/数据补洞/综合调试阶段 |
| repair discipline | 每一轮都先诊断、再修复、再重跑 |

## 13. 当前结论

Asteria 当前不是“快结束”，而是进入后半场：

```text
主干模块施工完成第一轮闭环；
系统验证正式开始；
第一个真实 blocker 是 2024 自然年 coverage gap；
下一步应先开 coverage-gap diagnosis card。
```

当前最稳的下一步：

```text
pipeline-year-replay-coverage-gap-diagnosis-and-repair-scope-freeze-20260509-01
```
