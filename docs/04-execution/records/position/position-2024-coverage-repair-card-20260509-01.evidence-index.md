# Position 2024 Coverage Repair Evidence Index

日期：2026-05-10

run_id：`position-2024-coverage-repair-card-20260509-01`

## 1. Repo Records

| evidence | path |
|---|---|
| card | `docs/04-execution/records/position/position-2024-coverage-repair-card-20260509-01.card.md` |
| record | `docs/04-execution/records/position/position-2024-coverage-repair-card-20260509-01.record.md` |
| conclusion | `docs/04-execution/records/position/position-2024-coverage-repair-card-20260509-01.conclusion.md` |
| conclusion index | `docs/04-execution/00-conclusion-index-v1.md` |
| gate ledger | `docs/03-refactor/00-module-gate-ledger-v1.md` |
| roadmap | `docs/03-refactor/04-asteria-full-system-roadmap-v1.md` |
| governance registry | `governance/module_gate_registry.toml` |

## 2. Runtime Evidence

| evidence | path |
|---|---|
| source Signal DB | `H:\Asteria-data\signal.duckdb` |
| target Position DB | `H:\Asteria-data\position.duckdb` |
| live system manifest lock | `H:\Asteria-data\system.duckdb` |
| audit summary | `H:\Asteria-report\position\2026-05-10\position-2024-coverage-repair-card-20260509-01\position-day-audit-summary.json` |
| repair closeout | `H:\Asteria-report\position\2026-05-10\position-2024-coverage-repair-card-20260509-01\closeout.md` |
| repair manifest | `H:\Asteria-report\position\2026-05-10\position-2024-coverage-repair-card-20260509-01\manifest.json` |
| follow-up coverage matrix | `H:\Asteria-report\pipeline\2026-05-10\position-2024-coverage-repair-card-20260509-01-followup-diagnosis\coverage-matrix.json` |
| follow-up attribution | `H:\Asteria-report\pipeline\2026-05-10\position-2024-coverage-repair-card-20260509-01-followup-diagnosis\coverage-attribution.md` |
| validated zip | `H:\Asteria-Validated\Asteria-position-2024-coverage-repair-card-20260509-01.zip` |

## 3. Audit Result

| check | result |
|---|---|
| focus trading dates | `2024-01-02..2024-01-05` |
| candidate earliest day | `2024-01-02` |
| entry earliest day | `2024-01-04` |
| exit earliest day | `2024-01-04` |
| hard_fail_count | `0` |
| follow-up attribution | `downstream_surface_gap:position` |
| allowed next action | `position_2024_coverage_repair_card` |

## 4. Boundary

本证据只证明 released Position day surface 的最小 focus-window repair 已真实执行，并证明
Position candidate surface 已前移到 `2024-01-02`。它不宣称 Position full build、
Portfolio Plan repair passed、Trade repair passed、System / Pipeline semantic repair、full rebuild、
daily incremental、resume/idempotence 或 `v1 complete`。
