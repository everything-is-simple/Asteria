# Data Production Release Closeout Evidence Index

日期：2026-05-02

状态：`passed`

## 1. Evidence Assets

| asset | path |
|---|---|
| run_id | `data-production-release-closeout-20260502-01` |
| report_dir | `H:\Asteria-report\data\2026-05-02\data-production-release-closeout-20260502-01` |
| closeout | `H:\Asteria-report\data\2026-05-02\data-production-release-closeout-20260502-01\closeout.md` |
| manifest | `H:\Asteria-report\data\2026-05-02\data-production-release-closeout-20260502-01\manifest.json` |
| audit_summary | `H:\Asteria-report\data\2026-05-02\data-production-release-closeout-20260502-01\audit-summary.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-data-production-release-closeout-20260502-01.zip` |

## 2. Formal DB Scope

| DB | release status |
|---|---|
| `H:\Asteria-data\raw_market.duckdb` | production foundation released |
| `H:\Asteria-data\market_base_day.duckdb` | production foundation released |
| `H:\Asteria-data\market_base_week.duckdb` | production foundation released |
| `H:\Asteria-data\market_base_month.duckdb` | production foundation released |

## 3. Hard Audit

| check | result |
|---|---|
| source trace | passed |
| natural key uniqueness | passed |
| latest pointer uniqueness | passed |
| price line separation | passed |
| daily incremental behavior | passed |
| checkpoint resume behavior | passed |
| no strategy leakage | passed |
