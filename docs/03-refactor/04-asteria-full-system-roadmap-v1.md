# Asteria 全系统重构 Roadmap / Master Todo v1

日期：2026-04-29

## 1. Summary

当前基线：`MALF day bounded proof` 与 `Alpha freeze review` 已通过；下一步只允许
`Alpha bounded proof build card`。

本路线图依据以下权威资产刷新：

```text
H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.md
H:\Asteria-Validated\Asteria-docs-code-20260428-214427.zip
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2.zip
```

深度研究报告中的 “机器可读门禁、统一 schema registry、模块 API 合同、pipeline ledger
运行时” 缺口已部分被 repo 后续治理实现补齐；尚未放行的是 pipeline runtime 与
全系统日更/断点续传运行时。

系统完成路径固定为：

```text
设计/契约冻结 -> bounded proof -> evidence -> release gate -> 下游授权
```

正式分三条轨道：

```text
Foundation Track:
Data Foundation -> feeds MALF only as source-fact infrastructure

Strategy Mainline:
MALF -> Alpha -> Signal -> Position -> Portfolio Plan -> Trade -> System Readout

Governance / Orchestration Track:
Governance controls gates
Pipeline schedules and records only
```

`Data Foundation` 不进入策略主线排序，不占主线施工位；`Pipeline` 不定义业务语义。

## 2. Phase 0: Governance Closure

- [x] 修正 `governance/module_gate_registry.toml`：把 MALF `next_card` 从 `malf_day_bounded_proof` 改为 `alpha_freeze_review`。
- [x] 增加治理检查：校验 gate ledger、execution conclusion、registry 的 current/next 状态一致。
- [x] 增加 evidence 完备性检查：当前 MALF day release 与 docs authority refresh 必须有 `card`、`record`、`evidence-index`、`conclusion`、report manifest、validated zip。
- [ ] 建立统一 release gate checklist：governance、ruff、format、mypy、pytest、DB audit、evidence audit 全部记录。
- [x] 通过后只授权 `Alpha freeze review`，不打开 Alpha 代码施工，也不打开任何下游施工。

## 3. Foundation Track: Data Foundation

- [ ] 保持 Data Foundation 定位：基础设施与 source-fact service，不是策略主线模块。
- [ ] 重审 Data 六件套，决定何时从 `foundation six-doc draft` 进入正式 freeze review。
- [ ] 冻结 raw market、market meta、market base day/week/month 的正式 schema 与自然键。
- [ ] 实现正式 Data builder 前，继续限制当前能力为 bounded bootstrap support。
- [ ] 正式 Data builder 必须支持 source manifest、run ledger、checkpoint、replay scope、audit summary。
- [ ] Data release 只放行“可供 MALF 消费的客观事实”，不产生 MALF/Alpha/Signal 语义。

## 4. Phase 1: Alpha Freeze Review

- [ ] 重审 Alpha 六件套，确认 Alpha 只读消费 `malf_wave_position` / `malf_wave_position_latest`。
- [ ] 冻结 Alpha 输入：MALF WavePosition、必要 Data Foundation 客观事实、alpha family 私有事实。
- [ ] 明确 Alpha 输出：alpha event、alpha score、alpha signal candidate。
- [ ] 明确禁止输出：position size、portfolio allocation、order intent。
- [ ] 冻结 `alpha_bof/tst/pb/cpb/bpb.duckdb` schema 与自然键。
- [ ] 写 Alpha build card，只允许 Alpha bounded proof。
- [x] Alpha freeze review 通过后，更新 gate ledger 与 registry。

## 5. Phase 2: Alpha Bounded Proof

- [ ] 实现 Alpha bounded runner，支持 `bounded`、`resume`、`audit-only`。
- [ ] 建立 Alpha run ledger、schema version、rule version、checkpoint、replay scope。
- [ ] 对至少一个 alpha family 跑通真实 bounded sample，再扩展到五个 family。
- [ ] 审计 Alpha 不回写 MALF、不制造 MALF 语义、不输出资金/订单。
- [ ] 产出 Alpha evidence 包与 conclusion。
- [ ] Release gate 通过后，只授权 `Signal freeze review`。

## 6. Phase 3: Signal Freeze + Bounded Proof

- [ ] 重审 Signal 六件套，确认 Signal 只聚合 Alpha 输出。
- [ ] 冻结 `signal.duckdb` schema：formal signal ledger、signal run、schema/rule version。
- [ ] 实现 Signal bounded runner，输入只来自已放行 Alpha ledgers。
- [ ] 审计 Signal 不做资金分配、不生成订单、不回写 Alpha/MALF。
- [ ] 产出 Signal evidence 与 release conclusion。
- [ ] Release gate 通过后，只授权 `Position freeze review`。

## 7. Phase 4: Position Freeze + Bounded Proof

- [ ] 重审 Position 六件套，确认 Position 把 formal signal 转为 position candidate / entry plan / exit plan。
- [ ] 冻结 `position.duckdb` schema、自然键、状态机、幂等写入规则。
- [ ] 实现 Position bounded runner 与 replay/checkpoint。
- [ ] 审计 Position 不做组合级资金裁决、不修改 Signal。
- [ ] 产出 Position evidence 与 release conclusion。
- [ ] Release gate 通过后，只授权 `Portfolio Plan freeze review`。

