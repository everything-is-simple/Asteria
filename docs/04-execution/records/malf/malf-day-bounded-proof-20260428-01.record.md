# MALF Day Bounded Proof Record

日期：2026-04-28

## 1. 卡信息

| 项 | 值 |
|---|---|
| module | `malf` |
| run_id | `malf-day-bounded-proof-20260428-01` |
| result | `passed` |

## 2. 执行前约束

1. 本轮只允许施工并放行 MALF day，不得顺手进入 Alpha 或全链路 pipeline。
2. 输入样本固定为 `H:\Asteria-temp\data-bootstrap-smoke-all-2\market_base_day.duckdb` 的 bounded scope。
3. 只有在 hard audit 全部通过后，才允许把三层 DB promote 到 `H:\Asteria-data`。

## 3. 执行顺序

1. 以 `run_id = malf-day-bounded-proof-20260428-01` 固定本次正式 bounded proof。
2. 在 `H:\Asteria-temp\malf\malf-day-bounded-proof-20260428-01\` 下生成 staging Core / Lifespan / Service 三库。
3. 对 staging 三库执行 hard audit，确认 `hard_fail_count = 0`，并核对 `birth_type`、WavePosition、interface audit 等关键覆盖。
4. 审计通过后，将正式库落到 `H:\Asteria-data\malf_core_day.duckdb`、`H:\Asteria-data\malf_lifespan_day.duckdb`、`H:\Asteria-data\malf_service_day.duckdb`。
5. 生成 `closeout.md`、`manifest.json`、`table-counts.json`、`audit-summary.json`，并归档 `H:\Asteria-Validated\Asteria-malf-day-bounded-proof-20260428-01.zip`。
6. 更新门禁文档，明确 MALF day bounded proof 已通过，下一步只允许进入 `Alpha freeze review`。
7. 确认本卡不打开 Alpha 代码施工、不创建 Alpha 正式 DB、不允许任何下游写回 MALF。

## 4. 关键验证

| 验证 | 结果 |
|---|---|
| Core / Lifespan / Service staging build | 通过 |
| hard audit | `hard_fail_count = 0` |
| birth_type 覆盖 | `initial` / `same_direction_after_break` / `opposite_direction_after_break` 全覆盖 |
| WavePosition 发布 | `621` 行，latest `4` 行 |
| interface audit | `7` 行，全部 `pass` |
| formal promote consistency | staging 与正式三库计数一致 |
| release gate checks | governance、ruff、format、mypy、pytest 全通过 |

## 5. 外部证据资产

| 资产 | 路径 |
|---|---|
| report_dir | `H:\Asteria-report\malf\2026-04-28\malf-day-bounded-proof-20260428-01` |
| manifest | `H:\Asteria-report\malf\2026-04-28\malf-day-bounded-proof-20260428-01\manifest.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-malf-day-bounded-proof-20260428-01.zip` |
| formal DBs | `H:\Asteria-data\malf_core_day.duckdb`; `H:\Asteria-data\malf_lifespan_day.duckdb`; `H:\Asteria-data\malf_service_day.duckdb` |

## 6. 文档更新

- [MALF bounded proof checklist](../../../03-refactor/03-malf-day-bounded-proof-construction-checklist-v1.md)
- [module gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
- report closeout: `H:\Asteria-report\malf\2026-04-28\malf-day-bounded-proof-20260428-01\closeout.md`

## 7. 门禁更新

| 项 | 结果 |
|---|---|
| conclusion index registered | `yes` |
| allowed next action after card | `Alpha freeze review` |
| still blocked | `Alpha code construction; Alpha formal DB; downstream module construction; full-chain pipeline; downstream writeback to MALF` |

## 8. 关联页面

- [card](malf-day-bounded-proof-20260428-01.card.md)
- [evidence-index](malf-day-bounded-proof-20260428-01.evidence-index.md)
- [conclusion](malf-day-bounded-proof-20260428-01.conclusion.md)
