# MALF v1.4 Core Formal Rebuild Repair Conclusion

日期：2026-05-04

状态：`passed`

## 1. Conclusion

`malf-v1-4-core-formal-rebuild-repair-20260504-01` 已完成并通过。MALF day formal rebuild
runner 现在对历史 promoted DuckDB 使用显式列名写入，不再依赖历史正式表的物理列顺序。

正式 rerun 已证明这张 repair 真正解开了原始阻塞：`core` 不再在首个正式写入事务内触发
`ConversionException`，`lifespan` 和 `service` 也能继续完成正式写入；v1.4 policy 字段已确认
写入正确列名下，而不是落入 `created_at`。

## 2. Gate Result

| 项 | 结果 |
|---|---|
| legacy column-order compatibility | `fixed` |
| MALF day explicit-column insert contract | `active` |
| legacy promoted regression coverage | `added and passed` |
| formal core/lifespan/service writes | `completed` |
| current runtime evidence switched by this card | `no` |
| current runtime evidence at repair completion | `malf-v1-3-formal-rebuild-closeout-20260502-01` |

## 3. Boundary

本卡只修复“历史正式库列位兼容写入”问题，不等于 v1.4 day runtime proof passed。
repair 通过后立即执行的 closeout rerun 已暴露新的 hard audit 阻塞；该问题不属于本卡范围，
必须转入新的 audit repair card。

## 4. Next

| 项 | 结果 |
|---|---|
| allowed next action | `malf_v1_4_core_formal_rebuild_audit_repair` |
| Position freeze review reentry restored | `no` |
| v1.4 day runtime proof passed | `no` |

下一步已切换为：

```text
malf_v1_4_core_formal_rebuild_audit_repair
```

不得据此恢复 Position freeze review reentry，不得宣称 v1.4 day runtime proof passed。

## 5. Evidence Links

- [card](malf-v1-4-core-formal-rebuild-repair-20260504-01.card.md)
- [record](malf-v1-4-core-formal-rebuild-repair-20260504-01.record.md)
- [evidence-index](malf-v1-4-core-formal-rebuild-repair-20260504-01.evidence-index.md)
