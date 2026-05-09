# MALF 2024 Natural-Year Coverage Repair Card

日期：2026-05-09

状态：`prepared / not executed`

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
