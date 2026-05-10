# Portfolio Plan 2024 Coverage Repair Card

日期：2026-05-10

状态：`prepared / not executed`

## 1. 目标

在 `position-2024-coverage-repair-card-20260509-01` 已真实完成之后，只对 released
Portfolio Plan day surface 做最小 `2024-01-02..2024-01-05` focus-window coverage repair，
并判断 downstream 首断点是否继续下移到 Trade。

## 2. 触发事实

| item | value |
|---|---|
| upstream Position earliest day | `2024-01-02` |
| released Portfolio Plan earliest day | `2024-01-09` |
| released Trade earliest day | `2024-01-09` |
| handoff conclusion | `downstream_surface_gap:portfolio_plan` |

## 3. 允许动作

- 只补 released Portfolio Plan day surface 对 `2024-01-02..2024-01-05` focus trading dates 的最小 coverage repair。
- 保持 Portfolio Plan 语义、schema、runner 合同仍然只在 Portfolio Plan 模块边界内收敛。
- repair 完成后只能重新判定下一个 released downstream 断点，不得顺手打开 Trade / System full build。

## 4. 仍然禁止

| forbidden | decision |
|---|---|
| Data / MALF / Alpha / Signal / Position 再次 repair | 禁止，除非出现新的反证 |
| Trade / System full rebuild | 禁止 |
| full rebuild | 禁止 |
| daily incremental | 禁止 |
| v1 complete | 禁止 |

## 5. 完成标准

- Portfolio Plan released day surface 对四个 focus trading dates 给出可复核的最小 repair 结果。
- 若 Portfolio Plan repair 后首断点下移，则把 live authority truthful 切到下一层 Trade repair card。
- 若 Portfolio Plan repair 后仍不能单点归因，则不得伪装成 Portfolio Plan 已 ready。
