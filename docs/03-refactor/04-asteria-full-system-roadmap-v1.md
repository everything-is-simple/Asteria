# Asteria 全系统重构路线图 / 总待办 v1

日期：2026-04-29

## 1. 摘要

当前基线：Data Foundation production baseline 已封版；`MALF day bounded proof`、
`Alpha freeze review`、`Alpha bounded proof`、`Signal freeze review`、`Signal bounded proof`
与 `MALF complete alignment closeout` 已通过；MALF v1.4 day runtime sync implementation
已通过，MALF week/month bounded proof build、Alpha production builder hardening、
Signal production builder hardening、upstream pre-position release decision、Position bounded proof、
Portfolio Plan freeze review、Portfolio Plan bounded proof、Trade freeze review、Trade bounded proof、
System Readout freeze review、System Readout bounded proof build、Pipeline freeze review 与
Pipeline build/runtime authorization scope freeze、`pipeline-single-module-orchestration-build-card-20260508-01`
与 `pipeline-full-chain-dry-run-authorization-scope-freeze-20260508-01`、
`pipeline-full-chain-dry-run-card-20260508-01` 与
`pipeline-full-chain-bounded-proof-authorization-scope-freeze-20260508-01` 已通过。当前 allowed next action 为
Pipeline full-chain bounded proof build 与 closeout 已通过；one-year strategy behavior replay authorization scope freeze 已通过；
year replay build 已执行但因完整自然年覆盖不足而 blocked；MALF 最小 repair 已通过；随后 rerun 已真实执行但继续 blocked；
`alpha-signal-2024-coverage-repair-card-20260509-01`、`position-2024-coverage-repair-card-20260509-01` 与
`portfolio-plan-2024-coverage-repair-card-20260509-01` 与
`trade-2024-coverage-repair-card-20260509-01` 现已通过，当前 live `current_allowed_next_card`
已切到 `pipeline_year_replay_source_selection_repair_card`。

地基轨道 `data-formal-promotion-evidence-20260502-01` 的 allowed next action
`MALF v1.3 formal rebuild closeout` 已由当前 MALF v1.3 closeout 闭环。
MALF v1.4 authority sync 只改变后续实现同步的权威输入，不改变 allowed next action。
Data reference maintenance closeout 已完成 source inventory 裁决，MALF week/month proof、Alpha production
hardening、Signal production hardening、upstream release decision、Position bounded proof、
Portfolio Plan freeze review、Portfolio Plan bounded proof、Trade freeze review、Trade bounded proof、
System Readout freeze review 与 System Readout bounded proof build 已闭环。Portfolio Plan bounded proof 的 allowed next action
`trade_freeze_review` 已由本轮 Trade freeze review 承接；Trade freeze review 的 allowed next action
`trade_bounded_proof_build_card` 已由本轮 Trade bounded proof 承接；`system_readout_bounded_proof_build_card`
已由本轮 System Readout bounded proof 承接；其历史 allowed next action `pipeline_freeze_review`
也已由本轮 Pipeline freeze review 闭环。
历史 MALF month 结论的 allowed next action `alpha_production_builder_hardening` 已由本轮 Alpha 卡闭环。
历史 Alpha 结论的 allowed next action `signal_production_builder_hardening` 已由本轮 Signal 卡闭环。
历史 Signal 结论的 allowed next action `upstream_pre_position_release_decision` 已由本轮 release decision 闭环。
历史 Position release decision 的 allowed next action `position_bounded_proof_build_card`
已由本轮 Position bounded proof 闭环。
历史 Position bounded proof 的 allowed next action `portfolio_plan_freeze_review`
已由本轮 Portfolio Plan freeze review 闭环。
历史 Portfolio Plan freeze review 的 allowed next action `portfolio_plan_bounded_proof_build_card`
已由本轮 Portfolio Plan bounded proof 闭环。

本路线图依据以下权威资产刷新：

```text
H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.md
H:\Asteria-Validated\Asteria-docs-code-20260502-104932.zip
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4.zip
H:\Asteria-Validated\Asteria-data-formal-promotion-evidence-20260502-01.zip
H:\Asteria-Validated\Asteria-malf-v1-3-formal-rebuild-closeout-20260502-01.zip
H:\Asteria-Validated\Asteria-malf-week-bounded-proof-build-20260506-01.zip
H:\Asteria-Validated\Asteria-malf-month-bounded-proof-build-20260506-01.zip
H:\Asteria-Validated\Asteria-alpha-production-builder-hardening-20260506-01.zip
```

