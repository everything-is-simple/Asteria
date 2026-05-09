# Pipeline One-Year Strategy Behavior Replay Rerun Build Record

日期：2026-05-09

## 1. 背景

`malf-2024-natural-year-coverage-repair-card-20260509-01` 已通过，并已把
`000020.SZ` 的 released MALF day surface 补到 `2024-01-02..2024-01-05`。
本卡按 live authority 实际执行 `year_replay_rerun`，检查当前 released System Readout
观察链是否已经真正消费这次最小 MALF repair。

## 2. Formal Execution

| stage | command summary |
|---|---|
| year replay rerun | `run_pipeline_bounded_proof.py --module-scope year_replay_rerun --mode bounded --target-year 2024 --run-id pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01 --source-chain-release-version system-readout-bounded-proof-build-card-20260508-01` |

## 3. Result

| item | value |
|---|---|
| status | `failed / blocked` |
| step_count | `7` |
| gate_snapshot_count | `11` |
| manifest_count | `21` |
| audit_count | `9` |
| hard_fail_count | `2` |
| blocking audit 1 | `pipeline_year_replay_full_year_coverage` |
| blocking audit 2 | `pipeline_year_replay_rerun_malf_source_locked` |

## 4. Key Findings

| item | value |
|---|---|
| system readout observed_start | `2024-01-08` |
| system readout observed_end | `2024-12-31` |
| released manifest MALF source | `malf-v1-4-core-runtime-sync-implementation-20260505-01` |
| expected rerun MALF source | `malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001` |
| repaired MALF run earliest date | `2024-01-02` |
| released signal earliest date | `2024-01-08` |
| released position earliest date | `2024-01-09` |

这说明 Pipeline 本轮没有“取错库”或“偷换源”。
它如实读取了当前 released `system.duckdb` source manifest；
真正还没补到 released observation chain 的断点，已经从 MALF 下移到 Alpha / Signal。

## 5. Behavior Summary

| item | value |
|---|---|
| readout_count | `4633` |
| signal_count | `5494` |
| position_candidate_count | `1158` |
| portfolio_admission_count | `1158` |
| order_intent_count | `3` |
| execution_plan_count | `3` |
| fill_count | `0` |
| rejection_count | `1155` |

主要拒单原因：

- `superseded_by_newer_position_candidate = 999`
- `position_candidate_rejected = 154`
- `max_active_symbols_constraint = 2`

## 6. Decision

结合 `pipeline-year-replay-coverage-gap-diagnosis-and-repair-scope-freeze-20260509-01`
预先冻结的诊断矩阵，本卡当前应把唯一 prepared next card 切到：

```text
alpha-signal-2024-coverage-repair-card-20260509-01
```

原因是：

- MALF repaired run 已存在并覆盖 `2024-01-02..2024-01-05`
- released Alpha family 仍消费旧 MALF released run
- released Signal 仍从 `2024-01-08` 开始
- 因此当前最小 repair 已不再是 MALF，也不是 Pipeline source-selection

## 7. Evidence

- `H:\Asteria-report\pipeline\2026-05-09\pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01\behavior-summary.json`
- `H:\Asteria-report\pipeline\2026-05-09\pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01\closeout.md`
- `H:\Asteria-report\pipeline\2026-05-09\pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01\manifest.json`
- `H:\Asteria-report\pipeline\2026-05-09\pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01-audit-summary.json`
- `H:\Asteria-Validated\Asteria-pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01.zip`
