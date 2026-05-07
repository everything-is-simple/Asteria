# Portfolio Plan Freeze Review Card

日期：2026-05-07

状态：`executed / passed`

## 1. 背景

`position-bounded-proof-build-card-20260506-01` 已通过，Position day bounded proof
surface 已形成 repo 内结论和 Validated evidence。下一步只允许进入 Portfolio Plan
freeze review，不授权 Portfolio Plan build。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `portfolio_plan` |
| run_id | `portfolio-plan-freeze-review-20260507-01` |
| stage | `freeze-review / executed / passed` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| upstream release | `Position bounded proof passed` |
| source DB | `H:\Asteria-data\position.duckdb` |
| source tables | `position_candidate_ledger`; `position_entry_plan`; `position_exit_plan`; `position_audit` |
| source boundary | `read-only released Position bounded proof surface` |
| formal DB permission | `not allowed in this review card` |

## 4. 允许动作

- 后续执行 turn 可 review-only 审阅 Portfolio Plan 六件套。
- 后续执行 turn 可冻结 Portfolio Plan design / schema / runner / audit 合同表面。
- 后续执行 turn 必须生成 Portfolio Plan freeze review 的 record、evidence-index、conclusion。

## 5. 当前仍禁止

- 不创建 `portfolio_plan.duckdb`。
- 不创建 `src\asteria\portfolio_plan` 或 `scripts\portfolio_plan` 正式 runner。
- 不运行 Portfolio Plan bounded proof、full build、segmented production build 或 daily incremental build。
- 不创建 Trade / System / Pipeline 正式 runner 或正式 DB。
- 不允许 Portfolio Plan 直接读取 Signal、Alpha 或 MALF 绕过 Position。

## 6. 验收与后续门禁

Portfolio Plan freeze review 通过后，才允许准备 Portfolio Plan bounded proof build card。
