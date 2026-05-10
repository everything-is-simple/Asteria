# Pipeline Year Replay Disposition Decision Card

日期：2026-05-10

状态：`prepared / not executed`

## 1. 目标

在 `pipeline-year-replay-source-selection-repair-card-20260509-01` 已通过之后，
基于当前 released year replay truth，正式裁定下一步应当是：

- 重跑 `year_replay_rerun`
- 做 truthful closeout
- 或把后续工作转入 Stage 11 队列

## 2. 已知前提

| item | value |
|---|---|
| released system run | `system-readout-bounded-proof-build-card-20260508-01` |
| observed released window | `2024-01-02..2024-12-31` |
| source lock clean | `true` |
| follow-up attribution | `calendar_semantic_gap_only` |

## 3. 允许动作

- 只做 disposition decision 与 live next-card truth 裁决。
- 只读复核当前 released evidence、门禁、roadmap 和 Stage 11 backlog。
- 必要时冻结唯一后续执行卡，但不在本卡内代为执行。

## 4. 仍然禁止

| forbidden | decision |
|---|---|
| 直接执行 `year_replay_rerun` | 禁止 |
| 打开 System full build / Pipeline semantic repair | 禁止 |
| 打开 full rebuild / daily incremental / `v1 complete` | 禁止 |
