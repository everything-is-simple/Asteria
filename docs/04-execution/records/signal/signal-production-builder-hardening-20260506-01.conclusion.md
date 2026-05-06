# Signal Production Builder Hardening Conclusion

日期：2026-05-06

状态：`passed`

## 1. Conclusion

`signal-production-builder-hardening-20260506-01` 已通过。Signal 已在
`alpha-production-builder-hardening-20260506-01` 放行的五个 Alpha family DB 上完成
day/week/month production builder hardening，并通过 hard audit：

```text
hard_fail_count = 0
```

本结论只放行 Signal formal signal ledger 的 production builder 表面。它不打开 Position
construction，不创建 `position.duckdb`，不输出 position candidate、entry/exit plan、portfolio
allocation、order 或 fill。

## 2. Gate Result

| 项 | 结果 |
|---|---|
| source Alpha run | `alpha-production-builder-hardening-20260506-01` |
| target DB | `H:\Asteria-data\signal.duckdb` |
| timeframes | `day / week / month` |
| day formal_signal rows | `4633` |
| week formal_signal rows | `759` |
| month formal_signal rows | `102` |
| day input snapshot / component rows | `23165 / 23165` |
| week input snapshot / component rows | `3795 / 3795` |
| month input snapshot / component rows | `510 / 510` |
| hard_fail_count | `0` |
| formal signal natural-key duplicate groups | `0` |
| component natural-key duplicate groups | `0` |
| validated evidence | `H:\Asteria-Validated\Asteria-signal-production-builder-hardening-20260506-01.zip` |
| allowed next action | `upstream_pre_position_release_decision` |

## 3. Boundary

Signal 仍只读消费 Alpha，不直接读取 MALF 形成业务 signal，不写回 Alpha / MALF。Position
bounded proof 仍必须等待 `upstream-pre-position-release-decision-20260506-01` 形成 conclusion
后再裁定是否恢复。

## 4. Evidence

- [record](signal-production-builder-hardening-20260506-01.record.md)
- [evidence-index](signal-production-builder-hardening-20260506-01.evidence-index.md)
