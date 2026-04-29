# Asteria 模块门禁账本 v1

日期：2026-04-29

权威依据：

```text
H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.md
H:\Asteria-Validated\Asteria-docs-code-20260428-214427.zip
H:\Asteria-Validated\Asteria-docs-code-20260429-130309.zip
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2.zip
```

`214427` 快照是 2026-04-28 docs/code 基线；`130309` 快照是三天重构成果的
当前系统 docs/code 归档。快照之后的 repo HEAD 事实以执行记录、
conclusion index、governance registry 和 Validated release evidence 为准。

## 1. 当前状态

当前已完成施工对象：

```text
refactor-governance
```

当前已交付主线模块文档索引：

```text
docs/02-modules/04-mainline-module-delivery-index-v1.md
```

当前唯一冻结主线模块：

```text
MALF
```

当前最新通过门禁：

```text
MALF day bounded proof
```

当前允许进入下一执行卡的模块：

```text
Alpha bounded proof build card
```

当前唯一已通过 bounded proof 的主线模块：

```text
MALF day
```

Alpha 已通过 freeze review 并冻结六件套，但仍不允许直接施工。Signal、Position、
Portfolio Plan、Trade、System Readout 和 Pipeline 为 pre-gate six-doc draft，不允许施工。
当前只允许写 Alpha bounded proof build card。

## 2. 模块状态表

| 顺序 | 模块 | 文档状态 | 冻结状态 | 是否允许施工 | 文档位置 | 说明 |
|---:|---|---|---|---:|---|---|
| 0 | Data Foundation | foundation six-doc draft | not frozen | 否 | `docs/02-modules/data/` | 地基输入契约，非策略主线，不占主线施工位 |
| 1 | MALF | delivered six-doc set / day proof passed | frozen | 否 | `docs/02-modules/malf/` | day bounded proof 已通过；week/month 或 full build 需另开卡 |
| 2 | Alpha | frozen six-doc set / freeze review passed | frozen | 否 | `docs/02-modules/alpha/` | 只允许 Alpha bounded proof build card，不允许直接代码施工 |
| 3 | Signal | pre-gate six-doc draft | not frozen | 否 | `docs/02-modules/signal/` | 等 Alpha 放行后重新审阅并冻结 |
| 4 | Position | pre-gate six-doc draft | not frozen | 否 | `docs/02-modules/position/` | 等 Signal 放行后重新审阅并冻结 |
| 5 | Portfolio Plan | pre-gate six-doc draft | not frozen | 否 | `docs/02-modules/portfolio_plan/` | 等 Position 放行后重新审阅并冻结 |
| 6 | Trade | pre-gate six-doc draft | not frozen | 否 | `docs/02-modules/trade/` | 等 Portfolio Plan 放行后重新审阅并冻结 |
| 7 | System Readout | pre-gate six-doc draft | not frozen | 否 | `docs/02-modules/system_readout/` | 等 Trade 放行后重新审阅并冻结 |
| 8 | Pipeline | pre-gate six-doc draft | not frozen | 否 | `docs/02-modules/pipeline/` | 只编排和记录，不抢业务施工位 |

## 3. 文档交付清单

Data Foundation 本轮六件套草案：

| 文档 | 状态 |
|---|---|
| `docs/02-modules/data/00-authority-design-v1.md` | draft / foundation-contract / not frozen |
| `docs/02-modules/data/01-semantic-contract-v1.md` | draft / foundation-contract / not frozen |
| `docs/02-modules/data/02-database-schema-spec-v1.md` | draft / foundation-contract / not frozen |
| `docs/02-modules/data/03-runner-contract-v1.md` | draft / foundation-contract / not frozen |
| `docs/02-modules/data/04-audit-spec-v1.md` | draft / foundation-contract / not frozen |
| `docs/02-modules/data/05-build-card-v1.md` | draft / foundation-contract / bounded-bootstrap-support |

Data Foundation 模块整体仍为 `not frozen`。`bounded-bootstrap-support` 只记录当前已有
TDX txt 到 raw/base day 的最小输入准备能力，不授权正式 Data Foundation builder、正式
Data DuckDB 建库或下游主线施工。

MALF 冻结文档与当前 proof 状态：

| 文档 | 状态 |
|---|---|
| `docs/02-modules/malf/00-authority-design-v1.md` | frozen / day bounded proof passed |
| `docs/02-modules/malf/01-semantic-contract-v1.md` | frozen / day bounded proof passed |
| `docs/02-modules/malf/02-database-schema-spec-v1.md` | frozen / day bounded proof passed |
| `docs/02-modules/malf/03-runner-contract-v1.md` | frozen / day bounded proof passed |
| `docs/02-modules/malf/04-audit-spec-v1.md` | frozen / day bounded proof passed |
| `docs/02-modules/malf/05-build-card-v1.md` | frozen / superseded by passed day proof |
| `docs/02-modules/malf/06-implementation-traceability-annex-v1.md` | annex / traceability only / no semantic amendment |

