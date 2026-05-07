# Portfolio Plan Bounded Proof Build Card

日期：2026-05-07

状态：`prepared / not executed`

## 1. 背景

`portfolio-plan-freeze-review-20260507-01` 已通过，Portfolio Plan 六件套已冻结为
`frozen / freeze review passed / build not executed`。下一步只允许准备 Portfolio Plan
bounded proof build card；本文件仅登记下一卡，不代表已执行 build。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `portfolio_plan` |
| run_id | `portfolio-plan-bounded-proof-build-card-20260507-01` |
| stage | `bounded-proof-build / prepared / not executed` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| upstream release | `Portfolio Plan freeze review passed` |
| source DB | `H:\Asteria-data\position.duckdb` |
| source tables | `position_candidate_ledger`; `position_entry_plan`; `position_exit_plan`; `position_audit` |
| source boundary | `read-only released Position bounded proof surface` |

## 4. 允许动作

- 后续执行 turn 可实现 Portfolio Plan bounded proof 的最小 runner / audit 表面。
- 后续执行 turn 可在审计通过后创建 `H:\Asteria-data\portfolio_plan.duckdb`。
- 后续执行 turn 必须生成 Portfolio Plan bounded proof 的 record、evidence-index、conclusion。

## 5. 当前仍禁止

- 不执行 Portfolio Plan full build、segmented production build 或 daily incremental build。
- 不创建 Trade / System / Pipeline 正式 runner 或正式 DB。
- 不允许 Portfolio Plan 直接读取 Signal、Alpha 或 MALF 绕过 Position。
- 不允许 Portfolio Plan 回写 Position 或输出 order / execution / fill 语义。

## 6. 验收与后续门禁

Portfolio Plan bounded proof 通过后，才允许准备 Trade freeze review。
