# System Readout Build Card v1

日期：2026-04-27

状态：draft / pre-gate / not frozen

## 1. 本卡目标

补齐 System Readout pre-gate 六件套 draft，为 Trade released 之后的 System Readout 设计冻结做准备。

本卡不允许代码施工，不允许创建正式 DuckDB，不允许冻结 System Readout。

## 2. 当前卡位

| 项 | 值 |
|---|---|
| active_module | `system_readout` |
| card_type | pre-gate documentation draft |
| implementation_allowed | no |
| formal_db_write_allowed | no |
| freeze_allowed | no |

## 3. 前置门槛

System Readout 进入 design freeze 前必须等待：

```text
Trade released
```

## 4. 本轮允许

| 项 | 裁决 |
|---|---|
| 创建 System Readout 六件套 draft | 允许 |
| 明确 System Readout 只读消费全链路正式账本 | 允许 |
| 定义 System Readout 不写回任何业务模块的硬边界 | 允许 |
| 定义 `system.duckdb` 的 draft schema | 允许 |
| 定义 runner / audit draft contract | 允许 |
| 更新模块文档索引和门禁账本中的 draft 状态 | 允许 |

## 5. 本轮不允许

| 项 | 裁决 |
|---|---|
| 冻结 System Readout 设计 | 禁止 |
| 迁移旧 System engine | 禁止 |
| 创建正式 System DuckDB | 禁止 |
| 修改 MALF / Alpha / Signal / Position / Portfolio Plan / Trade 代码 | 禁止 |
| 触发上游业务重算 | 禁止 |
| 把 Trade pre-gate draft 直接当作 released 上游 | 禁止 |

## 6. 下一步入口

Trade released 后，System Readout 才能进入：

```text
System Readout design freeze review
```

该 review 必须重新审阅：

```text
docs/02-modules/system_readout/00-authority-design-v1.md
docs/02-modules/system_readout/01-semantic-contract-v1.md
docs/02-modules/system_readout/02-database-schema-spec-v1.md
docs/02-modules/system_readout/03-runner-contract-v1.md
docs/02-modules/system_readout/04-audit-spec-v1.md
docs/02-modules/system_readout/05-build-card-v1.md
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
| System Readout pre-gate 文档 | `H:\Asteria\docs\02-modules\system_readout\` |
| 模块门禁账本 | `H:\Asteria\docs\03-refactor\00-module-gate-ledger-v1.md` |
| 主线模块文档索引 | `H:\Asteria\docs\02-modules\04-mainline-module-delivery-index-v1.md` |
