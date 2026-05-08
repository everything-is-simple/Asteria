# Pipeline Single-Module Orchestration Build Evidence Index

日期：2026-05-08

## 1. Execution Summary

| item | value |
|---|---|
| module | `pipeline` |
| run_id | `pipeline-single-module-orchestration-build-card-20260508-01` |
| source release | `system-readout-bounded-proof-build-card-20260508-01` |
| module_scope | `system_readout` |
| target DB | `H:\Asteria-data\pipeline.duckdb` |

## 2. Audit Result

| check | result |
|---|---|
| step_count | `1` |
| gate_snapshot_count | `6` |
| manifest_count | `5` |
| audit_count | `7` |
| hard_fail_count | `0` |
| resume reuse | `passed` |
| audit-only rerun | `passed` |

## 3. Report Assets

| asset | path |
|---|---|
| closeout | `H:\Asteria-report\pipeline\2026-05-08\pipeline-single-module-orchestration-build-card-20260508-01\closeout.md` |
| manifest | `H:\Asteria-report\pipeline\2026-05-08\pipeline-single-module-orchestration-build-card-20260508-01\manifest.json` |
| audit summary | `H:\Asteria-report\pipeline\2026-05-08\pipeline-single-module-orchestration-build-card-20260508-01-audit-summary.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-pipeline-single-module-orchestration-build-card-20260508-01.zip` |

## 4. Boundary

本证据只放行 Pipeline 的 `system_readout` 单模块 orchestration surface。它不授权 full-chain dry-run、
full-chain bounded proof 或任何业务语义写入。
