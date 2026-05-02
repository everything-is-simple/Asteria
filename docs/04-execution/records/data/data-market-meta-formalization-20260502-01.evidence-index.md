# Data Market Meta Formalization Evidence Index

日期：2026-05-02

状态：`passed`

## 1. Evidence Assets

| asset | path |
|---|---|
| run_id | `data-market-meta-formalization-20260502-01` |
| report_dir | `H:\Asteria-report\data\2026-05-02\data-market-meta-formalization-20260502-01` |
| closeout | `H:\Asteria-report\data\2026-05-02\data-market-meta-formalization-20260502-01\closeout.md` |
| manifest | `H:\Asteria-report\data\2026-05-02\data-market-meta-formalization-20260502-01\manifest.json` |
| audit_summary | `H:\Asteria-report\data\2026-05-02\data-market-meta-formalization-20260502-01\audit-summary.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-data-market-meta-formalization-20260502-01.zip` |

## 2. Formal DB Scope

| DB | release status |
|---|---|
| `H:\Asteria-data\raw_market.duckdb` | existing formal input |
| `H:\Asteria-data\market_base_day.duckdb` | existing formal input with `execution_price_line / none` |
| `H:\Asteria-data\market_base_week.duckdb` | existing formal input |
| `H:\Asteria-data\market_base_month.duckdb` | existing formal input |
| `H:\Asteria-data\market_meta.duckdb` | minimal formalized / reference gaps retained |

## 3. Hard Audit

| check | result |
|---|---|
| market_meta exists | passed |
| required meta tables exist | passed |
| meta natural keys unique | passed |
| `tradability_fact` source policy | passed |
| `industry_classification` source gap retained | passed |
| Data production audit `hard_fail_count` | 0 |
