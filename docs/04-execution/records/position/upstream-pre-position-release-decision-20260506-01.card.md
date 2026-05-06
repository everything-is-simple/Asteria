# Upstream Pre-Position Release Decision Card

日期：2026-05-06

状态：`passed / review-only release decision closed`

## 1. 背景

本卡是七张上游修补路线的总控裁决卡。它不施工 Position，只在 Data、MALF、Alpha、
Signal 修补卡全部形成结论后，回答是否恢复 Position bounded proof build card。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `position` |
| run_id | `upstream-pre-position-release-decision-20260506-01` |
| stage | `release-decision / review-only / closed` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| prerequisite cards | `data-reference-target-maintenance-scope`; `data-reference-target-maintenance-closeout`; `malf-week-bounded-proof-build`; `malf-month-bounded-proof-build`; `alpha-production-builder-hardening`; `signal-production-builder-hardening` |
| current blocker | `upstream-pre-position-completeness-synthesis-20260506-01` |
| Position docs | `docs/02-modules/position` |
| target decision | `whether to reopen position-bounded-proof-build-card` |

## 4. 权威边界

| 项 | 值 |
|---|---|
| upstream semantics | `review-only synthesis; no upstream semantic rewrite` |
| formal DB permission | `not allowed; this card creates no Position DB` |
| allowed next action before card | `upstream_pre_position_release_decision` |

## 5. 允许动作

- 汇总六张上游修补卡的 conclusion、evidence-index、DB audit 和 no-downstream 证明。
- 裁定上游是否达到选定的 Position 前置标准。
- 若通过，只把下一步改为 `position_bounded_proof_build_card`，不在本卡施工 Position。
- 若未通过，记录剩余 blocker，并把 next card 指向下一张具体修补卡。

## 6. 禁止动作

- 不创建 `src\asteria\position`。
- 不创建 `scripts\position`。
- 不创建 `H:\Asteria-data\position.duckdb`。
- 不打开 Portfolio、Trade、System 或 Pipeline runtime。
- 不把 Signal full build 结论偷换成 Position construction passed。

## 7. 后续门禁

只有本卡 conclusion 明确通过并同步 registry / gate ledger / conclusion index 后，才允许恢复：

```text
position-bounded-proof-build-card-20260506-01
```

## 8. 关联入口

- [Upstream completeness synthesis](upstream-pre-position-completeness-synthesis-20260506-01.conclusion.md)
- [Position bounded proof prepared card](position-bounded-proof-build-card-20260506-01.card.md)
- [gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
