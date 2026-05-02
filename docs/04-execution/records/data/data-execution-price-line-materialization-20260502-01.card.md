# Data Execution Price Line Materialization Card

日期：2026-05-02

状态：`passed`

## 1. 目标

把 `H:\tdx_offline_Data\stock-day\Non-Adjusted` 正式物化为 live
`execution_price_line / none`，写入：

```text
H:\Asteria-data\raw_market.duckdb
H:\Asteria-data\market_base_day.duckdb
```

同时保留 `market_meta.duckdb` 为 future card，不在本卡施工。

## 2. 允许范围

| 项 | 裁决 |
|---|---|
| Data bootstrap / audit 代码更新 | 允许 |
| live `raw_market.duckdb` 与 `market_base_day.duckdb` execution line 物化 | 允许 |
| Data 六件套、gate ledger、conclusion index、API contract 校正 | 允许 |
| repo 内执行四件套与外部 evidence | 允许 |

## 3. 禁止范围

| 项 | 裁决 |
|---|---|
| 创建 `market_meta.duckdb` | 禁止，后续另开卡 |
| week/month execution line 施工 | 禁止 |
| Position / Trade / System 施工 | 禁止 |
| Pipeline runtime 或 `pipeline.duckdb` | 禁止 |
