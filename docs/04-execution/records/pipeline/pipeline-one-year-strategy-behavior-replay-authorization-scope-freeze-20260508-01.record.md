# Pipeline One-Year Strategy Behavior Replay Authorization Scope Freeze Record

日期：2026-05-08

## 1. 背景

在 `full-chain day bounded proof passed` 之后，本卡只冻结“一年策略行为回放”的授权边界，
先把观察对象、禁止扩权项和 target year 讲清楚，再允许执行 build card。

## 2. 冻结摘要

- 观察对象限定为 `signal / position / portfolio_plan / trade(order_intent / execution_plan / rejection) / system_readout`。
- 明确不把 `fill_count = 0`、真实 cash ledger、真实成交 PnL 缺口包装成 release truth。
- target year 固定为 `2024`，并要求完整自然年覆盖才可 passed。

## 3. Evidence

- `H:\Asteria-report\pipeline\2026-05-08\pipeline-one-year-strategy-behavior-replay-authorization-scope-freeze-20260508-01\closeout.md`
- `H:\Asteria-report\pipeline\2026-05-08\pipeline-one-year-strategy-behavior-replay-authorization-scope-freeze-20260508-01\manifest.json`
- `H:\Asteria-Validated\Asteria-pipeline-one-year-strategy-behavior-replay-authorization-scope-freeze-20260508-01.zip`
