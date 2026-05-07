# Trade Bounded Proof Build Card

日期：2026-05-07

状态：`passed`

## 1. 背景

`trade-freeze-review-20260507-01` 已通过，Trade 六件套已冻结。本卡执行 day bounded proof
build，不创建 System / Pipeline 正式库，不写回 Portfolio Plan / Position / Signal /
Alpha / MALF，不伪造成交事实。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `trade` |
| run_id | `trade-bounded-proof-build-card-20260507-01` |
| stage | `bounded-proof-build / passed` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| upstream release | `Portfolio Plan bounded proof passed` |
| source DB | `H:\Asteria-data\portfolio_plan.duckdb` |
| source tables | `portfolio_admission_ledger`; `portfolio_target_exposure`; `portfolio_trim_ledger`; `portfolio_plan_audit` |
| source boundary | `read-only released Portfolio Plan bounded proof surface` |
| target DB permission | `allowed only during this build card execution` |

## 4. 允许动作

- 已创建 `src\asteria\trade` 与 `scripts\trade` 的最小 bounded proof surface。
- 已创建 `H:\Asteria-data\trade.duckdb`，仅放行 day bounded proof 表面。
- 已写入 `trade_portfolio_snapshot`、`order_intent_ledger`、`execution_plan_ledger`、`order_rejection_ledger`、`trade_audit`。
- `fill_ledger` 保持空表；没有 evidence-backed execution / fill source，因此只记录 retained gap。
- 已生成 Trade bounded proof 的 record、evidence-index、conclusion，并输出 `H:\Asteria-report` / `H:\Asteria-Validated` 证据。

## 5. 当前仍禁止

- 不执行 Trade full build、segmented build 或 daily incremental build。
- 不创建 System / Pipeline 正式 runner 或正式 DB。
- 不允许 Trade 回写 Portfolio Plan、Position、Signal、Alpha 或 MALF。
- 不允许使用 Data `analysis_price_line`、Portfolio Plan target exposure 或人工样例伪造真实成交价。

## 6. 验收与后续门禁

Trade bounded proof 通过后，下一步允许准备 System Readout freeze review。
