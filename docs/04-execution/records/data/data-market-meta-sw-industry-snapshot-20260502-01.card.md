# Data Market Meta SW Industry Snapshot Card

日期：2026-05-02

状态：`passed`

## 1. 目标

本卡只把 validated 申万行业分类 xlsx 中，能匹配当前正式
`market_meta.duckdb.instrument_master` 的 A 股申万 2021 当前行业快照写入：

```text
H:\Asteria-data\market_meta.duckdb.industry_classification
```

正式 run_id：

```text
data-market-meta-sw-industry-snapshot-20260502-01
```

## 2. 允许范围

| 项 | 裁决 |
|---|---|
| 申万当前行业快照 xlsx 解析 | 允许 |
| `industry_classification` staged update 与 formal promote | 允许 |
| Data production audit 行业 source policy 扩展 | 允许 |
| Data 六件套、registry、execution records 与 evidence 同步 | 允许 |

## 3. 禁止范围

| 项 | 裁决 |
|---|---|
| ST、停牌、真实上市/退市事实伪造 | 禁止 |
| 历史行业沿革正式写入 | 禁止 |
| `.HK/.N/.O` 等非当前 Data 股票宇宙写入 | 禁止 |
| MALF / Alpha / Signal / Position 语义修改 | 禁止 |
| Position construction 或下游施工 | 禁止 |
