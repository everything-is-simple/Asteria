# MALF 2024 Natural-Year Coverage Repair Card

日期：2026-05-09

状态：`passed / minimal released surface repair`

## 1. 目标

只修 released MALF day surface 对 `2024-01-02..2024-01-05` 的覆盖缺口，使最早 released-surface break
不再停在 MALF。

## 2. 范围

| item | decision |
|---|---|
| target module | `MALF` |
| target surface | `malf_service_day.duckdb.malf_wave_position` |
| focus dates | `2024-01-02..2024-01-05` |
| expected source | released Data day + calendar/tradability facts |
| allowed work | minimal MALF released day surface repair |
| formal repaired symbol set | `000020.SZ` |
| released service run after pass | `malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001` |

## 3. 仍然禁止

| forbidden | decision |
|---|---|
| Alpha / Signal / downstream repair | 禁止 |
| System Readout / Pipeline semantic repair | 禁止 |
| year replay rerun | 禁止 |
| full rebuild / daily incremental / v1 complete | 禁止 |

## 4. 完成标准

- MALF repair 只回答为什么 released MALF day surface从 `2024-01-08` 才开始。
- 形成最小 evidence，证明 `2024-01-02..2024-01-05` 是否可被 MALF released day surface 正式放行。
- 不把该卡偷换成 Alpha / Signal / System / Pipeline repair。

## 5. 实际结果

- 当前 released `system_source_manifest` 仍锁定旧 MALF run
  `malf-v1-4-core-runtime-sync-implementation-20260505-01`，其 surface 从 `2024-01-08` 才开始。
- 本卡使用现有 MALF day segmented repair 路径，对 `000020.SZ` 执行 full-year symbol-scoped repair，
  生成新的 released service run
  `malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001`。
- 新 run 已正式覆盖 `2024-01-02..2024-01-05` 四个 focus trading dates，`hard_fail_count = 0`。
- 本卡通过后，只允许准备 `pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01`；
  不在本卡内直接 rerun year replay。
