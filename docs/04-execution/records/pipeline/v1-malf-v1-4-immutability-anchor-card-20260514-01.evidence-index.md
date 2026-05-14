# V1 MALF v1.4 Immutability Anchor Evidence Index

日期：2026-05-14

run_id：`v1-malf-v1-4-immutability-anchor-card-20260514-01`

## 1. Status

`passed / MALF v1.4 immutability anchored`

## 2. Repo Evidence

| file | role |
|---|---|
| `docs/03-refactor/06-asteria-core-module-recovery-and-proof-roadmap-v1.md` | core recovery / proof route authority and updated second-card state |
| `docs/04-execution/00-conclusion-index-v1.md` | repo conclusion registration with terminal live-next preserved |
| `docs/03-refactor/00-module-gate-ledger-v1.md` | post-terminal route status sync |
| `docs/02-modules/malf/00-authority-design-v1.md` | repo-local MALF v1.4 authority bridge |
| `docs/04-execution/records/malf/malf-v1-4-core-operational-boundary-authority-sync-20260503-01.conclusion.md` | v1.4 authority sync conclusion |
| `docs/04-execution/records/malf/malf-v1-4-core-runtime-sync-implementation-20260505-01.conclusion.md` | v1.4 day runtime-aligned evidence boundary |
| `governance/module_gate_registry.toml` | live terminal truth: `current_allowed_next_card = ""` |

## 3. MALF Authority Evidence

| Artifact | Path | Role |
|---|---|---|
| MALF v1.4 package | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4` | current MALF authority anchor |
| MALF v1.4 archive | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4.zip` | archived authority package |
| Package manifest | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4\MANIFEST.json` | package relationship and forbidden interpretations |
| Bridge | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4\MALF_00_Three_Documents_Bridge_v1_4.md` | v1.4 entrypoint and governance boundary |
| Core baseline | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4\MALF_01_Core_Definitions_Theorems_v1_4.md` | inherited Core semantic baseline |
| Core operational delta | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4\MALF_01B_Core_Operational_Boundary_Rules_v1_4.md` | normative v1.4 operational rules |
| Lifespan baseline | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4\MALF_02_Lifespan_Stats_Definitions_Theorems_v1_4.md` | inherited Lifespan semantics |
| Service baseline | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4\MALF_03_System_Service_Interface_v1_4.md` | readonly WavePosition interface |

## 4. External Evidence

| Artifact | Path |
|---|---|
| Immutability anchor report | `H:\Asteria-report\pipeline\2026-05-14\v1-malf-v1-4-immutability-anchor-card-20260514-01\malf-v1-4-immutability-anchor-report.md` |
| Immutability anchor manifest | `H:\Asteria-report\pipeline\2026-05-14\v1-malf-v1-4-immutability-anchor-card-20260514-01\malf-v1-4-immutability-anchor-manifest.json` |
| Validated archive | `H:\Asteria-Validated\Asteria-v1-malf-v1-4-immutability-anchor-card-20260514-01.zip` |

## 5. Verification Commands

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_asteria_workflow.py --strict
```

## 6. Non-Evidence

本卡不提供：

- MALF runtime execution、schema migration、formal DB rebuild 或 promote；
- Alpha/PAS contract redesign、bounded proof 或收益 proof；
- 历史 Alpha/PAS 代码迁移；
- broker adapter feasibility、真实账户连接或实盘委托；
- 对 `H:\Asteria-data` 的任何 mutation。
