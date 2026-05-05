# MALF v1.4 Core 运行同步评审证据索引

run_id: `malf-v1-4-core-runtime-sync-review-20260503-01`

prepared_card_date: 2026-05-03

execution_date: 2026-05-04

status: `只读评审已执行 / 运行同步未打开`

## 1. Repo 执行文件

| 资产 | 证据作用 |
|---|---|
| `docs/04-execution/records/malf/malf-v1-4-core-runtime-sync-review-20260503-01.card.md` | 准备态运行同步评审卡与范围边界 |
| `docs/04-execution/records/malf/malf-v1-4-core-runtime-sync-review-20260503-01.record.md` | 评审执行记录 |
| `docs/04-execution/records/malf/malf-v1-4-core-runtime-sync-review-20260503-01.conclusion.md` | 评审结论与允许的下一步动作 |

## 2. 权威证据

| 资产 | 证据作用 |
|---|---|
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4` | 当前 MALF v1.4 权威定义包 |
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4.zip` | 当前 validated 的 MALF v1.4 权威归档 |
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4\MALF_01_Core_Definitions_Theorems_v1_4.md` | bar-level break 与 Core 语义定义 |
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4\MALF_01B_Core_Operational_Boundary_Rules_v1_4.md` | O1/O2/O3/O4/O7 操作边界规则 |
| `docs/04-execution/records/malf/malf-v1-4-core-operational-boundary-authority-sync-20260503-01.conclusion.md` | 证明 v1.4 authority sync 已完成，且没有宣称运行证明 |

## 3. 当前 runtime 证据保留情况

| 资产 | 证据作用 |
|---|---|
| `docs/04-execution/records/malf/malf-v1-3-formal-rebuild-closeout-20260502-01.conclusion.md` | 当前 MALF day formal-data bounded 运行结论 |
| `docs/04-execution/records/malf/malf-v1-3-formal-rebuild-closeout-20260502-01.evidence-index.md` | 当前 MALF day formal-data bounded 运行证据索引 |
| `H:\Asteria-data\malf_core_day.duckdb` | 本次用于核验 schema surface 的 live MALF Core day DB |
| `H:\Asteria-data\malf_lifespan_day.duckdb` | live MALF Lifespan day DB，本次未重建 |
| `H:\Asteria-data\malf_service_day.duckdb` | live MALF Service day DB，本次未重建 |

## 4. 实现层证据

| 资产 | 证据作用 |
|---|---|
| `src/asteria/malf/core_engine.py` | 当前 Core event 与 structure 实现 |
| `src/asteria/malf/schema.py` | 当前 MALF Core/Lifespan/Service schema bootstrap |
| `src/asteria/malf/contracts.py` | 当前 `MalfDayRequest` 合同 |
| `src/asteria/malf/bootstrap.py` | 当前 runner 持久化与 run ledger 写入逻辑 |

## 5. 治理证据

| 资产 | 证据作用 |
|---|---|
| `README.md` | 当前权威状态与允许的下一步动作 |
| `docs/00-governance/00-asteria-refactor-charter-v1.md` | 主线与模块施工规则 |
| `docs/01-architecture/00-mainline-authoritative-map-v1.md` | MALF 边界与下游锁定关系 |
| `docs/01-architecture/01-database-topology-v1.md` | 正式 DB 拓扑与当前 MALF day DB 状态 |
| `docs/03-refactor/00-module-gate-ledger-v1.md` | 当前模块门禁状态 |
| `docs/04-execution/00-conclusion-index-v1.md` | 对本次 review-only 结论做登记，但不打开 MALF build |
| `governance/module_gate_registry.toml` | 当前 allowed next card；本次评审未更新 |

## 6. 非证据项

本次评审不提供 v1.4 运行证明、schema migration、formal DB rebuild、
week/month proof、downstream construction 或 full-chain pipeline 的证据。
