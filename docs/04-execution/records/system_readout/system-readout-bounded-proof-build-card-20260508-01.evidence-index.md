# System Readout Bounded Proof Build Evidence Index

日期：2026-05-08

## 1. Execution Summary

| item | value |
|---|---|
| module | `system_readout` |
| run_id | `system-readout-bounded-proof-build-card-20260508-01` |
| source release | `trade-bounded-proof-build-card-20260507-01` |
| source DB count | `10` |
| target DB | `H:\Asteria-data\system.duckdb` |

## 2. Audit Result

| check | result |
|---|---|
| source_manifest_count | `10` |
| module_status_count | `6` |
| readout_count | `4633` |
| summary_count | `4633` |
| audit_snapshot_count | `6` |
| hard_fail_count | `0` |
| real sample status coverage | `complete`; `partial` |
| fixture-only status coverage | `source_gap`; `audit_gap` |

## 3. Report Assets

| asset | path |
|---|---|
| closeout | `H:\Asteria-report\system_readout\2026-05-08\system-readout-bounded-proof-build-card-20260508-01\closeout.md` |
| manifest | `H:\Asteria-report\system_readout\2026-05-08\system-readout-bounded-proof-build-card-20260508-01\manifest.json` |
| audit summary | `H:\Asteria-report\system_readout\2026-05-08\system-readout-bounded-proof-build-card-20260508-01-day-audit-summary.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-system-readout-bounded-proof-build-card-20260508-01.zip` |

## 4. Boundary

本证据只放行 System Readout day bounded proof。它不授权 System full build、Pipeline
runtime、single-module orchestration build 或 full-chain pipeline。
