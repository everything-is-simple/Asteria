# MALF Daily Incremental Ledger Build Card Conclusion

日期：2026-05-11

状态：`passed / malf daily incremental sample hardened`

## 1. 结论

`malf-daily-incremental-ledger-build-card` 已闭环。本卡在 MALF `day` 三库样板边界内实现并验证了
`daily_incremental`、`resume` 与 `audit-only` 三种模式：正式消费 Data 卡放行的
`source_manifest`、`daily_dirty_scope` 与 `checkpoint`，并输出 MALF 自身
`derived_replay_scope`、`daily_impact_scope`、`source_run_id -> target_run_id` lineage、
`batch-ledger.jsonl`、`checkpoint.json` 与 `audit-summary.json`。

本卡 replay 语义固定为：按 `symbol` 聚合最早 dirty 日期，并从该日期起向后 replay 到当前
`market_base_day.duckdb` source 末端；不把 MALF 错做成“只补 dirty 当天”的单点写入。

## 2. Gate Result

| 项 | 结果 |
|---|---|
| allowed next action | `alpha_signal_daily_incremental_ledger_build_card` |
| prepared next card | `alpha-signal-daily-incremental-ledger-build-card` |
| formal `H:\Asteria-data` mutation | `no` |
| week/month daily incremental opened | `no` |
| Alpha/Signal daily runtime opened | `no` |
| downstream daily runtime opened | `no` |
| Pipeline full daily chain opened | `no` |
| full rebuild / v1 complete claim | `no` |

## 3. 样板 Proof

| proof | result |
|---|---|
| day daily incremental sample | `passed` |
| resume sample | `passed` |
| audit-only sample | `passed` |
| replay from earliest dirty date forward | `passed` |
| `malf_wave_position` natural-key uniqueness | `passed` |
| week/month no-write boundary | `passed` |

## 4. Links

- [card](malf-daily-incremental-ledger-build-card.card.md)
- [record](malf-daily-incremental-ledger-build-card.record.md)
- [evidence-index](malf-daily-incremental-ledger-build-card.evidence-index.md)
- [prepared next card](../pipeline/alpha-signal-daily-incremental-ledger-build-card.card.md)
