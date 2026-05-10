# System Readout 2024 Coverage Repair Card

日期：2026-05-10

状态：`prepared / not executed`

## 1. 目标

在 `trade-2024-coverage-repair-card-20260509-01` 已真实完成之后，只对 released
System Readout day surface 做最小 `2024-01-02..2024-01-05` focus-window coverage repair，
并判断 year replay 的首断点是否继续下移到 Pipeline 语义层或只剩 calendar-semantic gap。

## 2. 触发事实

| item | value |
|---|---|
| released Trade rejection earliest day | `2024-01-02` |
| released Trade order intent earliest day | `2024-01-05` |
| released Trade execution plan earliest day | `2024-01-05` |
| released System Readout earliest day | `2024-01-08` |
| handoff conclusion | `released_surface_gap:system_readout` |

## 3. 允许动作

- 只补 released System Readout day surface 对 `2024-01-02..2024-01-05` focus trading dates 的最小 coverage repair。
- 保持 System Readout 语义、schema、runner 合同仍然只在 System Readout 模块边界内收敛。
- repair 完成后只能重新判定下一个 released downstream 断点，不得顺手打开 Pipeline semantic repair 或 full rebuild。

## 4. 仍然禁止

| forbidden | decision |
|---|---|
| Data / MALF / Alpha / Signal / Position / Portfolio Plan / Trade 再次 repair | 禁止，除非出现新的反证 |
| Pipeline semantic repair / source-selection repair | 禁止 |
| System full build | 禁止 |
| full rebuild | 禁止 |
| daily incremental | 禁止 |
| v1 complete | 禁止 |

## 5. 完成标准

- System Readout released day surface 对四个 focus trading dates 给出可复核的最小 repair 结果。
- 若 System Readout repair 后首断点继续下移，则把 live authority truthful 切到下一层卡。
- 若 System Readout repair 后仍不能单点归因，则不得伪装成 System 已 ready。
