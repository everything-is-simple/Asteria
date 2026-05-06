# Data Reference Target Maintenance Scope Card

日期：2026-05-06

状态：`prepared / not executed`

## 1. 背景

`upstream-pre-position-completeness-synthesis-20260506-01` 已裁定：Data Foundation
可作为当前 bounded mainline 输入底座，但不能按最终完整目标宣称 reference facts 已齐。
本卡是上游修补路线的第一张卡，只冻结 Data reference maintenance 的施工范围。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `data` |
| run_id | `data-reference-target-maintenance-scope-20260506-01` |
| stage | `maintenance-scope / prepared / not executed` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| source docs | `docs/02-modules/data` |
| current evidence | `data-foundation-production-baseline-seal-20260502-01` |
| review blocker | `data-foundation-target-completeness-review-20260506-01` |
| scope question | `ST / suspension / listing-delisting / historical industry / index-block / week-month execution price line` |
| formal DB path | `H:\Asteria-data\market_meta.duckdb`; `H:\Asteria-data\market_base_*.duckdb` |

## 4. 权威边界

| 项 | 值 |
|---|---|
| upstream semantics | `source facts only; no strategy semantics` |
| formal DB permission | `not created or modified by this prepared card` |
| allowed next action before card | `data_reference_target_maintenance_scope` |

## 5. 允许动作

- 审阅 Data 六件套、baseline seal 证据和 upstream completeness 结论。
- 明确哪些 reference gaps 是 Position 前置必需，哪些可延后到后续 maintenance card。
- 输出 Data reference maintenance 的硬范围矩阵和验收合同。
- 若范围不清，记录 blocker，不进入 Data DB 修改。

## 6. 禁止动作

- 不修改 `raw_market.duckdb`、`market_base_*.duckdb` 或 `market_meta.duckdb`。
- 不伪造 ST、停牌、真实上市/退市、历史行业或 index/block 事实。
- 不进入 MALF、Alpha、Signal、Position 或 Pipeline runtime。
- 不创建 `position.duckdb` 或任何下游正式库。

## 7. 后续门禁

本卡执行并形成结论后，若范围可冻结，下一张卡才允许进入：

```text
data-reference-target-maintenance-closeout-20260506-01
```

## 8. 关联入口

- [Data target completeness review](data-foundation-target-completeness-review-20260506-01.conclusion.md)
- [gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
- [completion gap audit](../../../00-governance/05-mainline-module-completion-gap-audit-v1.md)
