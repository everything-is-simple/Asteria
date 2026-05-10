# System Readout 2024 Coverage Repair Record

日期：2026-05-10

run_id：`system-readout-2024-coverage-repair-card-20260509-01`

## 1. Execution

| stage | action |
|---|---|
| resolve live locks | 读取 `system.duckdb.system_readout_run` 与 `system_source_manifest`，锁定 released System run |
| repair | 仅对 `2024-01-02..2024-01-05` focus window 重写 released System Readout rows |
| audit | 生成 `system-readout-day-audit-summary.json`，确认 `hard_fail_count = 0` |
| follow-up | 对修复后的 released `system.duckdb` 跑 year replay coverage gap diagnosis |
| evidence | 写出 repo 四件套、`H:\Asteria-report` 证据与 `H:\Asteria-Validated` zip |

## 2. Outputs

| item | value |
|---|---|
| released_system_run_id | `system-readout-bounded-proof-build-card-20260508-01` |
| focus_trading_dates | `2024-01-02, 2024-01-03, 2024-01-04, 2024-01-05` |
| source_manifest_count | `10` |
| module_status_count | `6` |
| readout_count | `4637` |
| summary_count | `4637` |
| audit_snapshot_count | `6` |
| hard_fail_count | `0` |
| follow-up next card | `pipeline-year-replay-source-selection-repair-card-20260509-01` |
| follow-up attribution | `calendar_semantic_gap_only` |

## 3. Runtime Evidence

- `H:\Asteria-data\system.duckdb`
- `H:\Asteria-report\system_readout\2026-05-10\system-readout-2024-coverage-repair-card-20260509-01\manifest.json`
- `H:\Asteria-report\system_readout\2026-05-10\system-readout-2024-coverage-repair-card-20260509-01\closeout.md`
- `H:\Asteria-report\system_readout\2026-05-10\system-readout-2024-coverage-repair-card-20260509-01\system-readout-day-audit-summary.json`
- `H:\Asteria-report\pipeline\2026-05-10\system-readout-2024-coverage-repair-card-20260509-01-followup-diagnosis\coverage-matrix.json`
- `H:\Asteria-report\pipeline\2026-05-10\system-readout-2024-coverage-repair-card-20260509-01-followup-diagnosis\coverage-attribution.md`
- `H:\Asteria-Validated\Asteria-system-readout-2024-coverage-repair-card-20260509-01.zip`

## 4. Findings

- released System Readout day surface 已覆盖 `2024-01-02..2024-01-05`。
- released System earliest day 已前移到 `2024-01-02`。
- follow-up 只剩 `calendar_semantic_gap_only`。
- 这张卡不打开 System full build、full rebuild 或 daily incremental。
