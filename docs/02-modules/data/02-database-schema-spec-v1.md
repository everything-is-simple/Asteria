# Data Foundation Database Schema Spec v1

日期：2026-04-27

状态：draft / foundation-contract / not frozen

## 1. 目标拓扑

Data Foundation 目标正式库共五个：

| DB | 路径 | 定位 |
|---|---|---|
| `raw_market.duckdb` | `H:\Asteria-data\raw_market.duckdb` | 原始行情与同步审计 |
| `market_meta.duckdb` | `H:\Asteria-data\market_meta.duckdb` | 客观参考事实 |
| `market_base_day.duckdb` | `H:\Asteria-data\market_base_day.duckdb` | 日线基础价格线 |
| `market_base_week.duckdb` | `H:\Asteria-data\market_base_week.duckdb` | 周线基础价格线 |
| `market_base_month.duckdb` | `H:\Asteria-data\market_base_month.duckdb` | 月线基础价格线 |

本文件定义表族、自然键与字段口径，不等于可直接执行的物理 DDL。

## 2. raw_market.duckdb

### 2.1 表族

| 表 | 职责 |
|---|---|
| `raw_market_sync_run` | 同步与入库运行审计 |
| `raw_market_source_file` | 源文件或源批次登记 |
| `raw_market_bar` | 原始行情行 |
| `raw_market_reject_audit` | 被拒绝或脏记录审计 |
| `raw_schema_version` | schema 版本 |

当前最小 bootstrap 实现已落地 `raw_market_sync_run`、`raw_market_source_file`、`raw_market_bar`
和 `raw_schema_version`。`raw_market_reject_audit` 保持 schema contract，等待 reject isolation
卡进入实现。

### 2.2 自然键

| 表 | 自然键 |
|---|---|
| `raw_market_sync_run` | `sync_run_id` |
| `raw_market_source_file` | `source_vendor + source_batch_id + source_file_name` |
| `raw_market_bar` | `source_vendor + source_symbol + timeframe + bar_dt + price_line + source_revision` |
| `raw_market_reject_audit` | `reject_id` |
| `raw_schema_version` | `schema_version` |

TDX 离线 txt bootstrap 必须保留以下 source manifest 字段：

```text
source_path
source_size_bytes
source_mtime
source_content_hash
source_vendor
source_batch_id
source_revision
run_id
schema_version
```

## 3. market_meta.duckdb

### 3.1 表族

| 表 | 职责 |
|---|---|
| `trade_calendar` | 交易日历 |
| `instrument_master` | 标的主数据 |
| `instrument_alias` | 代码映射与别名 |
| `industry_classification` | 行业分类 |
| `universe_membership` | 宇宙成员关系 |
| `tradability_fact` | 客观可交易事实 |
| `meta_run` | meta build 审计 |
| `meta_schema_version` | schema 版本 |

### 3.2 自然键

| 表 | 自然键 |
|---|---|
| `trade_calendar` | `calendar_code + trade_date` |
| `instrument_master` | `instrument_id` |
| `instrument_alias` | `source_vendor + source_symbol + effective_date` |
| `industry_classification` | `instrument_id + industry_schema + effective_date` |
| `universe_membership` | `universe_name + instrument_id + effective_date` |
| `tradability_fact` | `instrument_id + trade_date + fact_name` |
| `meta_run` | `meta_run_id` |
| `meta_schema_version` | `schema_version` |

## 4. market_base_{day,week,month}.duckdb

三个 timeframe DB 结构同构，仅 `timeframe` 与构建来源不同。

### 4.1 表族

| 表 | 职责 |
|---|---|
| `market_base_bar` | 标准基础 bar |
| `market_base_latest` | 每个 symbol 当前最后一条正式 bar 指针 |
| `market_base_run` | base build 审计 |
| `market_base_dirty_scope` | 增量重算影响范围 |
| `market_base_schema_version` | schema 版本 |

### 4.2 自然键

| 表 | 自然键 |
|---|---|
| `market_base_bar` | `symbol + timeframe + bar_dt + price_line + adj_mode` |
| `market_base_latest` | `symbol + timeframe + price_line + adj_mode` |
| `market_base_run` | `base_run_id` |
| `market_base_dirty_scope` | `symbol + timeframe + adj_mode + run_id` |
| `market_base_schema_version` | `schema_version` |

## 5. 版本字段

正式表默认字段：

```text
run_id
schema_version
created_at
```

涉及来源追溯的表还必须记录：

```text
source_vendor
source_batch_id
source_revision
```

涉及映射或聚合的表还必须记录：

```text
mapping_version
calendar_version
```

## 6. 推荐字段簇

### 6.1 raw_market_bar

推荐字段簇：

```text
source_vendor
source_symbol
timeframe
bar_dt
trade_date
price_line
open_px
high_px
low_px
close_px
volume
amount
source_revision
run_id
schema_version
created_at
```

### 6.2 instrument_master

推荐字段簇：

```text
instrument_id
symbol
exchange_code
list_status
list_date
delist_date
currency_code
run_id
schema_version
created_at
```

### 6.3 market_base_bar

推荐字段簇：

```text
symbol
timeframe
bar_dt
trade_date
price_line
adj_mode
open_px
high_px
low_px
close_px
volume
amount
source_vendor
source_batch_id
mapping_version
calendar_version
run_id
schema_version
created_at
```

## 7. 写入边界

| DB | 写入边界 |
|---|---|
| `raw_market.duckdb` | 只允许 raw sync 与 reject audit 写入 |
| `market_meta.duckdb` | 只允许 meta build 写入 |
| `market_base_{tf}.duckdb` | 只允许对应 timeframe 的 base build 写入 |

MALF 及所有下游模块只能只读消费这些正式库。

## 8. 索引与唯一性要求

DuckDB 不以传统二级索引为主，但逻辑上必须保证：

| 约束 | 要求 |
|---|---|
| 自然键唯一 | 正式事实层不得冲突 |
| latest 单行性 | 每个 `symbol + timeframe + price_line + adj_mode` 仅一行最新指针 |
| 运行审计唯一 | 每次 run 必须有唯一 run ledger |
| 版本可追溯 | 任一正式事实必须能回指版本字段 |

## 9. 第一批建库优先级

与当前架构总图一致，Data Foundation 首批优先支持：

```text
market_meta.duckdb
market_base_day.duckdb
```

它们是 MALF day bounded proof 的直接上游输入契约。

首轮 `market_base_day` 默认把 `stock-day\Backward-Adjusted` 物化为：

```text
price_line = analysis_price_line
adj_mode = backward
```

`Non-Adjusted` 保留给未来 Trade execution price line，`Forward-Adjusted` 暂作为审计备用价格线。
