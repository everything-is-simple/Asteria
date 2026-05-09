# Alpha-Signal 2024 Coverage Repair Card

日期：2026-05-09

状态：`prepared / not executed`

## 1. 目标

在 `pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01`
已如实 blocked 之后，补齐 released Alpha family 与 released Signal day surface，
让 `2024-01-02..2024-01-05` 能继续从 repaired MALF run 传到下游观察链。

## 2. 触发事实

| item | value |
|---|---|
| repaired MALF run already exists | `malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001` |
| released system manifest MALF source still locked to | `malf-v1-4-core-runtime-sync-implementation-20260505-01` |
| released signal earliest date | `2024-01-08` |
| released position earliest date | `2024-01-09` |

## 3. 允许动作

- 仅为当前 released Alpha family day surface 与 released Signal day surface补最小 coverage repair。
- 明确锁定 repaired MALF released run，不得自行改写成其他 source 解释。
- truthful 记录 repair 后 earliest released date 是否前移到 `2024-01-02`。

## 4. 仍然禁止

| forbidden | decision |
|---|---|
| Data / MALF / System / Pipeline semantic repair | 禁止 |
| Position / Portfolio Plan / Trade / System full rebuild | 禁止 |
| full rebuild | 禁止 |
| daily incremental | 禁止 |
| v1 complete | 禁止 |

## 5. 完成标准

- released Alpha family 明确消费 repaired MALF run。
- released Signal 明确消费 repaired Alpha surface。
- 若 repair 后下游 earliest released date 仍未前移，truthful 给出新的首断点，不得越级宣称全链已修完。
