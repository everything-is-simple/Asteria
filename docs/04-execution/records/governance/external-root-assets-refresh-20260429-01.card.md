# External Root Assets Refresh Card

日期：2026-04-29

## 1. 背景

本卡承接根配置刷新之后的外部资产根目录对齐。目标是确认
`H:\Asteria-Validated`、`H:\Asteria-report`、`H:\Asteria-temp` 三个 repo 外根目录
继续保持分工清晰：Validated 只放正式权威/证据资产，Report 放人读 closeout 与 manifest，
Temp 只放临时构建、缓存和 run-scoped staging。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `governance` |
| run_id | `external-root-assets-refresh-20260429-01` |
| stage | `external-assets-governance-refresh` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| validated root | `H:\Asteria-Validated` |
| report root | `H:\Asteria-report` |
| temp root | `H:\Asteria-temp` |
| docs/code snapshot | `H:\Asteria-Validated\Asteria-docs-code-20260428-214427.zip` |
| MALF authority directory | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2` |
| execution index | `docs/04-execution/00-conclusion-index-v1.md` |

## 3.1 权威边界

| 项 | 值 |
|---|---|
| upstream semantics | `read-only; no MALF semantic rewrite` |
| formal DB permission | `not allowed` |
| allowed next action before card | `Alpha freeze review` |

## 4. 允许动作

- 生成外部根目录 inventory，记录 Validated / Report / Temp 当前分工和资产状态。
- 在 `H:\Asteria-report\governance\2026-04-29\external-root-assets-refresh-20260429-01\` 生成 closeout、manifest 与 root inventory。
- 在 `H:\Asteria-Validated` 生成本卡 validated zip。
- 更新 repo 内 execution 四件套、conclusion index 和 Validated 资产清单。

## 5. 禁止动作

- 不把 `H:\Asteria-temp` 的缓存或 staging 提升为权威输入。
- 不删除或重写既有 Validated 权威资产。
- 不进入 Alpha 代码施工，不创建 Alpha 或下游正式 DuckDB。
- 不修改 MALF 业务语义，不允许任何下游写回 MALF。

## 6. 关联入口

- [validated asset inventory](../../../01-architecture/02-validated-asset-inventory-v1.md)
- [execution discipline](../../00-execution-discipline-v1.md)
- [module gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
