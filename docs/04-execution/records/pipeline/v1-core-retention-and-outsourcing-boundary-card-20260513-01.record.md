# V1 Core Retention And Outsourcing Boundary Record

日期：2026-05-13

run_id：`v1-core-retention-and-outsourcing-boundary-card-20260513-01`

## 1. Execution Summary

本卡已完成。它只读核对当前 Asteria v1 使用价值裁决、当前 Trade / fill 事实、
历史版本成熟语义和外部量化框架分工，冻结 Asteria 后续“核心自研 + 外围外包/adapter”
的战略边界。

## 2. Steps

1. 重读 Asteria live authority，确认 `final-release-closeout-card` 已通过且当前 live next 仍为 `none / terminal`。
2. 复核 `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md`，确认第 4 卡已裁决 `research_usable_with_caveats`。
3. 核对当前 Trade 表面：`execution_plan` 仍是 planned surface，`fill_ledger` 是 retained gap，不是成交闭环。
4. 核对历史版本回收点：Data producer、T+1 open、filled / rejected、broker kernel、risk unit、system readout。
5. 核对外部项目分工：backtesting.py、vectorbt、qlib、Hikyuu、FinHack、easytrader、backtrader。
6. 更新 roadmap Phase 2，冻结 core retention / outsourcing boundary。
7. 生成 repo 四件套，并同步 conclusion index 与 module gate ledger 的 post-terminal 状态。

## 3. Boundary Result

| 分类 | 裁决 |
|---|---|
| retain_self_built | `Data source fact + MALF + Alpha + Signal` |
| freeze_self_build_expansion | `Position / Portfolio Plan / Trade / System Readout` |
| outsource_or_adapter | `Backtest / Portfolio Analytics / Fill Simulation / Broker / Report` |
| first proof target | `backtesting.py` |
| second proof target | `vectorbt` |
| future broker target | `easytrader` / `vn.py` feasibility after backtest semantics stabilize |

## 4. Key Truths

- `MALF + Alpha` 是 Asteria 的研究灵魂。
- `Data + Signal` 是让研究灵魂能被外部框架消费的契约层。
- 当前 Asteria 没有正式收益回测、真实成交闭环或实盘交易能力。
- 下一阶段必须显式保留 `T+0 signal -> T+1 open execution`。
- 历史版本只回收语义、契约和经验，不直接迁移运行时代码。

## 5. Verification

本卡为 roadmap-only / read-only / post-terminal strategic boundary，不执行 runtime、不安装依赖、
不写正式 DB。验证范围为 roadmap / execution four-piece / conclusion index / module gate ledger
一致性检查。