深度研究报告中的 “机器可读门禁、统一 schema registry、模块 API 合同、pipeline ledger
运行时” 缺口已部分被 repo 后续治理实现补齐；尚未放行的是 pipeline runtime 与
全系统日更/断点续传运行时。

主线模块设计、实现与正式 DB 证据的当前完成度判定见：

```text
docs/00-governance/05-mainline-module-completion-gap-audit-v1.md
```

系统完成路径固定为：

```text
设计/契约冻结 -> bounded proof（边界证明） -> evidence（证据） -> release gate（放行门禁） -> 下游授权
```

正式分三条轨道：

```text
地基轨道：
Data Foundation -> 只作为 source-fact infrastructure 向 MALF 供给

策略主线：
MALF -> Alpha -> Signal -> Position -> Portfolio Plan -> Trade -> System Readout

治理 / 编排轨道：
Governance 控制门禁
Pipeline 只调度和记录
```

`Data Foundation` 不进入策略主线排序，不占主线施工位；`Pipeline` 不定义业务语义。

## 2. 阶段 0：治理闭环

- [x] 修正 `governance/module_gate_registry.toml`：把 MALF `next_card` 从 `malf_day_bounded_proof` 改为 `alpha_freeze_review`。
- [x] 增加治理检查：校验 gate ledger（门禁账本）、execution conclusion（执行结论）、registry（注册表）的 current/next 状态一致。
- [x] 增加 evidence（证据）完备性检查：当前 MALF day release 与 docs authority refresh 必须有 `card`、`record`、`evidence-index`、`conclusion`、report manifest、validated zip。
- [ ] 建立统一 release gate checklist（放行检查清单）：governance、ruff、format、mypy、pytest、DB audit、evidence audit 全部记录。
- [x] 通过后只授权 `Alpha freeze review`，不打开 Alpha 代码施工，也不打开任何下游施工。

## 3. 地基轨道：Data Foundation

- [x] 保持 Data Foundation 定位：基础设施与 source-fact service，不是策略主线模块。
- [x] 冻结旧版 Lifespan raw/base 库首轮导入合同：`stock-only + day/week/month + backward adjusted base`。
- [x] 实现 `data legacy import runner working build`，仅输出 `H:\Asteria-temp\data\<run_id>` working DB。
- [x] 执行 `data formal promotion evidence`，审计并 promote 首轮正式 Data DB。
- [ ] 冻结 raw market、market meta、market base day/week/month 的正式 schema 与自然键。
- [ ] 实现正式 Data builder 前，继续限制当前能力为 bounded bootstrap support 与 legacy source intake。
- [ ] 正式 Data builder 必须支持 source manifest、run ledger、checkpoint、replay scope、audit summary。
- [ ] Data release 只放行“可供 MALF 消费的客观事实”，不产生 MALF/Alpha/Signal 语义。

## 4. 阶段 1：Alpha 冻结评审

- [ ] 重审 Alpha 六件套，确认 Alpha 只读消费 `malf_wave_position` / `malf_wave_position_latest`。
- [ ] 冻结 Alpha 输入：MALF WavePosition、必要 Data Foundation 客观事实、alpha family 私有事实。
- [ ] 明确 Alpha 输出：alpha event、alpha score、alpha signal candidate。
- [ ] 明确禁止输出：position size、portfolio allocation、order intent。
- [ ] 冻结 `alpha_bof/tst/pb/cpb/bpb.duckdb` schema 与自然键。
- [x] 写 Alpha build card，只允许 Alpha bounded proof。
- [x] Alpha freeze review 通过后，更新 gate ledger 与 registry。

## 5. 阶段 2：Alpha 边界证明

- [x] 实现 Alpha bounded runner，支持 `bounded`、`resume`、`audit-only`。
- [x] 建立 Alpha run ledger、schema version、rule version、checkpoint、replay scope。
- [x] 对至少一个 alpha family 跑通真实 bounded sample，再扩展到五个 family。
- [x] 审计 Alpha 不回写 MALF、不制造 MALF 语义、不输出资金/订单。
- [x] 产出 Alpha evidence 包与 conclusion。
- [x] Release gate（放行门禁）通过后，只授权 `Signal freeze review`。

## 6. 阶段 3：Signal 冻结 + 边界证明

