# MALF Authority Design v1

日期：2026-04-27

状态：frozen

## 1. 模块定义

MALF 是 Asteria 第一主线模块，负责把 Data Foundation 提供的基础行情事实转化为市场结构事实、波段生命统计位置和下游只读服务接口。

MALF 全称：

```text
Market Lifespan Framework
```

## 2. 权威来源

MALF 的唯一语义权威为：

```text
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2.zip
```

| 权威文档 | 本模块承接范围 |
|---|---|
| `MALF_01_Core_Definitions_Theorems_v1_3.md` | pivot、structure primitive、wave、break、transition、candidate |
| `MALF_02_Lifespan_Stats_Definitions_Theorems_v1_2.md` | new-count、no-new-span、rank、life-state、position quadrant |
| `MALF_03_System_Service_Interface_v1_2.md` | WavePosition 与 Alpha-facing interface |
| `MALF_00_Three_Documents_Bridge_v1_2.md` | Core、Lifespan、Service 的关系 |

## 3. 模块只回答什么

| 问题 | MALF 是否回答 |
|---|---:|
| 当前结构 wave 是什么 | 是 |
| wave 是否 alive 或 terminated | 是 |
| 系统是否处于 transition | 是 |
| 波段推进次数与停滞跨度 | 是 |
| 当前 lifespan 位置和象限 | 是 |
| Alpha 能否稳定只读消费结构位置 | 是 |

## 4. 模块不回答什么

| 禁止输出 | 归属模块 |
|---|---|
| 买入、卖出、看多、看空 | Alpha / Signal |
| 仓位大小、入场计划、退出计划 | Position |
| 组合资金与容量裁决 | Portfolio Plan |
| 订单与成交 | Trade |
| 全链路读出与运行摘要 | System Readout |

## 5. 输入

MALF 第一施工对象只读取 day 级别基础行情：

```text
H:\Asteria-data\market_base_day.duckdb
```

Data Foundation 仍是地基服务，不属于策略主线模块。

## 6. 输出

MALF 按 timeframe 拆为三库：

| 层 | day DB | 职责 |
|---|---|---|
| Core | `malf_core_day.duckdb` | 结构事实 |
| Lifespan | `malf_lifespan_day.duckdb` | 统计位置 |
| Service | `malf_service_day.duckdb` | WavePosition 服务接口 |

正式路径：

```text
H:\Asteria-data\malf_core_day.duckdb
H:\Asteria-data\malf_lifespan_day.duckdb
H:\Asteria-data\malf_service_day.duckdb
```

## 7. 状态与数据流

```mermaid
flowchart TD
    A[market_base_day bars] --> B[MALF Core]
    B --> C[MALF Lifespan Stats]
    C --> D[MALF Service]
    D --> E[WavePosition]
    E --> F[Alpha readonly consumer]
```

```mermaid
stateDiagram-v2
    [*] --> alive
    alive --> terminated: break
    terminated --> transition: open transition
    transition --> alive: candidate confirmed as new wave
```

## 8. 核心表族

| DB | 表族 |
|---|---|
| `malf_core_day` | `malf_pivot_ledger`, `malf_structure_ledger`, `malf_wave_ledger`, `malf_break_ledger`, `malf_transition_ledger`, `malf_candidate_ledger`, `malf_core_run`, `malf_schema_version` |
| `malf_lifespan_day` | `malf_lifespan_snapshot`, `malf_lifespan_profile`, `malf_sample_version`, `malf_rule_version`, `malf_lifespan_run` |
| `malf_service_day` | `malf_wave_position`, `malf_wave_position_latest`, `malf_service_run`, `malf_interface_audit` |

## 9. 上下游边界

上游：

```text
Data Foundation -> market_base_day
```

下游：

```text
Alpha -> readonly WavePosition
```

Alpha、Signal、Position、Portfolio Plan、Trade、System Readout 均不得写回 MALF。

## 10. 上线门禁

MALF day 首轮放行必须满足：

| 门禁 | 要求 |
|---|---|
| Design | 三份 MALF 终稿已映射到 Asteria 文档 |
| Schema | day 三库表族、自然键、版本字段冻结 |
| Runner | bounded proof / segmented / full / resume 语义冻结 |
| Audit | Core、Lifespan、Service 硬审计冻结 |
| Evidence | 构建证据落入 `H:\Asteria-report` 或 `H:\Asteria-Validated` |
