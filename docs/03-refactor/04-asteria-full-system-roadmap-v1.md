# Asteria 全系统重构路线图 / 总待办 v1

日期：2026-04-29

## 1. 摘要

当前基线：Data Foundation production baseline 已封版；`MALF day bounded proof`、
`Alpha freeze review`、`Alpha bounded proof`、`Signal freeze review`、`Signal bounded proof`
与 `MALF complete alignment closeout` 已通过；MALF v1.4 day runtime sync implementation
已通过，MALF week/month bounded proof build 已通过。当前上游修补队列下一步只允许
`alpha_production_builder_hardening`，Position bounded proof 仍暂停。

地基轨道 `data-formal-promotion-evidence-20260502-01` 的 allowed next action
`MALF v1.3 formal rebuild closeout` 已由当前 MALF v1.3 closeout 闭环。
MALF v1.4 authority sync 只改变后续实现同步的权威输入，不改变 allowed next action。
Data reference maintenance closeout 已完成 source inventory 裁决，MALF week/month proof 已闭环；
当前 allowed next action 已切到 `alpha_production_builder_hardening`。

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
- [ ] 实现 Position bounded runner 与 replay/checkpoint。
- [ ] 审计 Position 不做组合级资金裁决、不修改 Signal。
- [ ] 产出 Position evidence 与 release conclusion。
- [ ] Release gate（放行门禁）通过后，只授权 `Portfolio Plan freeze review`。

## 8. 阶段 5：Portfolio Plan 冻结 + 边界证明

- [ ] 重审 Portfolio Plan 六件套，冻结资金、容量、组合约束、准入/裁剪语义。
- [ ] 冻结 `portfolio_plan.duckdb` schema。
- [ ] 实现 bounded runner，输入只来自 Position candidates/plans。
- [ ] 审计 Portfolio Plan 不修改 Alpha/Signal/Position 历史语义。
- [ ] 产出 Portfolio Plan evidence 与 release conclusion。
- [ ] Release gate（放行门禁）通过后，只授权 `Trade freeze review`。

## 9. 阶段 6：Trade 冻结 + 边界证明

- [ ] 重审 Trade 六件套，冻结 order intent、execution line、fill ledger、rejection semantics。
- [ ] 冻结 `trade.duckdb` schema。
- [ ] 实现 bounded runner，输入只来自 Portfolio Plan。
- [ ] 审计 Trade 不产生策略评分、不修改组合历史裁决。
- [ ] 产出 Trade evidence 与 release conclusion。
- [ ] Release gate（放行门禁）通过后，只授权 `System Readout freeze review`。

## 10. 阶段 7：System Readout 冻结 + 边界证明

- [ ] 重审 System Readout 六件套，确认只读全链路 official ledgers。
- [ ] 冻结 `system.duckdb` schema：summary、audit snapshot、readout tables。
- [ ] 实现只读 bounded runner。
- [ ] 审计 System Readout 不触发业务重算、不回写任何上游模块。
- [ ] 产出 System evidence 与 release conclusion。
- [ ] Release gate（放行门禁）通过后，才允许 `Pipeline integration review`。

## 11. 阶段 8：Pipeline 集成

- [ ] 在任何 Pipeline runtime 施工前，先确认当前 active card 明确授权 Pipeline freeze review。
- [ ] 重审 Pipeline 六件套，确认 Pipeline 只调度、记录、汇总状态，不定义业务语义。
- [ ] 冻结 `pipeline.duckdb` schema：pipeline_run、pipeline_step_run、module_gate_snapshot、build_manifest。
- [ ] 实现单模块调度。
- [ ] 实现全链路 dry-run。
- [ ] 实现全链路 bounded run。
- [ ] 审计 Pipeline 不绕过 module gate、不写业务表、不替模块解释字段。
- [ ] 产出 full-chain evidence 与 release conclusion。

## 12. 阶段 9：Timeframe 扩展

- [ ] 在 day 主链稳定后，复制 MALF 到 week/month：core、lifespan、service 三库各自 proof。
- [ ] 扩展 Alpha/Signal 对 timeframe 字段的正式支持。
- [ ] 对 cross-timeframe 读取做 contract tests，避免下游自造 MALF 语义。
- [ ] 产出 week/month evidence 包。
- [ ] 更新 topology registry 与 module contracts。

## 13. 阶段 10：全系统放行

- [ ] 建立 full rebuild card：从 Data Foundation official facts 输入 MALF，再沿策略主线跑到 System Readout。
- [ ] 建立 daily incremental card：source manifest、dirty queue/replay scope、checkpoint、audit summary。
- [ ] 运行 full rebuild proof。
- [ ] 运行 daily incremental proof。
- [ ] 运行恢复测试：中断后 resume，重复运行幂等。
- [ ] 生成 final release evidence：DB manifest、schema versions、rule versions、row counts、audit summaries、known limits。
- [ ] 标记系统达到 `v1 complete`。

## 14. 公开合同

- 每个模块必须有六件套：authority design（权威设计）、semantic contract（语义合同）、database schema spec（数据库 schema 规范）、runner contract（runner 合同）、audit spec（审计规范）、build card（构建卡）。
- 每个正式 DB 必须有：run ledger、schema version、checkpoint/replay scope、audit summary。
- 每个 runner 至少支持：`bounded`、`resume`、`audit-only`；进入完整系统前补齐 `segmented/full/daily_incremental`。
- 每个 release 必须落档：`card.md`、`record.md`、`evidence-index.md`、`conclusion.md`、report manifest、validated zip。
- 下游只读上游正式 ledgers；禁止回写、禁止重定义上游字段语义。

## 15. 测试计划

- 每个 phase 必跑：`check_project_governance.py`、`ruff check`、`ruff format --check`、`mypy src`、`pytest`。
- 每个模块新增 contract tests：输入表、输出表、自然键、版本字段、禁止输出项。
- 每个 bounded proof 新增 DB audit：row count、natural key uniqueness、status distribution、hard fail count。
- 每个 release gate 新增 evidence audit：证明包存在、manifest 可读、conclusion 与 registry 状态一致。
- Pipeline phase 增加端到端测试：单模块失败不污染下游，resume 不重复写入，full-chain 只按 gate 顺序运行。

## 16. 前提假设

- 当前事实基线以 `Data foundation production baseline sealed`、`MALF v1.3 day formal-data bounded closeout 已通过`、
  `Alpha bounded proof 已通过` 和 `Signal bounded proof 已通过` 为准。
- MALF v1.4 是当前语义与操作边界权威包；day runtime sync 已通过，week/month proof 和 full build 仍需另开卡。
- 当前下一卡固定为 `Position freeze review reentry`，不是 Position construction。
- Data Foundation 是地基轨道，不进入策略主线排序。
- Pipeline 是编排与记录轨道，不进入业务主线排序。
- 不同时施工两个策略主线模块。
- `wave_core_state` 与 `system_state` 永远保持分离。
- `H:\Asteria-data` 放正式 DB，`H:\Asteria-temp` 放临时构建，`H:\Asteria-report` 放人读报告，`H:\Asteria-Validated` 放正式证据资产。