- [x] 重审 Signal 六件套，确认 Signal 只聚合 Alpha 输出。
- [x] 冻结 `signal.duckdb` schema contract：formal signal ledger、signal run、schema/rule version；不创建正式 DB。
- [x] 实现 Signal bounded runner，输入只来自已放行 Alpha ledgers。
- [x] 审计 Signal 不做资金分配、不生成订单、不回写 Alpha/MALF。
- [x] 产出 Signal evidence 与 release conclusion。
- [x] Release gate（放行门禁）通过后，只授权 `Position freeze review`。
- [x] Position freeze review 已登记 blocked，当前回退到 `MALF Lifespan dense bar snapshot resolution`。
- [x] MALF Lifespan dense bar snapshot resolution 已通过，当前只授权 `Position freeze review reentry`。
- [x] MALF v1.4 Core operational boundary authority sync 已通过；只作为后续 MALF 实现同步输入，不打开下游施工。

## 7. 阶段 4：Position 冻结 + 边界证明

- [ ] 先执行 `Position freeze review reentry`，只做只读评审（review-only），不创建 Position runner 或 DB。
- [ ] 重审 Position 六件套，确认 Position 把 formal signal 转为 position candidate / entry plan / exit plan。
- [ ] 冻结 `position.duckdb` schema、自然键、状态机、幂等写入规则。
- [x] 实现 Position bounded runner 与 replay/checkpoint。
- [x] 审计 Position 不做组合级资金裁决、不修改 Signal。
- [x] 产出 Position evidence 与 release conclusion。
- [x] Release gate（放行门禁）通过后，只授权 `Portfolio Plan freeze review`。

## 8. 阶段 5：Portfolio Plan 冻结 + 边界证明

- [x] 重审 Portfolio Plan 六件套，冻结资金、容量、组合约束、准入/裁剪语义。
- [x] 冻结 `portfolio_plan.duckdb` schema 合同。
- [x] 实现 bounded runner，输入只来自 Position candidates/plans。
- [x] 审计 Portfolio Plan 不修改 Alpha/Signal/Position 历史语义。
- [x] 产出 Portfolio Plan evidence 与 release conclusion。
- [x] Release gate（放行门禁）通过后，只授权 `Trade freeze review`。

## 9. 阶段 6：Trade 冻结 + 边界证明

- [x] 重审 Trade 六件套，冻结 order intent、execution line、fill ledger、rejection semantics。
- [x] 冻结 `trade.duckdb` schema 合同；正式 DB 尚未创建。
- [x] 实现 bounded runner，输入只来自 Portfolio Plan。
- [x] 审计 Trade 不产生策略评分、不修改组合历史裁决。
- [x] 产出 Trade evidence 与 release conclusion。
- [x] Release gate（放行门禁）通过后，只授权 `System Readout freeze review`。

## 10. 阶段 7：System Readout 冻结 + 边界证明

- [x] 重审 System Readout 六件套，确认只读全链路 official ledgers。
- [x] 冻结 System Readout 冻结评审口径：`frozen six-doc set / freeze review passed / bounded proof passed / full build not executed`。
- [x] 创建 `system.duckdb`，并新增 `src/asteria/system_readout` 与 `scripts/system_readout` 的 day bounded proof 表面。
- [x] 实现只读 bounded runner。
- [x] 审计 System Readout freeze review 不触发业务重算、不回写任何上游模块。
- [x] 产出 System freeze review evidence 与 release conclusion。
- [x] Release gate（放行门禁）已通过 `system_readout_bounded_proof_build_card`；其历史下游 handoff `pipeline_freeze_review` 已闭环。

## 11. 阶段 8：Pipeline 集成

