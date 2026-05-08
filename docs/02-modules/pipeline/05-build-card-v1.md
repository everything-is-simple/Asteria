# Pipeline Build Card v1

日期：2026-04-29

状态：draft / pre-gate / not frozen

## 1. 本卡目标

补齐 Pipeline pre-gate 六件套 draft，为后续明确授权的 Pipeline 设计冻结做准备。
MALF bounded proof gate 已通过，但当前主线下一步仍是 `Alpha freeze review`。

本卡不允许代码施工，不允许建立全链路业务运行，不允许冻结 Pipeline。

## 2. 当前卡位

| 项 | 值 |
|---|---|
| active_module | `pipeline` |
| card_type | pre-gate documentation draft |
| implementation_allowed | no |
| formal_db_write_allowed | no |
| freeze_allowed | no |

## 3. 前置门槛

Pipeline 进入 design freeze 前必须等待：

```text
MALF bounded proof gate passed
active card explicitly authorizes Pipeline freeze review
```

## 4. 本轮允许

| 项 | 裁决 |
|---|---|
| 创建 Pipeline 六件套 draft | 允许 |
| 明确 Pipeline 只做编排和记录 | 允许 |
| 定义 Pipeline 不写回业务模块的硬边界 | 允许 |
| 定义 `pipeline.duckdb` 的 draft schema | 允许 |
| 定义 runner / audit draft contract | 允许 |
| 更新模块文档索引和门禁账本中的 draft 状态 | 允许 |

## 5. 本轮不允许

| 项 | 裁决 |
|---|---|
| 冻结 Pipeline 设计 | 禁止 |
| 建立全链路施工 | 禁止 |
| 创建正式 Pipeline DuckDB | 禁止 |
| 修改任何业务模块代码或输出 | 禁止 |
| 在 Pipeline 中定义业务语义 | 禁止 |
| 绕过单模块施工门禁 | 禁止 |

## 6. 下一步入口

MALF bounded proof gate 已通过后，Pipeline 仍必须等待明确 Pipeline 卡，才可进入：

```text
Pipeline freeze review
```

该 review 必须重新审阅：

```text
docs/02-modules/pipeline/00-authority-design-v1.md
docs/02-modules/pipeline/01-semantic-contract-v1.md
docs/02-modules/pipeline/02-database-schema-spec-v1.md
docs/02-modules/pipeline/03-runner-contract-v1.md
docs/02-modules/pipeline/04-audit-spec-v1.md
docs/02-modules/pipeline/05-build-card-v1.md
```

## 7. 验收命令

文档交付后必须运行：

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
```

release gate 前再运行：

```powershell
H:\Asteria\.venv\Scripts\ruff.exe check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\ruff.exe format --check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\mypy.exe src --cache-dir H:\Asteria-temp\mypy-cache
H:\Asteria\.venv\Scripts\pytest.exe
```

## 8. 交付物

| 交付物 | 路径 |
|---|---|
| Pipeline pre-gate 文档 | `H:\Asteria\docs\02-modules\pipeline\` |
| 模块门禁账本 | `H:\Asteria\docs\03-refactor\00-module-gate-ledger-v1.md` |
| 主线模块文档索引 | `H:\Asteria\docs\02-modules\04-mainline-module-delivery-index-v1.md` |
