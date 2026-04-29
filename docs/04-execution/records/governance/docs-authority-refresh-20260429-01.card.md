# Docs Authority Refresh Card

日期：2026-04-29

## 1. 背景

本卡承接文档权威链与新鲜度门禁计划。继续写大量代码前，需要确认
`H:\Asteria-Validated`、repo 内 `docs/`、`governance/`、执行结论和自动检查之间
形成可追溯闭环。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `governance` |
| run_id | `docs-authority-refresh-20260429-01` |
| stage | `docs-authority-refresh` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| primary snapshot | `H:\Asteria-Validated\Asteria-docs-code-20260428-214427.zip` |
| deep research report | `H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.md` |
| MALF authority | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2.zip` |
| MALF authority directory | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2` |
| prerequisite docs | `README.md`, `AGENTS.md`, `docs/00-governance/00-asteria-refactor-charter-v1.md`, `docs/01-architecture/00-mainline-authoritative-map-v1.md`, `docs/01-architecture/01-database-topology-v1.md`, `docs/03-refactor/00-module-gate-ledger-v1.md` |

## 3.1 权威边界

| 项 | 值 |
|---|---|
| upstream semantics | `read-only; MALF semantics remain in Validated three-part design set` |
| formal DB permission | `not allowed` |
| allowed next action before card | `Alpha freeze review` |

## 4. 允许动作

- 更新 Validated 资产清单和文档入口，使 `214427` docs/code 快照成为当前重要快照锚点。
- 增加 docs sync 检查，验证关键 Validated 资产存在。
- 增加 MALF 权威桥接检查，验证三份终稿和桥接总纲均被 repo 文档引用。
- 增加 governance 单元测试覆盖资产漂移和 MALF 桥接漂移。
- 生成本卡 closeout、manifest 和 Validated 归档。

## 5. 禁止动作

- 不进入 Alpha 代码施工。
- 不迁移旧 Alpha / Signal / Position / Portfolio Plan / Trade / System 代码。
- 不创建任何 Alpha 或下游正式 DuckDB。
- 不修改 MALF 业务语义，不允许任何下游写回 MALF。
- 不把 `H:\Asteria-Validated` 当作临时 scratch。

## 6. 关联入口

- [validated asset inventory](../../../01-architecture/02-validated-asset-inventory-v1.md)
- [MALF authority bridge](../../../02-modules/02-malf-authoritative-design-bridge-v1.md)
- [module gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
- [execution discipline](../../00-execution-discipline-v1.md)
