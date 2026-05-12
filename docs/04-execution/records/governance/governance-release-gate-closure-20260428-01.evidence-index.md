# Governance Release Gate Closure Evidence Index

日期：2026-04-28

## 1. 基本信息

| 项 | 值 |
|---|---|
| module | `governance` |
| run_id | `governance-release-gate-closure-20260428-01` |
| status | `passed` |

## 2. 资产入口

| 资产 | 路径 |
|---|---|
| report_dir | `H:\Asteria-report\governance\2026-04-28\governance-release-gate-closure-20260428-01` |
| closeout | `H:\Asteria-report\governance\2026-04-28\governance-release-gate-closure-20260428-01\closeout.md` |
| manifest | `H:\Asteria-report\governance\2026-04-28\governance-release-gate-closure-20260428-01\manifest.json` |
| gate_snapshot | `not applicable; release gate state is recorded in module gate ledger and conclusion` |
| run_manifest | `not applicable; this run used manifest.json as the evidence manifest` |
| source_manifest | `not applicable; authority sources are declared in this index and card` |
| validated_zip | `H:\Asteria-Validated\2.backups\Asteria-governance-release-gate-closure-20260428-01.zip` |
| docs/code snapshot | `H:\Asteria-Validated\2.backups\Asteria-docs-code-20260428-214427.zip` |
| deep research report | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_0\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.md` |
| MALF authority directory | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2` |
| formal_db | `not applicable; no formal DB created` |

## 3. 关键结果

| 指标 | 值 |
|---|---:|
| governance unit tests | `18 passed` |
| full pytest | `33 passed` |
| release gate check module | `src/asteria/governance/release_gates.py` |
| release gate regression tests | `5` |

## 4. 关键审计

| 项 | 值 |
|---|---|
| project governance | `passed` |
| ruff check | `passed` |
| ruff format check | `passed` |
| mypy src | `passed` |
| Alpha construction opened | `no` |
| downstream construction opened | `no` |
| allowed next action | `Alpha freeze review` |
| conclusion index registered | `yes` |

## 5. 关联记录

- [card](governance-release-gate-closure-20260428-01.card.md)
- [record](governance-release-gate-closure-20260428-01.record.md)
- [conclusion](governance-release-gate-closure-20260428-01.conclusion.md)