- [x] 在 review-only 范围内完成 Pipeline freeze review，确认当前 card 只授权冻结文档合同，不授权 runtime。
- [x] 用 `pipeline-build-runtime-authorization-scope-freeze-20260508-01` 把下一步施工范围冻结为 `pipeline_single_module_orchestration_build_card`，不直接跳 full-chain。
- [x] 重审 Pipeline 六件套，确认 Pipeline 只调度、记录、汇总状态，不定义业务语义。
- [x] 冻结 `pipeline.duckdb` schema 文档表面：pipeline_run、pipeline_step_run、module_gate_snapshot、build_manifest。
- [x] 在 `pipeline-single-module-orchestration-build-card-20260508-01` 中实现单模块调度。
- [x] 用 `pipeline-full-chain-dry-run-authorization-scope-freeze-20260508-01` 把下一步范围冻结为 `pipeline_full_chain_dry_run_card`，不直接跳 bounded proof。
- [x] 在 `pipeline-full-chain-dry-run-card-20260508-01` 中实现全链路 dry-run。
- [x] 用 `pipeline-full-chain-bounded-proof-authorization-scope-freeze-20260508-01` 把下一步范围冻结为 `pipeline_full_chain_bounded_proof_build_card`，不直接把 prepared card 偷换成 passed runtime。
- [x] 在 `pipeline-full-chain-bounded-proof-build-card-20260508-01` 中实现全链路 bounded run。
- [x] 接住 `pipeline-full-chain-bounded-proof-build-card-20260508-01` 的 allowed next action `pipeline_full_chain_bounded_proof_closeout`，独立完成 closeout / release evidence 封存。
- [x] 审计 Pipeline 不绕过 module gate、不写业务表、不替模块解释字段。
- [x] 产出 full-chain evidence 与 release conclusion。
- [x] 把 bounded proof closeout 的 allowed next action 明确切到 `pipeline_one_year_strategy_behavior_replay_authorization_scope_freeze`，不提前开 full rebuild 长线卡。
- [x] 冻结 `pipeline-one-year-strategy-behavior-replay-authorization-scope-freeze-20260508-01`，把 observation scope 限定为 `signal -> position -> portfolio_plan -> trade(order_intent / execution_plan / rejection) -> system_readout`。
- [x] 接住 year replay scope freeze 的 allowed next action `pipeline_one_year_strategy_behavior_replay_build_card`，只执行一年行为回放，不偷换成 full rebuild。
- [x] 执行 `pipeline-one-year-strategy-behavior-replay-build-card-20260508-01`，并 truthful 记录 `2024` 完整自然年覆盖不足导致的 `blocked`。
- [x] 将原主干模块施工 roadmap 收束到当前总路线图的“系统验证与修补阶段”，并已由 diagnosis 结论把唯一 prepared card 切到 `malf_2024_natural_year_coverage_repair_card`。

## 12. 阶段 9：系统验证与修补 Roadmap

卡 4 的 truthful blocked 说明 Asteria 已从“主干模块施工”进入“系统级验证 + 数据补洞 + 综合调试”阶段。
本阶段继续留在本路线图内维护，不再并行维护第二张独立 roadmap。

当前唯一 live next card：

```text
pipeline-year-replay-source-selection-repair-card-20260509-01
```

当前已知 live truth：

- `pipeline-one-year-strategy-behavior-replay-build-card-20260508-01` 已真实执行，但因 `2024` 完整自然年覆盖不足而 `blocked`
- `pipeline-year-replay-coverage-gap-diagnosis-and-repair-scope-freeze-20260509-01` 已完成 formal read-only diagnosis
- diagnosis 结论已锁定最早 released surface break 在 MALF
- `malf-2024-natural-year-coverage-repair-card-20260509-01` 已通过最小 MALF released day surface repair，并生成 `malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001`
- 历史 allowed next action `pipeline_one_year_strategy_behavior_replay_rerun_build_card` 已真实放行并已被执行
- `pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01` 已真实执行，但 `observed_start` 仍是 `2024-01-08`，且 source lock 未指向 repaired MALF run
- `alpha-signal-2024-coverage-repair-card-20260509-01` 已通过，released Alpha / Signal day surface 已前移到 `2024-01-02`
- `coverage-gap-evidence-incomplete-closeout-card-20260509-01` 已真实执行并通过，确认 released Position / Portfolio Plan / Trade day surface 的最早日期都落在 `2024-01-09`
- `position-2024-coverage-repair-card-20260509-01` 已于 `2026-05-10` 真实执行并完成；released Position candidate day surface 已前移到 `2024-01-02`，entry / exit 仍从 `2024-01-04` 起步，但这与 `2024-01-02` 与 `2024-01-03` 的 released Signal 状态 `rejected / no_active_alpha_candidate` 一致，因此 follow-up attribution 已真实下移到 `downstream_surface_gap:portfolio_plan`
- `portfolio-plan-2024-coverage-repair-card-20260509-01` 随后也已于 `2026-05-10` 真实执行并完成；released Portfolio Plan admission surface 已前移覆盖 `2024-01-02..2024-01-05`，而 target exposure 只在真实 admitted day `2024-01-05` 存在，因此 follow-up attribution 已继续下移到 `downstream_surface_gap:trade`
- `pipeline-portfolio-plan-2024-coverage-repair-handoff-20260510-01` 已通过，正式接住 Portfolio Plan repair follow-up attribution，并把 allowed next action 同步为 `trade_2024_coverage_repair_card`
- `trade-2024-coverage-repair-card-20260509-01` 已于 `2026-05-10` 真实执行并完成；released Trade rejection surface 已前移到 `2024-01-02`，而 `order_intent` / `execution_plan` 只在真实 admitted day `2024-01-05` 存在，因此 follow-up attribution 已继续下移到 `released_surface_gap:system_readout`
- `pipeline-trade-2024-coverage-repair-handoff-20260510-01` 已通过，正式接住 Trade repair follow-up attribution，并把 allowed next action 同步为 `system_readout_2024_coverage_repair_card`
- `system-readout-2024-coverage-repair-card-20260509-01` 已真实执行并完成，follow-up attribution 只剩 `calendar_semantic_gap_only`
- `pipeline-system-readout-2024-coverage-repair-handoff-20260510-01` 已通过，正式接住 System Readout repair follow-up attribution，并把 allowed next action 同步为 `pipeline_year_replay_source_selection_repair_card`
- 当前唯一 live next card 只允许 Pipeline source selection repair，不得扩成 System full build、Pipeline semantic repair、full rebuild、daily incremental 或 `v1 complete`

