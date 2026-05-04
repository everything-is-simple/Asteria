# MALF v1.4 Core Formal Rebuild Closeout Conclusion

日期：2026-05-04

状态：`blocked`

## 1. Conclusion

`malf-v1-4-core-formal-rebuild-closeout-20260504-01` 已在 repair 后重新执行。历史正式库的列位
兼容写入问题已经解除，Core / Lifespan / Service / Audit 都能完成正式执行；但本卡仍未形成新的
v1.4 day runtime proof，因为 hard audit 失败。

当前阻塞根因已经切换为新的 audit 失败，而不是原先的写入兼容问题：

- `service_wave_position_natural_key_unique = 4767`
- `core_new_candidate_replaces_previous = 3579`
- `service_v13_trace_matches_lifespan = 392`

因此：

- 当前正式 runtime evidence 仍是 `malf-v1-3-formal-rebuild-closeout-20260502-01`
- 本卡不放行 v1.4 day runtime proof
- 当前允许下一张卡切换为 `malf_v1_4_core_formal_rebuild_audit_repair`

## 2. Gate Result

| 项 | 结果 |
|---|---|
| source DB | `H:\Asteria-data\market_base_day.duckdb` |
| scope | `day / 2024-01-01..2024-12-31 / symbol_limit=20` |
| blocked stage | `hard audit after service publication` |
| core / lifespan / service write compatibility | `fixed by prior repair` |
| hard audit | `hard_fail_count = 8738` |
| current runtime evidence | `malf-v1-3-formal-rebuild-closeout-20260502-01` |
| allowed next action | `malf_v1_4_core_formal_rebuild_audit_repair` |
| downstream construction | `not opened` |

## 3. Next

下一步必须先执行：

```text
malf_v1_4_core_formal_rebuild_audit_repair
```

该 repair card 只允许修复当前 hard audit 暴露出的 MALF day Core / Lifespan / Service / Audit
语义问题。在新的 repair 完成前，不得宣称 v1.4 day runtime proof passed，不得恢复 Position
freeze review reentry。

## 4. Evidence Links

- [card](malf-v1-4-core-formal-rebuild-closeout-20260504-01.card.md)
- [record](malf-v1-4-core-formal-rebuild-closeout-20260504-01.record.md)
- [evidence-index](malf-v1-4-core-formal-rebuild-closeout-20260504-01.evidence-index.md)
