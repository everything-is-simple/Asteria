# MALF Lifespan Dense Bar Snapshot Resolution Record

日期：2026-04-29

状态：`opened`

## 1. 执行经过

本记录登记 MALF dense bar-level WavePosition gap 的正式 resolution 卡。该卡由
Position freeze review 的 blocked 结论回退触发，用于防止主线继续停在已完成且被阻断的
`position_freeze_review`。

## 2. 当前事实

| 项 | 事实 |
|---|---|
| MALF day bounded proof | `passed` |
| dense gap | `blocked upstream gap` |
| Position freeze review | `blocked / review-only` |
| previous stale next card | `position_freeze_review` |
| new current next card | `malf_lifespan_dense_bar_snapshot_resolution` |

## 3. 处理边界

本卡只处理 MALF Lifespan 与 MALF Service 的 dense bar-level 发布语义，以及必要治理
状态同步。Signal Alpha release pinning 另开独立卡；Position 不得用自身逻辑绕过
MALF dense gap。

## 4. 验证要求

| 验证 | 要求 |
|---|---|
| MALF unit tests | dense snapshot and transition span tests pass |
| governance unit tests | stale blocked next-card and release-gate ledger checks pass |
| project governance | `scripts\governance\check_project_governance.py` passes |
| release checks | Ruff, mypy, and pytest use `H:\Asteria-temp` caches |
