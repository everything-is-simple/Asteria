# Portfolio Plan 2024 Coverage Repair Evidence Index

日期：2026-05-10

run_id：`portfolio-plan-2024-coverage-repair-card-20260509-01`

## 1. Repo Records

| evidence | path |
|---|---|
| card | `docs/04-execution/records/portfolio_plan/portfolio-plan-2024-coverage-repair-card-20260509-01.card.md` |
| record | `docs/04-execution/records/portfolio_plan/portfolio-plan-2024-coverage-repair-card-20260509-01.record.md` |
| conclusion | `docs/04-execution/records/portfolio_plan/portfolio-plan-2024-coverage-repair-card-20260509-01.conclusion.md` |
| conclusion index | `docs/04-execution/00-conclusion-index-v1.md` |
| gate ledger | `docs/03-refactor/00-module-gate-ledger-v1.md` |
| roadmap | `docs/03-refactor/04-asteria-full-system-roadmap-v1.md` |
| governance registry | `governance/module_gate_registry.toml` |

## 2. Runtime Evidence

| evidence | path |
|---|---|
| source Position DB | `H:\Asteria-data\position.duckdb` |
| target Portfolio Plan DB | `H:\Asteria-data\portfolio_plan.duckdb` |
| target Trade DB | `H:\Asteria-data\trade.duckdb` |
| live system manifest lock | `H:\Asteria-data\system.duckdb` |
| audit summary | `H:\Asteria-report\portfolio_plan\2026-05-10\portfolio-plan-2024-coverage-repair-card-20260509-01\portfolio-plan-day-audit-summary.json` |
| repair closeout | `H:\Asteria-report\portfolio_plan\2026-05-10\portfolio-plan-2024-coverage-repair-card-20260509-01\closeout.md` |
| repair manifest | `H:\Asteria-report\portfolio_plan\2026-05-10\portfolio-plan-2024-coverage-repair-card-20260509-01\manifest.json` |
| follow-up coverage matrix | `H:\Asteria-report\pipeline\2026-05-10\portfolio-plan-2024-coverage-repair-card-20260509-01-followup-diagnosis\coverage-matrix.json` |
| follow-up attribution | `H:\Asteria-report\pipeline\2026-05-10\portfolio-plan-2024-coverage-repair-card-20260509-01-followup-diagnosis\coverage-attribution.md` |
| validated zip | `H:\Asteria-Validated\Asteria-portfolio-plan-2024-coverage-repair-card-20260509-01.zip` |

## 3. Audit Result

| check | result |
|---|---|
| focus trading dates | `2024-01-02..2024-01-05` |
| admission earliest day | `2024-01-02` |
| target exposure earliest day | `2024-01-05` |
| hard_fail_count | `0` |
| follow-up attribution | `downstream_surface_gap:trade` |
| allowed next action | `trade_2024_coverage_repair_card` |

## 4. Boundary

本证据只证明 released Portfolio Plan day surface 的最小 focus-window repair 已真实执行，并证明
Portfolio Plan 语义断点已下移到 Trade。它不宣称 Trade repair passed、System repair passed、
Portfolio Plan full build、Trade full build、System / Pipeline semantic repair、full rebuild、
daily incremental、resume/idempotence 或 `v1 complete`。
