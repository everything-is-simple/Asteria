# V1 Downstream Reference Audit Card

日期：2026-05-13

状态：`passed / downstream semantics benchmark input generated`

## 1. 背景

`v1-usage-readout-report-card-20260513-01` 已通过，并暴露了 downstream 读出口径
需要在第 4 卡前被解释清楚：`order_intent_ledger = 1` 是样本内读数，而
`order_rejection_ledger = 1158` 因缺少 `symbol` 字段只能作为 2024 窗口全量读数。

本卡作为 `v1-usage-value-decision-card` 的只读 supplemental input，不改变当前
live truth：`none / terminal`。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `v1-downstream-reference-audit-20260513-01` |
| route type | `roadmap-only / read-only / post-terminal / supplement` |
| predecessor | `v1-usage-readout-report-card-20260513-01` |
| decision input for | `v1-usage-value-decision-card` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| formal DB root | `H:\Asteria-data` |
| usage readout manifest | `H:\Asteria-report\pipeline\2026-05-13\v1-usage-readout-report-card-20260513-01\usage-readout-manifest.json` |
| external references | Hikyuu / FinHack / easytrader public docs |
| 权限 | `read_only` |

## 4. 允许动作

- 只读读取第 3 卡 usage readout manifest。
- 只读检查 `trade.duckdb` 中 `order_rejection_ledger` 与 `fill_ledger` 的 schema / row count。
- 将 Hikyuu / FinHack / easytrader 作为概念参考，生成 downstream semantics benchmark。
- 在 `H:\Asteria-report` 生成人读报告和 machine-readable manifest。
- 在 `H:\Asteria-temp` 落 run-scoped temp manifest。
- 在 `H:\Asteria-Validated` 归档 validated zip。

## 5. 禁止动作

- 不修改、重建、补写或 promote `H:\Asteria-data`。
- 不把外部项目差异自动升级为 Asteria usage blocker。
- 不复制外部项目代码。
- 不重定义 Position / Portfolio Plan / Trade / System Readout 语义。
- 不打开实盘交易、production daily incremental activation 或新的 live next card。

## 6. 验收口径

本卡只证明：第 4 卡裁决前已有一份可追溯的 downstream 同类项目语义对照输入。
它不代表使用价值裁决已经完成。
