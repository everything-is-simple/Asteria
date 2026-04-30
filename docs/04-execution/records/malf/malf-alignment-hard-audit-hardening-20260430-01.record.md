# MALF Alignment Hard Audit Hardening Record

日期：2026-04-30

状态：`passed`

## 1. 执行经过

本记录闭环 MALF 设计与实现一致性评审后发现的两个缺口：hard audit 未逐条覆盖
Core 设计铁律，以及 MALF 本地 authority design 仍停留在旧的 Alpha freeze review
next action 文案。

## 2. 执行动作

| stage | 动作 |
|---|---|
| red tests | 新增 MALF hard audit failure tests，先确认新增 check 缺失时失败 |
| audit hardening | 在 `audit_engine.py` 增加 Core 设计铁律与 WavePosition 自然键 hard checks |
| clean pass | 增加 clean bounded fixture 下新增 checks 全部 pass 的回归测试 |
| docs sync | 同步 MALF authority design 与 gate ledger 的 dense resolution 状态 |

## 3. 新增 hard checks

| check_name | 目标 |
|---|---|
| `core_terminated_wave_not_alive` | terminated wave 不得重新 alive |
| `core_break_does_not_extend_old_wave` | break 后不得延伸旧 wave |
| `core_single_active_candidate_per_transition` | 同一 transition 只能一个 active candidate |
| `core_new_candidate_replaces_previous` | 新 candidate 必须替代旧 candidate |
| `core_new_wave_candidate_confirmation_required` | new wave 必须由 candidate guard 与 confirmation 创建 |
| `core_candidate_confirmation_threshold` | candidate up/down confirmation 阈值必须成立 |
| `service_wave_position_natural_key_unique` | `malf_wave_position` 自然键必须唯一 |

## 4. 边界

本卡只强化 MALF audit 证明力，不重算正式 MALF DB，不改变已通过的 MALF dense
resolution 结论，不打开任何 Position construction 或下游施工。
