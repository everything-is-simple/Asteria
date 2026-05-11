# MALF Daily Incremental Ledger Build Card Record

日期：2026-05-11

## 1. 卡信息

| 项 | 值 |
|---|---|
| module | `malf` |
| run_id | `malf-daily-incremental-ledger-build-card` |
| result | `passed / malf daily incremental sample hardened` |
| next allowed action | `alpha_signal_daily_incremental_ledger_build_card` |

## 2. 执行顺序

1. 新增 `src/asteria/malf/daily_incremental_ledger.py`，包装 MALF `day` 三库样板增量闭环。
2. 扩展 `src/asteria/malf/contracts.py`，允许 `daily_incremental` 进入 MALF day runner mode surface。
3. 读取 Data 样板卡放行的 `source_manifest`、`daily_dirty_scope` 与 `checkpoint`，按 `symbol` 聚合最早 dirty 日期。
4. 对每个 symbol 从最早 dirty 日期起向后 replay 到当前 source 末端，复用 MALF supplemental builder 的 batch / resume / promote 机制。
5. 在 `H:\Asteria-temp` 产出 MALF sample target DB、`derived-replay-scope.json`、`daily-impact-scope.json`、`lineage.json`、`batch-ledger.jsonl`、`checkpoint.json` 与 `audit-summary.json`。
6. 将 live next 从 `malf_daily_incremental_ledger_build_card` 前推到 `alpha_signal_daily_incremental_ledger_build_card`，但不提前执行 Alpha/Signal runtime。

## 3. 关键验证

| 验证 | 结果 |
|---|---|
| `tests\unit\malf\test_daily_incremental_ledger.py` | `5 passed` |
| sample `daily_incremental` runner | `passed` |
| sample `resume` runner | `passed` |
| sample `audit-only` runner | `passed` |
| `malf_wave_position` natural key duplicate groups | `0` |

## 4. 边界

- 本卡只覆盖 `malf_core_day.duckdb`、`malf_lifespan_day.duckdb`、`malf_service_day.duckdb` 的 sample-hardening。
- `week/month` MALF DB 不写入，也不打开对应 daily incremental runtime。
- 本卡样板 target 落在 `H:\Asteria-temp` / `H:\Asteria-report`，不修改正式 `H:\Asteria-data`。
- Alpha/Signal、Position、Portfolio Plan、Trade、System Readout 与 Pipeline full daily chain 均未执行。
