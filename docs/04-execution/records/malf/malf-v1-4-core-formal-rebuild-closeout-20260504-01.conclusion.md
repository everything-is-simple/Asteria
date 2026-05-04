# MALF v1.4 Core Formal Rebuild Closeout Conclusion

日期：2026-05-04

状态：`blocked`

## 1. Conclusion

`malf-v1-4-core-formal-rebuild-closeout-20260504-01` 已执行，但在 `core` formal rebuild
首个正式写入事务内阻塞，未形成新的 v1.4 day runtime proof。

阻塞根因不是 Data 输入异常，而是历史正式 MALF DuckDB 与 v1.4 runner 的列位契约不兼容：
正式库中的 `created_at` 仍保留在旧位置，v1.4 策略字段通过追加列进入表尾；当前 rebuild
runner 仍按 `insert into ... values (...)` 的位置语义写入，导致
`pivot_detection_rule_version` 被投递到 timestamp 列位并触发转换失败。

因此：

- 当前正式 runtime evidence 仍是 `malf-v1-3-formal-rebuild-closeout-20260502-01`
- 本卡不放行 v1.4 day runtime proof
- 当前允许下一张卡切换为 `malf_v1_4_core_formal_rebuild_repair`

## 2. Gate Result

| 项 | 结果 |
|---|---|
| source DB | `H:\Asteria-data\market_base_day.duckdb` |
| scope | `day / 2024-01-01..2024-12-31 / symbol_limit=20` |
| blocked stage | `core formal rebuild` |
| error type | `ConversionException` |
| dirty rows for this run_id | `0 across core/lifespan/service` |
| hard audit | `not reached` |
| current runtime evidence | `malf-v1-3-formal-rebuild-closeout-20260502-01` |
| allowed next action | `malf_v1_4_core_formal_rebuild_repair` |
| downstream construction | `not opened` |

## 3. Next

下一步必须先执行：

```text
malf_v1_4_core_formal_rebuild_repair
```

该 repair card 只允许修复 MALF day 正式 rebuild 与历史正式库列位兼容问题，并在修复后重新
执行 `malf-v1-4-core-formal-rebuild-closeout-20260504-01`。在 repair card 完成前，不得宣称
v1.4 day runtime proof passed，不得恢复 Position freeze review reentry。

## 4. Evidence Links

- [card](malf-v1-4-core-formal-rebuild-closeout-20260504-01.card.md)
- [record](malf-v1-4-core-formal-rebuild-closeout-20260504-01.record.md)
- [evidence-index](malf-v1-4-core-formal-rebuild-closeout-20260504-01.evidence-index.md)
