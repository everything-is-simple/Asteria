# MALF Complete Alignment Closeout Record

日期：2026-04-30

状态：`passed`

## 1. 执行经过

本记录闭环 MALF complete alignment closeout。执行顺序为：

1. 修复 Lifespan zero-day dense snapshot 发布边界。
2. 修复 Core candidate reference 语义。
3. 增强 audit source-run binding 与 candidate reference hard check。
4. 在 run-scoped staging 目录重建 MALF Core / Lifespan / Service day DB。
5. hard audit 通过且 Service 自然键重复为 0 后，备份旧正式 DB 并 promote 新正式 DB。

## 2. 执行命令

| stage | 命令摘要 |
|---|---|
| core | `run_malf_day_core_build.py --source-db H:\Asteria-temp\data-bootstrap-smoke-all-2\market_base_day.duckdb --run-id malf-complete-alignment-closeout-20260430-01 --rule-version core-rule-fractal-1bar-v1` |
| lifespan | `run_malf_day_lifespan_build.py --run-id malf-complete-alignment-closeout-20260430-01 --rule-version lifespan-dense-bar-v1 --sample-version malf-day-bounded-2024-s4` |
| service | `run_malf_day_service_build.py --run-id malf-complete-alignment-closeout-20260430-01 --service-version malf-wave-position-dense-v1` |
| audit | `run_malf_day_audit.py --source-db H:\Asteria-temp\data-bootstrap-smoke-all-2\market_base_day.duckdb --run-id malf-complete-alignment-closeout-20260430-01` |

## 3. Formal DB Promotion

| 项 | 值 |
|---|---|
| staging_dir | `H:\Asteria-temp\malf\malf-complete-alignment-closeout-20260430-01\formal-staging` |
| backup_dir | `H:\Asteria-data\archive\malf-complete-alignment-closeout-20260430-01` |
| formal_core_db | `H:\Asteria-data\malf_core_day.duckdb` |
| formal_lifespan_db | `H:\Asteria-data\malf_lifespan_day.duckdb` |
| formal_service_db | `H:\Asteria-data\malf_service_day.duckdb` |

## 4. 关键结果

| 项 | 值 |
|---|---:|
| core_wave_count | 71 |
| core_candidate_count | 689 |
| lifespan_snapshot_count | 933 |
| service_wave_position_count | 933 |
| service_latest_count | 4 |
| service_audit_rows | 20 |
| hard_fail_count | 0 |
| wave_position_natural_key_duplicate_groups | 0 |
| candidate_reference_mismatch_count | 0 |

## 5. 边界声明

本卡只关闭 MALF day bounded dense evidence 洞。它不授权 Position bounded proof、
Position construction、Signal full build、下游 construction 或全链路 pipeline。

## 6. 证据链接

- report closeout: `H:\Asteria-report\malf\2026-04-30\malf-complete-alignment-closeout-20260430-01\closeout.md`
- manifest: `H:\Asteria-report\malf\2026-04-30\malf-complete-alignment-closeout-20260430-01\manifest.json`
- validated zip: `H:\Asteria-Validated\Asteria-malf-complete-alignment-closeout-20260430-01.zip`
- [card](malf-complete-alignment-closeout-20260430-01.card.md)
- [evidence-index](malf-complete-alignment-closeout-20260430-01.evidence-index.md)
- [conclusion](malf-complete-alignment-closeout-20260430-01.conclusion.md)
