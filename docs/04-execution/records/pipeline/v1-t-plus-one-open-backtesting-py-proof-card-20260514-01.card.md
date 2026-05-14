# v1-t-plus-one-open-backtesting-py-proof-card-20260514-01

## Card Type

`roadmap-only / read-only / post-terminal / backtesting.py proof`

## Mission

Run the first small external backtest proof for Asteria Core output:

```text
T+0 signal -> T+1 open execution
```

This card proves that the frozen Signal export contract can be consumed by
`backtesting.py` and can produce basic PnL, drawdown, trade count, and skip reason
readouts.

## Inputs

- `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md`
- `docs/04-execution/records/pipeline/v1-signal-export-contract-card-20260513-01.conclusion.md`
- `H:\Asteria-report\pipeline\2026-05-12\v1-usage-validation-scope-card-20260512-01\scope-manifest.json`
- `H:\Asteria-data\signal.duckdb::formal_signal_ledger`
- `H:\Asteria-data\market_base_day.duckdb::market_base_bar`

## Authorized Actions

- Read the frozen 31-symbol sample and 2024 date window.
- Read active day signals from `formal_signal_ledger`.
- Read `execution_price_line / none` OHLCV bars from `market_base_day.duckdb`.
- Run one `backtesting.py` proof per symbol with active signals.
- Write report artifacts under `H:\Asteria-report`.
- Write temp manifest under `H:\Asteria-temp`.
- Write validated archive under `H:\Asteria-Validated`.

## Forbidden Actions

- Do not write `H:\Asteria-data`.
- Do not create or update a formal fill ledger.
- Do not update account cash, holdings, or broker state.
- Do not claim portfolio-level production backtest quality.
- Do not claim broker adapter or live trading capability.
- Do not reopen live next; current live next remains `none / terminal`.

## Pass Criteria

- Runner status is `passed / t+1 open backtesting.py proof completed`.
- `formal_db_mutation = no`.
- Manifest records `T_PLUS_1_OPEN`, `next_trading_day_after_signal_date`, and `open`.
- Report includes PnL, drawdown, trade count, and skip reason readouts.
- Route advances to `v1-vectorbt-portfolio-analytics-proof-card`.
