# Pipeline One-Year Strategy Behavior Replay Build Record

日期：2026-05-08

## 1. 背景

`pipeline-one-year-strategy-behavior-replay-authorization-scope-freeze-20260508-01` 已通过。
本卡真实执行 `year_replay`，并把 2024 年 released surfaces 上能观察到的策略行为提取出来。

## 2. Formal Execution

| stage | 命令摘要 |
|---|---|
| year replay | `run_pipeline_bounded_proof.py --module-scope year_replay --mode bounded --target-year 2024 --run-id pipeline-one-year-strategy-behavior-replay-build-card-20260508-01 --source-chain-release-version system-readout-bounded-proof-build-card-20260508-01` |

## 3. Result

| item | value |
|---|---|
| status | `failed / blocked` |
| step_count | `7` |
| gate_snapshot_count | `11` |
| manifest_count | `21` |
| audit_count | `8` |
| hard_fail_count | `1` |
| blocking audit | `pipeline_year_replay_full_year_coverage` |

## 4. Behavior Summary

| item | value |
|---|---|
| observed_start | `2024-01-08` |
| observed_end | `2024-12-31` |
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

## 5. Boundary

本卡已经产出了可读的行为摘要，但因为 `2024-01-01..2024-12-31` 这个完整自然年未满足，
不能把它登记成 passed release evidence。当前只能如实记为 `blocked`。

## 6. Evidence

- `H:\Asteria-report\pipeline\2026-05-08\pipeline-one-year-strategy-behavior-replay-build-card-20260508-01\behavior-summary.json`
- `H:\Asteria-report\pipeline\2026-05-08\pipeline-one-year-strategy-behavior-replay-build-card-20260508-01\closeout.md`
- `H:\Asteria-report\pipeline\2026-05-08\pipeline-one-year-strategy-behavior-replay-build-card-20260508-01\manifest.json`
- `H:\Asteria-report\pipeline\2026-05-08\pipeline-one-year-strategy-behavior-replay-build-card-20260508-01-audit-summary.json`
- `H:\Asteria-Validated\Asteria-pipeline-one-year-strategy-behavior-replay-build-card-20260508-01.zip`
