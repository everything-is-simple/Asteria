# Alpha/PAS Contract Redesign Card

日期：2026-05-14

## 1. Card Identity

| item | value |
|---|---|
| module | `pipeline` |
| run_id | `v1-alpha-pas-contract-redesign-card-20260514-01` |
| roadmap card | `v1-alpha-pas-contract-redesign-card` |
| card type | `post-terminal / roadmap-only / contract-freeze` |
| owner | `codex` |

## 2. Objective

冻结 `Alpha_PAS_Design_Set_v1_0` 与新版 Alpha/PAS 文档合同，使后续
`v1-alpha-pas-bounded-proof-build-card` 可以按明确合同实现 bounded proof。

本卡只冻结定义包和 service surface，不迁移历史代码，不执行 runtime，
不写正式 DB，不证明收益，不接 broker。

## 3. Inputs

| input | role |
|---|---|
| `docs/03-refactor/06-asteria-core-module-recovery-and-proof-roadmap-v1.md` | route authority and card order |
| `docs/03-refactor/08-alpha-pas-authority-map-v1.md` | authority map input |
| `docs/04-execution/records/pipeline/v1-alpha-pas-authority-map-card-20260514-01.conclusion.md` | predecessor conclusion |
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4` | immutable MALF authority anchor |

## 4. Allowed Actions

- Create `H:\Asteria-Validated\Alpha_PAS_Design_Set_v1_0`.
- Create `H:\Asteria-Validated\Alpha_PAS_Design_Set_v1_0.zip`.
- Freeze the Alpha/PAS service surface for Signal and T+1 open proof.
- Register repo four-piece, report / manifest, and validated evidence archive.
- Sync roadmap, module gate ledger, and conclusion index.

## 5. Forbidden Actions

| forbidden | decision |
|---|---|
| write `H:\Asteria-data` | forbidden |
| migrate historical code | forbidden |
| run Alpha/PAS bounded proof | forbidden |
| create runtime schema | forbidden |
| claim return / PnL / broker readiness | forbidden |
| emit position size / portfolio allocation / broker order / fill / account state | forbidden |

## 6. Pass Criteria

- `Alpha_PAS_Design_Set_v1_0` exists with all required package files and `MANIFEST.json`.
- Contract includes source lineage, rule version, confidence / strength, reason code, and T+1 open hint fields.
- Contract explicitly consumes MALF v1.4 WavePosition / service facts and setup-time visible facts.
- Contract can be consumed by Signal and T+1 proof.
- Contract does not output position, portfolio, order, fill, account, profit, or broker state.
- Roadmap marks card 5 as passed and card 6 as prepared next route card.
- Gate ledger and conclusion index register the card while preserving live next as `none / terminal`.

## 7. Verification Plan

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_asteria_workflow.py --strict
git diff --check
```

This card changes Markdown, manifest, report, and validated package assets only.
It does not touch Python, schema, runner, tests, or formal DuckDB assets.
