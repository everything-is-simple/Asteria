# V1 Core Retention And Outsourcing Boundary Card

日期：2026-05-13

状态：`passed / core retention and outsourcing boundary frozen`

## 1. 背景

`v1-usage-value-decision-card-20260513-01` 已裁决 Asteria 当前 v1
`research_usable_with_caveats`。该结论证明当前结构、机会、信号、组合和交易意图读出
具备研究价值，但不证明收益回测、真实成交闭环或实盘交易能力。

本卡作为 `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md` 的 Phase 2
战略边界裁决卡，回答下一阶段是否继续自研完整量化平台。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `v1-core-retention-and-outsourcing-boundary-card-20260513-01` |
| route type | `roadmap-only / read-only / post-terminal / strategic boundary` |
| owner | `codex` |

## 3. 输入范围

| 输入 | 用途 |
|---|---|
| `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md` | v1 使用验证与 Phase 2 路线权威 |
| `docs/04-execution/records/pipeline/v1-usage-value-decision-card-20260513-01.conclusion.md` | 第 4 卡价值裁决输入 |
| `src/asteria/trade/rules.py` / `src/asteria/trade/schema.py` | 当前 Trade execution / fill retained gap 事实 |
| `G:\malf-history\*` | 历史版本中可回收语义与经验 |
| Hikyuu / FinHack / easytrader / backtesting.py / vectorbt / qlib / backtrader | 外部框架角色分工参考 |

## 4. 授权动作

- 只读核对当前 Asteria、历史版本和外部项目边界。
- 在 roadmap 中追加 Phase 2 战略路线。
- 冻结 `retain_self_built / freeze_self_build_expansion / outsource_or_adapter` 三类裁决。
- 登记新卡四件套，并同步 conclusion index / module gate ledger 的 post-terminal 路线说明。

## 5. 禁止动作

- 不写、不重建、不 promote `H:\Asteria-data`。
- 不安装 backtesting.py、vectorbt、qlib、easytrader、backtrader 或其他外部依赖。
- 不迁移历史版本代码。
- 不删除 Position / Portfolio Plan / Trade / System Readout 现有 v1 readout 证据。
- 不把外部项目差异自动升级为 Asteria blocker。
- 不把本卡扩写成收益回测、真实成交闭环、broker adapter 或 production daily activation。

## 6. 通过标准

- 明确裁决 Asteria 后续不再默认自研完整量化平台。
- 明确保留自研核心：`Data source fact + MALF + Alpha + Signal`。
- 明确冻结平台化扩张：`Position / Portfolio Plan / Trade / System Readout`。
- 明确第一外部 proof target 为 `backtesting.py` 的 T+1 open PnL proof。
- 明确 `T+0 signal -> T+1 open execution` 是下一阶段硬语义。
- 当前 live next 仍保持 `none / terminal`。
