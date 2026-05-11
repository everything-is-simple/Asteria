# System-Wide Daily Dirty Scope Protocol Record

日期：2026-05-11

run_id：`system-wide-daily-dirty-scope-protocol-card`

## 1. Inputs

- `docs/04-execution/records/pipeline/system-wide-daily-dirty-scope-protocol-card.card.md`
- `docs/03-refactor/04-asteria-full-system-roadmap-v1.md`
- `governance/module_gate_registry.toml`
- `governance/module_api_contracts/pipeline.toml`
- `governance/module_api_contracts/system_readout.toml`
- `src/asteria/pipeline/stage11_daily_protocol_contracts.py`

## 2. Formal Execution

| stage | command summary |
|---|---|
| protocol freeze | define Stage 11 `day`-only dirty scope / impact scope / checkpoint / lineage / writer-read-only boundary |
| governance sync | move live next card to `data_ledger_daily_incremental_hardening_card` |
| contract sync | update Pipeline/System Readout contract skeleton without opening daily runtime |
| next-card prep | create `data-ledger-daily-incremental-hardening-card` as the only prepared follow-up card |

## 3. Protocol Result

- Stage 11 入口协议已冻结为 `day only`。
- `daily_dirty_scope` 固定使用 `symbol + trade_date + timeframe + source_run_id` 口径。
- `daily_impact_scope` 固定表达受影响重算面，不承载新的业务语义。
- `checkpoint / resume` 固定记录 `module_scope + timeframe + trade_date + symbol + source_run_id`。
- `source_run_id -> target_run_id` 被正式冻结为跨模块 lineage 口径。
- `system_readout` 与 `pipeline` 被正式冻结为 read-only consumer，不得充当 writer。

## 4. Live Truth Update

1. 关闭 `system_wide_daily_dirty_scope_protocol_card` 的 prepared 状态。
2. 将顶层 live `current_allowed_next_card` 切换为 `data_ledger_daily_incremental_hardening_card`。
3. 将 `active_foundation_card` 切换为 `data-ledger-daily-incremental-hardening-card`。
4. 将 Pipeline 当前 active card / proof run / release conclusion / evidence index 同步到
   `system-wide-daily-dirty-scope-protocol-card`。

## 5. Boundary

- 本卡不执行任何 `daily runner`、`full rebuild` 或 `daily incremental` runtime。
- 本卡不改 `year replay` 审计语义。
- 本卡不改任何主线业务字段，也不把 `system_readout` / `pipeline` 提升为业务 writer。
