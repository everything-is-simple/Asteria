# Data Foundation Production Baseline Seal Evidence Index

日期：2026-05-02

状态：`passed`

## 1. Evidence Assets

| asset | path |
|---|---|
| run_id | `data-foundation-production-baseline-seal-20260502-01` |
| report_dir | `H:\Asteria-report\data\2026-05-02\data-foundation-production-baseline-seal-20260502-01` |
| closeout | `H:\Asteria-report\data\2026-05-02\data-foundation-production-baseline-seal-20260502-01\closeout.md` |
| manifest | `H:\Asteria-report\data\2026-05-02\data-foundation-production-baseline-seal-20260502-01\manifest.json` |
| production_audit_summary | `H:\Asteria-report\data\2026-05-02\data-foundation-production-baseline-seal-20260502-01\production-audit-summary.json` |
| live_db_snapshot | `H:\Asteria-report\data\2026-05-02\data-foundation-production-baseline-seal-20260502-01\live-db-snapshot.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-data-foundation-production-baseline-seal-20260502-01.zip` |

## 2. Formal DB Scope

| DB | seal status |
|---|---|
| `H:\Asteria-data\raw_market.duckdb` | sealed input baseline |
| `H:\Asteria-data\market_base_day.duckdb` | sealed input baseline |
| `H:\Asteria-data\market_base_week.duckdb` | sealed input baseline |
| `H:\Asteria-data\market_base_month.duckdb` | sealed input baseline |
| `H:\Asteria-data\market_meta.duckdb` | sealed input baseline |

## 3. Hard Audit

| check | result |
|---|---|
| Data production audit `hard_fail_count` | 0 |
| base natural keys | passed |
| latest pointer uniqueness | passed |
| execution price line presence | passed |
| market_meta required tables | passed |
| market_meta natural keys | passed |
| tradability source policy | passed |
| industry source policy | passed |

## 4. Gaps Retained

| gap | status |
|---|---|
| ST status | retained |
| suspension status | retained |
| listing / delisting status | retained |
| historical industry lineage | retained |
| index / block mainline integration | retained |
