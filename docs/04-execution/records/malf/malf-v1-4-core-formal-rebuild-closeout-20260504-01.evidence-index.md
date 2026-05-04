# MALF v1.4 Core Formal Rebuild Closeout Evidence Index

日期：2026-05-04

状态：`passed`

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
| `H:\Asteria-data\malf_core_day.duckdb` | `core rebuild completed; current release run rows written` |
| `H:\Asteria-data\malf_lifespan_day.duckdb` | `lifespan rebuild completed; current release run rows written` |
| `H:\Asteria-data\malf_service_day.duckdb` | `service rebuild and audit completed; release passed` |

## 3. Diagnostic Results

| check | result |
|---|---:|
| source rows | `1,280,703` |
| core wave rows | `314` |
| core snapshot rows | `4,613` |
| lifespan snapshot rows | `4,613` |
| service wave position rows | `4,613` |
| service latest rows | `20` |
| interface audit rows | `22` |
| hard_fail_count | `0` |
| current runtime evidence switched | `1` |

## 4. Repair Outcome

| surface | observation |
|---|---|
| `service_wave_position_natural_key_unique` | `0` |
| `core_new_candidate_replaces_previous` | `0` |
| `service_v13_trace_matches_lifespan` | `0` |
| source-row scope | `analysis_price_line / backward only` |

## 5. Current Runtime Evidence

`malf-v1-4-core-formal-rebuild-closeout-20260504-01` is current.
