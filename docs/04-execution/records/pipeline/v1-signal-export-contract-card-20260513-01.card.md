# v1-signal-export-contract-card-20260513-01

## Card Type

`roadmap-only / read-only / post-terminal / contract freeze`

## Mission

Freeze the minimum signal export contract that lets external backtest frameworks consume
Asteria Core output without reopening the live gate or expanding Asteria into a full
self-built trading platform.

Human version:

```text
Asteria keeps Data + MALF + Alpha + Signal as its core, then exports signals in a
small, traceable, T+1-open-aware format for external backtesting.
```

## Inputs

- `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md`
- `docs/03-refactor/00-module-gate-ledger-v1.md`
- `docs/04-execution/00-conclusion-index-v1.md`
- `governance/module_api_contracts/signal.toml`
- `docs/02-modules/signal/00-authority-design-v1.md`
- `H:\Asteria-data\signal.duckdb::formal_signal_ledger` as the future formal source
- optional `signal_component_ledger` as the future lineage expansion source

## Frozen Contract

Required external fields:

- `symbol`
- `timeframe`
- `signal_date`
- `signal_type`
- `signal_strength`
- `signal_family`
- `source_run_id`
- `schema_version`
- `signal_rule_version`
- `source_alpha_release_version`
- `lineage`
- `execution_hint`
- `execution_signal_date`
- `execution_trade_date_policy`
- `execution_price_field`

Required execution semantics:

```text
T+0 signal -> T+1 open execution
execution_hint = T_PLUS_1_OPEN
execution_trade_date_policy = next_trading_day_after_signal_date
execution_price_field = open
```

## Boundaries

- This card does not write `H:\Asteria-data`.
- This card does not install or run `backtesting.py`.
- This card does not calculate PnL, drawdown, account cash, fills, or broker orders.
- This card does not redefine MALF, Alpha, Signal, Position, Portfolio Plan, Trade, or System semantics.
- This card keeps current live next as `none / terminal`.

## Pass Criteria

- Roadmap Phase 2 records `v1-signal-export-contract-card` as passed.
- Roadmap records `v1-t-plus-one-open-backtesting-py-proof-card` as the prepared next route card.
- The contract explicitly includes `symbol`, `signal_date`, `signal_strength`, `signal_family`,
  `source_run_id`, `lineage`, and `T_PLUS_1_OPEN`.
- The contract explicitly states that current Asteria still has no formal PnL backtest, real fill loop,
  account update loop, or live trading capability.
- Repo execution four-piece set exists for this card.
