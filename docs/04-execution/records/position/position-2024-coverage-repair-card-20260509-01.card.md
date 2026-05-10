# Position 2024 Coverage Repair Card

日期：2026-05-09

状态：`completed / downstream breakpoint moved to portfolio plan`

## 1. 目标

在 `coverage-gap-evidence-incomplete-closeout-card-20260509-01` 已完成 downstream closeout 之后，
把新的首断点锁定到 `position`，并只对 released Position day surface 做最小 2024 focus-window
coverage repair。

## 2. 触发事实

| item | value |
|---|---|
| upstream Alpha earliest day | `2024-01-02` |
| upstream Signal earliest day | `2024-01-02` |
| released Position earliest day | `2024-01-09` |
| released Portfolio Plan earliest day | `2024-01-09` |
| released Trade earliest day | `2024-01-09` |
| handoff conclusion | `downstream_surface_gap:position` |

## 3. 允许动作

- 只补 Position released day surface 对 `2024-01-02..2024-01-05` focus trading dates 的最小 coverage repair。
- 保持 Position 语义、schema、runner 合同仍然只在 Position 模块边界内收敛。
- repair 完成后只能重新判定下一个 released downstream 断点，不得顺手打开 Portfolio / Trade / System full build。

## 4. 仍然禁止

| forbidden | decision |
|---|---|
| MALF / Alpha / Signal 再次 repair | 禁止，除非出现新的反证 |
| Portfolio Plan / Trade / System full rebuild | 禁止 |
| full rebuild | 禁止 |
| daily incremental | 禁止 |
| v1 complete | 禁止 |

## 5. 完成标准

- Position released day surface 对四个 focus trading dates 给出可复核的最小 repair 结果。
- 若 Position repair 后首断点下移，则把 live authority truthful 切到下一层 repair card。
- 若 Position repair 后仍不能单点归因，则不得伪装成 Position 已 ready。

## 6. 实际结果

- 本卡已于 `2026-05-10` 真实执行并完成最小 Position released day surface repair。
- released Position candidate day surface 已前移到 `2024-01-02`。
- released Position entry / exit day surface 仍从 `2024-01-04` 起步，但这与 released Signal 在
  `2024-01-02` 与 `2024-01-03` 的 live 状态
  `rejected / no_active_alpha_candidate` 一致，因此不再构成 Position 语义缺口。
- follow-up closeout 已把 downstream 首断点真实下移到
  `portfolio-plan-2024-coverage-repair-card-20260509-01`。
