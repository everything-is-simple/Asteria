# Data Foundation Runner Contract v1

日期：2026-05-02

状态：production-foundation released / execution day line materialized / market_meta minimal formalized

## 1. 目的

本合同定义 Data Foundation 后续正式 runner 的命令边界、输入输出、幂等与断点规则。

当前 `scripts/data/run_data_bootstrap.py` 已支持 bounded/full/audit-only/resume/daily_incremental
的 Data foundation 实现；其中 `stock / none / full` 已通过 DuckDB native CSV bulk path
正式物化到 live day execution line。`scripts/data/run_data_production_audit.py` 提供
release audit，并已将 `market_meta.duckdb` 纳入 hard check。
这不授权 Pipeline runtime 或下游施工。

## 2. 目标 runner

| runner | 职责 |
|---|---|
| `scripts/data/run_raw_market_sync.py` | 原始行情同步与落地 |
| `scripts/data/run_market_meta_build.py` | 日历、标的、行业、宇宙、tradability 物化 |
| `scripts/data/run_market_base_day_build.py` | 日线基础价格线物化 |
| `scripts/data/run_market_base_week_build.py` | 周线基础价格线物化 |
| `scripts/data/run_market_base_month_build.py` | 月线基础价格线物化 |
| `scripts/data/run_data_audit.py` | Data Foundation 硬审计 |

当前最小可执行入口：

| runner | 职责 |
|---|---|
| `scripts/data/run_data_bootstrap.py` | 从 TDX 离线 txt 执行 raw + market_base_day bounded bootstrap，并生成 dirty scope 与 checkpoint |
| `scripts/data/run_legacy_data_import.py` | 从旧版 Lifespan raw/base DuckDB 导入 `stock / backward / day-week-month` 到 working DB；正式 promote 需后续审计卡 |
| `scripts/data/run_market_meta_build.py` | 从正式 raw/base DB 推导最小 `market_meta.duckdb`，先 staging 后 audit/promote |

## 3. 输入输出合同

### raw sync

输入：

```text
source config
vendor files or api response
target = H:\Asteria-data\raw_market.duckdb
working = H:\Asteria-temp\data\<run_id>\
```

首轮 source config 固定支持：

```text
source_root = H:\tdx_offline_Data
asset_type = stock / index / block
adj_mode = backward / forward / none / all
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
H:\Asteria-data\raw_market.duckdb
H:\Asteria-data\market_base_day.duckdb
H:\Asteria-data\market_base_week.duckdb
H:\Asteria-data\market_base_month.duckdb
working = H:\Asteria-temp\data\<run_id>\
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
meta_schema_version
meta_source_manifest
```

当前 `run_market_meta_build.py` 支持 `full / bounded / audit-only`。`full` 与 `bounded`
均先写 staging DB，审计通过后 promote 到正式路径；`audit-only` 只审计 existing
`market_meta.duckdb`，不写业务事实。行业、ST、停牌和真实上市/退市状态仍是
reference source gap，不得由 runner 推断或伪造。

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

### legacy Lifespan import

输入：

```text
raw_root = H:\Lifespan-data\raw
base_root = H:\Lifespan-data\base
asset_type = stock
adj_mode = backward
timeframes = day, week, month
working = H:\Asteria-temp\data\<run_id>\
```

输出：

```text
H:\Asteria-temp\data\<run_id>\raw_market.duckdb
H:\Asteria-temp\data\<run_id>\market_base_day.duckdb
H:\Asteria-temp\data\<run_id>\market_base_week.duckdb
H:\Asteria-temp\data\<run_id>\market_base_month.duckdb
```

该 runner 的首轮职责是导入旧库 source facts 并证明 working DB 可审计；不得直接写
`H:\Asteria-data`，正式 promote 由单独 evidence 卡执行。

## 4. 运行模式

Data Foundation runner 至少必须支持：

| 模式 | 含义 |
|---|---|
| `bounded` | 小样本构建与最小验证 |
| `segmented` | 分段或分交易日范围构建 |
| `full` | 全量构建 |
| `resume` | 从 checkpoint 或上次中断点续跑 |
| `audit-only` | 只做硬审计，不写业务事实 |
| `daily_incremental` | 按 source manifest diff 跳过未变文件，变化文件进入 dirty scope |

`scripts/data/run_data_bootstrap.py` 的公共参数必须包含：

```text
--source-root
--target-root
--temp-root
--asset-type
--adj-mode
--mode
--run-id
--start-dt
--end-dt
--symbol-limit
```

### 4.1 当前最小 bootstrap 模式边界

`scripts/data/run_data_bootstrap.py` 当前已经接受上述 `--mode` 公共参数，但各模式的
生产级语义尚未全部落地：

| 模式 | 当前行为 | 后续正式 runner 要求 |
|---|---|---|
| `bounded` | 已用于小样本 raw + market_base_day bootstrap | 保持小样本可重算、幂等、可审计 |
| `resume` | 已支持复用 completed checkpoint，避免重复 promote 已完成 run | 扩展为 batch / source / date-window 级断点续跑 |
| `audit-only` | 已返回只审计摘要，不写业务事实 | 扩展为正式 Data hard audit，不写正式事实 |
| `segmented` | 参数已接受，当前仍走最小 bootstrap 路径 | 后续实现日期窗口和 symbol batch 分片语义 |
| `full` | 可按当前 Data foundation 合同构建全量 source scope；`market_meta` 已支持正式 full build | 后续扩展 index / block |
| `daily_incremental` | 已按 source hash/size 执行跳过或重算 | 后续接入 pipeline manifest |

因此，当前实现可证明 Data bounded bootstrap support 已存在，并已支撑
`malf-day-bounded-proof-20260428-01` 通过；但不得被解释为正式 `segmented` /
`full` Data Foundation builder 已经放行。

## 5. 幂等与断点

每个 runner 必须满足：

| 能力 | 要求 |
|---|---|
| 幂等 | 同一输入、同一版本、同一 run scope 重跑结果一致 |
| checkpoint | 可记录处理到的源批次或时间范围 |
| replay scope | 可按 source batch、trade_date、symbol 范围重放 |
| reject isolation | 脏记录进入 reject audit，不污染正式事实 |

当前 checkpoint 位置：

```text
H:\Asteria-temp\data\<run_id>\checkpoint.json
```

已完成 run 以 `resume` 重入时不得重复 promote 已完成的 batch。未完成 checkpoint
重入时，已记录的 processed source scope 必须跳过，剩余 source scope 继续处理。

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

TDX source manifest 至少记录：

```text
source_path
source_size_bytes
source_mtime
source_content_hash
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

还不得：

| 禁止项 | 原因 |
|---|---|
| 直接复制 `H:\Lifespan-data\astock_lifespan_alpha` 下游库 | 旧下游只能作为旁证，不能越过新主线门禁 |
| 让 MALF 直接读 TDX txt 或旧 `malf_day.duckdb` | MALF 只能消费新 Data Foundation 的正式 market_base |

## 9. 最小放行条件

Data Foundation runner 当前生产级地基放行要求：

| 门禁 | 要求 |
|---|---|
| bounded build | 小样本可重算、幂等 |
| source traceability | 正式事实可追溯到 source |
| calendar consistency | 日期和交易日历一致 |
| uniqueness | 自然键无冲突 |
| evidence | 构建与审计证据已落档 |

当前 release 结论已推进到 `data-market-meta-formalization-20260502-01`；后续扩展
index/block、参考源行业/ST/停牌/上市退市或全链路 Pipeline 必须另开卡。
