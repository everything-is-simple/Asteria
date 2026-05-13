# V1 Downstream Reference Audit Record

日期：2026-05-13

## 1. 卡信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `v1-downstream-reference-audit-20260513-01` |
| result | `passed / downstream semantics benchmark input generated` |

## 2. 执行内容

1. 重读 Asteria live authority，确认 `final-release-closeout-card` 已通过且当前 live next 仍为 `none / terminal`。
2. 复核第 3 卡 `usage-readout-manifest.json`，确认 downstream 读出口径已含 Trade rejection scope note。
3. 通过 public docs 只读参考 Hikyuu / FinHack / easytrader 的同类边界。
4. 使用 `read_only=True` 打开正式 `H:\Asteria-data\trade.duckdb`，核对 `order_rejection_ledger` 与 `fill_ledger` schema / row count。
5. 生成 `downstream-reference-audit-manifest.json`、`downstream-reference-audit-report.md`、`closeout.md` 与 run-scoped temp manifest。
6. 归档 `H:\Asteria-Validated\Asteria-v1-downstream-reference-audit-20260513-01.zip`。

## 3. Benchmark Result

| 项 | 值 |
|---|---|
| live next preserved | `yes` |
| current live next | `none / terminal` |
| next route card | `v1-usage-value-decision-card` |
| issue_count | `0` |
| H:\Asteria-data mutation | `no` |

## 4. 分类结果

| category | count | 第 4 卡裁决含义 |
|---|---:|---|
| covered | 4 | 当前下游职责拆分基本可接受 |
| expression_risk | 2 | 读出口径必须在 value decision 中明确解释 |
| real_gap | 1 | `fill_ledger` 缺少真实成交源，作为 source caveat 进入裁决 |
| not_applicable_reference | 1 | easytrader 类 broker adapter 不适用于当前只读使用验证 |

## 5. Trade 读出口径

| 项 | 读出 |
|---|---|
| `order_intent_ledger` | `1`，样本内过滤后读数 |
| `order_rejection_ledger` | `1158`，因无 `symbol` 字段，为 2024 窗口全量 rejection 读数 |
| rejection reasons | `1000 / 156 / 2` |
| `order_rejection_ledger.has_symbol` | `false` |
| `fill_ledger.row_count` | `0` |

## 6. 验收口径

本卡完成后，第 4 卡可以把 downstream concern 拆成：

- `strategy_quality_issue`：order intent / rejection scope 表达风险；
- `source_caveat`：真实 fill source gap；
- `future_enhancement`：更丰富的风险模型、资金管理模型与 broker adapter。

本卡不把上述内容升级为 live release blocker。
