# Signal Build Card v1

日期：2026-04-27

状态：frozen / freeze review passed / superseded by Signal bounded proof build card

## 1. 本卡目标

记录 Signal freeze review 通过后的冻结边界，为下一张 Signal bounded proof build card 做准备。

本卡不允许代码施工，不允许创建正式 DuckDB。Signal freeze review 已冻结 Signal 六件套，但不授权
Signal construction。

## 2. 当前卡位

| 项 | 值 |
|---|---|
| active_module | `signal` |
| card_type | freeze review closure |
| implementation_allowed | no |
| formal_db_write_allowed | no |
| freeze_allowed | yes; completed by `signal-freeze-review-20260429-01` |

## 3. 前置门槛

Signal bounded proof build card 前必须等待：

```text
Signal freeze review passed
```

## 4. 本轮允许

| 项 | 裁决 |
|---|---|
| 审阅并冻结 Signal 六件套 | 已完成 |
| 明确 Signal 只读消费 Alpha 输出 | 已完成 |
| 定义 Signal 不回写 Alpha / MALF 的硬边界 | 已完成 |
| 定义 `signal.duckdb` 的目标 schema contract | 已完成 |
| 定义 runner / audit contract | 已完成 |
| 更新模块文档索引和门禁账本中的 freeze review passed 状态 | 允许 |

## 5. 本轮不允许

| 项 | 裁决 |
|---|---|
| 迁移旧 Signal engine | 禁止 |
| 创建正式 Signal DuckDB | 禁止 |
| 修改 MALF / Alpha / Position / Portfolio / Trade / System 代码 | 禁止 |
| 建立 Position 持仓逻辑 | 禁止 |
| 把 Alpha 以外的 MALF/legacy/downstream 输入当作 Signal 正式输入 | 禁止 |
| 直接打开 Signal bounded proof 代码施工 | 禁止，必须另开 build card |

## 6. 下一步入口

Signal freeze review 通过后的唯一下一步为：

```text
Signal bounded proof build card
```

该下一卡必须继续遵守本次冻结的六件套：

```text
docs/02-modules/signal/00-authority-design-v1.md
docs/02-modules/signal/01-semantic-contract-v1.md
docs/02-modules/signal/02-database-schema-spec-v1.md
docs/02-modules/signal/03-runner-contract-v1.md
docs/02-modules/signal/04-audit-spec-v1.md
docs/02-modules/signal/05-build-card-v1.md
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
| Signal pre-gate 文档 | `H:\Asteria\docs\02-modules\signal\` |
| 模块门禁账本 | `H:\Asteria\docs\03-refactor\00-module-gate-ledger-v1.md` |
| 主线模块文档索引 | `H:\Asteria\docs\02-modules\04-mainline-module-delivery-index-v1.md` |
