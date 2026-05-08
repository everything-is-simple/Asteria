# Pipeline Single-Module Orchestration Build Card

日期：2026-05-08

状态：`prepared / not executed`

## 1. 背景

`pipeline-build-runtime-authorization-scope-freeze-20260508-01` 已把 Pipeline 的下一步授权范围冻结为
single-module orchestration build first。本卡是当前唯一已准备但未执行的 Pipeline runtime 入口。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `pipeline-single-module-orchestration-build-card-20260508-01` |
| stage | `single-module-orchestration-build / prepared / not executed` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| prerequisite conclusion | `docs/04-execution/records/pipeline/pipeline-build-runtime-authorization-scope-freeze-20260508-01.conclusion.md` |
| source docs | `docs/02-modules/pipeline/00-authority-design-v1.md` through `05-build-card-v1.md` |
| runtime scope | `one module per run; orchestration metadata only` |
| target DB path | `H:\Asteria-data\pipeline.duckdb` |
| working path | `H:\Asteria-temp\pipeline\<run_id>\` |

## 4. 权威边界

| 项 | 值 |
|---|---|
| upstream semantics | `orchestration and record only` |
| formal DB permission | `may be created only when this card is explicitly executed` |
| allowed run modes | `bounded`; `resume`; `audit-only` |
| required module scope | `exactly one module per run` |

## 5. 本卡允许

- 在未来执行时创建最小 Pipeline runner、schema、audit 和测试。
- 在未来执行时只记录单模块 scope 的 pipeline_run / pipeline_step_run / module_gate_snapshot / build_manifest。
- 在 future execution 中验证 active module lock、gate snapshot traceability 与 no business-semantic writeback。

## 6. 本卡仍禁止

- 不直接执行 full-chain dry-run 或 full-chain bounded proof。
- 不让一个 run 同时施工多个主线模块。
- 不修改任何业务模块代码、DB 或正式输出。
- 不把 step status、gate snapshot 或 manifest 字段解释成业务语义。

## 7. 验收与后续门禁

本卡若在后续 turn 被执行，必须形成完整四件套：

```text
card
record
evidence-index
conclusion
```

single-module orchestration build 若通过，才允许讨论是否另开 full-chain dry-run 授权卡。

## 8. 验收命令

本卡和门禁状态更新后必须运行：

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
```

实际执行 single-module orchestration build 前还必须运行：

```powershell
H:\Asteria\.venv\Scripts\ruff.exe check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\ruff.exe format --check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\mypy.exe src --cache-dir H:\Asteria-temp\mypy-cache
H:\Asteria\.venv\Scripts\pytest.exe --basetemp=H:/Asteria-temp/pytest-tmp-pipeline-single-module-20260508-01 -o cache_dir=H:/Asteria-temp/pytest-cache-pipeline-single-module-20260508-01
```

## 9. 关联入口

- [scope freeze conclusion](pipeline-build-runtime-authorization-scope-freeze-20260508-01.conclusion.md)
- [gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
- [conclusion index](../../00-conclusion-index-v1.md)
