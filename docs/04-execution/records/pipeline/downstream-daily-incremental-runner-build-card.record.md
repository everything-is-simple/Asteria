# Downstream Daily Incremental Runner Build Card Record

日期：2026-05-12

## 1. 卡信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `downstream-daily-incremental-runner-build-card` |
| result | `passed / downstream daily incremental sample hardened` |
| next allowed action | `pipeline_full_daily_incremental_chain_build_card` |

## 2. 执行顺序

1. 扩展 `position / portfolio_plan / trade / system_readout` 四个模块的 contract mode surface，放开 `daily_incremental` 并新增 wrapper request/summary。
2. 新增四个 module-local `daily_incremental_ledger.py`，统一消费上游 `daily-impact-scope`、`lineage` 与 `checkpoint`，支持 `daily_incremental / resume / audit-only`。
3. 新增四个 CLI wrapper，把 downstream day-only sample target 固定落到 `H:\Asteria-temp` / `H:\Asteria-report`。
4. 新增 `scripts/pipeline/run_downstream_daily_incremental_ledger.py`，显式串联 Position -> Portfolio Plan -> Trade -> System Readout。
5. 将 live next 从 `downstream_daily_incremental_runner_build_card` 前推到 `pipeline_full_daily_incremental_chain_build_card`，但不提前执行 full chain runtime。

## 3. 关键验证

| 验证 | 结果 |
|---|---|
| `tests\unit\position\test_position_daily_incremental_ledger.py` | `passed` |
| `tests\unit\portfolio_plan\test_portfolio_plan_daily_incremental_ledger.py` | `passed` |
| `tests\unit\trade\test_trade_daily_incremental_ledger.py` | `passed` |
| `tests\unit\system_readout\test_system_readout_daily_incremental_ledger.py` | `passed` |
| `tests\unit\pipeline\test_downstream_daily_incremental_ledger.py` | `passed` |
| `tests\unit\governance\test_downstream_daily_incremental_runner_gate_transition.py` | `passed` |
| sample `daily_incremental` runner | `passed` |
| sample `resume` runner | `passed` |
| sample `audit-only` runner | `passed` |

## 4. 边界

- 本卡只覆盖 downstream `day`-only daily incremental sample runner。
- 所有 target 与审计结果只落在 `H:\Asteria-temp` / `H:\Asteria-report`，不修改正式 `H:\Asteria-data`。
- 本卡不自动产出 `H:\Asteria-Validated` evidence zip。
- `pipeline-full-daily-incremental-chain-build-card` 仅被准备，不在本卡执行。
