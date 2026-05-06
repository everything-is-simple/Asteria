# MALF Week Bounded Proof Build Card

日期：2026-05-06

状态：`prepared / not executed`

## 1. 背景

MALF day runtime evidence 已升级到 v1.4 day runtime sync implementation，但 week 正式
Core/Lifespan/Service 三库仍未构建。本卡是 Data reference maintenance closeout 之后的
第一张 MALF 多周期修补卡。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `malf` |
| run_id | `malf-week-bounded-proof-build-20260506-01` |
| stage | `bounded-proof / week / prepared / not executed` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| prerequisite card | `data-reference-target-maintenance-closeout-20260506-01` |
| authority assets | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4` |
| source DB | `H:\Asteria-data\market_base_week.duckdb`; `H:\Asteria-data\market_meta.duckdb` |
| target DBs | `malf_core_week.duckdb`; `malf_lifespan_week.duckdb`; `malf_service_week.duckdb` |
| temp path | `H:\Asteria-temp\malf\<run_id>\` |

## 4. 权威边界

| 项 | 值 |
|---|---|
| upstream semantics | `read-only Data source facts` |
| formal DB permission | `allowed only when this card is explicitly executed` |
| allowed next action before card | `malf_week_bounded_proof_build` |

## 5. 允许动作

- 复用 MALF day v1.4 runtime 口径，冻结 week timeframe 的输入、schema、runner 和 audit。
- 构建 week Core、Lifespan、Service staging DB，并通过 hard audit 后 promote。
- 证明 week `WavePosition` 自然键唯一、hard fail 为 0、run/audit/version 表面完整。
- 生成完整执行四件套与外部证据。

## 6. 禁止动作

- 不修改 MALF 语义权威定义。
- 不创建 MALF month 正式库。
- 不打开 Alpha full build、Signal full build、Position construction 或 Pipeline runtime。
- 不允许 Alpha、Signal 或任何下游写回 MALF。

## 7. 后续门禁

本卡通过后，才允许进入：

```text
malf-month-bounded-proof-build-20260506-01
```

## 8. 关联入口

- [MALF target completeness review](malf-authority-runtime-completeness-review-20260506-01.conclusion.md)
- [MALF v1.4 runtime sync conclusion](malf-v1-4-core-runtime-sync-implementation-20260505-01.conclusion.md)
- [gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
