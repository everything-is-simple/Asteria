# MALF v1.3 Authority Sync Code Revision Record

日期：2026-05-01

状态：`code-only passed`

## 1. Execution Scope

本记录只覆盖 MALF v1.3 代码修订执行：

- `src/asteria/malf/` schema、Core、Lifespan、Service、audit 与 runner contract。
- `governance/module_api_contracts/malf.toml` contract metadata。
- `tests/unit/malf` 单测与回归测试。
- repo 内 card / conclusion / evidence-index 最小落档。

本记录不覆盖正式 DuckDB 重建、promotion 或 release evidence 更新。

## 2. Boundary

| 项 | 结果 |
|---|---|
| formal DB creation | `not performed` |
| formal DB promotion | `not performed` |
| `H:\Asteria-data` promotion | `not touched` |
| current gate change | `none` |
| current allowed next action | `Position freeze review reentry / review-only` |

## 3. Verification Commands

```powershell
H:\Asteria\.venv\Scripts\pytest.exe tests\unit\malf -q --basetemp=H:/Asteria-temp/pytest-tmp-malf-v13-code-revision -o cache_dir=H:/Asteria-temp/pytest-cache-malf-v13-code-revision
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\ruff.exe check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\ruff.exe format --check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\mypy.exe src --cache-dir H:\Asteria-temp\mypy-cache
git diff --check
```

## 4. Links

- [card](malf-v1-3-authority-sync-code-revision-20260501-01.card.md)
- [conclusion](malf-v1-3-authority-sync-code-revision-20260501-01.conclusion.md)
- [evidence-index](malf-v1-3-authority-sync-code-revision-20260501-01.evidence-index.md)
