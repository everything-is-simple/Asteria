# MALF v1.4 Core Operational Boundary Authority Sync Record

run_id: `malf-v1-4-core-operational-boundary-authority-sync-20260503-01`

date: 2026-05-03

## Execution Log

1. Created `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4` from the v1.3 Markdown baseline.
2. Added `MALF_01B_Core_Operational_Boundary_Rules_v1_4.md` with eight Core engineering boundary rules:
   pivot rule version, same-bar event ordering, strict compare policy, candidate refresh/replacement,
   transition primitive context, initial candidate reset, `malf_core_state_snapshot`, and replay determinism.
3. Updated the v1.4 bridge to define the package as v1.3 semantic authority plus v1.4 Core operational boundary addendum.
4. Added `MANIFEST.json` to record package scope, PDF status, runtime evidence boundary, and forbidden interpretations.
5. Synced repo governance docs and registries so current MALF authority points to v1.4.
6. Preserved v1.3 formal-data bounded closeout as current MALF day runtime evidence.
7. Created `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4.zip` containing only the v1.4 authority package contents.

## Scope Control

No Python files, DuckDB schemas, runners, formal DBs, Alpha/Signal/Position/downstream modules,
or pipeline runtime were changed by this card.

## Verification Commands

- `H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py`
- `git diff --check`
- PowerShell zip content inspection for `MALF_Three_Part_Design_Set_v1_4.zip`
- Text searches for v1.3/v1.4 authority and runtime-proof wording
