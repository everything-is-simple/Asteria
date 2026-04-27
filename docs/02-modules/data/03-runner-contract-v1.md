# Data Foundation Runner Contract v1

日期：2026-04-27

状态：draft / foundation-contract / not frozen

## 1. 目的

本合同定义 Data Foundation 后续 runner 的命令边界、输入输出、幂等与断点规则。

本轮不实现 runner，只冻结未来 runner 应遵守的口径。

## 2. 目标 runner

| runner | 职责 |
|---|---|
| `scripts/data/run_raw_market_sync.py` | 原始行情同步与落地 |
| `scripts/data/run_market_meta_build.py` | 日历、标的、行业、宇宙、tradability 物化 |
| `scripts/data/run_market_base_day_build.py` | 日线基础价格线物化 |
| `scripts/data/run_market_base_week_build.py` | 周线基础价格线物化 |
| `scripts/data/run_market_base_month_build.py` | 月线基础价格线物化 |
| `scripts/data/run_data_audit.py` | Data Foundation 硬审计 |

## 3. 输入输出合同

### raw sync

输入：

```text
source config
vendor files or api response
target = H:\Asteria-data\raw_market.duckdb
working = H:\Asteria-temp\data\<run_id>\
```

输出：

```text
raw_market_sync_run
raw_market_source_file
raw_market_bar
raw_market_reject_audit
```

### meta build

输入：

```text
reference source files
validated mapping inputs
target = H:\Asteria-data\market_meta.duckdb
```

输出：

```text
trade_calendar
instrument_master
instrument_alias
industry_classification
universe_membership
tradability_fact
meta_run
```

### base build

输入：

```text
raw_market.duckdb
market_meta.duckdb
timeframe-specific build scope
target = H:\Asteria-data\market_base_{tf}.duckdb
```

输出：

```text
market_base_bar
market_base_latest
market_base_run
```

## 4. 运行模式

Data Foundation runner 至少必须支持：

| 模式 | 含义 |
|---|---|
| `bounded` | 小样本构建与最小验证 |
| `segmented` | 分段或分交易日范围构建 |
| `full` | 全量构建 |
| `resume` | 从 checkpoint 或上次中断点续跑 |
| `audit-only` | 只做硬审计，不写业务事实 |

## 5. 幂等与断点

每个 runner 必须满足：

| 能力 | 要求 |
|---|---|
| 幂等 | 同一输入、同一版本、同一 run scope 重跑结果一致 |
| checkpoint | 可记录处理到的源批次或时间范围 |
| replay scope | 可按 source batch、trade_date、symbol 范围重放 |
| reject isolation | 脏记录进入 reject audit，不污染正式事实 |

## 6. run ledger

每个 runner 都必须生成 run ledger，至少记录：

```text
run_id
runner_name
mode
scope_start
scope_end
status
schema_version
created_at
```

若消费上游输入，还必须记录：

```text
source_vendor
source_batch_id
input_snapshot
```

## 7. 路径边界

正式写入路径：

```text
H:\Asteria-data\*.duckdb
```

工作路径：

```text
H:\Asteria-temp\data\<run_id>\
```

报告与证据路径：

```text
H:\Asteria-report\data\<date>\
H:\Asteria-Validated\<asset-set>\
```

不得把缓存、working DB 或报告写入 repo 根目录。

## 8. 禁止项

Data Foundation runner 不得：

| 禁止项 | 原因 |
|---|---|
| 写入 MALF 或下游 DB | 地基层不回写业务模块 |
| 生成策略字段 | Data 不是策略层 |
| 读取交易结果来修正基础事实 | 交易结果不定义基础事实 |
| 绕过 `market_meta` 直接伪造统一 `symbol` | 映射必须可审计 |

## 9. 最小放行条件

未来 Data Foundation runner 放行至少要求：

| 门禁 | 要求 |
|---|---|
| bounded build | 小样本可重算、幂等 |
| source traceability | 正式事实可追溯到 source |
| calendar consistency | 日期和交易日历一致 |
| uniqueness | 自然键无冲突 |
| evidence | 构建与审计证据已落档 |
