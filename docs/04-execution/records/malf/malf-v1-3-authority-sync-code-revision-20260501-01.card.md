# MALF v1.3 Authority Sync Code Revision Card

日期：2026-05-01

状态：`code-only executed / no formal DB promotion`

## 1. 背景

`H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_3` 已形成新的 MALF 权威定义包。
本包明确了 `current_effective_HL/LH`、transition 双边界、active candidate guard、
progress confirmation、birth descriptors 与 Service 只读追溯字段。

本卡执行 MALF v1.3 代码修订范围。它不创建或 promote 正式 DuckDB，不改变当前 gate。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `malf` |
| run_id | `malf-v1-3-authority-sync-code-revision-20260501-01` |
| stage | `authority-sync / code-revision-card` |
| status | `code-only executed / no formal DB promotion` |
| owner | `Asteria governance` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| authority source | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_3` |
| repo docs | `docs/02-modules/malf/` |
| implementation scope | `src/asteria/malf/`; `scripts/malf/`; `tests/unit/malf/`; `governance/module_api_contracts/malf.toml` |
| formal DB scope | not allowed in this code-only execution |
| current evidence baseline | `malf-complete-alignment-closeout-20260430-01` |

## 4. 权威边界

| 项 | 裁决 |
|---|---|
| upstream semantics | MALF v1.3 authority definitions |
| downstream writeback | forbidden |
| current allowed next action before this card | `Position freeze review reentry / review-only` |
| gate effect | none |

本卡不得被解释为 Alpha full build、Signal full build、Position construction、下游施工或
full-chain pipeline 授权。

## 5. 允许动作

- 同步 MALF v1.3 到 `docs/02-modules/malf/`。
- 修订 MALF Core / Lifespan / Service schema 与实现以覆盖 v1.3 字段。
- 修订 runner mode enforcement。
- 修订 MALF API contract metadata。
- 扩展 hard audit 与 MALF unit tests。
- 落档 code-only conclusion，作为后续正式 evidence 重建前的代码修订结论。

## 6. 禁止动作

- 不得在未执行代码修订和审计前声明 MALF v1.3 passed。
- 不得让 build runner 的 `audit-only` 写业务表。
- 不得让 `segmented` 在无 scope 的情况下执行。
- 不得让 Alpha、Signal、Position、Portfolio、Trade、System 写回 MALF。
- 不得把 `wave_core_state` 与 `system_state` 合并。
- 不得在本 prepared card 中创建或 promote 正式 DuckDB。

## 7. Required Fixes

| Finding / v1.3 delta | Required fix |
|---|---|
| Runner modes are accepted but not enforced | build runner 必须拒绝 `audit-only`；`segmented` 必须有 segmented scope |
| API contract metadata lags closeout | `malf.toml` release evidence 与 advertised modes 必须对齐当前事实 |
| v1.3 transition boundary | Core transition ledger、Service WavePosition、audit 必须覆盖 `transition_boundary_high/low` |
| v1.3 candidate lifecycle | candidate replacement 与 progress confirmation 必须可追溯 |
| v1.3 birth descriptors | Lifespan / Service 必须发布并审计 birth descriptor 字段 |

## 8. Test Plan

```powershell
H:\Asteria\.venv\Scripts\pytest.exe tests\unit\malf -q --basetemp=H:/Asteria-temp/pytest-tmp-malf-v13-code-revision -o cache_dir=H:/Asteria-temp/pytest-cache-malf-v13-code-revision
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\ruff.exe check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\ruff.exe format --check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\mypy.exe src --cache-dir H:\Asteria-temp\mypy-cache
```

本卡不新增正式 DB evidence index。若后续单独授权正式 DB 重建，必须另开执行记录、
evidence index 与 conclusion，并明确 promotion 边界。

## 9. 执行结果

| 项 | 结果 |
|---|---|
| code revision | `passed by unit/governance/static checks` |
| formal DB creation / promotion | `not performed` |
| v1.3 release evidence | `not claimed` |
| gate effect | `none` |
| current allowed next action | `Position freeze review reentry / review-only` |

本卡只证明 MALF v1.3 代码修订面已通过本地单测、治理检查与静态检查；它不替代
`malf-complete-alignment-closeout-20260430-01` 的当前正式 release evidence。

## 10. 关联入口

- [MALF v1.3 sync plan](../../../02-modules/malf/07-v1-3-authority-sync-and-code-revision-plan.md)
- [gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
- [conclusion index](../../00-conclusion-index-v1.md)