## 8. Phase 5: Portfolio Plan Freeze + Bounded Proof

- [ ] 重审 Portfolio Plan 六件套，冻结资金、容量、组合约束、准入/裁剪语义。
- [ ] 冻结 `portfolio_plan.duckdb` schema。
- [ ] 实现 bounded runner，输入只来自 Position candidates/plans。
- [ ] 审计 Portfolio Plan 不修改 Alpha/Signal/Position 历史语义。
- [ ] 产出 Portfolio Plan evidence 与 release conclusion。
- [ ] Release gate 通过后，只授权 `Trade freeze review`。

## 9. Phase 6: Trade Freeze + Bounded Proof

- [ ] 重审 Trade 六件套，冻结 order intent、execution line、fill ledger、rejection semantics。
- [ ] 冻结 `trade.duckdb` schema。
- [ ] 实现 bounded runner，输入只来自 Portfolio Plan。
- [ ] 审计 Trade 不产生策略评分、不修改组合历史裁决。
- [ ] 产出 Trade evidence 与 release conclusion。
- [ ] Release gate 通过后，只授权 `System Readout freeze review`。

## 10. Phase 7: System Readout Freeze + Bounded Proof

- [ ] 重审 System Readout 六件套，确认只读全链路 official ledgers。
- [ ] 冻结 `system.duckdb` schema：summary、audit snapshot、readout tables。
- [ ] 实现只读 bounded runner。
- [ ] 审计 System Readout 不触发业务重算、不回写任何上游模块。
- [ ] 产出 System evidence 与 release conclusion。
- [ ] Release gate 通过后，才允许 `Pipeline integration review`。

## 11. Phase 8: Pipeline Integration

- [ ] 在任何 Pipeline runtime 施工前，先确认当前 active card 明确授权 Pipeline freeze review。
- [ ] 重审 Pipeline 六件套，确认 Pipeline 只调度、记录、汇总状态，不定义业务语义。
- [ ] 冻结 `pipeline.duckdb` schema：pipeline_run、pipeline_step_run、module_gate_snapshot、build_manifest。
- [ ] 实现单模块调度。
- [ ] 实现全链路 dry-run。
- [ ] 实现全链路 bounded run。
- [ ] 审计 Pipeline 不绕过 module gate、不写业务表、不替模块解释字段。
- [ ] 产出 full-chain evidence 与 release conclusion。

## 12. Phase 9: Timeframe Expansion

- [ ] 在 day 主链稳定后，复制 MALF 到 week/month：core、lifespan、service 三库各自 proof。
- [ ] 扩展 Alpha/Signal 对 timeframe 字段的正式支持。
- [ ] 对 cross-timeframe 读取做 contract tests，避免下游自造 MALF 语义。
- [ ] 产出 week/month evidence 包。
- [ ] 更新 topology registry 与 module contracts。

## 13. Phase 10: Full System Release

- [ ] 建立 full rebuild card：从 Data Foundation official facts 输入 MALF，再沿策略主线跑到 System Readout。
- [ ] 建立 daily incremental card：source manifest、dirty queue/replay scope、checkpoint、audit summary。
- [ ] 运行 full rebuild proof。
- [ ] 运行 daily incremental proof。
- [ ] 运行恢复测试：中断后 resume，重复运行幂等。
- [ ] 生成 final release evidence：DB manifest、schema versions、rule versions、row counts、audit summaries、known limits。
- [ ] 标记系统达到 `v1 complete`。

## 14. Public Contracts

- 每个模块必须有六件套：authority design、semantic contract、database schema spec、runner contract、audit spec、build card。
- 每个正式 DB 必须有：run ledger、schema version、checkpoint/replay scope、audit summary。
- 每个 runner 至少支持：`bounded`、`resume`、`audit-only`；进入完整系统前补齐 `segmented/full/daily_incremental`。
- 每个 release 必须落档：`card.md`、`record.md`、`evidence-index.md`、`conclusion.md`、report manifest、validated zip。
- 下游只读上游正式 ledgers；禁止回写、禁止重定义上游字段语义。

## 15. Test Plan

- 每个 phase 必跑：`check_project_governance.py`、`ruff check`、`ruff format --check`、`mypy src`、`pytest`。
- 每个模块新增 contract tests：输入表、输出表、自然键、版本字段、禁止输出项。
- 每个 bounded proof 新增 DB audit：row count、natural key uniqueness、status distribution、hard fail count。
- 每个 release gate 新增 evidence audit：证明包存在、manifest 可读、conclusion 与 registry 状态一致。
- Pipeline phase 增加端到端测试：单模块失败不污染下游，resume 不重复写入，full-chain 只按 gate 顺序运行。

## 16. Assumptions

- 当前事实基线以 `MALF day bounded proof passed` 为准。
- 下一张卡固定为 `Alpha bounded proof build card`，不是无卡 Alpha 代码施工。
- Data Foundation 是地基轨道，不进入策略主线排序。
- Pipeline 是编排与记录轨道，不进入业务主线排序。
- 不同时施工两个策略主线模块。
- `wave_core_state` 与 `system_state` 永远保持分离。
- `H:\Asteria-data` 放正式 DB，`H:\Asteria-temp` 放临时构建，`H:\Asteria-report` 放人读报告，`H:\Asteria-Validated` 放正式证据资产。
