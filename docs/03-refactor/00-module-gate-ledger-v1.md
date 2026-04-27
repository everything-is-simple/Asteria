# Asteria 模块门禁账本 v1

日期：2026-04-27

## 1. 当前状态

当前已完成施工对象：

```text
refactor-governance
```

当前唯一活跃设计卡：

```text
01-malf-schema-and-runner-contract-freeze-card-20260427
```

## 2. 模块状态表

| 顺序 | 模块 | 当前状态 | 是否允许施工 | 说明 |
|---:|---|---|---:|---|
| 0 | Data Foundation | `draft` | 否 | 先冻结输入契约，不作为第一主线施工 |
| 1 | MALF | `design-card-draft` | 否 | schema / runner / audit 冻结卡已创建，未冻结 |
| 2 | Alpha | `pending` | 否 | 等 MALF WavePosition 放行 |
| 3 | Signal | `pending` | 否 | 等 Alpha 放行 |
| 4 | Position | `pending` | 否 | 等 Signal 放行 |
| 5 | Portfolio Plan | `pending` | 否 | 等 Position 放行 |
| 6 | Trade | `pending` | 否 | 等 Portfolio Plan 放行 |
| 7 | System Readout | `pending` | 否 | 等 Trade 放行 |
| 8 | Pipeline | `pending` | 否 | 只做编排，不抢业务模块施工位 |

## 3. 今日完成目标

| 项 | 状态 |
|---|---|
| 建立 Asteria 根文档入口 | done |
| 明确 `data` 非策略主线 | done |
| 明确主线模块顺序 | done |
| 明确 DuckDB 目标拓扑 | done |
| 明确单模块施工门禁 | done |
| 启动 MALF schema spec | done |

## 4. 下一张卡

当前设计卡：

```text
01-malf-schema-and-runner-contract-freeze-card-20260427
```

目标：

| 内容 | 要求 |
|---|---|
| MALF day 三库 schema | `malf_core_day / malf_lifespan_day / malf_service_day` |
| Core 表族 | pivot / structure / wave / break / transition / candidate |
| Lifespan 表族 | snapshot / profile / sample / rule |
| Service 表族 | wave_position / latest / audit |
| Runner contract | bounded proof first, full build later |
| Audit spec | Core + Lifespan + Service 不变量 |

## 5. 施工锁

在下一张卡未冻结前，不允许：

| 禁止项 |
|---|
| 迁移旧 MALF engine |
| 创建正式 MALF DuckDB |
| 修改 Alpha |
| 修改 Position / Portfolio / Trade |
| 建立 pipeline 全链路 |

## 6. 放行定义

MALF day 首轮放行标准：

| 门禁 | 要求 |
|---|---|
| Design | 三份 MALF 终稿已引用并映射到 Asteria schema |
| Schema | day 三库表族自然键冻结 |
| Bounded Build | 小样本可重算、幂等 |
| Invariant Audit | 硬规则全通过 |
| Alpha Contract | WavePosition 字段满足 Alpha 只读消费 |
| Evidence | 证据落入 `H:\Asteria-report` 或 `H:\Asteria-Validated` |
