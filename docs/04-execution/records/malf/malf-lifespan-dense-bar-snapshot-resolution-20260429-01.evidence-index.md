# MALF Lifespan Dense Bar Snapshot Resolution Evidence Index

日期：2026-04-30

状态：`passed`

当前证据状态：`superseded_by malf-complete-alignment-closeout-20260430-01`

本 evidence index 保留为历史 resolution 记录。当前 MALF dense formal evidence 以
[malf-complete-alignment-closeout-20260430-01](malf-complete-alignment-closeout-20260430-01.evidence-index.md)
为准。

## 1. 记录入口

| 项 | 值 |
|---|---|
| module | `malf` |
| run_id | `malf-lifespan-dense-bar-snapshot-resolution-20260429-01` |
| status | `passed` |
| card | `docs/04-execution/records/malf/malf-lifespan-dense-bar-snapshot-resolution-20260429-01.card.md` |
| record | `docs/04-execution/records/malf/malf-lifespan-dense-bar-snapshot-resolution-20260429-01.record.md` |
| conclusion | `docs/04-execution/records/malf/malf-lifespan-dense-bar-snapshot-resolution-20260429-01.conclusion.md` |

## 2. Evidence Scope

| 资产 | 路径 |
|---|---|
| report_dir | `H:\Asteria-report\malf\2026-04-30\malf-lifespan-dense-bar-snapshot-resolution-20260429-01` |
| closeout | `H:\Asteria-report\malf\2026-04-30\malf-lifespan-dense-bar-snapshot-resolution-20260429-01\closeout.md` |
| manifest | `H:\Asteria-report\malf\2026-04-30\malf-lifespan-dense-bar-snapshot-resolution-20260429-01\manifest.json` |
| audit_summary | `H:\Asteria-report\malf\2026-04-30\malf-lifespan-dense-bar-snapshot-resolution-20260429-01\audit-summary.json` |
| validated_zip | `H:\Asteria-Validated\2.backups\Asteria-malf-lifespan-dense-bar-snapshot-resolution-20260429-01.zip` |
| source_db | `H:\Asteria-temp\data-bootstrap-smoke-all-2\market_base_day.duckdb` |
| formal_core_db | `H:\Asteria-data\malf_core_day.duckdb` |
| formal_lifespan_db | `H:\Asteria-data\malf_lifespan_day.duckdb` |
| formal_service_db | `H:\Asteria-data\malf_service_day.duckdb` |

## 3. 关键结果

| 指标 | 值 |
|---|---:|
| core_wave_count | 67 |
| lifespan_snapshot_count | 935 |
| lifespan_transition_count | 561 |
| service_wave_position_count | 935 |
| service_latest_count | 4 |
| service_audit_rows | 10 |
| hard_fail_count | 0 |

## 4. Gate Impact

| 项 | 值 |
|---|---|
| allowed next action | `Position freeze review reentry` |
| Position bounded proof opened | `no` |
| downstream writeback opened | `no` |
