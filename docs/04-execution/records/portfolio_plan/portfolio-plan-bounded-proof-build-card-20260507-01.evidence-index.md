# Portfolio Plan Bounded Proof Build Evidence Index

日期：2026-05-07

状态：`passed`

## 1. Evidence Assets

| asset | path |
|---|---|
| report_dir | `H:\Asteria-report\portfolio_plan\2026-05-07\portfolio-plan-bounded-proof-build-card-20260507-01\` |
| manifest | `H:\Asteria-report\portfolio_plan\2026-05-07\portfolio-plan-bounded-proof-build-card-20260507-01\manifest.json` |
| closeout | `H:\Asteria-report\portfolio_plan\2026-05-07\portfolio-plan-bounded-proof-build-card-20260507-01\closeout.md` |
| day audit | `H:\Asteria-report\portfolio_plan\2026-05-07\portfolio-plan-bounded-proof-build-card-20260507-01-day-audit-summary.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-portfolio-plan-bounded-proof-build-card-20260507-01.zip` |

## 2. Formal DB

| item | value |
|---|---|
| target DB | `H:\Asteria-data\portfolio_plan.duckdb` |
| source Position DB | `H:\Asteria-data\position.duckdb` |
| source Position run | `position-bounded-proof-build-card-20260506-01` |
| source Position release | `position-bounded-proof-build-card-20260506-01` |

## 3. Audit Result

| check | result |
|---|---|
| timeframe | `day` |
| bounded scope | `symbol_limit = 5` |
| input_position_count | `1158` |
| admission_count | `1158` |
| target_exposure_count | `5` |
| trim_count | `2` |
| hard_fail_count | `0` |
| allowed next action | `trade_freeze_review` |

## 4. Boundary

本证据只放行 Portfolio Plan day bounded proof。它不授权 Portfolio Plan full build、
Position full build、Trade / System 施工或 full-chain Pipeline runtime。
