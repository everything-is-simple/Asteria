# MALF Day Bounded Proof Evidence Index

日期：2026-04-28

## 1. 基本信息

| 项 | 值 |
|---|---|
| module | `malf` |
| run_id | `malf-day-bounded-proof-20260428-01` |
| status | `passed` |

## 2. 资产入口

| 资产 | 路径 |
|---|---|
| report_dir | `H:\Asteria-report\malf\2026-04-28\malf-day-bounded-proof-20260428-01` |
| closeout | `H:\Asteria-report\malf\2026-04-28\malf-day-bounded-proof-20260428-01\closeout.md` |
| manifest | `H:\Asteria-report\malf\2026-04-28\malf-day-bounded-proof-20260428-01\manifest.json` |
| gate_snapshot | `not applicable; gate effect is recorded in module gate ledger and conclusion` |
| run_manifest | `not applicable; this run used manifest.json as the evidence manifest` |
| source_manifest | `not applicable; source DB and authority assets are declared in this index and card` |
| table_counts | `H:\Asteria-report\malf\2026-04-28\malf-day-bounded-proof-20260428-01\table-counts.json` |
| audit_summary | `H:\Asteria-report\malf\2026-04-28\malf-day-bounded-proof-20260428-01\audit-summary.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-malf-day-bounded-proof-20260428-01.zip` |
| MALF authority directory | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2` |
| MALF authority zip | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2.zip` |
| docs/code snapshot | `H:\Asteria-Validated\Asteria-docs-code-20260428-214427.zip` |
| formal_core_db | `H:\Asteria-data\malf_core_day.duckdb` |
| formal_lifespan_db | `H:\Asteria-data\malf_lifespan_day.duckdb` |
| formal_service_db | `H:\Asteria-data\malf_service_day.duckdb` |

## 3. 关键结果

Core：

| 指标 | 值 |
|---|---:|
| pivot rows | 1035 |
| structure rows | 1027 |
| wave rows | 67 |
| break rows | 66 |
| transition rows | 66 |
| candidate rows | 709 |

birth_type 覆盖：

| birth_type | count |
|---|---:|
| `initial` | 4 |
| `opposite_direction_after_break` | 46 |
| `same_direction_after_break` | 17 |

Lifespan / Service：

| 指标 | 值 |
|---|---:|
| lifespan snapshot rows | 621 |
| lifespan profile rows | 4 |
| wave_position rows | 621 |
| wave_position_latest rows | 4 |
| interface_audit rows | 7 |

WavePosition 状态分布：

| system_state | wave_core_state | count |
|---|---|---:|
| `down_alive` | `alive` | 72 |
| `transition` | `terminated` | 444 |
| `up_alive` | `alive` | 105 |

## 4. 关键审计

| 项 | 值 |
|---|---:|
| hard_fail_count | 0 |
| service_audit_pass_rows | 7 |
| published_row_count | 621 |
| core_wave_count | 67 |
| lifespan_snapshot_count | 621 |
| allowed next action | `Alpha freeze review` |
| conclusion index registered | `yes` |
| downstream writeback opened | `no` |

## 5. 关联记录

- [card](malf-day-bounded-proof-20260428-01.card.md)
- [record](malf-day-bounded-proof-20260428-01.record.md)
- [conclusion](malf-day-bounded-proof-20260428-01.conclusion.md)
