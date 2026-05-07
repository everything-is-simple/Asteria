# Position Bounded Proof Build Evidence Index

日期：2026-05-07

状态：`passed`

## 1. Evidence Assets

| asset | path |
|---|---|
| report_dir | `H:\Asteria-report\position\2026-05-07\position-bounded-proof-build-card-20260506-01\` |
| manifest | `H:\Asteria-report\position\2026-05-07\position-bounded-proof-build-card-20260506-01\manifest.json` |
| closeout | `H:\Asteria-report\position\2026-05-07\position-bounded-proof-build-card-20260506-01\closeout.md` |
| day audit | `H:\Asteria-report\position\2026-05-07\position-bounded-proof-build-card-20260506-01-day-audit-summary.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-position-bounded-proof-build-card-20260506-01.zip` |

## 2. Formal DB

| item | value |
|---|---|
| target DB | `H:\Asteria-data\position.duckdb` |
| source Signal DB | `H:\Asteria-data\signal.duckdb` |
| source Signal run | `signal-production-builder-hardening-20260506-01` |
| source Signal release | `signal-production-builder-hardening-20260506-01` |

## 3. Audit Result

| check | result |
|---|---|
| timeframe | `day` |
| bounded scope | `symbol_limit = 5` |
| input_signal_count | `1158` |
| position_candidate_count | `1158` |
| entry_plan_count | `1004` |
| exit_plan_count | `1004` |
| hard_fail_count | `0` |
| allowed next action | `portfolio_plan_freeze_review` |

## 4. Boundary

本证据只放行 Position day bounded proof。它不授权 Position full build、
Portfolio Plan build、Trade / System 施工或 full-chain Pipeline runtime。
