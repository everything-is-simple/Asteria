# Data Formal Promotion Evidence Record

日期：2026-05-02

run_id：`data-formal-promotion-evidence-20260502-01`

## 1. Inputs

- `H:\Asteria-temp\data\data-legacy-import-runner-working-build-20260502-01`
- `docs/04-execution/records/data/data-legacy-import-runner-working-build-20260502-01.conclusion.md`

## 2. Formal Outputs

| DB | path |
|---|---|
| raw | `H:\Asteria-data\raw_market.duckdb` |
| base day | `H:\Asteria-data\market_base_day.duckdb` |
| base week | `H:\Asteria-data\market_base_week.duckdb` |
| base month | `H:\Asteria-data\market_base_month.duckdb` |

## 3. Row Counts

| scope | rows |
|---|---:|
| raw stock backward all timeframes | 20,628,416 |
| base day | 16,348,113 |
| base week | 3,453,967 |
| base month | 826,336 |

## 4. Audit Result

| check | result |
|---|---:|
| hard_fail_count | 0 |
| raw duplicate groups | 0 |
| base duplicate groups | 0 |
| latest duplicate groups | 0 |
| forbidden strategy fields | 0 |

## 5. Boundary

本卡只放行首轮 `stock / backward / day-week-month` Data source-fact DB。完整 Data
Foundation full build、market_meta 和 index/block 主线接入仍需后续卡。
