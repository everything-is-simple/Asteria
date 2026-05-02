# Data Production Release Closeout Card

日期：2026-05-02

状态：`passed`

## 1. 目标

把现有四个正式 Data DB 从首轮 formal promotion 底座推进为生产级 Data Foundation：

```text
raw_market.duckdb
market_base_day.duckdb
market_base_week.duckdb
market_base_month.duckdb
```

本卡冻结 MALF -> System 的数据输入矩阵，补齐 `analysis_price_line = backward` 与
`execution_price_line = none` 的边界，并实现 Data foundation 的 daily incremental、
checkpoint/resume 和 release audit。

## 2. 允许范围

| 项 | 裁决 |
|---|---|
| Data 六件套更新 | 允许 |
| Data API contract / topology / historical ledger registry | 允许 |
| Data runner 最小增量能力 | 允许 |
| Data release audit | 允许 |
| repo 内执行四件套与外部 evidence | 允许 |

## 3. 禁止范围

| 项 | 裁决 |
|---|---|
| 创建 `market_meta.duckdb` | 禁止，后续另开卡 |
| Position / Trade / System 施工 | 禁止 |
| Pipeline runtime 或 `pipeline.duckdb` | 禁止 |
| 把后复权价当真实成交价 | 禁止 |
| 迁移旧下游业务语义 | 禁止 |
