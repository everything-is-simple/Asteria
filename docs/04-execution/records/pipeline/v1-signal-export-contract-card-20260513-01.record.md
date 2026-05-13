# v1-signal-export-contract-card-20260513-01 Record

## Execution Summary

Status: `passed / signal export contract frozen`

Execution date: `2026-05-13`

Route type: `roadmap-only / read-only / post-terminal / contract freeze`

Live next: `none / terminal`

Formal DB mutation: `no`

## Work Performed

1. Confirmed Phase 2 had already frozen the core retention and outsourcing boundary.
2. Promoted `v1-signal-export-contract-card` from prepared route card to passed route card.
3. Froze the minimum external signal contract for future backtesting adapters.
4. Registered `T+0 signal -> T+1 open execution` as the required next-stage execution hint.
5. Registered `v1-t-plus-one-open-backtesting-py-proof-card` as the next prepared route card.

## Frozen Field Set

| Field | Status |
|---|---|
| `symbol` | required |
| `timeframe` | required; first external proof consumes `day` |
| `signal_date` | required; exported alias for `signal_dt` |
| `signal_type` | required |
| `signal_strength` | required |
| `signal_family` | required derived label |
| `source_run_id` | required |
| `schema_version` | required |
| `signal_rule_version` | required |
| `source_alpha_release_version` | required |
| `lineage` | required machine-readable object |
| `execution_hint` | required literal `T_PLUS_1_OPEN` |
| `execution_signal_date` | required, same as `signal_date` |
| `execution_trade_date_policy` | required literal `next_trading_day_after_signal_date` |
| `execution_price_field` | required literal `open` |

## Explicit Non-Claims

- No formal return backtest was run.
- No real fill ledger was completed.
- No broker adapter was activated.
- No account cash, position balance, or PnL ledger was updated.
- No production daily incremental activation was opened.

## Next Route Card

```text
v1-t-plus-one-open-backtesting-py-proof-card
```

This next card may consume the frozen signal export contract and run a small
`backtesting.py` proof. It still must not claim live trading capability.
