# Alpha/PAS Source Inventory Card

日期：2026-05-14

## 1. Card Identity

| item | value |
|---|---|
| module | `pipeline` |
| run_id | `v1-alpha-pas-source-inventory-card-20260514-01` |
| roadmap card | `v1-alpha-pas-source-inventory-card` |
| card type | `post-terminal / source-inventory / read-only` |
| owner | `codex` |

## 2. Objective

只读盘点 Alpha/PAS 来源材料，为下一张 `v1-alpha-pas-authority-map-card` 提供可审计输入。

本卡只输出 source inventory，不冻结新版 Alpha/PAS contract，不迁移历史代码，
不执行收益 proof，不接 broker。

## 3. Scope

| source group | path |
|---|---|
| current Asteria Alpha | `docs/02-modules/alpha`; `src/asteria/alpha`; `scripts/alpha`; `tests/unit/alpha`; `docs/04-execution/records/alpha` |
| current formal Alpha evidence | `H:\Asteria-data\alpha_*.duckdb` |
| historical systems | `G:\malf-history\*`; `H:\Asteria-Validated\MALF-system-history` |
| book / reference roots | `G:\《股市浮沉二十载》\2020.(Au)LanceBeggs`; `2021.Bob_Volman外汇超短线交易`; `2018.(CHINA)简简单单做股票` |
| YTC chapter anchors | 卷 2 第 3 章；卷 3 第 4 / 5 章 |
| sufficiency rereview | historical PAS runtime/docs, YTC, Bob Volman, and A 股历史系统是否足以定义独立 PAS 语义层 |

## 4. Explicit Non-Changes

| item | decision |
|---|---|
| `governance/module_gate_registry.toml` | not changed |
| `H:\Asteria-data` | not written |
| historical code migration | not opened |
| book content copying | not allowed |
| Alpha/PAS contract redesign | not executed |
| T+1 return proof | not executed |
| broker adapter feasibility | still deferred |

## 5. Pass Criteria

- `docs/03-refactor/07-alpha-pas-source-inventory-v1.md` exists and lists current / historical / reference source roots.
- Inventory records the PAS split between completed-wave baseline and in-flight confirmation.
- Inventory records `sufficient_for_definition` but not legacy migration, profit proof, or broker readiness.
- Roadmap marks card 3 as passed and card 4 as prepared next route card.
- Gate ledger and conclusion index register this post-terminal route card while preserving live next as `none / terminal`.
- External report, manifest, and validated archive are produced.

## 6. Verification Plan

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_asteria_workflow.py --strict
```

本卡只改 Markdown 与 repo 外 evidence，不执行 runtime、不改 Python、不写正式 DB。
若治理检查暴露代码或测试期望漂移，再扩大到 targeted pytest。
