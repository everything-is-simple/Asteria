# Alpha Freeze Review Evidence Index

日期：2026-04-29

## 1. 基本信息

| 项 | 值 |
|---|---|
| module | `alpha` |
| run_id | `alpha-freeze-review-20260429-01` |
| status | `passed` |

## 2. 资产入口

| 资产 | 路径 |
|---|---|
| report_dir | `H:\Asteria-report\alpha\2026-04-29\alpha-freeze-review-20260429-01` |
| closeout | `H:\Asteria-report\alpha\2026-04-29\alpha-freeze-review-20260429-01\closeout.md` |
| manifest | `H:\Asteria-report\alpha\2026-04-29\alpha-freeze-review-20260429-01\manifest.json` |
| review_summary | `H:\Asteria-report\alpha\2026-04-29\alpha-freeze-review-20260429-01\review-summary.json` |
| gate_snapshot | `not applicable; gate effect is recorded in module gate ledger and conclusion` |
| run_manifest | `not applicable; this review used manifest.json as the evidence manifest` |
| source_manifest | `not applicable; source DB and authority assets are declared in this index and card` |
| validated_zip | `H:\Asteria-Validated\2.backups\Asteria-alpha-freeze-review-20260429-01.zip` |
| formal_db | `not applicable; no Alpha formal DB created` |

## 3. 关键结果

| 指标 | 值 |
|---|---:|
| Alpha six-doc files reviewed | 6 |
| `malf_wave_position` rows | 621 |
| `malf_wave_position_latest` rows | 4 |
| `malf_interface_audit` rows | 7 |
| service versions reviewed | 1 |
| formal Alpha DB files created | 0 |
| formal Alpha runner files created | 0 |

## 4. 关键审计

| 项 | 值 |
|---|---:|
| hard_fail_count | 0 |
| `malf_interface_audit` fail rows | 0 |
| Alpha read-only MALF boundary | `passed` |
| `wave_core_state` / `system_state` separation preserved | `passed` |
| no position / portfolio / order output | `passed` |
| no downstream writeback opened | `passed` |

## 5. 门禁影响

| 项 | 值 |
|---|---|
| allowed next action | `Alpha bounded proof build card` |
| construction opened | `no` |
| formal Alpha DB opened | `no` |
| downstream writeback opened | `no` |

## 6. 关联记录

- [card](alpha-freeze-review-20260429-01.card.md)
- [record](alpha-freeze-review-20260429-01.record.md)
- [conclusion](alpha-freeze-review-20260429-01.conclusion.md)
