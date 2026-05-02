# Data Execution Price Line Materialization Evidence Index

日期：2026-05-02

状态：`passed`

## 1. Evidence Assets

| asset | path |
|---|---|
| run_id | `data-execution-price-line-materialization-20260502-01` |
| report_dir | `H:\Asteria-report\data\2026-05-02\data-execution-price-line-materialization-20260502-01` |
| closeout | `H:\Asteria-report\data\2026-05-02\data-execution-price-line-materialization-20260502-01\closeout.md` |
| manifest | `H:\Asteria-report\data\2026-05-02\data-execution-price-line-materialization-20260502-01\manifest.json` |
| audit_summary | `H:\Asteria-report\data\2026-05-02\data-execution-price-line-materialization-20260502-01\audit-summary.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-data-execution-price-line-materialization-20260502-01.zip` |

## 2. Formal DB Scope

| DB | release status |
|---|---|
| `H:\Asteria-data\raw_market.duckdb` | `backward` + `none` source facts released |
| `H:\Asteria-data\market_base_day.duckdb` | `analysis_price_line / backward` + `execution_price_line / none` released |
| `H:\Asteria-data\market_base_week.duckdb` | unchanged analysis line only |
| `H:\Asteria-data\market_base_month.duckdb` | unchanged analysis line only |

## 3. Hard Audit

| check | result |
|---|---|
| natural key uniqueness | passed |
| latest pointer uniqueness | passed |
| price line separation | passed |
| execution day line present | passed |
| market_meta not silently claimed released | passed |
