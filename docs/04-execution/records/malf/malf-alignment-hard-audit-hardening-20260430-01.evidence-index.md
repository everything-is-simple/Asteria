# MALF Alignment Hard Audit Hardening Evidence Index

日期：2026-04-30

状态：`passed`

当前证据状态：`superseded_by malf-complete-alignment-closeout-20260430-01`

本 evidence index 保留为 hard audit 代码增强记录。当前 formal dense DB evidence 以
[malf-complete-alignment-closeout-20260430-01](malf-complete-alignment-closeout-20260430-01.evidence-index.md)
为准。

## 1. 记录入口

| 项 | 值 |
|---|---|
| module | `malf` |
| run_id | `malf-alignment-hard-audit-hardening-20260430-01` |
| status | `passed` |
| card | `docs/04-execution/records/malf/malf-alignment-hard-audit-hardening-20260430-01.card.md` |
| record | `docs/04-execution/records/malf/malf-alignment-hard-audit-hardening-20260430-01.record.md` |
| conclusion | `docs/04-execution/records/malf/malf-alignment-hard-audit-hardening-20260430-01.conclusion.md` |

## 2. Evidence Scope

| 资产 | 路径 |
|---|---|
| code | `src/asteria/malf/audit_engine.py` |
| tests | `tests/unit/malf/test_dense_closeout.py` |
| MALF authority design | `docs/02-modules/malf/00-authority-design-v1.md` |
| gate ledger | `docs/03-refactor/00-module-gate-ledger-v1.md` |
| closeout | `H:\Asteria-report\malf\2026-04-30\malf-alignment-hard-audit-hardening-20260430-01\closeout.md` |
| manifest | `H:\Asteria-report\malf\2026-04-30\malf-alignment-hard-audit-hardening-20260430-01\manifest.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-malf-alignment-hard-audit-hardening-20260430-01.zip` |
| formal DB rerun | `not created; no formal DB rerun` |

## 3. Verification

| 命令 | 结果 |
|---|---|
| `pytest tests/unit/malf -q` | `11 passed` |
| `pytest tests/unit/malf tests/unit/governance -q` | `passed` |
| `scripts/governance/check_project_governance.py` | `passed` |
| `ruff check .` | `passed` |
| `ruff format --check .` | `passed` |
| `mypy src` | `passed` |
| `pytest -q` | `60 passed` |

## 4. Gate Impact

| 项 | 值 |
|---|---|
| MALF dense resolution | `still passed` |
| allowed next action | `Position freeze review reentry` |
| Position bounded proof opened | `no` |
| downstream writeback opened | `no` |
