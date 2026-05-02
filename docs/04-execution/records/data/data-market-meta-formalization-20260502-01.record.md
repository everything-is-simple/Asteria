# Data Market Meta Formalization Record

日期：2026-05-02

run_id：`data-market-meta-formalization-20260502-01`

## 1. 执行内容

| 项 | 结果 |
|---|---|
| `market_meta.duckdb` schema bootstrap | passed |
| full build staging path | `H:\Asteria-temp\data\data-market-meta-formalization-20260502-01\market_meta.duckdb` |
| formal promote path | `H:\Asteria-data\market_meta.duckdb` |
| production audit | passed |

## 2. 物化结果

| 表 | 行数 |
|---|---:|
| `trade_calendar` | 8,684 |
| `instrument_master` | 5,503 |
| `instrument_alias` | 16,513 |
| `universe_membership` | 5,503 |
| `tradability_fact` | 16,376,944 |
| `industry_classification` | 0 |
| `meta_source_manifest` | 4 |

## 3. 当前放行

本卡只放行可从正式 raw/base DB 推导的最小客观事实。当前主线下一步仍是：

```text
Position freeze review reentry
```

行业、ST、停牌、真实上市/退市状态与完整证券主数据仍需后续参考源卡。
