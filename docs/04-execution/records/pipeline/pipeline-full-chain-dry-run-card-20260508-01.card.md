# Pipeline Full-Chain Dry-Run Card

日期：2026-05-08

状态：`passed`

## 1. 背景

`pipeline-full-chain-dry-run-authorization-scope-freeze-20260508-01` 已通过。
本卡已执行通过。它只证明 Pipeline 在 released day bounded surfaces 上完成了一次全链路 dry-run，
并且只记录 orchestration metadata。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `pipeline-full-chain-dry-run-card-20260508-01` |
| stage | `full-chain-dry-run / passed` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| prerequisite conclusion | `docs/04-execution/records/pipeline/pipeline-full-chain-dry-run-authorization-scope-freeze-20260508-01.conclusion.md` |
| source releases | `released day bounded surfaces from MALF through System Readout` |
| runtime scope | `full-chain dry-run only; orchestration metadata only` |
| target DB path | `H:\Asteria-data\pipeline.duckdb` |
| working path | `H:\Asteria-temp\pipeline\<run_id>\` |

## 4. Result

| 项 | 结果 |
|---|---|
| step_count | `7` |
| gate_snapshot_count | `11` |
| manifest_count | `21` |
| audit_count | `7` |
| hard_fail_count | `0` |
| resume reuse | `passed` |
| audit-only rerun | `passed` |

## 5. Boundary

- 只在 full-chain dry-run 范围内记录 Pipeline orchestration metadata。
- 不写业务语义字段，不重算或改写任何业务模块正式结果。
- 不得把 dry-run 结果解释为 bounded proof。
- 不得绕过后续门禁直接进入 full-chain bounded proof。
