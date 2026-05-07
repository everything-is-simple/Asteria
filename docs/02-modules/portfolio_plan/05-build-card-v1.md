# Portfolio Plan Build Card v1

日期：2026-04-27

状态：frozen / freeze review passed / bounded proof passed / full build not executed

## 1. 本卡目标

补齐 Portfolio Plan pre-gate 六件套 draft 的历史卡已由
`portfolio-plan-freeze-review-20260507-01` 承接并冻结为 review-only 合同表面。

本历史 pre-gate 卡不直接执行代码施工。Portfolio Plan bounded proof 已由
`portfolio-plan-bounded-proof-build-card-20260507-01` 执行通过；full build 仍必须另开卡。

## 2. 当前卡位

| 项 | 值 |
|---|---|
| active_module | `portfolio_plan` |
| card_type | freeze review passed / historical pre-gate card |
| implementation_allowed | no |
| formal_db_write_allowed | no |
| freeze_allowed | completed by `portfolio-plan-freeze-review-20260507-01` |

## 3. 前置门槛

Portfolio Plan design freeze 已在以下上游 release 后完成：

```text
Position bounded proof passed
```

## 4. 本轮允许

| 项 | 裁决 |
|---|---|
| 保留 Portfolio Plan 六件套冻结合同 | 允许 |
| 明确 Portfolio Plan 只读消费 Position 输出 | 允许 |
| 定义 Portfolio Plan 不回写 Position / Signal / Alpha / MALF 的硬边界 | 允许 |
| 冻结 `portfolio_plan.duckdb` schema 合同 | 允许 |
| 冻结 runner / audit contract | 允许 |
| 更新模块文档索引和门禁账本中的 freeze review passed 状态 | 允许 |

## 5. 本轮不允许

| 项 | 裁决 |
|---|---|
| 迁移旧 Portfolio engine | 禁止 |
| 创建正式 Portfolio Plan DuckDB | 禁止 |
| 修改 MALF / Alpha / Signal / Position / Trade / System 代码 | 禁止 |
| 建立 Trade 执行逻辑 | 禁止 |
| 执行 Portfolio Plan bounded proof / full build / segmented build | 禁止 |

## 6. 下一步入口

freeze review 通过后，Portfolio Plan 只能准备下一张卡：

```text
portfolio-plan-bounded-proof-build-card-20260507-01
```

该下一卡必须继续只读消费：

```text
H:\Asteria-data\position.duckdb
```

本卡不执行下一卡。

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
H:\Asteria\.venv\Scripts\pytest.exe --basetemp=H:/Asteria-temp/pytest-tmp-portfolio-plan-freeze-review-20260507-01 -o cache_dir=H:/Asteria-temp/pytest-cache-portfolio-plan-freeze-review-20260507-01
```

## 8. 交付物

| 交付物 | 路径 |
|---|---|
| Portfolio Plan pre-gate 文档 | `H:\Asteria\docs\02-modules\portfolio_plan\` |
| 模块门禁账本 | `H:\Asteria\docs\03-refactor\00-module-gate-ledger-v1.md` |
| 主线模块文档索引 | `H:\Asteria\docs\02-modules\04-mainline-module-delivery-index-v1.md` |
