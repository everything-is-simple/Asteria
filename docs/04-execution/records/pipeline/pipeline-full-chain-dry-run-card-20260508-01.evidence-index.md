# Pipeline Full-Chain Dry-Run Evidence Index

日期：2026-05-08

## 1. Execution Summary

| item | value |
|---|---|
| module | `pipeline` |
| run_id | `pipeline-full-chain-dry-run-card-20260508-01` |
| source release | `system-readout-bounded-proof-build-card-20260508-01` |
| module_scope | `full_chain_day` |
| target DB | `H:\Asteria-data\pipeline.duckdb` |

## 2. Audit Result

| check | result |
|---|---|
| step_count | `7` |
| gate_snapshot_count | `11` |
| manifest_count | `21` |
| audit_count | `7` |
| hard_fail_count | `0` |
| resume reuse | `passed` |
| audit-only rerun | `passed` |

## 3. Step Releases

| module | release |
|---|---|
| `malf` | `malf-v1-4-core-runtime-sync-implementation-20260505-01` |
| `alpha` | `alpha-production-builder-hardening-20260506-01` |
| `signal` | `signal-production-builder-hardening-20260506-01` |
| `position` | `position-bounded-proof-build-card-20260506-01` |
| `portfolio_plan` | `portfolio-plan-bounded-proof-build-card-20260507-01` |
| `trade` | `trade-bounded-proof-build-card-20260507-01` |
| `system_readout` | `system-readout-bounded-proof-build-card-20260508-01` |

## 4. Report Assets

| asset | path |
|---|---|
| closeout | `H:\Asteria-report\pipeline\2026-05-08\pipeline-full-chain-dry-run-card-20260508-01\closeout.md` |
| manifest | `H:\Asteria-report\pipeline\2026-05-08\pipeline-full-chain-dry-run-card-20260508-01\manifest.json` |
| audit summary | `H:\Asteria-report\pipeline\2026-05-08\pipeline-full-chain-dry-run-card-20260508-01-audit-summary.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-pipeline-full-chain-dry-run-card-20260508-01.zip` |

## 5. Boundary

本证据只放行 Pipeline 的 full-chain dry-run orchestration metadata surface。它不授权
full-chain bounded proof、System full build 或任何业务语义写入。
