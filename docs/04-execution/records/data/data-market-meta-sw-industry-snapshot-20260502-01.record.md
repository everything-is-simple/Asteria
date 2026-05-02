# Data Market Meta SW Industry Snapshot Record

日期：2026-05-02

run_id：`data-market-meta-sw-industry-snapshot-20260502-01`

## 1. 执行内容

| 项 | 结果 |
|---|---|
| source xlsx hash check | passed |
| source required columns | passed |
| source duplicate stock code check | passed |
| staging path | `H:\Asteria-temp\data\data-market-meta-sw-industry-snapshot-20260502-01\market_meta.duckdb` |
| formal promote path | `H:\Asteria-data\market_meta.duckdb` |
| production audit | passed |

## 2. 物化结果

| 项 | 行数 |
|---|---:|
| source total rows | 5,284 |
| source A 股 rows | 4,430 |
| matched formal Data instruments | 4,237 |
| formal `industry_classification` rows inserted | 4,237 |
| unmatched A 股 rows, report only | 193 |
| non-A-share rows, report only | 854 |
| formal Data instruments not in source snapshot | 1,266 |

## 3. 当前放行

本卡只放行 `sw2021_level3_snapshot` 当前行业快照：

```text
industry_schema = sw2021_level3_snapshot
effective_date = 2021-07-31
source_vendor = sw_industry_reference_xlsx
```

`effective_date` 仅按源文件名“截至7月末”推断，不声明为外部公告验证日期。
ST、停牌、真实上市/退市状态与历史行业沿革仍需后续参考源卡。
