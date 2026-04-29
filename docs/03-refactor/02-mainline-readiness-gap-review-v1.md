# Asteria 主线准备度缺口审查 v1

日期：2026-04-29

## 1. 审查目的

本审查文档用于把当前 Asteria 从 `Data Foundation` 到 `System Readout`，以及
`Pipeline` 编排层的准备度一次性拉平，回答以下四个问题：

```text
文档是否齐
正式 DB / evidence 是否存在
是否允许施工
下一步是否与主线一致
```

本文件是审查产物，不改写门禁状态，不替代：

```text
docs/03-refactor/00-module-gate-ledger-v1.md
docs/02-modules/04-mainline-module-delivery-index-v1.md
governance/module_gate_registry.toml
```

## 2. 权威依据

本轮审查依据：

| 证据来源 | 用途 |
|---|---|
| `H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.md` | 治理、主线、数据、编排四个剖切面 |
| `H:\Asteria-Validated\Asteria-docs-code-20260428-214427.zip` | docs/code 快照基线 |
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2` | MALF 语义权威目录 |
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2.zip` | MALF 语义权威 zip |
| `docs/04-execution/records/malf/malf-day-bounded-proof-20260428-01.conclusion.md` | MALF day proof 放行结论 |
| `docs/04-execution/00-conclusion-index-v1.md` | 执行结论索引 |
| `governance/module_gate_registry.toml` | 机器可读 next gate |

`214427` 快照之后的变化不得用旧 zip 覆盖；必须由 repo HEAD、执行记录、governance
registry 与新的 Validated 归档补齐。

## 3. 开场判断

当前事实已经从 2026-04-27 的 “准备 MALF day bounded proof” 推进到：

```text
MALF day bounded proof passed
```

同时，深度研究报告提出的四个关键治理缺口已经部分补齐：

| 缺口 | 当前状态 |
|---|---|
| 机器可读门禁 | 已有 `module_gate_registry.toml` 与 governance checker |
| 统一 DB / topology registry | 已有 `database_topology_registry.toml` |
| 模块 API 合同 | 已有 `governance/module_api_contracts/*.toml` |
| pipeline ledger 运行时 | 仍未冻结、未施工 |

因此当前主矛盾不再是 “MALF proof 尚未形成”，而是：

```text
只允许 Alpha freeze review；禁止 Alpha 代码施工与下游越级施工。
```

## 4. 主矩阵

| 模块 | 角色定位 | 文档状态 | DB / evidence 状态 | 当前阻塞 | 下一步 |
|---|---|---|---|---|---|
| Data Foundation | 地基层 / source-fact 服务 / 非策略主线 | foundation six-doc draft / not frozen | bounded bootstrap support 已服务 MALF day；完整 Data 五库未冻结 | 不是当前主线施工位；完整 Data builder 未放行 | 保持 foundation contract，未来另开 Data freeze review |
| MALF | 主线结构事实 / lifespan / WavePosition 服务 | frozen / day bounded proof passed | day 三库已由 release evidence 证明；week/month 未放行 | day 已通过；扩大到 week/month/full build 需另开卡 | 不继续扩大 MALF；转入 Alpha freeze review |
| Alpha | 机会解释层 | pre-gate six-doc draft / freeze review next | 正式 Alpha DB 未建 | freeze review 尚未 passed | 当前唯一允许动作：Alpha freeze review |
| Signal | 正式 signal 聚合层 | pre-gate six-doc draft / not frozen | `signal.duckdb` 未建 | Alpha 未 released | 等 Alpha release 后重审并冻结 |
| Position | 持仓候选 / 进出场计划层 | pre-gate six-doc draft / not frozen | `position.duckdb` 未建 | Signal 未 released | 等 Signal release 后重审并冻结 |
| Portfolio Plan | 组合约束 / 准入 / 目标暴露层 | pre-gate six-doc draft / not frozen | `portfolio_plan.duckdb` 未建 | Position 未 released | 等 Position release 后重审并冻结 |
| Trade | 订单意图 / 执行 / 成交账本层 | pre-gate six-doc draft / not frozen | `trade.duckdb` 未建 | Portfolio Plan 未 released | 等 Portfolio Plan release 后重审并冻结 |
| System Readout | 全链路只读汇总 / 审计快照层 | pre-gate six-doc draft / not frozen | `system.duckdb` 未建 | Trade 未 released | 等 Trade release 后重审并冻结 |
| Pipeline | 编排层 / 运行记录层 / 非业务语义模块 | pre-gate six-doc draft / not frozen | `pipeline.duckdb` runtime 未冻结 | 当前卡位不授权 Pipeline freeze 或全链路 | 等明确 Pipeline freeze review 卡，不抢 Alpha 卡位 |

## 5. 关键缺口

### 5.1 当前仍缺

| 缺口 | 说明 |
|---|---|
| Alpha freeze review 结论 | 当前只允许 review，不允许直接施工 |
| Pipeline runtime | 深度研究报告要求的 pipeline ledger 运行时尚未落地 |
| full release checklist | 仍需统一记录 governance、ruff、format、mypy、pytest、DB audit、evidence audit |
| daily incremental runtime | 日更、dirty scope、checkpoint、resume 仍是后续系统级目标 |
| week/month MALF proof | day 通过不自动放行 week/month |

### 5.2 当前已经不是缺口

| 曾经缺口 | 当前状态 |
|---|---|
| MALF day release evidence | 已由 `malf-day-bounded-proof-20260428-01` 通过 |
| WavePosition 可供 Alpha 只读审阅 | 已成为 Alpha freeze review 前置事实 |
| release conclusion 落档 | 已登记到 execution records 与 conclusion index |
| 关键 Validated 资产引用 | 已由 docs authority refresh 门禁检查 |

## 6. 当前唯一下一步

当前唯一与门禁账本、交付索引、数据库拓扑、执行结论和 Validated 资产链同时一致的下一步是：

```text
Alpha freeze review
```

该步骤只允许：

| 允许项 | 裁决 |
|---|---|
| 重审 Alpha 六件套 | 允许 |
| 核对 Alpha 只读消费 WavePosition | 允许 |
| 核对 Alpha 不写回 MALF | 允许 |
| 裁决 Alpha 是否可冻结 | 允许 |

该步骤不允许：

| 禁止项 | 裁决 |
|---|---|
| 创建正式 Alpha DuckDB | 禁止 |
| 迁移旧 Alpha engine | 禁止 |
| 运行 Signal / Position / Portfolio / Trade / System | 禁止 |
| 建立 pipeline 全链路 | 禁止 |
| 修改 MALF 语义或回写 MALF | 禁止 |

## 7. 结论

当前 Asteria 已经越过 MALF day bounded proof 的关键门槛，但尚未进入 Alpha 实现。

系统准备度可概括为：

```text
MALF day released for review consumption.
Alpha freeze review is next.
Everything downstream remains locked.
Pipeline records only after explicit authorization.
```

后续任何正式施工都必须从 Alpha freeze review 的 `passed` 结论和新的 Alpha build card 开始。