本阶段固定节奏：

```text
诊断归因 -> 最小 repair -> year replay rerun -> Alpha/Signal repair -> downstream closeout -> behavior quality review
```

候选 repair queue 只作为 backlog 顺序参考，不得压过“当前唯一下一卡”：

| 优先级 | 候选卡 | 说明 |
|---|---|---|
| P0 | `pipeline-year-replay-source-selection-repair-card-20260509-01` | System Readout repair 已真实收口后，当前唯一 live next card |
| P1 | `pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01` | 仅作近程 blocked backlog 参考，不得压过当前唯一下一卡 |
| P2 | `trade-2024-coverage-repair-card-20260509-01` | 已 completed；不再是 live next card |
| P2 | `portfolio-plan-2024-coverage-repair-card-20260509-01` | 已 completed；不再是 live next card |
| P2 | `position-2024-coverage-repair-card-20260509-01` | 已 completed；不再是 live next card |
| P2 | `malf-2024-natural-year-coverage-repair-card-20260509-01` | 已 passed，不再是 prepared next card |
| P2 | `alpha-signal-2024-coverage-repair-card-20260509-01` | 已 passed，不再是 prepared next card |

三层优先级总表：

| 层级 | 作用 | 当前内容 |
|---|---|---|
| 层 1 | 当前 live next card | `pipeline-year-replay-source-selection-repair-card-20260509-01` |
| 层 2 | 近程 backlog candidates | `pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01` |
| 层 3 | 长期阶段 11 队列 | `system-wide-daily-dirty-scope-protocol-card`，`data-ledger-daily-incremental-hardening-card`，`malf-daily-incremental-ledger-build-card`，`alpha-signal-daily-incremental-ledger-build-card`，`downstream-daily-impact-ledger-schema-card`，`downstream-daily-incremental-runner-build-card`，`pipeline-full-daily-incremental-chain-build-card`，`full-rebuild-and-daily-incremental-release-closeout-card` |

仍然禁止把当前阶段解释成：

```text
full rebuild passed
daily incremental passed
production release
v1 complete
```

## 13. 阶段 10：Timeframe 扩展

- [ ] 在 day 主链稳定后，复制 MALF 到 week/month：core、lifespan、service 三库各自 proof。
- [ ] 扩展 Alpha/Signal 对 timeframe 字段的正式支持。
- [ ] 对 cross-timeframe 读取做 contract tests，避免下游自造 MALF 语义。
- [ ] 产出 week/month evidence 包。
- [ ] 更新 topology registry 与 module contracts。

## 14. 阶段 11：25 库历史大帐本化与全系统放行

阶段 11 的目标不是增加新的业务 DuckDB 数量，而是在现有 25 库目标拓扑内，把正式库升级为
可长期运行的分账本体系：

```text
每日增量更新
每日断点续传
source manifest / dirty scope / checkpoint / audit summary
Pipeline 全链路 manifest
```

