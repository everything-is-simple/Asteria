# Position Bounded Proof Build Record

日期：2026-05-07

状态：`passed`

## 1. Scope

本卡只施工 Position bounded proof。它承接
`signal-production-builder-hardening-20260506-01`，只读消费
`H:\Asteria-data\signal.duckdb` 的 released day Signal surface。

本卡不执行 Position full build，不创建 Portfolio Plan / Trade / System / Pipeline
正式 runner 或正式 DB。

## 2. Implementation Summary

- 新增 `src\asteria\position` 最小 bounded proof 包：contracts、schema、rules、audit、bootstrap。
- 新增 `scripts\position` 三个 runner wrapper：build、audit、bounded proof。
- Position 输入锁定 `source_signal_run_id = signal-production-builder-hardening-20260506-01`。
- Position 输出只包含 `position_signal_snapshot`、`position_candidate_ledger`、
  `position_entry_plan`、`position_exit_plan` 与审计表面。
- hard audit 覆盖 Signal source、source run lock、自然键唯一、planned candidate entry/exit、
  rule version traceability、rejected reason、禁用下游字段。

## 3. Formal Execution

| stage | 命令摘要 |
|---|---|
| bounded proof | `run_position_bounded_proof.py --mode bounded --run-id position-bounded-proof-build-card-20260506-01 --symbol-limit 5` |

执行输入：

| 项 | 值 |
|---|---|
| source_signal_db | `H:\Asteria-data\signal.duckdb` |
| source_signal_run_id | `signal-production-builder-hardening-20260506-01` |
| target_position_db | `H:\Asteria-data\position.duckdb` |
| report_root | `H:\Asteria-report` |
| validated_root | `H:\Asteria-Validated` |
| timeframe | `day` |
| bounded scope | `symbol_limit = 5` |

## 4. Result

| item | count |
|---|---:|
| input_signal_count | 1158 |
| position_candidate_count | 1158 |
| entry_plan_count | 1004 |
| exit_plan_count | 1004 |
| hard_fail_count | 0 |

Natural key and boundary verification:

| check | result |
|---|---:|
| Position hard audit fail count | 0 |
| source Signal run ids | `signal-production-builder-hardening-20260506-01` only |
| forbidden downstream columns | 0 |

## 5. Evidence

| artifact | path |
|---|---|
| report dir | `H:\Asteria-report\position\2026-05-07\position-bounded-proof-build-card-20260506-01\` |
| validated zip | `H:\Asteria-Validated\Asteria-position-bounded-proof-build-card-20260506-01.zip` |
| audit summary | `H:\Asteria-report\position\2026-05-07\position-bounded-proof-build-card-20260506-01-day-audit-summary.json` |

## 6. Boundary

本卡只放行 Position day bounded proof surface。它不授权 Position full build、
Portfolio Plan build、Trade/System 施工或 full-chain Pipeline runtime。
