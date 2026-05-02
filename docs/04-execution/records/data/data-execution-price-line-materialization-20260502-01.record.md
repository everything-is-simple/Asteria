# Data Execution Price Line Materialization Record

日期：2026-05-02

run_id：`data-execution-price-line-materialization-20260502-01`

## 1. 执行内容

| 项 | 结果 |
|---|---|
| `stock-day/Non-Adjusted` live execution line materialization | passed |
| production audit hard check `execution_price_line_present` | passed |
| market_meta gap review | recorded / not built |

## 2. 物化结果

| 表面 | 结果 |
|---|---|
| `raw_market.duckdb` | 新增 `adj_mode = none` 共 `16,376,944` 行，`5,503` symbols |
| `market_base_day.duckdb` | 新增 `execution_price_line / none` 共 `16,376,944` 行，`5,503` symbols |
| `market_base_week.duckdb` | 保持 `analysis_price_line / backward` |
| `market_base_month.duckdb` | 保持 `analysis_price_line / backward` |

## 3. 当前放行

本卡只补齐 day execution price line。当前主线下一步仍是：

```text
Position freeze review reentry
```

`market_meta.duckdb`、Position / Trade / System 施工与 full-chain Pipeline 仍未放行。
