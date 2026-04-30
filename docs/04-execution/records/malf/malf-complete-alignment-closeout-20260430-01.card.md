# MALF Complete Alignment Closeout Card

日期：2026-04-30

状态：`passed`

## 1. 任务范围

本卡闭环 `malf-complete-alignment-closeout-20260430-01`。目标是修复 MALF
zero-day wave 在 dense Lifespan / Service 发布中的自然键重复，绑定 hard audit 到
真实 source Core / Lifespan run，统一 candidate reference 语义，并重建正式 MALF
day DB evidence。

## 2. 授权边界

| 项 | 值 |
|---|---|
| run_id | `malf-complete-alignment-closeout-20260430-01` |
| allowed work | MALF Core / Lifespan / Service / Audit closeout only |
| source DB | `H:\Asteria-temp\data-bootstrap-smoke-all-2\market_base_day.duckdb` |
| formal DB scope | `malf_core_day.duckdb`; `malf_lifespan_day.duckdb`; `malf_service_day.duckdb` |
| forbidden work | Position construction, Signal full build, downstream construction, pipeline widening |
| next action after pass | `Position freeze review reentry / review-only` |

## 3. Required Fixes

- Lifespan must not publish both alive and transition rows for the same
  `symbol + timeframe + bar_dt + service_version` on zero-day waves.
- Core candidate reference must use old wave final progress extreme for both
  same-direction and opposite-direction candidates.
- Audit must bind Core checks to `source_core_run_id`, Lifespan checks to
  `source_lifespan_run_id`, and Service checks to the audit run.
- Formal day DBs may only be promoted after hard audit passes and full-table
  Service natural-key duplicate count is zero.

## 4. Completion Evidence

- [record](malf-complete-alignment-closeout-20260430-01.record.md)
- [evidence-index](malf-complete-alignment-closeout-20260430-01.evidence-index.md)
- [conclusion](malf-complete-alignment-closeout-20260430-01.conclusion.md)
