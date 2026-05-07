# Trade Freeze Review Card

日期：2026-05-07

状态：`prepared / not executed`

## 1. 背景

`portfolio-plan-bounded-proof-build-card-20260507-01` 已通过，Portfolio Plan day bounded
proof surface 已放行。下一步只允许准备 Trade freeze review；本文件仅登记下一卡，
不代表已执行 review 或 build。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `trade` |
| run_id | `trade-freeze-review-20260507-01` |
| stage | `freeze-review / prepared / not executed` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| upstream release | `Portfolio Plan bounded proof passed` |
| source DB | `H:\Asteria-data\portfolio_plan.duckdb` |
| source tables | `portfolio_admission_ledger`; `portfolio_target_exposure`; `portfolio_trim_ledger`; `portfolio_plan_audit` |
| source boundary | `read-only released Portfolio Plan bounded proof surface` |
| formal DB permission | `not allowed in this review card` |

## 4. 允许动作

- 后续执行 turn 可 review-only 审阅 Trade 六件套。
- 后续执行 turn 可冻结 Trade design / schema / runner / audit 合同表面。
- 后续执行 turn 必须生成 Trade freeze review 的 record、evidence-index、conclusion。

## 5. 当前仍禁止

- 不创建 `H:\Asteria-data\trade.duckdb`。
- 不创建 `src\asteria\trade` 或 `scripts\trade`。
- 不执行 Trade bounded proof、full build、segmented build 或 daily incremental build。
- 不创建 System / Pipeline 正式 runner 或正式 DB。
- 不允许 Trade 回写 Portfolio Plan、Position、Signal、Alpha 或 MALF。

## 6. 验收与后续门禁

Trade freeze review 通过后，才允许准备 Trade bounded proof build card。
