# MALF v1.4 Core 运行同步评审准备卡

run_id: `malf-v1-4-core-runtime-sync-review-20260503-01`

date: 2026-05-03

module: `MALF`

status: `已准备 / 未打开 / 未执行运行同步`

## 1. 目的

本准备卡记录未来 MALF v1.4 Core 运行同步评审的范围。它的作用是保存当前
Core 语义评审结论，并为后续获得明确授权的评审者或实施者提供一份可确定执行的检查清单。

本卡不打开施工，不执行运行证明，不改变当前主线门禁，也不取代当前
MALF day 运行证据。

## 2. 权威输入

| 输入 | 作用 |
|---|---|
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4` | 当前 MALF v1.4 权威定义包 |
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4.zip` | 当前 MALF v1.4 已验证权威归档 |
| `H:\Asteria-Validated\Asteria-docs-code-20260503-110805.zip` | 本次准备评审所锚定的文档/代码参考快照 |
| repo HEAD | 后续任何同步动作之前必须先对照核验的当前实现真相 |
| `malf-v1-3-formal-rebuild-closeout-20260502-01` | 当前 MALF day formal-data bounded 运行证据 |
| `malf-v1-4-core-operational-boundary-authority-sync-20260503-01` | 权威同步结论，不是运行证明 |

## 3. 门禁边界

| 项 | 裁决 |
|---|---|
| v1.4 权威定义 | 已同步 |
| v1.4 运行证明 | 未执行 |
| MALF 运行证据 | 仍为 `malf-v1-3-formal-rebuild-closeout-20260502-01` |
| 当前允许的下一步业务动作 | `Position freeze review reentry / review-only` |
| MALF 施工状态 | 本准备卡不打开 |

本准备卡不得被理解为重新打开 MALF build 的许可。后续如果要从准备态评审范围升级为
已打开评审、实现同步或 runtime proof，必须经过单独授权，并同步更新对应治理面。

## 4. 评审目标

| 优先级 | 目标 | 评审问题 |
|---|---|---|
| P0 | bar-level break 判定 | Core 是否按 `bar_low < current_effective_HL.price` 与 `bar_high > current_effective_LH.price` 判定 break，而不是等待 confirmed opposite pivot？ |
| P0 | `malf_core_state_snapshot` | Core 是否发布了面向读取优化的状态快照面，使 Lifespan 和 Service 不必只靠事件账本反推当前状态？ |
| P1 | O1/O2/O3 运行账本字段 | `pivot_detection_rule_version`、`core_event_ordering_version`、`price_compare_policy`、`epsilon_policy` 是否进入 request、run ledger 与 audit surface？ |
| P1 | 上下文化 structure reference | `malf_structure_ledger.reference_pivot_id` 是否来自当前结构上下文，而不是全局 latest same-type pivot？ |
| P2 | candidate 事件类型 | candidate 历史是否区分 `candidate_created`、`same_direction_candidate_refresh`、`opposite_direction_candidate_replacement` 与 `confirmed`？ |

## 5. 禁止动作

- 不修改 Python 代码。
- 不做 DuckDB schema 迁移。
- 不做正式 DB 重建或 promote。
- 不执行 MALF week/month proof。
- 不进入 Position、Portfolio Plan、Trade、System、Pipeline、Alpha 或 Signal 施工。
- 不允许下游写回 MALF。
- 不得宣称 MALF v1.4 runtime proof 已通过。
- 不更新 `governance/module_gate_registry.toml`。
- 不更新 `docs/03-refactor/00-module-gate-ledger-v1.md`。
- 不得通过 `docs/04-execution/00-conclusion-index-v1.md` 改变门禁状态；如果本卡进入执行，
  conclusion index 只能登记 review-only 结论，不能据此打开 build。

## 6. 验收标准

- 本卡必须清楚区分 `v1.4 权威定义已同步` 与 `v1.4 运行证明未执行`。
- 本卡必须保留 `Position freeze review reentry / review-only` 作为当前允许的下一步业务动作。
- 本卡必须能作为后续单独授权的 MALF 运行同步评审卡或施工卡的输入材料。
- 本次评审不得修改 registry 或 gate ledger。若需要登记 conclusion index，必须保留
  `review-only` 状态，且不能暗示 MALF build 已重新打开。

## 7. 验证计划

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
git diff --check -- docs/04-execution/records/malf/malf-v1-4-core-runtime-sync-review-20260503-01.card.md
git diff -- docs/04-execution/records/malf/malf-v1-4-core-runtime-sync-review-20260503-01.card.md
```

## 8. 非声明

本卡不是 conclusion，不是 evidence index，不是运行证明，也不是 release gate。
它只是准备态评审卡。
