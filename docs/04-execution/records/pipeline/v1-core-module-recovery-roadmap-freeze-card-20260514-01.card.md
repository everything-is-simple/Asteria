# V1 Core Module Recovery Roadmap Freeze Card

日期：2026-05-14

状态：`passed / roadmap frozen / post-terminal route`

## 1. 背景

`v1-vectorbt-portfolio-analytics-proof-card-20260514-01` 已证明外部
portfolio analytics adapter 可运行，但结果仍显示 active Signal 覆盖稀疏、组合收益为负、
exposure time 极低。该事实不适合直接推进 broker feasibility。

本卡冻结 `docs/03-refactor/06-asteria-core-module-recovery-and-proof-roadmap-v1.md`，
正式把 post-terminal 研究路线从 broker feasibility 前移到核心模块恢复与证明。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `v1-core-module-recovery-roadmap-freeze-card-20260514-01` |
| route type | `roadmap-only / post-terminal / scope-freeze` |
| owner | `codex` |

## 3. 输入范围

| 输入 | 用途 |
|---|---|
| `docs/03-refactor/06-asteria-core-module-recovery-and-proof-roadmap-v1.md` | core recovery / proof 路线权威 |
| `docs/04-execution/records/pipeline/v1-vectorbt-portfolio-analytics-proof-card-20260514-01.conclusion.md` | 前置 vectorbt 组合 proof 结果 |
| `docs/04-execution/00-conclusion-index-v1.md` | terminal live next 与 post-terminal route 结论索引 |
| `docs/03-refactor/00-module-gate-ledger-v1.md` | gate ledger 与路线状态同步 |
| `governance/module_gate_registry.toml` | live next terminal truth sanity check |

## 4. 授权动作

- 冻结 core module recovery / proof roadmap 的 Stage 0。
- 把 `v1-broker-adapter-feasibility-card` 标记为 deferred，不作为近期 route card。
- 把 `v1-malf-v1-4-immutability-anchor-card` 标记为下一张 prepared route card。
- 登记执行四件套、外部 report / manifest 与 Validated archive。
- 同步 gate ledger 与 conclusion index 的 post-terminal 路线说明。

## 5. 禁止动作

- 不修改 `governance/module_gate_registry.toml` 的 `current_allowed_next_card`。
- 不写、不 rebuild、不 promote `H:\Asteria-data`。
- 不接真实 broker，不发送真实委托，不打开自动交易。
- 不重定义 MALF v1.4，不迁移 Alpha/PAS 历史代码，不冻结新版 Alpha/PAS 合同。
- 不执行收益 proof、组合 reproof、broker adapter feasibility 或实盘相关动作。

## 6. 通过标准

- 当前没有正式收益证明、真实成交闭环或实盘交易能力已明确登记。
- `v1-broker-adapter-feasibility-card` 已明确 deferred。
- `current live next = none / terminal` 保持不变。
- `H:\Asteria-data` mutation 为 `no`。
- 下一张 route card 明确为 `v1-malf-v1-4-immutability-anchor-card`。