下游本轮 pre-gate / 占位文档：

| 模块 | 占位文档 | 状态 |
|---|---|---|
| Alpha | `docs/02-modules/alpha/00-authority-design-v1.md` | frozen / freeze review passed |
| Alpha | `docs/02-modules/alpha/01-semantic-contract-v1.md` | frozen / freeze review passed |
| Alpha | `docs/02-modules/alpha/02-database-schema-spec-v1.md` | frozen / freeze review passed |
| Alpha | `docs/02-modules/alpha/03-runner-contract-v1.md` | frozen / freeze review passed |
| Alpha | `docs/02-modules/alpha/04-audit-spec-v1.md` | frozen / freeze review passed |
| Alpha | `docs/02-modules/alpha/05-build-card-v1.md` | frozen / freeze review passed / superseded by next build card |
| Signal | `docs/02-modules/signal/00-authority-design-v1.md` | draft / pre-gate / not frozen |
| Signal | `docs/02-modules/signal/01-semantic-contract-v1.md` | draft / pre-gate / not frozen |
| Signal | `docs/02-modules/signal/02-database-schema-spec-v1.md` | draft / pre-gate / not frozen |
| Signal | `docs/02-modules/signal/03-runner-contract-v1.md` | draft / pre-gate / not frozen |
| Signal | `docs/02-modules/signal/04-audit-spec-v1.md` | draft / pre-gate / not frozen |
| Signal | `docs/02-modules/signal/05-build-card-v1.md` | draft / pre-gate / not frozen |
| Position | `docs/02-modules/position/00-authority-design-v1.md` | draft / pre-gate / not frozen |
| Position | `docs/02-modules/position/01-semantic-contract-v1.md` | draft / pre-gate / not frozen |
| Position | `docs/02-modules/position/02-database-schema-spec-v1.md` | draft / pre-gate / not frozen |
| Position | `docs/02-modules/position/03-runner-contract-v1.md` | draft / pre-gate / not frozen |
| Position | `docs/02-modules/position/04-audit-spec-v1.md` | draft / pre-gate / not frozen |
| Position | `docs/02-modules/position/05-build-card-v1.md` | draft / pre-gate / not frozen |
| Portfolio Plan | `docs/02-modules/portfolio_plan/00-authority-design-v1.md` | draft / pre-gate / not frozen |
| Portfolio Plan | `docs/02-modules/portfolio_plan/01-semantic-contract-v1.md` | draft / pre-gate / not frozen |
| Portfolio Plan | `docs/02-modules/portfolio_plan/02-database-schema-spec-v1.md` | draft / pre-gate / not frozen |
| Portfolio Plan | `docs/02-modules/portfolio_plan/03-runner-contract-v1.md` | draft / pre-gate / not frozen |
| Portfolio Plan | `docs/02-modules/portfolio_plan/04-audit-spec-v1.md` | draft / pre-gate / not frozen |
| Portfolio Plan | `docs/02-modules/portfolio_plan/05-build-card-v1.md` | draft / pre-gate / not frozen |
| Trade | `docs/02-modules/trade/00-authority-design-v1.md` | draft / pre-gate / not frozen |
| Trade | `docs/02-modules/trade/01-semantic-contract-v1.md` | draft / pre-gate / not frozen |
| Trade | `docs/02-modules/trade/02-database-schema-spec-v1.md` | draft / pre-gate / not frozen |
| Trade | `docs/02-modules/trade/03-runner-contract-v1.md` | draft / pre-gate / not frozen |
| Trade | `docs/02-modules/trade/04-audit-spec-v1.md` | draft / pre-gate / not frozen |
| Trade | `docs/02-modules/trade/05-build-card-v1.md` | draft / pre-gate / not frozen |
| System Readout | `docs/02-modules/system_readout/00-authority-design-v1.md` | draft / pre-gate / not frozen |
| System Readout | `docs/02-modules/system_readout/01-semantic-contract-v1.md` | draft / pre-gate / not frozen |
| System Readout | `docs/02-modules/system_readout/02-database-schema-spec-v1.md` | draft / pre-gate / not frozen |
| System Readout | `docs/02-modules/system_readout/03-runner-contract-v1.md` | draft / pre-gate / not frozen |
| System Readout | `docs/02-modules/system_readout/04-audit-spec-v1.md` | draft / pre-gate / not frozen |
| System Readout | `docs/02-modules/system_readout/05-build-card-v1.md` | draft / pre-gate / not frozen |
| Pipeline | `docs/02-modules/pipeline/00-authority-design-v1.md` | draft / pre-gate / not frozen |
| Pipeline | `docs/02-modules/pipeline/01-semantic-contract-v1.md` | draft / pre-gate / not frozen |
| Pipeline | `docs/02-modules/pipeline/02-database-schema-spec-v1.md` | draft / pre-gate / not frozen |
| Pipeline | `docs/02-modules/pipeline/03-runner-contract-v1.md` | draft / pre-gate / not frozen |
| Pipeline | `docs/02-modules/pipeline/04-audit-spec-v1.md` | draft / pre-gate / not frozen |
| Pipeline | `docs/02-modules/pipeline/05-build-card-v1.md` | draft / pre-gate / not frozen |

