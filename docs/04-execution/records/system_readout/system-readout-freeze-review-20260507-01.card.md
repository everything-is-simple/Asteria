# System Readout Freeze Review Card

日期：2026-05-07

状态：`prepared / not executed`

## 1. 背景

`trade-bounded-proof-build-card-20260507-01` 已通过。System Readout 现在只允许准备
freeze review，用于只读审阅 Trade 输出边界；本文件仅登记下一卡，不代表已执行 review。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `system_readout` |
| run_id | `system-readout-freeze-review-20260507-01` |
| stage | `freeze-review / prepared / not executed` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| upstream release | `Trade bounded proof passed` |
| source DB | `H:\Asteria-data\trade.duckdb` |
| source tables | `trade_portfolio_snapshot`; `order_intent_ledger`; `execution_plan_ledger`; `fill_ledger`; `order_rejection_ledger`; `trade_audit` |
| source boundary | `read-only released Trade bounded proof surface` |
| formal DB permission | `not allowed in this review card` |

## 4. 允许动作

- 后续执行 turn 可 review-only 审阅 System Readout 六件套。
- 后续执行 turn 可冻结 System Readout design / schema / runner / audit 合同表面。
- 后续执行 turn 必须生成 System Readout freeze review 的 record、evidence-index、conclusion。

## 5. 当前仍禁止

- 不创建 `H:\Asteria-data\system.duckdb`。
- 不创建 `src\asteria\system_readout` 或 `scripts\system_readout`。
- 不执行 System Readout bounded proof、full build、segmented build 或 daily incremental build。
- 不允许 System Readout 回写 Trade、Portfolio Plan、Position、Signal、Alpha 或 MALF。
- 不创建 Pipeline 正式 runner 或正式 DB。

## 6. 验收与后续门禁

System Readout freeze review 通过后，才允许准备 System Readout bounded proof build card。
