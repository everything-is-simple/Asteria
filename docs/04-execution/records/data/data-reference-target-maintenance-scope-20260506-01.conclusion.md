# Data Reference Target Maintenance Scope Conclusion

日期：2026-05-06

状态：`passed / scope frozen`

## 1. 结论

Data reference target maintenance 的范围已冻结。本卡只裁定下一张 Data closeout 允许补哪些 reference facts、怎样验收、哪些缺口必须保留为 unknown 或 blocker；不修改任何正式 DB。

## 2. 放行影响

| 项 | 结果 |
|---|---|
| allowed next action | `data_reference_target_maintenance_closeout` |
| Data DB mutation opened by this card | `no` |
| Position construction opened | `no` |
| position.duckdb created | `no` |
| Pipeline runtime opened | `no` |

## 3. 冻结范围

| 类别 | 裁决 |
|---|---|
| ST | 下一卡必补 source-backed 事实或显式 blocker |
| 停牌 / 可交易状态 | 下一卡必补 source-backed 事实或显式 blocker |
| 真实上市 / 退市生命周期 | 下一卡必补 source-backed 事实或显式 blocker |
| 历史行业沿革 | 下一卡必须给出 source-backed coverage decision；不得伪造历史 |
| index / block / universe membership | 下一卡必须完成 source inventory 与 release decision |
| week/month execution price line | 不作为 MALF week/month 前置必补；继续保留给未来 Trade/Position 执行语义卡 |

## 4. 证据入口

- [evidence-index](data-reference-target-maintenance-scope-20260506-01.evidence-index.md)
- [record](data-reference-target-maintenance-scope-20260506-01.record.md)
