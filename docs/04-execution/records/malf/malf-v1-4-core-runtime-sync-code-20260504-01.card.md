# MALF v1.4 Core Runtime Sync Code Card

日期：2026-05-04

状态：`code-only executed / formal rebuild not performed`

## 1. 背景

`MALF_Three_Part_Design_Set_v1_4` 已明确 Core operational boundary authority，但当前
runtime 仍停留在 `malf-v1-3-formal-rebuild-closeout-20260502-01` 的 day formal-data
evidence。本卡只执行 day 范围内的 v1.4 Core runtime sync 代码同步。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `malf` |
| run_id | `malf-v1-4-core-runtime-sync-code-20260504-01` |
| stage | `runtime-sync / code-card` |
| status | `code-only executed / formal rebuild not performed` |
| authority source | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4` |
| current runtime evidence baseline | `malf-v1-3-formal-rebuild-closeout-20260502-01` |

## 3. 本卡允许动作

- 修订 `src/asteria/malf/` 的 day Core / Lifespan / Service / audit / bootstrap。
- 修订 `scripts/malf/` 的 runner contract 参数承载。
- 修订 `tests/unit/malf/`，以 v1.4 gap 为主测试面。
- 修订 `docs/02-modules/malf/` 与 `governance/module_api_contracts/malf.toml`。
- 更新 repo 内 execution 四件套、gate ledger、conclusion index、registry，把 active module 切回 MALF。

## 4. 本卡必须收掉的 5 个 gap

1. break 改为 bar-level 判定，pivot 只负责结构与 confirmation。
2. 新增 `malf_core_state_snapshot` 作为 Core 当前状态读取面。
3. 为 request / run ledger / pivot ledger / audit payload 补齐 `pivot_detection_rule_version`、`core_event_ordering_version`、`price_compare_policy`、`epsilon_policy`。
4. 让 `malf_structure_ledger.reference_pivot_id` 按 `active_wave / transition_candidate / initial_candidate` 上下文派生。
5. 为 `malf_candidate_ledger` 增加显式 `candidate_event_type`。

## 5. 禁止动作

- 不得执行正式 DuckDB rebuild 或 promote。
- 不得声明 `v1.4 day runtime proof passed`。
- 不得扩张到 week / month。
- 不得打开 Alpha / Signal / Position / downstream 施工。
- 不得把本卡当成第二张 formal rebuild closeout 卡。

## 6. 验证命令

```powershell
H:\Asteria\.venv\Scripts\pytest.exe tests\unit\malf --basetemp=H:/Asteria-temp/pytest-tmp-malf-v14-all2 -o cache_dir=H:/Asteria-temp/pytest-cache-malf-v14-all2
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\ruff.exe check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\ruff.exe format --check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\mypy.exe src --cache-dir H:\Asteria-temp\mypy-cache
git diff --check
```

## 7. 本卡执行后门禁目标

| 项 | 目标 |
|---|---|
| current active mainline module | `malf` |
| current allowed next card | `malf_v1_4_core_formal_rebuild_closeout` |
| current runtime evidence | 仍为 `malf-v1-3-formal-rebuild-closeout-20260502-01` |
| Position freeze review reentry | `paused by MALF runtime sync` |
