# Pipeline One-Year Strategy Behavior Replay Rerun Build Card

日期：2026-05-09

状态：`prepared / not executed`

## 1. 目标

在 MALF 最小 released-surface repair 已通过后，重新执行一次 year replay，
验证 `2024-01-02..2024-01-05` 是否已被新的 released MALF source run 接入下游观察链。

## 2. 输入边界

| 项 | 值 |
|---|---|
| module_scope | `year_replay_rerun` |
| prerequisite conclusion | `malf-2024-natural-year-coverage-repair-card-20260509-01` |
| target year | `2024` |
| MALF source run to lock | `malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001` |
| expected observation gain | `system_chain_readout earliest date moves earlier than 2024-01-08` |

## 3. 允许动作

- 以 repair 后的 MALF released run 为唯一新增上游输入，重跑 one-year strategy behavior replay。
- 真实记录 year replay 是否已跨过 `2024-01-08` 的旧起点。
- 若 rerun 后仍有新首断点，truthful 记录新的 earliest released-surface break。

## 4. 仍然禁止

| forbidden | decision |
|---|---|
| Data / Alpha / Signal / System / Pipeline semantic repair | 禁止 |
| full rebuild | 禁止 |
| daily incremental | 禁止 |
| v1 complete | 禁止 |
| 假装旧 20-symbol MALF run 已整体修复 | 禁止 |

## 5. 完成标准

- rerun 明确锁到 `malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001`。
- 输出新的 year replay 观察窗口与行为摘要。
- truthful 给出 `passed` 或 `blocked`，不得跳过 rerun 直接宣称 coverage 全修完。
