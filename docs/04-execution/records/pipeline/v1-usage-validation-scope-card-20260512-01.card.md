# V1 Usage Validation Scope Card

日期：2026-05-12

状态：`passed / scope frozen / roadmap-only route`

## 1. 背景

`final-release-closeout-card` 已通过，Asteria 主线当前 truth 仍是 `none / terminal`。
本卡不重开 live gate，而是按
`docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md`
执行第一张 post-terminal 只读路线卡，把 v1 使用验证的题目先冻结下来。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `v1-usage-validation-scope-card-20260512-01` |
| route type | `roadmap-only / read-only / post-terminal` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| source roadmap | `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md` |
| current live truth | `governance/module_gate_registry.toml` + `docs/03-refactor/00-module-gate-ledger-v1.md` + `docs/04-execution/00-conclusion-index-v1.md` |
| source DBs | `H:\Asteria-data\market_meta.duckdb` + `H:\Asteria-data\market_base_day.duckdb` |
| industry source reference | `H:\Asteria-Validated\MALF-reference\申万行业分类\最新个股申万行业分类(完整版-截至7月末).xlsx` |

## 4. 冻结范围

| 项 | 冻结值 |
|---|---|
| 股票池 | `申万一级行业各取一只，共 31 只` |
| 选股规则 | `2024 年覆盖完整度优先，execution-line 平均 amount 次优先，可带理由人工 override` |
| 日期范围 | `2024-01-02..2024-12-31` |
| 研究问题 | `Asteria 当前链路能否给出可解释、可审计的结构-信号-持仓-交易意图读出` |
| 报告形态 | `双层输出：总报告 + 少量逐股 appendix` |
| 正式 DB 权限 | `read_only` |
| 下一张路线卡 | `v1-application-db-readiness-audit-card` |

## 5. 允许动作

- 只读读取正式 `market_meta.duckdb` 与 `market_base_day.duckdb`。
- 解析 `sw2021_level3_snapshot`，归并出 31 个申万一级行业。
- 对每个一级行业冻结 1 只代表股，并生成 machine-readable manifest。
- 在 repo 内落四件套，在 `H:\Asteria-report` 与 `H:\Asteria-Validated` 落外部证据。

## 6. 禁止动作

- 不修改 `governance/module_gate_registry.toml` 的 `current_allowed_next_card`。
- 不把本卡解释成新的主线 live next card。
- 不写 `H:\Asteria-data`，不重建、不补写、不 promote 正式 DB。
- 不把 ST、停牌、完整上市退市或历史行业沿革 gap 伪装成已正式解决。
- 不提前打开 `daily-incremental-production-scope-card`。

## 7. 后续门禁

本卡通过后，只允许沿 usage validation 路线进入：

```text
v1-application-db-readiness-audit-card
```

当前主线 live truth 继续保持：

```text
none / terminal
```
