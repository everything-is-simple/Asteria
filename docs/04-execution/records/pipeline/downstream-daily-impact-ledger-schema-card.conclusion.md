# Downstream Daily Impact Ledger Schema Card Conclusion

日期：2026-05-11

状态：`passed / downstream daily impact schema frozen`

## 1. 结论

`downstream-daily-impact-ledger-schema-card` 已闭环。本卡没有打开 downstream daily runtime，
而是把 Position / Portfolio Plan / Trade / System Readout 在 Stage 11 所需的
`daily_protocol_scope`、`daily_protocol_lineage`、`daily_protocol_replay_scope`、`daily impact`
日期锚点与 topology replay/checkpoint 口径冻结为 repo 内权威真相。

本卡明确保持：

- 业务自然键不改写为 `trade_date + symbol`
- `system_readout` 仍是 `read_only_consumer`
- `H:\Asteria-data` 不发生 formal mutation

## 2. Gate Result

| 项 | 结果 |
|---|---|
| allowed next action | `downstream_daily_incremental_runner_build_card` |
| prepared next card | `downstream-daily-incremental-runner-build-card` |
| downstream daily runtime opened | `no` |
| formal `H:\Asteria-data` mutation | `no` |
| full rebuild / `v1 complete` claim | `no` |

## 3. Freeze Coverage

| module | result |
|---|---|
| Position | `daily impact date anchors frozen` |
| Portfolio Plan | `daily impact date anchors frozen` |
| Trade | `daily impact date anchors frozen` |
| System Readout | `readout-only impact role frozen` |

## 4. Links

- [card](downstream-daily-impact-ledger-schema-card.card.md)
- [record](downstream-daily-impact-ledger-schema-card.record.md)
- [evidence index](downstream-daily-impact-ledger-schema-card.evidence-index.md)
- [prepared next card](downstream-daily-incremental-runner-build-card.card.md)
