# Data Foundation Production Baseline Seal Record

日期：2026-05-02

run_id：`data-foundation-production-baseline-seal-20260502-01`

## 1. 执行内容

| 项 | 结果 |
|---|---|
| DB rebuild | not executed |
| live DB read-only review | passed |
| Data production audit | passed |
| governance state sync | passed |
| Data 六件套状态 | production baseline sealed |

## 2. 封印表面

| DB / table | 当前事实 |
|---|---:|
| `raw_market.duckdb` | exists |
| `market_base_day.duckdb` analysis rows | 16,348,113 |
| `market_base_day.duckdb` execution rows | 16,376,944 |
| `market_base_week.duckdb` rows | 3,453,967 |
| `market_base_month.duckdb` rows | 826,336 |
| `trade_calendar` rows | 8,684 |
| `instrument_master` rows | 5,503 |
| `tradability_fact` rows | 16,376,944 |
| `industry_classification` rows | 4,237 |

## 3. 当前边界

Data 已封为主线输入底座，但不声明 ST、停牌、真实上市/退市状态、历史行业沿革、
完整证券主数据或 index/block 主线接入已经齐全。
