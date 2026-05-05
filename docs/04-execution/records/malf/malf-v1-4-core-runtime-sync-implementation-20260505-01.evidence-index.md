# MALF v1.4 Core Runtime Sync Implementation Evidence Index

日期：2026-05-05

状态：`passed`

## 1. Evidence Assets

| asset | path |
|---|---|
| run_id | `malf-v1-4-core-runtime-sync-implementation-20260505-01` |
| report_dir | `H:\Asteria-report\malf\2026-05-05\malf-v1-4-core-runtime-sync-implementation-20260505-01` |
| closeout | `H:\Asteria-report\malf\2026-05-05\malf-v1-4-core-runtime-sync-implementation-20260505-01\closeout.md` |
| manifest | `H:\Asteria-report\malf\2026-05-05\malf-v1-4-core-runtime-sync-implementation-20260505-01\manifest.json` |
| audit_summary | `H:\Asteria-report\malf\2026-05-05\malf-v1-4-core-runtime-sync-implementation-20260505-01-audit-summary.json` |
| table_counts | `H:\Asteria-report\malf\2026-05-05\malf-v1-4-core-runtime-sync-implementation-20260505-01\table-counts.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-malf-v1-4-core-runtime-sync-implementation-20260505-01.zip` |

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
| core waves | 304 |
| core snapshots | 4,837 |
| lifespan snapshots | 4,633 |
| service rows | 4,633 |
| service latest rows | 20 |
| service audit rows | 28 |

## 4. Structure Contexts

| context | rows |
|---|---:|
| `active_wave` | 713 |
| `initial_candidate` | 31 |
| `transition_candidate` | 872 |

## 5. Runtime Policy Surface

| field | value |
|---|---|
| `pivot_detection_rule_version` | `pivot-fractal-1bar-v1` |
| `core_event_ordering_version` | `core-event-order-v1` |
| `price_compare_policy` | `strict` |
| `epsilon_policy` | `none_after_price_normalization` |
| `source_market_base_run_id` | `data-production-release-closeout-20260502-01` |
| source line | `analysis_price_line / backward` |

## 6. Superseded Current Runtime Evidence

This closeout supersedes the current-runtime-evidence status of:

- `malf-v1-3-formal-rebuild-closeout-20260502-01`
- `malf-v1-4-core-runtime-sync-review-20260503-01`

Those records remain historical facts. Current MALF day runtime-aligned evidence is this
v1.4 runtime sync implementation closeout. week/month proof still remains `not performed`.
