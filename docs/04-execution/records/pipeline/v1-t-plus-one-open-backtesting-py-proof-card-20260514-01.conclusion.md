# v1-t-plus-one-open-backtesting-py-proof-card-20260514-01 Conclusion

## Final Status

`passed / t+1 open backtesting.py proof completed`

## Human Conclusion

Asteria has now run the first real external backtest proof from its frozen Signal contract.

The proved execution meaning is:

```text
T+0 signal -> T+1 open execution
```

The proof is intentionally narrow: one symbol in the 31-symbol sample had active Signal
coverage, and that symbol produced 6 trades under `backtesting.py`.

## What Is Now True

- `backtesting.py` is integrated as a project dependency.
- The runner reads formal DBs in read-only mode.
- The proof uses `execution_price_line / none` day bars.
- The proof records PnL, drawdown, trade count, and skip reasons.
- `formal_db_mutation = no`.
- Current live next remains `none / terminal`.
- The next route card is `v1-vectorbt-portfolio-analytics-proof-card`.

## What The Result Says

| Metric | Value |
|---|---:|
| selected_symbol_count | 31 |
| signal_symbol_count | 1 |
| completed_backtest_count | 1 |
| skipped_symbol_count | 30 |
| total_trade_count | 6 |
| mean_return_pct | -12.5930 |
| worst_drawdown_pct | -23.5430 |

The result is useful precisely because it is not polished: it shows that the adapter path
works, while also exposing that the current frozen 31-stock sample has very thin active
Signal coverage.

## What Is Still Not True

- This is not a production portfolio backtest.
- This is not a real fill ledger.
- This is not an account state transition loop.
- This is not a broker adapter.
- This is not live trading capability.

## Next Route Card

```text
v1-vectorbt-portfolio-analytics-proof-card
```

The next card should matrix the signal surface and answer whether this thin signal coverage
has useful portfolio-level research value, instead of extrapolating from one completed
single-symbol proof.
