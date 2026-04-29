# MALF Day Bounded Proof Card

日期：2026-04-28

## 1. 背景

本卡承接 MALF 六件套冻结、MALF day bounded proof 施工清单以及 MALF release gate，目标不是再发明 MALF 语义，而是把已经实现的 MALF day 主链条跑成正式可放行结果，并把放行过程整理成可追溯闭环。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `malf` |
| run_id | `malf-day-bounded-proof-20260428-01` |
| stage | `bounded-proof / release` |
| source DB | `H:\Asteria-temp\data-bootstrap-smoke-all-2\market_base_day.duckdb` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| timeframe | `day` |
| start_dt | `2024-01-01` |
| end_dt | `2024-12-31` |
| symbol_limit | `4` |
| core_rule_version | `core-rule-fractal-1bar-v1` |
| sample_version | `sample-v1` |
| MALF authority directory | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2` |
| MALF authority zip | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2.zip` |
| docs/code snapshot | `H:\Asteria-Validated\Asteria-docs-code-20260428-214427.zip` |
| deep research report | `H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.md` |

## 3.1 权威边界

| 项 | 值 |
|---|---|
| upstream semantics | `MALF three-part design set is authoritative; no downstream rewrite` |
| formal DB permission | `allowed only for MALF Core / Lifespan / Service day DBs after hard audit` |
| allowed next action before card | `MALF day bounded proof` |

## 4. 允许动作

- 在 staging 路径构建 MALF Core / Lifespan / Service 三库
- 跑 hard audit，生成 closeout、manifest、summary 等正式证据
- 审计通过后 promote 到 `H:\Asteria-data`
- 更新门禁与执行记录文档

## 5. 禁止动作

- 不进入 Alpha / Signal / Position / Portfolio Plan / Trade / System 施工
- 不把 `data` 当成策略模块扩展
- 不建立全链路 pipeline
- 不允许任何下游模块写回 MALF

## 6. 关联入口

- [MALF bounded proof checklist](../../../03-refactor/03-malf-day-bounded-proof-construction-checklist-v1.md)
- [module gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
- [MALF conclusion](malf-day-bounded-proof-20260428-01.conclusion.md)
