# Trade 2024 Coverage Repair Card

日期：2026-05-10

状态：`completed / downstream breakpoint moved to system_readout`

## 1. 目标

在 `portfolio-plan-2024-coverage-repair-card-20260509-01` 已真实完成之后，只对 released
Trade day surface 做最小 `2024-01-02..2024-01-05` focus-window coverage repair，
并判断 downstream 首断点是否继续下移到 System Readout。

## 2. 触发事实

| item | value |
|---|---|
| released Portfolio Plan admission earliest day | `2024-01-02` |
| released Portfolio Plan target exposure earliest day | `2024-01-05` |
| released Trade rejection earliest day | `2024-01-02` |
| released Trade order intent earliest day | `2024-01-05` |
| released Trade execution plan earliest day | `2024-01-05` |
| follow-up conclusion | `released_surface_gap:system_readout` |

## 3. 允许动作

- 只补 released Trade day surface 对 `2024-01-02..2024-01-05` focus trading dates 的最小 coverage repair。
- 保持 Trade 语义、schema、runner 合同仍然只在 Trade 模块边界内收敛。
- repair 完成后只能重新判定下一个 released downstream 断点，不得顺手打开 System / Pipeline full build。

## 4. 仍然禁止

| forbidden | decision |
|---|---|
| Data / MALF / Alpha / Signal / Position / Portfolio Plan 再次 repair | 禁止，除非出现新的反证 |
| System / Pipeline full rebuild | 禁止 |
| full rebuild | 禁止 |
| daily incremental | 禁止 |
| v1 complete | 禁止 |

## 5. 完成标准

- Trade released day surface 已对四个 focus trading dates 给出可复核的最小 repair 结果。
- live authority 已 truthful 切到下一层 `system_readout_2024_coverage_repair_card`。
- 本卡未把当前状态误报为 Trade full build、System repair passed、full rebuild、daily incremental 或 `v1 complete`。
