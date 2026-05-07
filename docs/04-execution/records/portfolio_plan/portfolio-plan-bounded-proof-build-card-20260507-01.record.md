# Portfolio Plan Bounded Proof Build Record

日期：2026-05-07

状态：`passed`

## 1. Scope

本卡只施工 Portfolio Plan bounded proof。它承接
`portfolio-plan-freeze-review-20260507-01`，只读消费
`H:\Asteria-data\position.duckdb` 的 released Position bounded proof surface。

本卡不执行 Portfolio Plan full build，不创建 Trade / System / Pipeline 正式 runner
或正式 DB。

## 2. Implementation Summary

- 新增 `src\asteria\portfolio_plan` 最小 bounded proof 包：contracts、schema、rules、audit、bootstrap。
- 新增 `scripts\portfolio_plan` 三个 runner wrapper：build、audit、bounded proof。
- Portfolio Plan 输入锁定 `source_position_run_id = position-bounded-proof-build-card-20260506-01`。
- Portfolio Plan 输出只包含 position snapshot、constraint、admission、target exposure、
  trim 与审计表面。
- hard audit 覆盖 Position source、source run lock、自然键唯一、admission/exposure/trim
  traceability、rule version traceability、禁用 Trade/System/order/fill 字段和 bounded sample
  场景覆盖。

## 3. Formal Execution

| stage | 命令摘要 |
|---|---|
| bounded proof | `run_portfolio_plan_bounded_proof.py --mode bounded --run-id portfolio-plan-bounded-proof-build-card-20260507-01 --symbol-limit 5` |

执行输入：

| 项 | 值 |
|---|---|
| source_position_db | `H:\Asteria-data\position.duckdb` |
| source_position_run_id | `position-bounded-proof-build-card-20260506-01` |
| target_portfolio_plan_db | `H:\Asteria-data\portfolio_plan.duckdb` |
| report_root | `H:\Asteria-report` |
| validated_root | `H:\Asteria-Validated` |
| timeframe | `day` |
| bounded scope | `symbol_limit = 5` |

## 4. Result

| item | count |
|---|---:|
| input_position_count | 1158 |
| admission_count | 1158 |
| target_exposure_count | 5 |
| trim_count | 2 |
| hard_fail_count | 0 |

Admission 状态分布：

| state | count |
|---|---:|
| admitted | 3 |
| expired | 999 |
| rejected | 154 |
| trimmed | 2 |

## 5. Evidence

| artifact | path |
|---|---|
| report dir | `H:\Asteria-report\portfolio_plan\2026-05-07\portfolio-plan-bounded-proof-build-card-20260507-01\` |
| validated zip | `H:\Asteria-Validated\Asteria-portfolio-plan-bounded-proof-build-card-20260507-01.zip` |
| audit summary | `H:\Asteria-report\portfolio_plan\2026-05-07\portfolio-plan-bounded-proof-build-card-20260507-01-day-audit-summary.json` |

## 6. Boundary

本卡只放行 Portfolio Plan day bounded proof surface。它不授权 Portfolio Plan full build、
Position full build、Trade/System 施工或 full-chain Pipeline runtime。
