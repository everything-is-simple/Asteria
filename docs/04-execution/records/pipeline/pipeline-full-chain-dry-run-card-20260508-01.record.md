# Pipeline Full-Chain Dry-Run Record

日期：2026-05-08

## 1. 背景

`pipeline-full-chain-dry-run-authorization-scope-freeze-20260508-01` 已通过。
本卡执行 Pipeline 的首个 full-chain dry-run runtime，范围严格限制为
released day bounded surfaces from MALF through System Readout，并且只记录 orchestration metadata。

## 2. 执行摘要

- 扩展 `src\asteria\pipeline`：在保留 `system_readout` 单模块 runtime 的同时，新增 full-chain dry-run request/runtime/audit 分支。
- 新增 `scripts\pipeline\run_pipeline_full_chain_dry_run.py`，并放行 `run_pipeline_record.py --module-scope full_chain_day` 的 audit-only 复审入口。
- full-chain dry-run 只读取 `H:\Asteria-data\system.duckdb` 的 released `system_source_manifest`、`system_module_status_snapshot` 与 live gate registry，不回读业务表去重算业务语义。
- `pipeline.duckdb` 新增 7 步编排记录，顺序固定为 `MALF -> Alpha -> Signal -> Position -> Portfolio Plan -> Trade -> System Readout`。
- promote 逻辑从“整体替换 target DB”改为“向既有 `pipeline.duckdb` 追加当前 run”，保留已通过的 single-module orchestration 历史 run。

## 3. Formal Execution

| stage | 命令摘要 |
|---|---|
| full-chain dry-run | `run_pipeline_full_chain_dry_run.py --run-id pipeline-full-chain-dry-run-card-20260508-01 --source-chain-release-version system-readout-bounded-proof-build-card-20260508-01` |
| resume | `run_pipeline_full_chain_dry_run.py --mode resume --run-id pipeline-full-chain-dry-run-card-20260508-01 ...` |
| audit-only | `run_pipeline_record.py --mode audit-only --module-scope full_chain_day --run-id pipeline-full-chain-dry-run-card-20260508-01 ...` |

执行输入：

| 项 | 值 |
|---|---|
| source_chain_release_version | `system-readout-bounded-proof-build-card-20260508-01` |
| source_system_db | `H:\Asteria-data\system.duckdb` |
| target_pipeline_db | `H:\Asteria-data\pipeline.duckdb` |
| module_scope | `full_chain_day` |
| report_root | `H:\Asteria-report` |
| validated_root | `H:\Asteria-Validated` |

## 4. Result

| item | count |
|---|---:|
| step_count | 7 |
| gate_snapshot_count | 11 |
| manifest_count | 21 |
| audit_count | 7 |
| hard_fail_count | 0 |

## 5. Step Chain

| step_seq | module_name | source_release_version |
|---:|---|---|
| 1 | `malf` | `malf-v1-4-core-runtime-sync-implementation-20260505-01` |
| 2 | `alpha` | `alpha-production-builder-hardening-20260506-01` |
| 3 | `signal` | `signal-production-builder-hardening-20260506-01` |
| 4 | `position` | `position-bounded-proof-build-card-20260506-01` |
| 5 | `portfolio_plan` | `portfolio-plan-bounded-proof-build-card-20260507-01` |
| 6 | `trade` | `trade-bounded-proof-build-card-20260507-01` |
| 7 | `system_readout` | `system-readout-bounded-proof-build-card-20260508-01` |

## 6. Boundary

Pipeline 本卡只记录编排元数据，不回写 MALF / Alpha / Signal / Position / Portfolio Plan /
Trade / System Readout，不定义任何业务字段，不把 gate 状态当作策略状态，也不打开
full-chain bounded proof。

## 7. Evidence

- `H:\Asteria-report\pipeline\2026-05-08\pipeline-full-chain-dry-run-card-20260508-01\closeout.md`
- `H:\Asteria-report\pipeline\2026-05-08\pipeline-full-chain-dry-run-card-20260508-01\manifest.json`
- `H:\Asteria-report\pipeline\2026-05-08\pipeline-full-chain-dry-run-card-20260508-01-audit-summary.json`
- `H:\Asteria-Validated\Asteria-pipeline-full-chain-dry-run-card-20260508-01.zip`
