# Signal/PAS Contract Alignment Card

日期：2026-05-14

## 1. Card Identity

| item | value |
|---|---|
| module | `pipeline` |
| runtime owner | `signal` |
| run_id | `v1-signal-contract-alignment-card-20260514-01` |
| roadmap card | `v1-signal-contract-alignment-card` |
| card type | `post-terminal / signal-contract-alignment / bounded-proof-only` |
| owner | `codex` |

## 2. Objective

让 Signal 对齐新版 Alpha/PAS v1.0 candidate surface，证明 Signal 可以消费第 6 卡
`pas_entry_candidate`，保留 lineage 与 T+1 open execution hint，并输出 temp-only
aligned Signal 表面。

本卡不写 `H:\Asteria-data`，不改现有正式 `signal.duckdb`，不要求收益，不进入 broker，
不改变当前 live next。

## 3. Inputs

| input | role |
|---|---|
| `H:\Asteria-temp\alpha_pas\v1-alpha-pas-bounded-proof-build-card-20260514-01\alpha_pas_bounded_proof.duckdb` | read-only Alpha/PAS proof DB |
| `pas_entry_candidate` | Signal alignment source candidate surface |
| `docs/03-refactor/06-asteria-core-module-recovery-and-proof-roadmap-v1.md` | route authority |
| `docs/04-execution/records/pipeline/v1-alpha-pas-bounded-proof-build-card-20260514-01.conclusion.md` | source card conclusion |

## 4. Allowed Actions

- Add Signal/PAS alignment-only contract, runner, artifact writer, and CLI.
- Read the 第 6 卡 PAS proof DB read-only.
- Write aligned DB only under `H:\Asteria-temp\signal_pas\<run_id>`.
- Write report JSON only under `H:\Asteria-report\pipeline\2026-05-14\<run_id>`.
- Create validated evidence zip under `H:\Asteria-Validated`.
- Register repo four-piece and sync roadmap / ledger / conclusion index.

## 5. Forbidden Actions

| forbidden | decision |
|---|---|
| write `H:\Asteria-data` | forbidden |
| modify formal `H:\Asteria-data\signal.duckdb` | forbidden |
| change existing `formal_signal_ledger` schema | forbidden |
| run return / PnL proof | forbidden |
| emit broker order, fill, account state, position size, portfolio allocation | forbidden |
| change `current live next = none / terminal` | forbidden |

## 6. Pass Criteria

- Signal output preserves `symbol`, `signal_date`, `source_run_id`, and `lineage`.
- Signal output preserves `T_PLUS_1_OPEN`, `next_trading_day_after_signal_date`, and `open`.
- Only PAS `triggered` and `reentry_candidate` candidates generate active aligned signals.
- Non-active PAS states remain in input snapshot but do not generate active signals.
- Forbidden broker / position / portfolio / fill / account / profit fields are absent.
- All output lineage traces PAS candidate id, PAS source run, MALF WavePosition run id, and source concept trace.
- Report, audit, manifest, and validated archive exist.

## 7. Verification Plan

```powershell
H:\Asteria\.venv\Scripts\pytest.exe tests\unit\signal\test_signal_pas_alignment.py -q --basetemp H:\Asteria-temp\pytest-tmp-v1-signal-contract-alignment-card-20260514-01 -o cache_dir=H:\Asteria-temp\pytest-cache-v1-signal-contract-alignment-card-20260514-01
H:\Asteria\.venv\Scripts\pytest.exe tests\unit\signal\test_signal_bounded_proof_runner.py -q --basetemp H:\Asteria-temp\pytest-tmp-signal-existing-guard -o cache_dir=H:\Asteria-temp\pytest-cache-signal-existing-guard
H:\Asteria\.venv\Scripts\ruff.exe check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\ruff.exe format --check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\mypy.exe src --cache-dir H:\Asteria-temp\mypy-cache
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_asteria_workflow.py --strict
git diff --check
```
