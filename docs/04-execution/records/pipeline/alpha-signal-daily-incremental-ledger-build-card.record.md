# Alpha Signal Daily Incremental Ledger Build Card Record

日期：2026-05-11

## 1. 卡信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `alpha-signal-daily-incremental-ledger-build-card` |
| result | `passed / alpha signal daily incremental sample hardened` |
| next allowed action | `downstream_daily_impact_ledger_schema_card` |

## 2. 执行顺序

1. 新增 `src/asteria/alpha/daily_incremental_ledger.py`，把 MALF `day` sample lineage 接入 Alpha 五族。
2. 扩展 `src/asteria/alpha/contracts.py`，放开 `daily_incremental` run mode，并新增 Alpha wrapper request/summary。
3. 新增 `src/asteria/signal/daily_incremental_ledger.py`，把 Alpha `day` sample lineage 接入 Signal。
4. 扩展 `src/asteria/signal/contracts.py`，放开 `daily_incremental` run mode，并新增 Signal wrapper request/summary。
5. 新增 `scripts/pipeline/run_alpha_signal_daily_incremental_ledger.py`，作为本卡唯一 pipeline orchestration 入口。
6. 在 `H:\Asteria-temp` / `H:\Asteria-report` 产出 Alpha/Signal sample target DB、`derived-replay-scope.json`、`daily-impact-scope.json`、`lineage.json`、`batch-ledger.jsonl`、`checkpoint.json` 与 `audit-summary.json`。
7. 将 live next 从 `alpha_signal_daily_incremental_ledger_build_card` 前推到 `downstream_daily_impact_ledger_schema_card`，但不提前打开 downstream daily runtime。

## 3. 关键验证

| 验证 | 结果 |
|---|---|
| `tests\unit\alpha\test_daily_incremental_ledger.py` | `passed` |
| `tests\unit\signal\test_signal_daily_incremental_ledger.py` | `passed` |
| `tests\unit\governance\test_alpha_signal_daily_incremental_ledger_gate_transition.py` | `passed` |
| sample `daily_incremental` runner | `passed` |
| sample `resume` runner | `passed` |
| Alpha family candidate natural key duplicate groups | `0` |
| Signal formal ledger natural key duplicate groups | `0` |

## 4. 边界

- 本卡只覆盖 Alpha 五族与 `signal.duckdb` 的 `day` daily incremental sample。
- 本卡样板 target 落在 `H:\Asteria-temp` / `H:\Asteria-report`，不修改正式 `H:\Asteria-data`。
- Position、Portfolio Plan、Trade、System Readout 与 Pipeline full daily chain 均未执行。
- 本卡不重定义 MALF scope / lineage 语义，只消费已通过的 MALF daily incremental sample 输出。
