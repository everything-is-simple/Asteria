# System Readout Bounded Proof Build Record

日期：2026-05-08

## 1. 背景

`system-readout-freeze-review-20260507-01` 已通过，System Readout 六件套已冻结。本卡执行
System Readout day bounded proof build，唯一允许的输入边界是 released full-chain day
bounded surfaces。

## 2. 执行摘要

- 新增 `src\asteria\system_readout` 最小 bounded proof 包：contracts、schema、rules、audit_engine、bootstrap。
- 新增 `scripts\system_readout` 三个 runner wrapper：build、audit、bounded proof。
- 读取 `H:\Asteria-data\malf_service_day.duckdb`、五个 `alpha_*.duckdb`、`signal.duckdb`、
  `position.duckdb`、`portfolio_plan.duckdb` 与 `trade.duckdb` 的 released day bounded surfaces。
- 只写入 `system_source_manifest`、`system_module_status_snapshot`、`system_chain_readout`、
  `system_summary_snapshot`、`system_audit_snapshot` 与 `system_readout_audit`。
- hard audit 覆盖 source release lock、全链路 source audit 状态、自然键唯一、readout traceability、
  forbidden columns absence，以及 `wave_core_state` / `system_state` 并列展示边界。

## 3. Formal Execution

| stage | 命令摘要 |
|---|---|
| bounded proof | `run_system_readout_bounded_proof.py --run-id system-readout-bounded-proof-build-card-20260508-01 --source-chain-release-version trade-bounded-proof-build-card-20260507-01 --start-dt 2024-01-01 --end-dt 2024-12-31 --symbol-limit 4` |

执行输入：

| 项 | 值 |
|---|---|
| source_chain_release_version | `trade-bounded-proof-build-card-20260507-01` |
| timeframe | `day` |
| source_manifest_count | `10` |
| target_system_db | `H:\Asteria-data\system.duckdb` |
| report_root | `H:\Asteria-report` |
| validated_root | `H:\Asteria-Validated` |

## 4. Result

| item | count |
|---|---:|
| source_manifest_count | 10 |
| module_status_count | 6 |
| readout_count | 4633 |
| summary_count | 4633 |
| audit_snapshot_count | 6 |
| hard_fail_count | 0 |

真实 bounded sample 本轮自然覆盖了 `complete` 与 `partial`；`source_gap` / `audit_gap`
仍由单元测试 fixture 覆盖，不得被夸大成真实 release 样本已出现。

## 5. Boundary

System Readout 只读消费 released full-chain day bounded surfaces，不回写 MALF / Alpha /
Signal / Position / Portfolio Plan / Trade。`fill_ledger` retained gap 不会被 readout 伪造成
真实成交事实；`wave_core_state` 与 `system_state` 只并列呈现，不得合并。

## 6. Evidence

- `H:\Asteria-report\system_readout\2026-05-08\system-readout-bounded-proof-build-card-20260508-01\closeout.md`
- `H:\Asteria-report\system_readout\2026-05-08\system-readout-bounded-proof-build-card-20260508-01\manifest.json`
- `H:\Asteria-report\system_readout\2026-05-08\system-readout-bounded-proof-build-card-20260508-01-day-audit-summary.json`
- `H:\Asteria-Validated\Asteria-system-readout-bounded-proof-build-card-20260508-01.zip`
