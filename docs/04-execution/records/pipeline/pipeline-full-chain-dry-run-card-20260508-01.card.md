# Pipeline Full-Chain Dry-Run Card

日期：2026-05-08

状态：`prepared / not executed`

## 1. 背景

`pipeline-full-chain-dry-run-authorization-scope-freeze-20260508-01` 已通过。
本卡是当前唯一允许恢复的下一张卡，但尚未执行。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `pipeline-full-chain-dry-run-card-20260508-01` |
| stage | `full-chain-dry-run / prepared / not executed` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| prerequisite conclusion | `docs/04-execution/records/pipeline/pipeline-full-chain-dry-run-authorization-scope-freeze-20260508-01.conclusion.md` |
| source releases | `released day bounded surfaces from MALF through System Readout` |
| runtime scope | `full-chain dry-run only; orchestration metadata only` |
| target DB path | `H:\Asteria-data\pipeline.duckdb` |
| working path | `H:\Asteria-temp\pipeline\<run_id>\` |

## 4. 目标

- 只在 full-chain dry-run 范围内记录 Pipeline orchestration metadata。
- 审计全链路步骤顺序、checkpoint、manifest 与 gate snapshot 一致性。
- 不写业务语义字段，不重算或改写任何业务模块正式结果。

## 5. 当前仍禁止

- 不得把本卡解释为 `passed`。
- 不得把 dry-run 结果解释为 bounded proof。
- 不得绕过后续门禁直接进入 full-chain bounded proof。
