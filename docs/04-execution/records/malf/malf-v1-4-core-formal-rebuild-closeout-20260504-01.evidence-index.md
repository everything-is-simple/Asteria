# MALF v1.4 Core Formal Rebuild Closeout Evidence Index

日期：2026-05-04

状态：`blocked`

## 1. Evidence Assets

| asset | path |
|---|---|
| run_id | `malf-v1-4-core-formal-rebuild-closeout-20260504-01` |
| report_dir | `H:\Asteria-report\malf\2026-05-04\malf-v1-4-core-formal-rebuild-closeout-20260504-01` |
| closeout | `H:\Asteria-report\malf\2026-05-04\malf-v1-4-core-formal-rebuild-closeout-20260504-01\closeout.md` |
| manifest | `H:\Asteria-report\malf\2026-05-04\malf-v1-4-core-formal-rebuild-closeout-20260504-01\manifest.json` |
| audit_summary | `H:\Asteria-report\malf\2026-05-04\malf-v1-4-core-formal-rebuild-closeout-20260504-01-audit-summary.json` |
| table_counts | `H:\Asteria-report\malf\2026-05-04\malf-v1-4-core-formal-rebuild-closeout-20260504-01\table-counts.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-malf-v1-4-core-formal-rebuild-closeout-20260504-01.zip` |

## 2. Formal DB Impact

| DB | status |
|---|---|
| `H:\Asteria-data\malf_core_day.duckdb` | `transaction failed before run rows committed` |
| `H:\Asteria-data\malf_lifespan_day.duckdb` | `not executed` |
| `H:\Asteria-data\malf_service_day.duckdb` | `not executed` |

## 3. Diagnostic Results

| check | result |
|---|---:|
| blocked stage | `core` |
| source rows | `2,561,406` |
| source symbol count | `5,348` |
| failed run rows in core DB | `0` |
| failed run rows in lifespan DB | `0` |
| failed run rows in service DB | `0` |
| current runtime evidence switched | `0` |

## 4. Root Cause Snapshot

| surface | observation |
|---|---|
| `malf_core_run` | historical formal table keeps `created_at` before v1.4 policy columns |
| `malf_pivot_ledger` | historical formal table keeps `created_at` before `pivot_detection_rule_version` |
| `malf_lifespan_run` | historical formal table still lacks v1.4 policy columns |
| `malf_service_run` | historical formal table still lacks v1.4 policy columns |
| write path | current runners use positional `insert into ... values (...)` rather than explicit column lists |

## 5. Current Runtime Evidence

`malf-v1-3-formal-rebuild-closeout-20260502-01` remains current.
