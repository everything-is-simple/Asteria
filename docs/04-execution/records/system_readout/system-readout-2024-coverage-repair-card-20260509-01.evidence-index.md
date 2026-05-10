# System Readout 2024 Coverage Repair Evidence Index

日期：2026-05-10

run_id：`system-readout-2024-coverage-repair-card-20260509-01`

## 1. Repo Records

| evidence | path |
|---|---|
| card | `docs/04-execution/records/system_readout/system-readout-2024-coverage-repair-card-20260509-01.card.md` |
| record | `docs/04-execution/records/system_readout/system-readout-2024-coverage-repair-card-20260509-01.record.md` |
| conclusion | `docs/04-execution/records/system_readout/system-readout-2024-coverage-repair-card-20260509-01.conclusion.md` |
| conclusion index | `docs/04-execution/00-conclusion-index-v1.md` |
| gate ledger | `docs/03-refactor/00-module-gate-ledger-v1.md` |
| roadmap | `docs/03-refactor/04-asteria-full-system-roadmap-v1.md` |
| governance registry | `governance/module_gate_registry.toml` |

## 2. Runtime Evidence

| evidence | path |
|---|---|
| source system db | `H:\Asteria-data\system.duckdb` |
| audit summary | `H:\Asteria-report\system_readout\2026-05-10\system-readout-2024-coverage-repair-card-20260509-01\system-readout-day-audit-summary.json` |
| repair closeout | `H:\Asteria-report\system_readout\2026-05-10\system-readout-2024-coverage-repair-card-20260509-01\closeout.md` |
| repair manifest | `H:\Asteria-report\system_readout\2026-05-10\system-readout-2024-coverage-repair-card-20260509-01\manifest.json` |
| follow-up coverage matrix | `H:\Asteria-report\pipeline\2026-05-10\system-readout-2024-coverage-repair-card-20260509-01-followup-diagnosis\coverage-matrix.json` |
| follow-up attribution | `H:\Asteria-report\pipeline\2026-05-10\system-readout-2024-coverage-repair-card-20260509-01-followup-diagnosis\coverage-attribution.md` |
| validated zip | `H:\Asteria-Validated\Asteria-system-readout-2024-coverage-repair-card-20260509-01.zip` |

## 3. Audit Result

| check | result |
|---|---|
| focus trading dates | `2024-01-02..2024-01-05` |
| released system earliest day | `2024-01-02` |
| hard_fail_count | `0` |
| source_manifest_count | `10` |
| module_status_count | `6` |
| readout_count | `4637` |
| summary_count | `4637` |
| audit_snapshot_count | `6` |
| follow-up next card | `pipeline-year-replay-source-selection-repair-card-20260509-01` |
| follow-up attribution | `calendar_semantic_gap_only` |

## 4. Boundary

本证据只证明 released System Readout day surface 的最小 focus-window repair 已真实执行，并证明
System Readout 语义断点已下移到 Pipeline source selection repair。它不宣称 System full build、
Pipeline semantic repair、full rebuild、daily incremental、resume/idempotence 或 `v1 complete`。
