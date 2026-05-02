# MALF v1.3 Formal Rebuild Closeout Evidence Index

日期：2026-05-02

状态：`passed`

## 1. Evidence Assets

| asset | path |
|---|---|
| run_id | `malf-v1-3-formal-rebuild-closeout-20260502-01` |
| report_dir | `H:\Asteria-report\malf\2026-05-02\malf-v1-3-formal-rebuild-closeout-20260502-01` |
| closeout | `H:\Asteria-report\malf\2026-05-02\malf-v1-3-formal-rebuild-closeout-20260502-01\closeout.md` |
| manifest | `H:\Asteria-report\malf\2026-05-02\malf-v1-3-formal-rebuild-closeout-20260502-01\manifest.json` |
| audit_summary | `H:\Asteria-report\malf\2026-05-02\malf-v1-3-formal-rebuild-closeout-20260502-01-audit-summary.json` |
| table_counts | `H:\Asteria-report\malf\2026-05-02\malf-v1-3-formal-rebuild-closeout-20260502-01\table-counts.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-malf-v1-3-formal-rebuild-closeout-20260502-01.zip` |

## 2. Formal DBs

| DB | status |
|---|---|
| `H:\Asteria-data\malf_core_day.duckdb` | rebuilt run appended / audited |
| `H:\Asteria-data\malf_lifespan_day.duckdb` | rebuilt run appended / audited |
| `H:\Asteria-data\malf_service_day.duckdb` | rebuilt run appended / audited |

## 3. Audit Results

| check | result |
|---|---:|
| hard_fail_count | 0 |
| source rows | 1,280,703 |
| core waves | 298 |
| lifespan snapshots | 4,633 |
| service rows | 4,633 |
| service latest rows | 20 |
| service audit rows | 22 |

## 4. Structure Contexts

| context | rows |
|---|---:|
| `initial_candidate` | 31 |
| `active_wave` | 904 |
| `transition_candidate` | 731 |
