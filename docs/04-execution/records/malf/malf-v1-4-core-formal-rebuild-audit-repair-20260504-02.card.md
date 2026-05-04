# MALF v1.4 Core Formal Rebuild Audit Repair Card

日期：2026-05-04

状态：`prepared / not executed`

## 1. 目的

本卡承接 `malf-v1-4-core-formal-rebuild-closeout-20260504-01` 在 rerun 后暴露出的新阻塞，只负责：

- 调查并修复 MALF day formal rebuild 完成后 hard audit 失败的问题。
- 收敛 `service_wave_position_natural_key_unique`、`core_new_candidate_replaces_previous`、
  `service_v13_trace_matches_lifespan` 三组 hard fail。
- 保证修复范围限定在 MALF day Core / Lifespan / Service / Audit，不回退已完成的列位兼容写入。
- 修复后重新放行回到 `malf_v1_4_core_formal_rebuild_closeout` 的下一次 rerun。

## 2. 当前边界

- 不允许回退 `malf-v1-4-core-formal-rebuild-repair-20260504-01` 已通过的显式列名写入契约。
- 不允许扩大到 week/month proof。
- 不允许切换当前 runtime evidence。
- 不允许打开 Position / downstream construction。

## 3. 当前阻塞事实

| check | failed_count |
|---|---:|
| `service_wave_position_natural_key_unique` | `4767` |
| `core_new_candidate_replaces_previous` | `3579` |
| `service_v13_trace_matches_lifespan` | `392` |
| `hard_fail_count total` | `8738` |

当前正式 runtime evidence 仍然保持：

```text
malf-v1-3-formal-rebuild-closeout-20260502-01
```
