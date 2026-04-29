# MALF Lifespan Dense Bar Snapshot Gap Card

日期：2026-04-29

## 1. 背景

MALF day bounded proof 已通过，但当前 Lifespan bounded proof 实现以 confirm、pivot、
break 和 candidate 等结构事件日期生成 snapshot。该证据足以证明 bounded sparse/event-level
路径可用，但不足以证明 full daily mainline 所需的 dense bar-level WavePosition 已落地。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `malf` |
| run_id | `malf-lifespan-dense-bar-snapshot-gap-20260429-01` |
| stage | `gap / blocked` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| source | `src/asteria/malf/lifespan_engine.py`; `src/asteria/malf/service_engine.py`; MALF schema docs |
| scope | `MALF day Lifespan and Service semantics` |
| prerequisite docs | `docs/02-modules/malf/` |
| authority assets | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2` |

## 4. 权威边界

| 项 | 值 |
|---|---|
| upstream semantics | `MALF defines structure and WavePosition` |
| formal DB permission | `not opened by this gap card` |
| allowed next action before card | `Signal bounded proof build card` |

## 5. 允许动作

- 记录当前 MALF Lifespan sparse/event-level implementation gap。
- 保留 MALF day bounded proof passed 结论。
- 阻断后续 full daily mainline 对 dense WavePosition 的过度声明。
- 要求后续 MALF dense snapshot 修复卡在 full daily mainline 前打开。

## 6. 禁止动作

- 不改 MALF Lifespan 或 Service runner。
- 不重建 MALF day formal DB。
- 不撤销 `malf-day-bounded-proof-20260428-01` 的 bounded proof 结论。
- 不授权 Signal、Position 或下游模块重新定义 MALF WavePosition。

## 7. 关联入口

- [gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
- [conclusion index](../../00-conclusion-index-v1.md)
- [MALF database schema spec](../../../02-modules/malf/02-database-schema-spec-v1.md)
- [MALF day bounded proof conclusion](malf-day-bounded-proof-20260428-01.conclusion.md)
