# Alpha/PAS Bounded Proof Build Card

日期：2026-05-14

## 1. Card Identity

| item | value |
|---|---|
| module | `pipeline` |
| runtime owner | `alpha` |
| run_id | `v1-alpha-pas-bounded-proof-build-card-20260514-01` |
| roadmap card | `v1-alpha-pas-bounded-proof-build-card` |
| card type | `post-terminal / bounded-proof-build` |
| owner | `codex` |

## 2. Objective

在小范围内实现新版 Alpha/PAS bounded proof，证明第 5 卡冻结的
`Alpha_PAS_Design_Set_v1_0` 可以从 MALF v1.4 WavePosition / service facts
落到可审计 PAS 输出。

本卡不写 `H:\Asteria-data`，不改 MALF，不运行收益 proof，不接 broker，
不改变当前 live next。

## 3. Inputs

| input | role |
|---|---|
| `H:\Asteria-data\malf_service_day.duckdb` | read-only MALF v1.4 WavePosition source |
| `H:\Asteria-Validated\Alpha_PAS_Design_Set_v1_0` | frozen Alpha/PAS v1.0 contract |
| `docs/03-refactor/08-alpha-pas-authority-map-v1.md` | authority map |
| `docs/03-refactor/06-asteria-core-module-recovery-and-proof-roadmap-v1.md` | route authority |

## 4. Allowed Actions

- Add Alpha/PAS proof-only contract, rules, artifact writer, and CLI.
- Write proof DB only under `H:\Asteria-temp\alpha_pas\<run_id>`.
- Write report JSON only under `H:\Asteria-report\pipeline\2026-05-14\<run_id>`.
- Create validated evidence zip under `H:\Asteria-Validated`.
- Register repo four-piece and sync roadmap / ledger / conclusion index.

## 5. Forbidden Actions

| forbidden | decision |
|---|---|
| write `H:\Asteria-data` | forbidden |
| rewrite MALF | forbidden |
| migrate historical PAS code | forbidden |
| run return / PnL proof | forbidden |
| emit broker order, fill, account state, position size, portfolio allocation | forbidden |
| change `current live next = none / terminal` | forbidden |

## 6. Pass Criteria

- Proof consumes MALF v1.4 day WavePosition read-only.
- Proof produces `pas_market_context`, `pas_strength_profile`, `pas_trigger_event`,
  `pas_candidate_lifecycle`, `pas_historical_rank_profile`, `pas_entry_candidate`,
  `pas_failure_state`, and `pas_source_lineage`.
- `pas_entry_candidate` includes all required service fields from `Alpha_PAS_Design_Set_v1_0`.
- Forbidden broker / position / portfolio / fill / account / profit fields are absent.
- Completed-wave baseline is separated from in-flight confirmation / invalidation.
- Lifecycle state catalog covers all eight PAS lifecycle states.
- Report, audit, manifest, and validated archive exist.

## 7. Verification Plan

```powershell
H:\Asteria\.venv\Scripts\pytest.exe tests\unit\alpha\test_alpha_pas_bounded_proof.py -q --basetemp H:\Asteria-temp\pytest-tmp-v1-alpha-pas-bounded-proof-build-card-20260514-01 -o cache_dir=H:\Asteria-temp\pytest-cache-v1-alpha-pas-bounded-proof-build-card-20260514-01
H:\Asteria\.venv\Scripts\pytest.exe tests\unit\alpha\test_alpha_bounded_proof_runner.py -q --basetemp H:\Asteria-temp\pytest-tmp-alpha-existing-guard -o cache_dir=H:\Asteria-temp\pytest-cache-alpha-existing-guard
H:\Asteria\.venv\Scripts\ruff.exe check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\ruff.exe format --check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\mypy.exe src --cache-dir H:\Asteria-temp\mypy-cache
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_asteria_workflow.py --strict
git diff --check
```
