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

当前唯一允许进入下一施工卡的模块：

```text
MALF
```

Alpha、Signal 和 Position 为 pre-gate six-doc draft，不允许施工。Portfolio Plan 到 Pipeline 仍为 pending placeholder，不允许施工。

## 2. 模块状态表

| 顺序 | 模块 | 文档状态 | 冻结状态 | 是否允许施工 | 文档位置 | 说明 |
|---:|---|---|---|---:|---|---|
| 0 | Data Foundation | delivered draft | not frozen | 否 | `docs/02-modules/01-data-foundation-design-v1.md` | 地基输入契约，非策略主线 |
| 1 | MALF | delivered six-doc set | frozen | 是 | `docs/02-modules/malf/` | 唯一可进入下一施工卡的主线模块 |
| 2 | Alpha | pre-gate six-doc draft | not frozen | 否 | `docs/02-modules/alpha/` | 等 MALF WavePosition 放行后重新审阅并冻结 |
| 3 | Signal | pre-gate six-doc draft | not frozen | 否 | `docs/02-modules/signal/` | 等 Alpha 放行后重新审阅并冻结 |
| 4 | Position | pre-gate six-doc draft | not frozen | 否 | `docs/02-modules/position/` | 等 Signal 放行后重新审阅并冻结 |
| 5 | Portfolio Plan | pending placeholder | not frozen | 否 | `docs/02-modules/portfolio_plan/` | 等 Position 放行 |
| 6 | Trade | pending placeholder | not frozen | 否 | `docs/02-modules/trade/` | 等 Portfolio Plan 放行 |
| 7 | System Readout | pending placeholder | not frozen | 否 | `docs/02-modules/system_readout/` | 等 Trade 放行 |
| 8 | Pipeline | pending placeholder | not frozen | 否 | `docs/02-modules/pipeline/` | 只编排，不抢业务施工位 |

## 3. 文档交付清单

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
| Portfolio Plan | `docs/02-modules/portfolio_plan/00-pending-module-gate-v1.md` | not frozen |
| Trade | `docs/02-modules/trade/00-pending-module-gate-v1.md` | not frozen |
| System Readout | `docs/02-modules/system_readout/00-pending-module-gate-v1.md` | not frozen |
| Pipeline | `docs/02-modules/pipeline/00-pending-module-gate-v1.md` | not frozen |

## 4. 交付资产

正式可交付压缩包：

```text
H:\Asteria-Validated\Asteria-mainline-module-docs-v1.zip
```

该 zip 是主线模块文档交付包，不是运行证据包，也不是 DuckDB 产物。

## 5. 下一张施工卡

下一张施工卡必须仍然只针对 MALF：

```text
MALF day bounded proof
```

目标：

| 内容 | 要求 |
|---|---|
| Core runner | bounded proof first |
| Lifespan runner | 基于 Core 输出 |
| Service runner | 发布 WavePosition |
| Audit runner | Core + Lifespan + Service 硬审计 |
| Evidence | 证据落入 `H:\Asteria-report` 或 `H:\Asteria-Validated` |

## 6. 施工锁

在 MALF day bounded proof 未通过前，不允许：

| 禁止项 |
|---|
| 迁移旧 Alpha / Signal / Position / Portfolio / Trade / System 代码 |
| 创建 Alpha / Signal / Position / Portfolio / Trade / System 正式 DB |
| 让下游模块补充自有语义 |
| 建立 pipeline 全链路 |
| 让 Alpha、Signal、Portfolio、Trade、System 写回 MALF |
| 合并 `wave_core_state` 与 `system_state` |

## 7. MALF 放行定义

MALF day 首轮放行标准：

| 门禁 | 要求 |
|---|---|
| Design | MALF 三份终稿已引用并映射到 Asteria 六件套 |
| Schema | day 三库表族自然键冻结 |
| Bounded Build | 小样本可重算、幂等 |
| Invariant Audit | 硬规则全通过 |
| Alpha Contract | WavePosition 字段满足 Alpha 只读消费 |
| Evidence | 证据落入 `H:\Asteria-report` 或 `H:\Asteria-Validated` |
