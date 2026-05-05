# MALF v1.4 Core Runtime Sync Implementation Record

日期：2026-05-05

run_id：`malf-v1-4-core-runtime-sync-implementation-20260505-01`

## 1. Inputs

- `H:\Asteria-data\market_base_day.duckdb`
- `docs/04-execution/records/malf/malf-v1-4-core-runtime-sync-review-20260503-01.conclusion.md`
- `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4`

## 2. Runtime Sync Repairs

- `MalfDayRequest`、run ledger 与 pivot ledger 增加 v1.4 policy/version metadata。
- Core runtime 新增 `malf_core_state_snapshot` 正式表面，并把 snapshot 纳入 hard audit。
- Core event 顺序改为按 bar 顺序处理；break 使用 first raw-bar guard breach，而不是等待更晚的 opposite pivot。
- `structure_context` 改为按 `initial_candidate / active_wave / transition_candidate` 上下文化追溯。
- candidate ledger 增加 `candidate_event_type`，区分 created / refresh / replacement / confirmed。
- MALF day Core 读取面收紧为 `analysis_price_line = backward`，不再把 `execution_price_line = none` 混入结构重放。
- Core / Lifespan / Service run table 写入改为显式列插入，以兼容 live formal DB 的历史列面。

## 3. Formal Rebuild

| stage | 命令摘要 |
|---|---|
| core | `run_malf_day_core_build.py --run-id malf-v1-4-core-runtime-sync-implementation-20260505-01 --rule-version core-rule-fractal-1bar-v1` |
| lifespan | `run_malf_day_lifespan_build.py --run-id malf-v1-4-core-runtime-sync-implementation-20260505-01 --rule-version lifespan-dense-bar-v1 --sample-version malf-day-formal-2024-s20-v14` |
| service | `run_malf_day_service_build.py --run-id malf-v1-4-core-runtime-sync-implementation-20260505-01 --service-version malf-wave-position-dense-v1` |
| audit | `run_malf_day_audit.py --run-id malf-v1-4-core-runtime-sync-implementation-20260505-01` |

执行 scope：

```text
day / 2024-01-01..2024-12-31 / symbol_limit=20
source line = market_base_day.market_base_bar / analysis_price_line / backward
```

## 4. Formal Outputs

- `H:\Asteria-data\malf_core_day.duckdb`
- `H:\Asteria-data\malf_lifespan_day.duckdb`
- `H:\Asteria-data\malf_service_day.duckdb`
- `H:\Asteria-report\malf\2026-05-05\malf-v1-4-core-runtime-sync-implementation-20260505-01-audit-summary.json`
- `H:\Asteria-report\malf\2026-05-05\malf-v1-4-core-runtime-sync-implementation-20260505-01\closeout.md`
- `H:\Asteria-report\malf\2026-05-05\malf-v1-4-core-runtime-sync-implementation-20260505-01\manifest.json`
- `H:\Asteria-report\malf\2026-05-05\malf-v1-4-core-runtime-sync-implementation-20260505-01\table-counts.json`

## 5. Verification

- `pytest tests/unit/malf -q`
- `run_malf_day_core_build.py`
- `run_malf_day_lifespan_build.py`
- `run_malf_day_service_build.py`
- `run_malf_day_audit.py`

最终结果：

```text
hard_fail_count = 0
```
