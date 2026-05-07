# Trade Bounded Proof Build Record

日期：2026-05-07

## 1. 背景

`trade-freeze-review-20260507-01` 已通过，Trade 六件套已冻结。本卡执行 Trade day
bounded proof build，唯一允许的上游输入是 released Portfolio Plan bounded proof
surface。

## 2. 执行摘要

- 新增 `src\asteria\trade` 最小 bounded proof 包：contracts、schema、rules、audit、bootstrap。
- 新增 `scripts\trade` 三个 runner wrapper：build、audit、bounded proof。
- 读取 `H:\Asteria-data\portfolio_plan.duckdb` 的 `portfolio_admission_ledger`、
  `portfolio_target_exposure`、`portfolio_trim_ledger` 与 `portfolio_plan_audit`。
- 只写入 `trade_portfolio_snapshot`、`order_intent_ledger`、`execution_plan_ledger`、
  `order_rejection_ledger` 与 `trade_audit`；`fill_ledger` 保持空表并显式记录 retained gap。
- hard audit 覆盖 source release lock、source surface presence、Trade 表族闭包、
  自然键唯一、order intent/execution plan traceability、禁用模拟 fill、禁用 forbidden columns
  与 unexpected tables。

## 3. Formal Execution

| stage | 命令摘要 |
|---|---|
| bounded proof | `run_trade_bounded_proof.py --run-id trade-bounded-proof-build-card-20260507-01 --source-portfolio-plan-release-version portfolio-plan-bounded-proof-build-card-20260507-01 --source-portfolio-plan-run-id portfolio-plan-bounded-proof-build-card-20260507-01` |

执行输入：

| 项 | 值 |
|---|---|
| source_portfolio_plan_db | `H:\Asteria-data\portfolio_plan.duckdb` |
| source_portfolio_plan_release_version | `portfolio-plan-bounded-proof-build-card-20260507-01` |
| source_portfolio_plan_run_id | `portfolio-plan-bounded-proof-build-card-20260507-01` |
| target_trade_db | `H:\Asteria-data\trade.duckdb` |
| report_root | `H:\Asteria-report` |
| validated_root | `H:\Asteria-Validated` |
| timeframe | `day` |

## 4. Result

| item | count |
|---|---:|
| input_portfolio_plan_count | 1158 |
| order_intent_count | 3 |
| execution_plan_count | 3 |
| fill_count | 0 |
| rejection_count | 1155 |
| hard_fail_count | 0 |

## 5. Boundary

Trade 只读消费 released Portfolio Plan bounded proof surface，不直接读取 Position /
Signal / Alpha / MALF 形成业务输出，不回写任何上游模块。fill_ledger 在本轮保持空表，
不得把 Data `analysis_price_line`、Portfolio Plan target exposure 或人工样例伪造成真实成交价。

## 6. Evidence

- `H:\Asteria-report\trade\2026-05-07\trade-bounded-proof-build-card-20260507-01\closeout.md`
- `H:\Asteria-report\trade\2026-05-07\trade-bounded-proof-build-card-20260507-01\manifest.json`
- `H:\Asteria-report\trade\2026-05-07\trade-bounded-proof-build-card-20260507-01-day-audit-summary.json`
- `H:\Asteria-Validated\Asteria-trade-bounded-proof-build-card-20260507-01.zip`
