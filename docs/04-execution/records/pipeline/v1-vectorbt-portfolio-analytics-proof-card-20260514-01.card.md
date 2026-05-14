# v1-vectorbt-portfolio-analytics-proof-card-20260514-01 Card

## Scope

This post-terminal route card runs a read-only `vectorbt` portfolio analytics proof against
the frozen 31-symbol, 2024 usage-validation sample.

## Allowed Actions

- Read the frozen scope manifest.
- Read active day signals from `formal_signal_ledger`.
- Read `execution_price_line / none` OHLCV bars from `market_base_day.duckdb`.
- Map `T+0 signal -> T+1 open execution`.
- Run one multi-asset `vectorbt` matrix proof.
- Write report artifacts under `H:\Asteria-report`.
- Write temp manifest under `H:\Asteria-temp`.
- Write validated archive under `H:\Asteria-Validated`.

## Forbidden Actions

- Do not write `H:\Asteria-data`.
- Do not create or update a formal fill ledger.
- Do not update account cash, holdings, or broker state.
- Do not claim production portfolio backtest quality.
- Do not claim broker adapter or live trading capability.
- Do not reopen live next; current live next remains `none / terminal`.

## Pass Criteria

- Runner status is `passed / vectorbt portfolio analytics proof completed`.
- `formal_db_mutation = no`.
- Manifest records `T_PLUS_1_OPEN`, `next_trading_day_after_signal_date`, `open`, and `close`.
- Report includes portfolio return, drawdown, trade count, exposure, turnover proxy, and skip reasons.
- Route advances to `v1-broker-adapter-feasibility-card`.
