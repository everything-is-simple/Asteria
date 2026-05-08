# Pipeline One-Year Strategy Behavior Replay Authorization Scope Freeze Card

日期：2026-05-08

状态：`passed`

## 1. 目标

冻结“一年策略行为回放”这张卡的观察边界，明确它是 behavior replay，不是 full rebuild release。

## 2. 冻结范围

| 项 | 裁决 |
|---|---|
| observation scope | `signal -> position -> portfolio_plan -> trade(order_intent / execution_plan / rejection) -> system_readout` |
| target year | `2024` |
| not observed as release truth | `fill-backed pnl / real cash ledger / production release / v1 complete` |
| next prepared card | `pipeline_one_year_strategy_behavior_replay_build_card` |