## 4. 交付资产

正式可交付压缩包：

```text
H:\Asteria-Validated\Asteria-mainline-module-docs-v1.zip
H:\Asteria-Validated\Asteria-docs-code-20260428-214427.zip
H:\Asteria-Validated\Asteria-docs-code-20260429-130309.zip
H:\Asteria-Validated\Asteria-docs-authority-refresh-20260429-01.zip
```

这些 zip 是文档/治理快照或权威刷新归档，不是 DuckDB 产物。运行证据必须另有
report closeout、manifest、repo execution record 和 Validated release evidence。

## 5. MALF Day Bounded Proof 放行记录

MALF day bounded proof 已通过。

| 项 | 值 |
|---|---|
| run_id | `malf-day-bounded-proof-20260428-01` |
| source DB | `H:\Asteria-temp\data-bootstrap-smoke-all-2\market_base_day.duckdb` |
| sample scope | `day / 2024-01-01..2024-12-31 / symbol_limit=4` |
| Core DB | `H:\Asteria-data\malf_core_day.duckdb` |
| Lifespan DB | `H:\Asteria-data\malf_lifespan_day.duckdb` |
| Service DB | `H:\Asteria-data\malf_service_day.duckdb` |
| closeout | `H:\Asteria-report\malf\2026-04-28\malf-day-bounded-proof-20260428-01\closeout.md` |
| validated evidence | `H:\Asteria-Validated\Asteria-malf-day-bounded-proof-20260428-01.zip` |
| execution conclusion | `docs/04-execution/records/malf/malf-day-bounded-proof-20260428-01.conclusion.md` |
| hard audit | `hard_fail_count = 0` |

MALF day 放行后打开的 Alpha freeze review 已通过。Alpha、Signal、Position、Portfolio
Plan、Trade、System Readout、Pipeline 仍不允许直接施工。

## 6. Alpha Freeze Review 放行记录

Alpha freeze review 已通过。

| 项 | 值 |
|---|---|
| run_id | `alpha-freeze-review-20260429-01` |
| source DB | `H:\Asteria-data\malf_service_day.duckdb` |
| review scope | Alpha 六件套 / MALF WavePosition 只读契约 / module API contracts |
| report dir | `H:\Asteria-report\alpha\2026-04-29\alpha-freeze-review-20260429-01` |
| closeout | `H:\Asteria-report\alpha\2026-04-29\alpha-freeze-review-20260429-01\closeout.md` |
| validated evidence | `H:\Asteria-Validated\Asteria-alpha-freeze-review-20260429-01.zip` |
| execution conclusion | `docs/04-execution/records/alpha/alpha-freeze-review-20260429-01.conclusion.md` |
| hard review | `hard_fail_count = 0` |

Alpha freeze review 只冻结 Alpha 六件套，不创建正式 Alpha DB，不授权直接代码施工。

## 7. 下一张施工卡

下一张施工卡必须先针对 Alpha bounded proof build card，不得直接进入无卡施工：

```text
Alpha bounded proof build card
```

目标：

| 内容 | 要求 |
|---|---|
| Build Scope | 只允许 Alpha bounded proof，不打开 full build |
| MALF Contract Boundary | 继续确认 Alpha 只读消费 WavePosition，不回写 MALF |
| Formal DB Permission | 只有 build card 明确授权后才允许创建 working / formal Alpha DB |
| Downstream Lock | 不打开 Signal / Position / Portfolio / Trade / System 施工 |

## 8. 施工锁

在 Alpha bounded proof build card 未打开前，不允许：

| 禁止项 |
|---|
| 迁移旧 Alpha / Signal / Position / Portfolio / Trade / System 代码 |
| 创建 Alpha / Signal / Position / Portfolio / Trade / System 正式 DB |
| 让下游模块补充自有语义 |
| 建立 pipeline 全链路 |
| 让 Alpha、Signal、Portfolio、Trade、System 写回 MALF |
| 合并 `wave_core_state` 与 `system_state` |

## 9. MALF 放行定义

MALF day 首轮放行标准：

| 门禁 | 要求 |
|---|---|
| Design | MALF 三份终稿已引用并映射到 Asteria 六件套 |
| Schema | day 三库表族自然键冻结 |
| Bounded Build | 小样本可重算、幂等 |
| Invariant Audit | 硬规则全通过 |
| Alpha Contract | WavePosition 字段满足 Alpha 只读消费 |
| Evidence | 证据落入 `H:\Asteria-report` 或 `H:\Asteria-Validated` |
