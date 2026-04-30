# MALF Lifespan Dense Bar Snapshot Resolution Record

日期：2026-04-30

状态：`passed`

## 1. 执行经过

本记录闭环 MALF dense bar-level WavePosition gap 的正式 resolution 卡。该卡由
Position freeze review 的 blocked 结论回退触发，用于防止主线继续停在已完成且被阻断的
`position_freeze_review`。

## 2. 执行命令

| stage | 命令摘要 |
|---|---|
| lifespan | `run_malf_day_lifespan_build.py --source-db H:\Asteria-temp\data-bootstrap-smoke-all-2\market_base_day.duckdb --run-id malf-lifespan-dense-bar-snapshot-resolution-20260429-01` |
| service | `run_malf_day_service_build.py --run-id malf-lifespan-dense-bar-snapshot-resolution-20260429-01 --service-version malf-wave-position-dense-v1` |
| audit | `run_malf_day_audit.py --source-db H:\Asteria-temp\data-bootstrap-smoke-all-2\market_base_day.duckdb --run-id malf-lifespan-dense-bar-snapshot-resolution-20260429-01` |

## 3. 关键结果

| 项 | 值 |
|---|---:|
| core_wave_count | 67 |
| lifespan_snapshot_count | 935 |
| lifespan_transition_count | 561 |
| service_wave_position_count | 935 |
| service_latest_count | 4 |
| service_audit_rows | 10 |
| hard_fail_count | 0 |

## 4. 处理边界

本卡只处理 MALF Lifespan 与 MALF Service 的 dense bar-level 发布语义，以及必要治理
状态同步。Signal Alpha release pinning 另开独立卡；Position re-entry 只允许
review-only，不授权 Position bounded proof。
