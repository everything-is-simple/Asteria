# V1 Usage Readout Report Record

日期：2026-05-13

## 1. 卡信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `v1-usage-readout-report-card-20260513-01` |
| result | `passed / usage readout report generated` |

## 2. 执行内容

1. 重读 Asteria live authority，确认 `final-release-closeout-card` 已通过且当前 live next 仍为 `none / terminal`。
2. 复核 `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md`，确认本卡是 post-terminal 只读路线卡。
3. 读取 `v1-usage-validation-scope-card-20260512-01` 冻结的 `31` 个代表股与 `2024-01-02..2024-12-31` 时间窗。
4. 使用 `read_only=True` 打开正式 `H:\Asteria-data` DB，并采集 v1 使用读出所需表面。
5. 生成 `usage-readout-manifest.json`、`usage-readout-report.md`、`closeout.md` 与 run-scoped temp manifest。
6. 归档 `H:\Asteria-Validated\Asteria-v1-usage-readout-report-card-20260513-01.zip`。

## 3. Readout Result

| 项 | 值 |
|---|---|
| live next preserved | `yes` |
| current live next | `none / terminal` |
| next route card | `v1-usage-value-decision-card` |
| selected_symbol_count | `31` |
| date_window | `2024-01-02..2024-12-31` |
| issue_count | `0` |
| H:\Asteria-data mutation | `no` |

## 4. 分层读出

| 层 | 表面 | rows |
|---|---|---:|
| MALF | `malf_wave_position` | 689 |
| MALF | `malf_lifespan_snapshot` | 689 |
| Alpha | `alpha_signal_candidate` x 5 families | 280 each |
| Signal | `formal_signal_ledger` | 280 |
| Position | `position_candidate_ledger` | 230 |
| Portfolio Plan | `portfolio_admission_ledger` | 230 |
| Trade | `order_intent_ledger` | 1 |
| Trade | `order_rejection_ledger` | 1158（因无 `symbol` 字段，属于 2024 窗口全量 rejection 读数，不是 31 股样本同口径子集） |
| System Readout | `system_chain_readout` | 230 |
| Pipeline | `build_manifest` | 47 |

Trade 补充说明：

- `order_intent_ledger = 1` 是按 `31` 个样本股与 `2024-01-02..2024-12-31` 窗口过滤后的结果。
- `order_rejection_ledger = 1158` 只能按日期过滤，不能按样本股过滤，因为正式表面没有 `symbol` 字段。
- `order_rejection_ledger` 的原因分布为：
  `superseded_by_newer_position_candidate = 1000`；
  `position_candidate_rejected = 156`；
  `max_active_symbols_constraint = 2`。

## 5. 边界与 caveat

| 项 | 裁决 |
|---|---|
| `fill_ledger` 真实成交源 | `retained source caveat` |
| ST / 停牌 / 上市退市 | `retained source caveat` |
| 历史行业沿革 | `retained source caveat` |
| calendar semantic gap | `retained usage-readout caveat` |
| 日更生产化 | `not opened` |

## 6. 验收口径

本卡的完成只代表：v1 当前正式库可以被只读读出成人读研究报告。它不代表：

- Asteria 主线重新打开；
- 使用价值裁决已经完成；
- retained source caveat 被修复；
- 日更生产化已经放行。
