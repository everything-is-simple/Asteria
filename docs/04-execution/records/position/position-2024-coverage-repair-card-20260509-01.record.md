# Position 2024 Coverage Repair Record

日期：2026-05-10

run_id：`position-2024-coverage-repair-card-20260509-01`

## 1. Inputs

- `H:\Asteria-data\signal.duckdb`
- `H:\Asteria-data\position.duckdb`
- `H:\Asteria-data\system.duckdb`
- `docs/04-execution/records/pipeline/coverage-gap-evidence-incomplete-closeout-card-20260509-01.conclusion.md`
- `docs/04-execution/records/position/position-2024-coverage-repair-card-20260509-01.card.md`

## 2. Preflight

- 锁定当前 released `system_readout_run = system-readout-bounded-proof-build-card-20260508-01`。
- 从 `system_source_manifest` 锁定 released `position` run 为
  `position-bounded-proof-build-card-20260506-01`。
- 从同一条 manifest 链锁定 released `signal` run 为
  `signal-production-builder-hardening-20260506-01`。
- 只读取 released Signal day surface 在 `2024-01-02..2024-01-05` 的 focus-window rows，
  不扩大到 MALF / Alpha / Portfolio Plan / Trade / System runtime 施工。

## 3. Execution

| stage | action |
|---|---|
| resolve live locks | 读取 `system.duckdb.system_source_manifest`，确认 released Position / Signal source lock |
| build | 复用现有 Position rules，在 released Position run_id 上重算 focus-window day rows |
| rewrite | 仅删除并重写 `position_signal_snapshot`、`position_candidate_ledger`、`position_entry_plan`、`position_exit_plan` 的 focus-window day rows |
| audit | 复用 Position audit，生成 `position-day-audit-summary.json` |
| follow-up | 构造只读 probe `system.duckdb`，复跑 downstream coverage diagnosis / closeout decision |
| evidence | 写出 repo 四件套、`H:\Asteria-report` 证据和 `H:\Asteria-Validated` zip |

## 4. Outputs

- `H:\Asteria-report\position\2026-05-10\position-2024-coverage-repair-card-20260509-01\position-day-audit-summary.json`
- `H:\Asteria-report\position\2026-05-10\position-2024-coverage-repair-card-20260509-01\manifest.json`
- `H:\Asteria-report\position\2026-05-10\position-2024-coverage-repair-card-20260509-01\closeout.md`
- `H:\Asteria-report\pipeline\2026-05-10\position-2024-coverage-repair-card-20260509-01-followup-diagnosis\coverage-matrix.json`
- `H:\Asteria-report\pipeline\2026-05-10\position-2024-coverage-repair-card-20260509-01-followup-diagnosis\coverage-attribution.md`
- `H:\Asteria-Validated\Asteria-position-2024-coverage-repair-card-20260509-01.zip`

## 5. Verified Findings

- `hard_fail_count = 0`
- released Position candidate earliest day 已前移到 `2024-01-02`
- released Position entry earliest day 仍是 `2024-01-04`
- released Position exit earliest day 仍是 `2024-01-04`
- follow-up next card 仍是 `position-2024-coverage-repair-card-20260509-01`
- truthful attribution 仍是 `downstream_surface_gap:position`

## 6. Root Cause

- released Signal 在 `2024-01-02` 与 `2024-01-03` 的 live 状态是
  `rejected / no_active_alpha_candidate`。
- 因此 Position 在这两天只能产出 `rejected` candidate，不能自然生成 entry / exit plan。
- 这意味着本卡虽然补齐了 Position candidate surface，但没有把 downstream 首断点下移到
  Portfolio Plan / Trade。
