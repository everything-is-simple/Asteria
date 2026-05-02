# Data Market Meta Formalization Card

日期：2026-05-02

状态：`passed`

## 1. 目标

按可证事实优先口径正式化：

```text
H:\Asteria-data\market_meta.duckdb
```

本卡只从当前正式 `raw_market.duckdb` 与 `market_base_day/week/month.duckdb`
推导客观元数据，不伪造行业、ST、停牌、真实上市/退市等缺少可靠来源的参考事实。

## 2. 允许范围

| 项 | 裁决 |
|---|---|
| Data meta schema / builder / runner | 允许 |
| `market_meta.duckdb` staging build 与 formal promote | 允许 |
| Data production audit hard check 扩展 | 允许 |
| Data 六件套、registry、execution records 与 evidence | 允许 |

## 3. 禁止范围

| 项 | 裁决 |
|---|---|
| 行业、ST、停牌、真实上市/退市事实伪造 | 禁止 |
| MALF / Alpha / Signal / Position 语义修改 | 禁止 |
| Position construction 或下游施工 | 禁止 |
| Pipeline runtime 或 `pipeline.duckdb` | 禁止 |
