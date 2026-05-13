# V1 Usage Readout Report Conclusion

日期：2026-05-13

状态：`passed / usage readout report generated`

## 1. 结论

`v1-usage-readout-report-card-20260513-01` 已通过。本卡在不改动 Asteria 主线
terminal truth 的前提下，完成了 v1 后使用验证路线的第三张只读使用读出报告卡。

当前读出结果是：

- 股票池为 `31` 个申万一级行业代表股；
- 时间窗为 `2024-01-02..2024-12-31`；
- `issue_count = 0`；
- 已生成人读 `usage-readout-report.md` 与 machine-readable `usage-readout-manifest.json`；
- 正式 DB 权限保持 `read_only`，没有重建、补写或 promote。

## 2. 放行影响

| 项 | 结果 |
|---|---|
| live next action | `none / terminal` |
| live next reopened by this card | `no` |
| next route card | `v1-usage-value-decision-card` |
| H:\Asteria-data mutation | `no` |
| usage readout report | `generated` |

## 3. 关键读出

| 问题 | 读出 |
|---|---|
| 市场结构是什么 | `malf_wave_position = 689`; `malf_lifespan_snapshot = 689` |
| 机会在哪里 | Alpha 五族各 `280`; `formal_signal_ledger = 280` |
| 持仓和组合如何解释 | `position_candidate_ledger = 230`; `portfolio_admission_ledger = 230` |
| 交易意图是什么 | `order_intent_ledger = 1`（31 股样本过滤后）；`order_rejection_ledger = 1158`（因无 `symbol` 字段，为 2024 窗口全量 rejection 读数） |
| 全链路是否自洽 | `system_chain_readout = 230`; `build_manifest = 47` |
| 哪些 caveat 保留 | fill source、reference facts、calendar semantic gap、日更生产化未打开 |

其中 `order_rejection_ledger` 的原因分布为：

- `superseded_by_newer_position_candidate = 1000`
- `position_candidate_rejected = 156`
- `max_active_symbols_constraint = 2`

## 4. 仍保留的 caveat

| 项 | 状态 |
|---|---|
| `fill_ledger` 真实成交源 | retained source caveat |
| ST / 停牌正式 coverage | retained |
| 完整上市 / 退市生命周期 | retained |
| 历史行业沿革 | retained |
| 日更生产化 | not opened |

## 5. 证据入口

- [evidence-index](v1-usage-readout-report-card-20260513-01.evidence-index.md)
- [record](v1-usage-readout-report-card-20260513-01.record.md)
- `H:\Asteria-report\pipeline\2026-05-13\v1-usage-readout-report-card-20260513-01\usage-readout-report.md`
