# V1 Application DB Readiness Audit Card

日期：2026-05-13

状态：`passed / application DB readiness audited`

## 1. 背景

`final-release-closeout-card` 已通过，Asteria 主线当前 truth 仍是 `none / terminal`。
本卡是 `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md` 中第二张
post-terminal 使用验证路线卡，只读检查正式 DB 是否足以支撑下一张人读应用验收报告。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `v1-application-db-readiness-audit-card-20260513-01` |
| route type | `roadmap-only / read-only / post-terminal` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| source roadmap | `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md` |
| scope predecessor | `v1-usage-validation-scope-card-20260512-01` |
| current live truth | `governance/module_gate_registry.toml` + `docs/03-refactor/00-module-gate-ledger-v1.md` + `docs/04-execution/00-conclusion-index-v1.md` |
| formal DB root | `H:\Asteria-data` |
| report root | `H:\Asteria-report` |
| validated root | `H:\Asteria-Validated` |

## 4. 允许动作

- 只读打开 `H:\Asteria-data` 当前 `25` 个正式 DuckDB。
- 核对 Data / MALF / Alpha / Signal 共 `20` 个上游应用输入 DB 的必备表面。
- 核对 Downstream / Pipeline 共 `5` 个 DB 的 readout surface 可读性。
- 将 retained caveat 分类登记到 report、Validated zip 和 repo 四件套。

## 5. 禁止动作

- 不修改 `governance/module_gate_registry.toml` 的 `current_allowed_next_card`。
- 不写、不重建、不补写、不 promote `H:\Asteria-data`。
- 不把本卡解释成新的 live next card。
- 不把 `fill_ledger` retained gap 伪装成真实成交闭环。
- 不提前打开 `daily-incremental-production-scope-card`。

## 6. 后续门禁

本卡通过后，只允许沿 usage validation 路线进入：

```text
v1-usage-readout-report-card
```

当前主线 live truth 继续保持：

```text
none / terminal
```
