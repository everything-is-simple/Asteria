# Data Legacy Source Audit Record

日期：2026-05-02

状态：`passed`

## 1. Execution

执行只读审计：

```powershell
H:\Asteria\.venv\Scripts\python.exe -c "<audit_legacy_raw_base_sources>"
```

审计入口：

```text
src/asteria/data/legacy_audit.py
```

报告输出：

```text
H:\Asteria-report\data\2026-05-02\data-legacy-source-audit-20260502-01\legacy-source-audit.md
H:\Asteria-report\data\2026-05-02\data-legacy-source-audit-20260502-01\legacy-source-audit.json
```

## 2. Result

| timeframe | raw rows | base rows | raw symbols | base symbols | raw-only symbols | base-only symbols |
|---|---:|---:|---:|---:|---:|---:|
| day | 16348113 | 16348113 | 5501 | 5501 | 0 | 0 |
| week | 3453967 | 3453967 | 5501 | 5501 | 0 | 0 |
| month | 826336 | 826336 | 5501 | 5501 | 0 | 0 |

Sidecar availability:

| timeframe | asset | raw rows | base rows | raw symbols | base symbols |
|---|---|---:|---:|---:|---:|
| day | index | 377711 | 377711 | 100 | 100 |
| day | block | 468542 | 468542 | 127 | 127 |
| week | index | 79398 | 79398 | 100 | 100 |
| week | block | 98719 | 98719 | 127 | 127 |
| month | index | 18774 | 18774 | 100 | 100 |
| month | block | 23260 | 23260 | 127 | 127 |

## 3. Boundary

本卡只证明 legacy stock backward raw/base source facts 可作为 Asteria Data Foundation
首轮导入输入。它不创建正式 Data DB，不改变 MALF 当前 release evidence。
