# Data Legacy Source Audit Evidence Index

日期：2026-05-02

状态：`passed / audit-only evidence`

## 1. Evidence Assets

| asset | path |
|---|---|
| run_id | `data-legacy-source-audit-20260502-01` |
| report_dir | `H:\Asteria-report\data\2026-05-02\data-legacy-source-audit-20260502-01` |
| closeout | `H:\Asteria-report\data\2026-05-02\data-legacy-source-audit-20260502-01\closeout.md` |
| manifest | `H:\Asteria-report\data\2026-05-02\data-legacy-source-audit-20260502-01\manifest.json` |
| source_audit_report | `H:\Asteria-report\data\2026-05-02\data-legacy-source-audit-20260502-01\legacy-source-audit.md` |
| source_audit_json | `H:\Asteria-report\data\2026-05-02\data-legacy-source-audit-20260502-01\legacy-source-audit.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-data-legacy-source-audit-20260502-01.zip` |

## 2. Repo Evidence

| 类别 | 入口 |
|---|---|
| card | [card](data-legacy-source-audit-20260502-01.card.md) |
| record | [record](data-legacy-source-audit-20260502-01.record.md) |
| conclusion | [conclusion](data-legacy-source-audit-20260502-01.conclusion.md) |
| audit code | `src/asteria/data/legacy_audit.py` |
| tests | `tests/unit/data/test_legacy_audit.py` |

## 3. External Evidence

| 类别 | 路径 |
|---|---|
| report_md | `H:\Asteria-report\data\2026-05-02\data-legacy-source-audit-20260502-01\legacy-source-audit.md` |
| report_json | `H:\Asteria-report\data\2026-05-02\data-legacy-source-audit-20260502-01\legacy-source-audit.json` |

## 4. Non-Evidence

- No formal Asteria Data Foundation DuckDB was created.
- No MALF DB was rebuilt.
- No downstream module construction was opened.
