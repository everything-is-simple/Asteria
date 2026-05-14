# v1-t-plus-one-open-backtesting-py-proof-card-20260514-01 Record

## Execution Summary

Status: `passed / t+1 open backtesting.py proof completed`

Execution date: `2026-05-14`

Route type: `roadmap-only / read-only / post-terminal / backtesting.py proof`

Live next: `none / terminal`

Formal DB mutation: `no`

## Work Performed

1. Added `backtesting.py` as an explicit project dependency.
2. Added the T+1 open proof runner, contracts, renderer, and CLI.
3. Added tests for the runner and route governance.
4. Ran the formal proof against the frozen 31-symbol, 2024 sample.
5. Generated report, manifest, closeout, temp manifest, and validated archive.
6. Updated roadmap, gate ledger, and conclusion index.

## Result

| Metric | Value |
|---|---:|
| selected_symbol_count | 31 |
| signal_symbol_count | 1 |
| completed_backtest_count | 1 |
| skipped_symbol_count | 30 |
| total_trade_count | 6 |
| mean_return_pct | -12.5930 |
| worst_drawdown_pct | -23.5430 |

## Skip Readout

| Reason | Count |
|---|---:|
| `no_active_signal_in_scope` | 30 |
| `down_signal_without_open_position` | 121 |
| `no_t_plus_one_open_bar` | 1 |

## Boundary Notes

- This proof is per-symbol and long-only.
- The result is a research adapter proof, not a production portfolio backtest.
- The low signal coverage is a retained strategy quality/source caveat for the next route card.
- No formal DB was mutated.

## Next Route Card

```text
v1-vectorbt-portfolio-analytics-proof-card
```
