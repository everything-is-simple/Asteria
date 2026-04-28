# Asteria 模块门禁账本 v1

日期：2026-04-27

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

当前允许进入下一评审卡的模块：

```text
Alpha freeze review
```

当前唯一已通过 bounded proof 的主线模块：

```text
MALF day
```

Alpha、Signal、Position、Portfolio Plan、Trade、System Readout 和 Pipeline 为 pre-gate six-doc draft，不允许施工。
Alpha 只允许进入 freeze review，不允许直接施工。

## 2. 模块状态表

| 顺序 | 模块 | 文档状态 | 冻结状态 | 是否允许施工 | 文档位置 | 说明 |
|---:|---|---|---|---:|---|---|
| 0 | Data Foundation | foundation six-doc draft | not frozen | 否 | `docs/02-modules/data/` | 地基输入契约，非策略主线，不占主线施工位 |
| 1 | MALF | delivered six-doc set | frozen | 是 | `docs/02-modules/malf/` | 唯一可进入下一施工卡的主线模块 |
| 2 | Alpha | pre-gate six-doc draft | not frozen | 否 | `docs/02-modules/alpha/` | 等 MALF WavePosition 放行后重新审阅并冻结 |
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

MALF 本轮冻结文档：

| 文档 | 状态 |
|---|---|
| `docs/02-modules/malf/00-authority-design-v1.md` | frozen |
| `docs/02-modules/malf/01-semantic-contract-v1.md` | frozen |
| `docs/02-modules/malf/02-database-schema-spec-v1.md` | frozen |
| `docs/02-modules/malf/03-runner-contract-v1.md` | frozen |
| `docs/02-modules/malf/04-audit-spec-v1.md` | frozen |
| `docs/02-modules/malf/05-build-card-v1.md` | frozen |

下游本轮 pre-gate / 占位文档：

| 模块 | 占位文档 | 状态 |
|---|---|---|
| Alpha | `docs/02-modules/alpha/00-authority-design-v1.md` | draft / pre-gate / not frozen |
| Alpha | `docs/02-modules/alpha/01-semantic-contract-v1.md` | draft / pre-gate / not frozen |
| Alpha | `docs/02-modules/alpha/02-database-schema-spec-v1.md` | draft / pre-gate / not frozen |
| Alpha | `docs/02-modules/alpha/03-runner-contract-v1.md` | draft / pre-gate / not frozen |
| Alpha | `docs/02-modules/alpha/04-audit-spec-v1.md` | draft / pre-gate / not frozen |
| Alpha | `docs/02-modules/alpha/05-build-card-v1.md` | draft / pre-gate / not frozen |
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
```

该 zip 是主线模块文档交付包，不是运行证据包，也不是 DuckDB 产物。

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

MALF day 放行后，只授权 Alpha freeze review。Alpha、Signal、Position、Portfolio
Plan、Trade、System Readout、Pipeline 仍不允许施工。

## 6. 下一张施工卡

下一张施工卡必须先针对 Alpha freeze review，不得直接进入 Alpha 代码施工：

```text
Alpha freeze review
```

目标：

| 内容 | 要求 |
|---|---|
| MALF Contract Review | 确认 Alpha 只读消费 WavePosition，不回写 MALF |
| Alpha Six-doc Review | 基于已放行 WavePosition 重审 Alpha 六件套 |
| Freeze Decision | 只在 review 通过后更新 Alpha 冻结状态 |
| Build Card | 若 Alpha 冻结，再写下一张 Alpha 施工卡 |

## 7. 施工锁

在 Alpha freeze review 未通过前，不允许：

| 禁止项 |
|---|
| 迁移旧 Alpha / Signal / Position / Portfolio / Trade / System 代码 |
| 创建 Alpha / Signal / Position / Portfolio / Trade / System 正式 DB |
| 让下游模块补充自有语义 |
| 建立 pipeline 全链路 |
| 让 Alpha、Signal、Portfolio、Trade、System 写回 MALF |
| 合并 `wave_core_state` 与 `system_state` |

## 8. MALF 放行定义

MALF day 首轮放行标准：

| 门禁 | 要求 |
|---|---|
| Design | MALF 三份终稿已引用并映射到 Asteria 六件套 |
| Schema | day 三库表族自然键冻结 |
| Bounded Build | 小样本可重算、幂等 |
| Invariant Audit | 硬规则全通过 |
| Alpha Contract | WavePosition 字段满足 Alpha 只读消费 |
| Evidence | 证据落入 `H:\Asteria-report` 或 `H:\Asteria-Validated` |
