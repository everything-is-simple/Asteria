# V1 Core Retention And Outsourcing Boundary Conclusion

日期：2026-05-13

状态：`passed / core retention and outsourcing boundary frozen`

## 1. 结论

`v1-core-retention-and-outsourcing-boundary-card-20260513-01` 已通过。本卡在不改动
Asteria 主线 terminal truth 的前提下，完成了 v1 后 Phase 2 战略边界裁决。

当前裁决是：

```text
Asteria 不再默认继续自研完整量化平台。
后续保留 Data source fact + MALF + Alpha + Signal 为自研核心，
Position / Portfolio Plan / Trade / System Readout 保留现有 v1 readout 证据，
但停止按完整平台化方向继续扩张。
```

人话结论：`MALF + Alpha` 是研究灵魂，`Data + Signal` 是外部消费契约层；回测、
组合绩效、成交模拟、broker adapter、实盘接口和绩效报告优先交给成熟外部框架或 adapter。

## 2. 分类结果

| 分类 | 裁决 |
|---|---|
| retain_self_built | `Data source fact + MALF + Alpha + Signal` |
| freeze_self_build_expansion | `Position / Portfolio Plan / Trade / System Readout` |
| outsource_or_adapter | `Backtest / Portfolio Analytics / Fill Simulation / Broker / Report` |

## 3. 放行影响

| 项 | 结果 |
|---|---|
| live next action | `none / terminal` |
| live next reopened by this card | `no` |
| formal DB mutation | `no` |
| production daily activation | `no` |
| first next route card | `v1-signal-export-contract-card` |
| daily production scope card | `deferred until outsourcing boundary is consumed` |

## 4. 下一阶段硬语义

- 下一阶段回测 adapter 必须显式实现 `T+0 signal -> T+1 open execution`。
- 第一版收益 proof 优先使用 `backtesting.py`，目标是可读、可审计、少魔法。
- 第二版组合级分析再接 `vectorbt`。
- easytrader / vn.py 只能在回测语义稳定后进入 broker adapter feasibility。

## 5. 证据入口

- [card](v1-core-retention-and-outsourcing-boundary-card-20260513-01.card.md)
- [record](v1-core-retention-and-outsourcing-boundary-card-20260513-01.record.md)
- [evidence-index](v1-core-retention-and-outsourcing-boundary-card-20260513-01.evidence-index.md)
- `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md`
- `docs/04-execution/00-conclusion-index-v1.md`

## 6. 保留边界

本结论不宣称收益回测已经实现，不宣称 `fill_ledger` 已形成真实成交闭环，
不宣称具备实盘交易能力，不删除当前 Position / Portfolio Plan / Trade / System Readout
的 v1 readout 证据，也不把外部项目差异自动升级为 blocker。
