# Asteria Mainline Module Completion Gap Audit v1

日期：2026-05-06

状态：governance audit / gate transition reflected / no runtime construction

## 1. Purpose

本文件把 Asteria 当前主线模块按三条线对齐：

```text
设计是否冻结
实现是否存在
正式 DuckDB / evidence 是否已经放行
```

它回答“哪些已经完全实现、哪些需要加强、哪些根本没有”。本次更新只反映
Position freeze review re-entry 的文档门禁结论，不修改任何 runner、schema 或正式
DuckDB。

## 2. Completion Matrix

| 模块 | 设计 | 实现 | 正式 DB / 证据 | 裁决 |
|---|---|---|---|---|
| Data Foundation | 已封版 | 当前 baseline 已实现 | `raw_market / market_base day-week-month / market_meta` 已存在 | 当前地基可用；后续只能 maintenance card 扩展 |
| MALF | day v1.4 权威已同步 | day runtime 已实现 | `malf_core_day / malf_lifespan_day / malf_service_day` 已存在 | day 可用；week/month/full-market 仍需补 |
| Alpha | 六件套冻结 | bounded runner 已实现 | 5 个 Alpha family DB 已存在 | bounded 完成；full/segmented production 需另开卡 |
| Signal | 六件套冻结 | bounded runner 已实现 | `signal.duckdb` 已存在 | bounded 完成；full build 权限仍未打开 |
| Position | 六件套 freeze review passed / design contract frozen | 无 runtime | 无 `position.duckdb` | 当前暂停施工；先完成上游完整性总控裁决 |
| Portfolio Plan | 草案 | 无 runtime | 无 `portfolio_plan.duckdb` | 依赖 Position，不插队 |
| Trade | 草案 | 无 runtime | 无 `trade.duckdb` | 依赖 Portfolio Plan，不插队 |
| System Readout | 草案 | 无 runtime | 无 `system.duckdb` | 依赖 Trade，不插队 |
| Pipeline | 草案 | 无 runtime | 无 `pipeline.duckdb` | 最后做，只调度记录，不定义业务语义 |

## 3. Evidence Anchors

本审计依据以下 repo-local truth：

| 证据 | 用途 |
|---|---|
| `governance/module_gate_registry.toml` | 当前 active module、allow_build、formal DB permission、next card |
| `governance/database_topology_registry.toml` | 目标 DB 拓扑、released / blocked DB module 口径 |
| `docs/04-execution/00-conclusion-index-v1.md` | 已登记 execution conclusion |
| `docs/01-architecture/01-database-topology-v1.md` | 目标 25 DuckDB 拓扑与当前状态说明 |
| `H:\Asteria-data` local DuckDB files | 物理 DB 存在性与当前样本行数观察 |

2026-05-06 本地 `H:\Asteria-data` 观察到：

| DB group | 物理状态 |
|---|---|
| Data | `raw_market.duckdb`、`market_base_day.duckdb`、`market_base_week.duckdb`、`market_base_month.duckdb`、`market_meta.duckdb` 存在 |
| MALF day | `malf_core_day.duckdb`、`malf_lifespan_day.duckdb`、`malf_service_day.duckdb` 存在 |
| Alpha | `alpha_bof.duckdb`、`alpha_tst.duckdb`、`alpha_pb.duckdb`、`alpha_cpb.duckdb`、`alpha_bpb.duckdb` 存在 |
| Signal | `signal.duckdb` 存在 |
| Downstream / Pipeline | `position.duckdb`、`portfolio_plan.duckdb`、`trade.duckdb`、`system.duckdb`、`pipeline.duckdb` 不存在 |

物理存在不等于 full release。`signal.duckdb` 是 Signal bounded proof evidence；
它不授权 Signal full build、Position construction 或 full-chain Pipeline。

## 4. What Needs Work

优先级固定如下：

| 优先级 | 补齐项 | 原因 |
|---|---|---|
| P0 | `data reference target maintenance scope` | 已通过；已冻结 Data reference closeout 必补范围 |
| P1 | `data reference target maintenance closeout` | 当前 repo next card；按 P0 冻结范围补 Data reference facts、DB 表面和审计 |
| P2 | `malf week bounded proof build` -> `malf month bounded proof build` | MALF day clean 但 week/month formal DBs 不存在 |
| P3 | `alpha production builder hardening` -> `signal production builder hardening` | bounded proof 已过，但 segmented/full production builder 仍未放行 |
| P4 | `upstream pre-position release decision` | 只有上游修补结论齐备后，才裁定是否恢复 Position bounded proof |
| P5 | `Position bounded proof build card` | 只有上游 release decision 允许后，才可实现 `src/asteria/position`、`scripts/position` 与 `position.duckdb` |
| P6 | Portfolio -> Trade -> System -> Pipeline | 严格按主线顺序，Pipeline 最后做编排与记录 |

所有后续 DB builder 必须遵守：

```text
docs/00-governance/04-database-build-runner-standard-v1.md
```

也就是说：staging、audit、promote、checkpoint/resume、batch ledger、自然键或 replay
scope 替换都必须是正式能力，不再允许一次性手工建库作为长期口径。

## 5. Non-Goals

本审计不声明：

```text
Position 已可施工
Portfolio / Trade / System 已可施工
Pipeline runtime 已打开
Alpha / Signal full production 已放行
MALF week/month proof 已执行
全系统 v1 complete
```

当前真实下一步已推进为：

```text
data reference target maintenance closeout / prepared / Position construction suspended
```
