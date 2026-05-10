# System Readout 2024 Coverage Repair Card

日期：2026-05-10

状态：`completed / calendar_semantic_gap_only`

## 1. 目标

在 `trade-2024-coverage-repair-card-20260509-01` 已真实完成之后，只对 released
System Readout day surface 做最小 `2024-01-02..2024-01-05` focus-window coverage repair，
并 truthfully 记录 follow-up 只剩 calendar-semantic gap，下一步切到 Pipeline
source selection repair。

## 2. 触发事实

| item | value |
|---|---|
| released Trade rejection earliest day | `2024-01-02` |
| released Trade order intent earliest day | `2024-01-05` |
| released Trade execution plan earliest day | `2024-01-05` |
| released System Readout earliest day | `2024-01-02` |
| focus trading dates | `2024-01-02, 2024-01-03, 2024-01-04, 2024-01-05` |
| hard_fail_count | `0` |
| follow-up next card | `pipeline-year-replay-source-selection-repair-card-20260509-01` |
| follow-up attribution | `calendar_semantic_gap_only` |

## 3. 结果

- released System Readout day surface 已真实覆盖 `2024-01-02..2024-01-05`。
- released System Readout earliest day 已前移到 `2024-01-02`。
- follow-up attribution 只剩 `calendar_semantic_gap_only`，不再是 System surface gap。
- live authority 已切到 Pipeline source selection repair。

## 4. 仍然禁止

| forbidden | decision |
|---|---|
| Data / MALF / Alpha / Signal / Position / Portfolio Plan / Trade 再次 repair | 禁止，除非出现新的反证 |
| Pipeline semantic repair / source-selection repair 之外的扩权 | 禁止 |
| System full build | 禁止 |
| full rebuild | 禁止 |
| daily incremental | 禁止 |
| v1 complete | 禁止 |

## 5. 完成标准

- System Readout released day surface 对四个 focus trading dates 给出可复核的最小 repair 结果。
- 若 System Readout repair 后首断点继续下移，则把 live authority truthful 切到下一层卡。
- 若 System Readout repair 后仍不能单点归因，则不得伪装成 System 已 ready。

## 6. Evidence

- [record](system-readout-2024-coverage-repair-card-20260509-01.record.md)
- [evidence-index](system-readout-2024-coverage-repair-card-20260509-01.evidence-index.md)
- [conclusion](system-readout-2024-coverage-repair-card-20260509-01.conclusion.md)
