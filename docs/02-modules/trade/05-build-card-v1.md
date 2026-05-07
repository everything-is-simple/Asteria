# Trade Build Card v1

日期：2026-04-27

状态：superseded by freeze review / next build card prepared

## 1. 本卡目标

本历史卡补齐 Trade pre-gate 六件套 draft；`trade-freeze-review-20260507-01` 已完成设计冻结。

本卡本身不允许代码施工，不允许创建正式 DuckDB；冻结结论由 `trade-freeze-review-20260507-01` 承接。后续唯一允许准备的执行卡为 `trade-bounded-proof-build-card-20260507-01`。

## 2. 当前卡位

| 项 | 值 |
|---|---|
| active_module | `trade` |
| card_type | pre-gate documentation draft |
| implementation_allowed | no |
| formal_db_write_allowed | no |
| freeze_allowed | no |

## 3. 前置门槛

Trade 进入 design freeze 前必须等待：

```text
Portfolio Plan released
```

## 4. 本轮允许

| 项 | 裁决 |
|---|---|
| 创建 Trade 六件套 draft | 允许 |
| 明确 Trade 只读消费 Portfolio Plan 输出 | 允许 |
| 定义 Trade 不回写 Portfolio Plan / Position / Signal / Alpha / MALF 的硬边界 | 允许 |
| 定义 `trade.duckdb` 的 draft schema | 允许 |
| 定义 runner / audit draft contract | 允许 |
| 更新模块文档索引和门禁账本中的 draft 状态 | 允许 |

## 5. 本轮不允许

| 项 | 裁决 |
|---|---|
| 冻结 Trade 设计 | 禁止 |
| 迁移旧 Trade engine | 禁止 |
| 创建正式 Trade DuckDB | 禁止 |
| 修改 MALF / Alpha / Signal / Position / Portfolio Plan / System 代码 | 禁止 |
| 建立 System Readout 读出逻辑 | 禁止 |
| 把 Portfolio Plan pre-gate draft 直接当作 released 上游 | 禁止 |

## 6. 下一步入口

Portfolio Plan released 后，Trade 才能进入：

```text
Trade design freeze review
```

该 review 必须重新审阅：

```text
docs/02-modules/trade/00-authority-design-v1.md
docs/02-modules/trade/01-semantic-contract-v1.md
docs/02-modules/trade/02-database-schema-spec-v1.md
docs/02-modules/trade/03-runner-contract-v1.md
docs/02-modules/trade/04-audit-spec-v1.md
docs/02-modules/trade/05-build-card-v1.md
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
| Trade pre-gate 文档 | `H:\Asteria\docs\02-modules\trade\` |
| 模块门禁账本 | `H:\Asteria\docs\03-refactor\00-module-gate-ledger-v1.md` |
| 主线模块文档索引 | `H:\Asteria\docs\02-modules\04-mainline-module-delivery-index-v1.md` |
