# Position Bounded Proof Build Conclusion

日期：2026-05-07

状态：`passed`

## 1. Conclusion

`position-bounded-proof-build-card-20260506-01` 已通过。Position 已在
`signal-production-builder-hardening-20260506-01` 放行的 day Signal surface 上完成
bounded proof，并通过 hard audit：

```text
hard_fail_count = 0
```

本结论只放行 Position day bounded proof surface。它不打开 Position full build、
Portfolio Plan build、Trade、System 或 full-chain Pipeline。

## 2. Gate Result

| 项 | 结果 |
|---|---|
| source Signal run | `signal-production-builder-hardening-20260506-01` |
| target DB | `H:\Asteria-data\position.duckdb` |
| timeframe | `day` |
| bounded scope | `symbol_limit = 5` |
| input_signal_count | `1158` |
| position_candidate_count | `1158` |
| entry_plan_count | `1004` |
| exit_plan_count | `1004` |
| hard_fail_count | `0` |
| validated evidence | `H:\Asteria-Validated\Asteria-position-bounded-proof-build-card-20260506-01.zip` |
| allowed next action | `portfolio_plan_freeze_review` |

## 3. Boundary

Position 仍只读消费 Signal，不直接读取 Alpha / MALF 形成持仓语义，不写回 Signal /
Alpha / MALF。Portfolio Plan 只能进入 freeze review；不得把本结论解释为 Portfolio
build、Trade/System 施工或全链路 Pipeline 放行。

## 4. Evidence

- [record](position-bounded-proof-build-card-20260506-01.record.md)
- [evidence-index](position-bounded-proof-build-card-20260506-01.evidence-index.md)
