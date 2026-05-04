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
| `H:\Asteria-data\malf_core_day.duckdb` | `core rebuild completed; run rows and snapshots written` |
| `H:\Asteria-data\malf_lifespan_day.duckdb` | `lifespan rebuild completed; snapshots written` |
| `H:\Asteria-data\malf_service_day.duckdb` | `service rebuild and audit completed; hard audit blocked release` |

## 3. Diagnostic Results

| check | result |
|---|---:|
| blocked stage | `hard audit after service publication` |
| source rows | `2,561,406` |
| core wave rows | `744` |
| core snapshot rows | `9,534` |
| lifespan snapshot rows | `9,534` |
| service wave position rows | `9,534` |
| service latest rows | `20` |
| interface audit rows | `22` |
| hard_fail_count | `8,738` |
| current runtime evidence switched | `0` |

## 4. Root Cause Snapshot

| surface | observation |
|---|---|
| `service_wave_position_natural_key_unique` | `4767` hard failures |
| `core_new_candidate_replaces_previous` | `3579` hard failures |
| `service_v13_trace_matches_lifespan` | `392` hard failures |
| write compatibility repair | explicit-column insert fix is already active and no longer the current blocker |

## 5. Current Runtime Evidence

`malf-v1-3-formal-rebuild-closeout-20260502-01` remains current.