25 个 DuckDB 仍是完整目标拓扑。后续施工优先在现有 DB 内补充增量控制表、impact
map、checkpoint 与 runner 能力；只有当现有 `pipeline.duckdb` 无法承载跨模块编排、
writer lease 或全链路 checkpoint 时，才允许另开治理卡评估是否需要新增控制库。

历史大帐本化的分层裁决：

| 层 | DB 范围 | 增量口径 | 裁决 |
|---|---|---|---|
| Data 行情账本 | `raw_market`; `market_base_day/week/month` | `source manifest -> symbol + date dirty scope` | 作为 Data/MALF 样板优先硬化 |
| Data reference 账本 | `market_meta` | `effective_date / reference_batch_id / source_version` | 不伪装成每日 bar 账本；只通过 maintenance card 扩展 |
| MALF | `malf_core/lifespan/service` x `day/week/month` | `market_base dirty scope -> symbol + bar_dt/week_dt/month_dt` | 复用 segmented/resume 样板补 daily incremental |
| Alpha / Signal | `alpha_*`; `signal` | `source MALF/Alpha run -> symbol + bar_dt/signal_dt` | 可接入每日脏域，但必须锁定 source run |
| Downstream | `position`; `portfolio_plan`; `trade`; `system` | `daily impact scope + 业务自然键映射` | 不把业务自然键硬改为 `trade_date + symbol` |
| Pipeline | `pipeline` | `pipeline_run + step checkpoint + module dirty manifest` | 只编排和记录，不定义业务语义 |

全链路 daily incremental 的统一原则：

```text
调度入口统一为 trade_date + symbol + timeframe。
业务表自然键保持模块原语义。
每个模块新增或复用 daily_dirty_scope / daily_impact_scope / incremental_checkpoint。
每个模块必须记录 source_run_id -> target_run_id 映射。
每次 promote 必须先 hard audit，再更新正式 surface 与 manifest。
```

不得把该目标误读为：

```text
把 Trade fill ledger 改成 trade_date + symbol 主键
把 Portfolio Plan 的组合裁决降级成单标的日线事实
让 System Readout 触发上游重算
让 Pipeline 定义业务字段语义
```

阶段 11 施工队列初稿如下，必须在当前 year replay rerun 及其 closeout 之后，逐卡进入 live authority：

| 顺序 | 候选卡 | 目标 |
|---:|---|---|
| 1 | `pipeline-year-replay-source-selection-repair-card-20260509-01` | System Readout repair 已通过；当前需收口 Pipeline source selection truth |
| 2 | `system-wide-daily-dirty-scope-protocol-card` | 冻结跨模块 dirty scope、daily impact scope、checkpoint、source_run lineage、writer/read-only 规则 |
| 3 | `data-ledger-daily-incremental-hardening-card` | 将 Data 4 个行情账本的 daily incremental / resume / audit evidence 做成生产级样板 |
| 4 | `malf-daily-incremental-ledger-build-card` | 让 MALF 正式消费 Data dirty scope，并生成 MALF 自身 daily impact scope |
| 5 | `alpha-signal-daily-incremental-ledger-build-card` | 将 Alpha/Signal 接入 `symbol + date + source_run_id` 脏域传播 |
| 6 | `downstream-daily-impact-ledger-schema-card` | 为 Position/Portfolio Plan/Trade/System 冻结 impact map 与必要日期维字段 |
| 7 | `downstream-daily-incremental-runner-build-card` | 实现下游按 daily impact scope 重算、断点续传、幂等 promote |
| 8 | `pipeline-full-daily-incremental-chain-build-card` | Pipeline 编排 Data -> MALF -> Alpha -> Signal -> Position -> Portfolio Plan -> Trade -> System |
| 9 | `full-rebuild-and-daily-incremental-release-closeout-card` | 运行 full rebuild proof、daily incremental proof、resume/idempotence proof，并生成 final release evidence |

阶段 11 的完成标准：

