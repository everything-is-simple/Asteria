# Validated Root Manifest Refresh Card

日期：2026-04-29

## 1. 背景

本卡承接 `external-root-assets-refresh-20260429-01`。外部三根目录已经完成分工登记后，
`H:\Asteria-Validated` 仍需要在根目录自带人读 README 和机器 manifest，避免权威资产、
历史快照、release evidence 与旁证资产只能靠人工记忆区分。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `governance` |
| run_id | `validated-root-manifest-refresh-20260429-01` |
| stage | `validated-root-manifest-refresh` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| validated root | `H:\Asteria-Validated` |
| previous external root refresh | `external-root-assets-refresh-20260429-01` |
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

- 在 `H:\Asteria-Validated` 增加根 README，说明 Validated 的职责、权威锚点和禁止用途。
- 在 `H:\Asteria-Validated` 增加机器 manifest，记录顶层资产、角色和 SHA256。
- 在 `H:\Asteria-report` 生成本卡 closeout 与 manifest。
- 在 `H:\Asteria-Validated` 生成本卡 release evidence zip。
- 更新 repo 内 execution 四件套、conclusion index 和 Validated 资产清单。

## 5. 禁止动作

- 不删除或覆盖既有 Validated 权威资产。
- 不把 Validated 当作临时 scratch。
- 不进入 Alpha 代码施工，不创建 Alpha 或下游正式 DuckDB。
- 不修改 MALF 业务语义，不允许任何下游写回 MALF。

## 6. 关联入口

- [validated asset inventory](../../../01-architecture/02-validated-asset-inventory-v1.md)
- [external root assets refresh](external-root-assets-refresh-20260429-01.conclusion.md)
- [execution discipline](../../00-execution-discipline-v1.md)
