# Data Foundation Semantic Contract v1

日期：2026-05-02

状态：production-foundation released / execution day line live / market_meta future card

当前裁决：Data Foundation 生产级地基已放行四个正式库；`market_base_day.duckdb`
已 live 物化 `execution_price_line = none`。当前正式库为：
`raw_market.duckdb`、`market_base_day.duckdb`、`market_base_week.duckdb`、
`market_base_month.duckdb`。`market_meta.duckdb` 和 index/block 主线接入仍需后续卡。

## 1. 目的

本合同定义 Data Foundation 的输入、输出与字段语义边界，确保它只提供客观事实，不掺入任何策略解释。

## 2. 基本语义

```text
raw market = source-native observed facts
market meta = objective reference facts
market base = normalized consumable price lines
```

其中：

| 语义对象 | 含义 |
|---|---|
| `raw market` | 原始供应商或本地源的逐条事实，不重写其原始含义 |
| `market meta` | 日历、标的、行业、宇宙、可交易性等客观参考事实 |
| `market base` | 为主线模块消费而归一化的标准价格线，不携带策略判断 |

## 3. 输入合同

输入记录至少必须可表达：

```text
source_vendor
source_symbol
source_batch_id
timeframe
bar_dt or trade_date
price fields or meta fields
source_revision
```

缺失来源追溯字段的输入，不得写入正式 DB。

### 3.1 Legacy Lifespan 字段映射

首轮旧库导入采用固定字段映射：

| Legacy 字段 | Asteria 字段 | 说明 |
|---|---|---|
| `code` | `symbol` / `source_symbol` | 首轮不重写代码语义，保留原始代码为统一消费代码 |
| `trade_date` | `bar_dt` / `trade_date` | day/week/month 均沿用旧库交易日期键 |
| `adjust_method` | `adj_mode` | 首轮只接收 `backward` |
| `open/high/low/close` | `open_px/high_px/low_px/close_px` | 客观价格字段映射 |
| `volume/amount` | `volume/amount` | 客观成交字段映射 |
| `source_bar_nk` / `bar_nk` | `source_revision` 或 trace key | 用于追溯旧库来源行 |
| `first_seen_run_id` / `last_materialized_run_id` | source/build audit 字段 | 用于 run lineage，不进入策略语义 |

旧库 `index` / `block` 数据只登记审计可用性；不得在本合同下输入 MALF 首轮证明。

## 4. 输出合同

### raw_market

`raw_market` 只保留 source-native 事实与同步审计：

| 类型 | 允许语义 |
|---|---|
| 原始 bar | 来自供应商或本地源的原始行 |
| 同步记录 | 某次同步的开始、结束、成功、失败 |
| 文件注册 | 某个源文件或批次是否已入库 |
| 拒绝审计 | 被丢弃或不合规的原始记录 |

### market_meta

`market_meta` 只保留客观参考事实：

| 类型 | 允许语义 |
|---|---|
| 交易日历 | 哪天是交易日、哪天不是 |
| 标的主数据 | 标识、交易所、上市状态、代码映射 |
| 行业分类 | 客观分类与生效日期 |
| 宇宙成员 | 某宇宙在某日包含哪些标的 |
| 可交易事实 | 停牌、ST、涨跌停、上市未满期等客观约束 |

### market_base

`market_base_{day/week/month}` 只保留可消费基础价格线：

| 类型 | 允许语义 |
|---|---|
| 标准 bar | 归一化 open/high/low/close/volume/amount 等 |
| latest 指针 | 当前最后一条正式基础 bar |
| build 审计 | 某次 build 输入、输出与断点状态 |

## 5. 核心字段语义

| 字段 | 语义 |
|---|---|
| `symbol` | Asteria 统一消费代码 |
| `source_symbol` | 上游源代码，不等同于统一 `symbol` |
| `timeframe` | `day / week / month` |
| `trade_date` | 交易日口径日期 |
| `bar_dt` | bar 对应日期时间键 |
| `price_line` | 消费价格线：`analysis_price_line` 或 `execution_price_line` |
| `adj_mode` | 复权或价格归一模式 |
| `calendar_code` | 所属交易日历 |
| `fact_name` | 客观事实名，如 `is_suspended` |
| `fact_value` | 客观事实值 |

## 6. 允许表达与禁止表达

允许表达：

```text
price facts
calendar facts
instrument facts
industry facts
universe facts
tradability facts
build and source audit facts
```

禁止表达：

```text
wave_state
wave_position
alpha_score
signal_strength
position_size
portfolio_weight
order_intent
system_readout
```

## 7. 派生边界

Data Foundation 可以做的派生：

| 允许派生 | 条件 |
|---|---|
| 代码映射归一化 | 规则可审计、版本可追溯 |
| 价格线归一化 | 由客观 corporate action 或价格线规则驱动 |
| week / month 聚合 | 由已冻结的 base build 规则驱动 |
| tradability 客观事实整合 | 只整合客观来源，不做策略筛选 |

Data Foundation 不可以做的派生：

| 禁止派生 | 原因 |
|---|---|
| 结构波段标签 | 属于 MALF |
| 机会解释标签 | 属于 Alpha |
| 交易建议 | 属于下游业务模块 |
| 用成交结果回修历史行情 | 交易不是行情事实来源 |

## 8. 下游读取合同

| 下游 | 只读合同 |
|---|---|
| MALF | 仅读取 `market_base_{day/week/month}` 与必要 `market_meta` |
| Alpha | 仅读取客观宇宙、行业、可交易性等辅助事实 |
| Portfolio Plan | 仅读取客观容量与准入辅助事实 |
| Trade | 仅读取执行价格线与日历 |

Data Foundation 不向任何下游授予写回权。

## 8.1 价格线合同

| 价格线 | 固定来源 | 允许消费者 | 禁止用途 |
|---|---|---|---|
| `analysis_price_line` | `adj_mode = backward` | MALF / Alpha / Signal / Position 参考 | 真实成交、fill、现金结算 |
| `execution_price_line` | `adj_mode = none` | Position / Portfolio Plan / Trade | MALF 结构定义、Alpha 机会评分 |

后复权价格只服务连续结构分析。不复权价格才允许进入未来 Trade 的 order price、
fill price、成交金额和现金账本。

## 9. 版本与溯源合同

所有正式输出必须可追溯到：

```text
schema_version
run_id
created_at
source_vendor
source_batch_id
source_revision
```

若存在映射或聚合，还必须能追溯到：

```text
mapping_version
calendar_version
source_trade_dates
```
