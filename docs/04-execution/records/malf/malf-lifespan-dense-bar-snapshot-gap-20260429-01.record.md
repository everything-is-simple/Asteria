# MALF Lifespan Dense Bar Snapshot Gap Record

日期：2026-04-29

## 1. 执行经过

本记录登记 MALF Lifespan dense bar-level WavePosition 差距，不执行代码修改或数据库重建。

## 2. 核查事实

| 项 | 事实 |
|---|---|
| bounded proof | `malf-day-bounded-proof-20260428-01` 已通过 |
| current Lifespan shape | 以 confirm、pivot、break、candidate 等事件日期生成 snapshot |
| frozen schema wording | `malf_lifespan_snapshot` 目标自然键为 `wave_id + bar_dt + lifespan_rule_version` |
| downstream risk | daily Signal / Position / Portfolio mainline 需要每 bar WavePosition |

## 3. 处理结果

| 项 | 结果 |
|---|---|
| runtime change | `none` |
| formal DB change | `none` |
| gate state change | `current next card moved to MALF dense resolution` |
| gap status | `blocked until dedicated MALF dense snapshot fix card` |

## 4. 后续要求

full daily mainline 前必须打开单独 MALF 修复卡，补齐 dense bar-level Lifespan snapshot 与
Service WavePosition 发布语义，并增加对应 audit/checker。
