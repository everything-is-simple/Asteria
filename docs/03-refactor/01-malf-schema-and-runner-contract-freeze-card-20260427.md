# 01 MALF Schema 与 Runner Contract 冻结卡

日期：2026-04-27

## 1. 当前卡位

| 项 | 值 |
|---|---|
| card_id | `01-malf-schema-and-runner-contract-freeze-card-20260427` |
| active_module | `malf` |
| card_type | design / schema / runner / audit freeze |
| implementation_allowed | no |
| formal_db_write_allowed | no |

## 2. 目标

把 MALF 三份终稿映射为 Asteria day 级别三库规格：

```text
malf_core_day.duckdb
malf_lifespan_day.duckdb
malf_service_day.duckdb
```

## 3. 权威输入

| 输入 | 路径 |
|---|---|
| MALF 三份终稿 | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2` |
| Asteria 主线图 | `docs/01-architecture/00-mainline-authoritative-map-v1.md` |
| Asteria DB 拓扑 | `docs/01-architecture/01-database-topology-v1.md` |
| MALF schema spec | `docs/02-modules/03-malf-schema-runner-audit-spec-v1.md` |

## 4. 本卡只允许做什么

| 允许项 |
|---|
| 审阅并修订 MALF schema spec |
| 补充 MALF runner contract |
| 补充 MALF audit spec |
| 明确 bounded proof 样本要求 |
| 决定是否冻结本卡 |

## 5. 本卡禁止做什么

| 禁止项 |
|---|
| 迁移旧 MALF engine |
| 创建正式 `H:\Asteria-data\malf_*.duckdb` |
| 修改 Alpha / Signal / Position / Portfolio / Trade |
| 启动全量 build |
| 把旧系统字段原样搬入新 schema |

## 6. 冻结条件

| 条件 | 状态 |
|---|---|
| Core 表族字段完整 | draft |
| Lifespan 表族字段完整 | draft |
| Service WavePosition 字段完整 | draft |
| 自然键定义完整 | draft |
| Runner build modes 定义完整 | draft |
| 硬审计清单完整 | draft |
| 首轮 bounded proof 范围明确 | draft |

## 7. 冻结后下一卡

冻结后下一张卡：

```text
02-malf-day-bounded-proof-implementation-card-20260427
```

下一卡才允许：

| 允许项 |
|---|
| 建立 MALF day 三库 bootstrap |
| 实现 bounded source adapter |
| 实现 Core bounded build |
| 实现 Lifespan bounded build |
| 实现 Service WavePosition bounded build |
| 实现 hard audit |

## 8. 当前裁决

本卡当前状态：

```text
draft
```

还不能开始代码施工。下一步是人工/系统审阅 `docs/02-modules/03-malf-schema-runner-audit-spec-v1.md`，确认是否冻结。