- [ ] 25 库 topology 保持不扩张；若确需新增控制库，必须先有独立治理卡裁决。
- [ ] 每个正式 DB 都具备 run ledger、schema version、source lineage、checkpoint/replay scope 与 audit summary。
- [ ] Data/MALF 样板证明每日 dirty scope 可重跑、可 resume、可幂等 promote。
- [ ] Alpha/Signal 证明 `source_run_id + symbol + date` 脏域传播不重定义 MALF 语义。
- [ ] Position/Portfolio Plan/Trade/System 证明 daily impact map 不破坏业务自然键。
- [ ] Pipeline 证明 full daily chain 可以从中断点恢复，且不会重复 promote 或跨库假装原子事务。
- [ ] 运行 full rebuild proof。
- [ ] 运行 daily incremental proof。
- [ ] 运行恢复测试：中断后 resume，重复运行幂等。
- [ ] 生成 final release evidence：DB manifest、schema versions、rule versions、row counts、audit summaries、known limits。
- [ ] 标记系统达到 `v1 complete`。

## 15. 公开合同

- 每个模块必须有六件套：authority design（权威设计）、semantic contract（语义合同）、database schema spec（数据库 schema 规范）、runner contract（runner 合同）、audit spec（审计规范）、build card（构建卡）。
- 每个正式 DB 必须有：run ledger、schema version、checkpoint/replay scope、audit summary。
- 每个 runner 至少支持：`bounded`、`resume`、`audit-only`；进入完整系统前补齐 `segmented/full/daily_incremental`。
- 每个 release 必须落档：`card.md`、`record.md`、`evidence-index.md`、`conclusion.md`、report manifest、validated zip。
- 下游只读上游正式 ledgers；禁止回写、禁止重定义上游字段语义。

## 16. 测试计划

- 每个 phase 必跑：`check_project_governance.py`、`ruff check`、`ruff format --check`、`mypy src`、`pytest`。
- 每个模块新增 contract tests：输入表、输出表、自然键、版本字段、禁止输出项。
- 每个 bounded proof 新增 DB audit：row count、natural key uniqueness、status distribution、hard fail count。
- 每个 release gate 新增 evidence audit：证明包存在、manifest 可读、conclusion 与 registry 状态一致。
- Pipeline phase 增加端到端测试：单模块失败不污染下游，resume 不重复写入，full-chain 只按 gate 顺序运行。

## 17. 前提假设

- 当前事实基线以 `Data foundation production baseline sealed`、`MALF v1.3 day formal-data bounded closeout 已通过`、
  `Alpha bounded proof 已通过` 和 `Signal bounded proof 已通过` 为准。
- MALF v1.4 是当前语义与操作边界权威包；day runtime sync 与 week/month proof 已通过，full build 仍需另开卡。
- 当前 live `current_allowed_next_card` 是 `pipeline_year_replay_source_selection_repair_card`；Pipeline 已通过
  `system_readout` 单模块 orchestration、full-chain dry-run 与 full-chain day bounded proof，并已执行过一次 one-year strategy
  behavior replay 与一次 year replay rerun。coverage gap diagnosis 已正式执行并确认最早 released surface break 在 MALF；`malf-2024-natural-year-coverage-repair-card-20260509-01`
  与 `alpha-signal-2024-coverage-repair-card-20260509-01` 也都已通过最小 repair；随后
  `coverage-gap-evidence-incomplete-closeout-card-20260509-01` 也已通过，并把新的 downstream 首断点收口到 `position`。
  `position-2024-coverage-repair-card-20260509-01` 随后已真实执行并完成，新的 live 首断点已下移到
  `portfolio-plan-2024-coverage-repair-card-20260509-01`；该卡随后也已真实执行并完成，当前 live 首断点已继续下移到
  `trade-2024-coverage-repair-card-20260509-01`；而 `trade-2024-coverage-repair-card-20260509-01`
  又已真实执行并完成，当前 live 首断点已继续下移到
  `system-readout-2024-coverage-repair-card-20260509-01`。随后
  `system-readout-2024-coverage-repair-card-20260509-01` 已真实执行并完成；follow-up attribution 只剩
  `calendar_semantic_gap_only`，并已把 current live `current_allowed_next_card` 切到
  `pipeline_year_replay_source_selection_repair_card`。下一步只允许继续 Pipeline source selection repair；
  这仍不是 System full build、Pipeline semantic repair、full rebuild、daily incremental 或 `v1 complete` 授权。
- Data Foundation 是地基轨道，不进入策略主线排序。
- Pipeline 是编排与记录轨道，不进入业务主线排序。
- 不同时施工两个策略主线模块。
- `wave_core_state` 与 `system_state` 永远保持分离。
- `H:\Asteria-data` 放正式 DB，`H:\Asteria-temp` 放临时构建，`H:\Asteria-report` 放人读报告，`H:\Asteria-Validated` 放正式证据资产。
