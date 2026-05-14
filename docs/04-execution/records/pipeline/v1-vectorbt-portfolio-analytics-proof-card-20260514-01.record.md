# v1-vectorbt-portfolio-analytics-proof-card-20260514-01 Record

## Execution Summary

Status: `passed / vectorbt portfolio analytics proof completed`

Execution date: `2026-05-14`

Route type: `roadmap-only / read-only / post-terminal / vectorbt portfolio proof`

Live next: `none / terminal`

Formal DB mutation: `no`

## Work Performed

1. Added `vectorbt` as an explicit project dependency.
2. Added the vectorbt portfolio proof runner, contracts, renderer, artifact IO, and CLI.
3. Added tests for the runner, T+1 execution matrix, no-signal blocked path, route governance, and runner surface allowlist.
4. Ran the formal proof against the frozen 31-symbol, 2024 sample.
5. Generated report, manifest, closeout, temp manifest, and validated archive.
6. Updated roadmap, gate ledger, and conclusion index.

## Result

| Metric | Value |
|---|---:|
| selected_symbol_count | 31 |
| signal_symbol_count | 1 |
| completed_portfolio_matrix | true |
| portfolio_total_return_pct | -13.2839 |
| portfolio_max_drawdown_pct | -24.6748 |
| total_trade_count | 6 |
| order_activity_count | 12 |
| active_position_day_count | 85 |
| mean_active_position_count | 0.3512 |
| exposure_time_pct | 1.1330 |
| turnover_proxy | 11.6788 |

## Skip Readout

| Reason | Count |
|---|---:|
| `no_active_signal_in_scope` | 30 |
| `no_t_plus_one_open_bar` | 1 |

## Boundary Notes

- This proof is portfolio-matrix research analytics, not production portfolio backtest certification.
- `open` is used as the T+1 order execution price; `close` is used as the valuation price.
- The low signal coverage is retained as a strategy quality/source caveat.
- No formal DB was mutated.

## Next Route Card

```text
v1-broker-adapter-feasibility-card
```
