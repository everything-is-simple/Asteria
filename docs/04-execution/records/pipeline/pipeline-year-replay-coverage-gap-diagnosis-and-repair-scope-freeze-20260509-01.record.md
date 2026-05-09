# Pipeline Year Replay Coverage Gap Diagnosis Record

日期：2026-05-09

## 1. 背景

`pipeline-one-year-strategy-behavior-replay-build-card-20260508-01` 已真实执行，但因
`2024-01-01..2024-12-31` 完整自然年覆盖不足而 `blocked`。本卡只做 formal read-only diagnosis，
不重跑 replay，不修改 released DuckDB，也不改 Pipeline gate 语义。

## 2. Formal Execution

| stage | command summary |
|---|---|
| diagnosis | `run_year_replay_coverage_gap_diagnosis.py --run-id pipeline-year-replay-coverage-gap-diagnosis-and-repair-scope-freeze-20260509-01 --target-year 2024` |

## 3. Findings

- 锁定 `system.duckdb` 当前 released `system_readout_run = system-readout-bounded-proof-build-card-20260508-01`。
- 锁定 `system_source_manifest` 指向的 released upstream runs，不自行改选更“合理”的 source run。
- `market_base_day`、`trade_calendar`、`tradability_fact` 都覆盖 `2024-01-02..2024-01-05`。
- released `malf_wave_position` 从 `2024-01-08` 才开始，因此最早 released surface break 出现在 MALF。
- Alpha / Signal / downstream surface 也都从 `2024-01-08` 才开始，但它们属于 MALF 缺口的下游连锁结果，不是首断点。
- `2024-01-01`、`2024-01-06`、`2024-01-07` 被单独登记为 calendar-semantic dates，不被伪装成 Data 缺口。

## 4. Decision

唯一允许的下一张 repair card：

```text
malf-2024-natural-year-coverage-repair-card-20260509-01
```
