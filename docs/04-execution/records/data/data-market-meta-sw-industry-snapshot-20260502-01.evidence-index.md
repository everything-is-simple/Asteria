# Data Market Meta SW Industry Snapshot Evidence Index

日期：2026-05-02

状态：`passed`

## 1. Evidence Assets

| asset | path |
|---|---|
| run_id | `data-market-meta-sw-industry-snapshot-20260502-01` |
| source_xlsx | `H:\Asteria-Validated\Market-Average-Lifespan-reference\申万行业分类\最新个股申万行业分类(完整版-截至7月末).xlsx` |
| report_dir | `H:\Asteria-report\data\2026-05-02\data-market-meta-sw-industry-snapshot-20260502-01` |
| closeout | `H:\Asteria-report\data\2026-05-02\data-market-meta-sw-industry-snapshot-20260502-01\closeout.md` |
| manifest | `H:\Asteria-report\data\2026-05-02\data-market-meta-sw-industry-snapshot-20260502-01\manifest.json` |
| audit_summary | `H:\Asteria-report\data\2026-05-02\data-market-meta-sw-industry-snapshot-20260502-01\audit-summary.json` |
| production_audit_summary | `H:\Asteria-report\data\2026-05-02\data-market-meta-sw-industry-snapshot-20260502-01\production-audit-summary.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-data-market-meta-sw-industry-snapshot-20260502-01.zip` |

## 2. Formal DB Scope

| DB | release status |
|---|---|
| `H:\Asteria-data\market_meta.duckdb` | SW industry snapshot partially released |
| `industry_classification` | 4,237 rows, matched A-share instruments only |

## 3. Hard Audit

| check | result |
|---|---|
| source xlsx exists and hash matches | passed |
| required columns exist | passed |
| duplicate source stock code count | 0 |
| matched formal Data instruments | 4,237 |
| `industry_classification` natural key uniqueness | passed |
| `industry_classification` source policy | passed |
| Data production audit `hard_fail_count` | 0 |

## 4. Source Gaps Retained

| gap | status |
|---|---|
| ST status | retained |
| suspension status | retained |
| listing / delisting status | retained |
| historical industry lineage | retained |
