# Alpha/PAS Authority Map Card

日期：2026-05-14

## 1. Card Identity

| item | value |
|---|---|
| module | `pipeline` |
| run_id | `v1-alpha-pas-authority-map-card-20260514-01` |
| roadmap card | `v1-alpha-pas-authority-map-card` |
| card type | `post-terminal / roadmap-only / read-only / authority-map` |
| owner | `codex` |

## 2. Objective

把当前 Alpha、历史 PAS 系统、YTC / Bob Volman / A 股经验与 MALF v1.4
映射成 Asteria 自己的 Alpha/PAS authority map。

本卡只冻结 authority map，不冻结新版 Alpha/PAS contract，不迁移历史代码，
不执行收益 proof，不接 broker。

## 3. Scope

| source group | path / anchor |
|---|---|
| route authority | `docs/03-refactor/06-asteria-core-module-recovery-and-proof-roadmap-v1.md` |
| predecessor inventory | `docs/03-refactor/07-alpha-pas-source-inventory-v1.md` |
| MALF authority | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4` |
| current Alpha surface | `docs/02-modules/alpha`; `src/asteria/alpha`; `H:\Asteria-data\alpha_*.duckdb` |
| historical PAS systems | `G:\malf-history\MarketLifespan-Quant`; `EmotionQuant-gamma`; `astock_lifespan-alpha` |
| book / reference anchors | YTC 卷 2 第 3 章；YTC 卷 3 第 4 / 5 章；Bob Volman references；A 股实操参考 |

## 4. Explicit Non-Changes

| item | decision |
|---|---|
| `governance/module_gate_registry.toml` | sanity check only, not changed |
| `H:\Asteria-data` | not written |
| historical code migration | not opened |
| book content copying | not allowed |
| Alpha/PAS contract redesign | not executed |
| T+1 return proof | not executed |
| broker adapter feasibility | still deferred |

## 5. Pass Criteria

- `docs/03-refactor/08-alpha-pas-authority-map-v1.md` exists and maps source classes to Asteria Alpha/PAS semantics.
- Authority map distinguishes `must_keep`、`needs_strengthening`、`contract_redesign_input`、`future_enhancement`、`retained_gap` and `rejected_or_not_applicable`.
- Authority map freezes completed-wave baseline versus in-flight confirmation.
- Authority map identifies `sword_blank / 剑胚` and `entry_level_a_share_survival_sword_candidate`.
- Authority map gives `source_sufficiency = sufficient_for_definition / insufficient_for_migration_or_profit_proof`.
- Roadmap marks card 4 as passed and card 5 as prepared next route card.
- Gate ledger and conclusion index register this post-terminal route card while preserving live next as `none / terminal`.
- External report, manifest, and validated archive are produced.

## 6. Verification Plan

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_asteria_workflow.py --strict
```

本卡只改 Markdown 与 repo 外 evidence，不执行 runtime、不改 Python、不写正式 DB。
若治理检查暴露代码或测试期望漂移，再扩大到 targeted pytest。
