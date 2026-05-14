# v1-vectorbt-portfolio-analytics-proof-card-20260514-01 Conclusion

## Status

`passed / vectorbt portfolio analytics proof completed`

## Decision

Asteria Signal can be consumed by `vectorbt` as a multi-asset portfolio matrix using
`T+0 signal -> T+1 open execution`, with `open` as order price and `close` as valuation price.

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
| exposure_time_pct | 1.1330 |
| turnover_proxy | 11.6788 |

## Caveats

- Signal coverage remains thin: only `1 / 31` selected symbols had active Signal rows in scope.
- The proof is a research analytics adapter proof, not production portfolio backtest certification.
- It does not create real fill evidence, update account state, connect a broker, or prove live trading capability.

## Live Gate Impact

None. Current live next remains `none / terminal`.

## Next Route Card

`v1-broker-adapter-feasibility-card`
