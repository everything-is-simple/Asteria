# System Readout Build Card v1

日期：2026-04-27

状态：frozen / freeze review passed / bounded proof passed / full build not executed

## 1. 本卡目标

本文件记录 System Readout 六件套在 freeze review 与 bounded proof 通过后的当前卡位：
设计、schema、runner、audit 合同已冻结，并已完成 day bounded proof。

当前已允许的事实是 day bounded proof passed / full build not executed；不代表 System full build
或 Pipeline runtime 已打开。

## 2. 当前卡位

| 项 | 值 |
|---|---|
| active_module | `system_readout` |
| card_type | frozen documentation contract after bounded proof |
| implementation_allowed | bounded proof surface only |
| formal_db_write_allowed | bounded proof surface only |
| freeze_allowed | already passed via `system-readout-freeze-review-20260507-01` |

## 3. 前置门槛

System Readout 进入 design freeze 前必须等待：

```text
Trade released
```

## 4. 本轮允许

| 项 | 裁决 |
|---|---|
| 创建 System Readout bounded proof 最小 runtime | 已完成 |
| 明确 System Readout 只读消费全链路正式账本 | 已完成 |
| 定义 System Readout 不写回任何业务模块的硬边界 | 已完成 |
| 创建 `system.duckdb` 的 bounded proof schema surface | 已完成 |
| 落地 runner / audit 最小合同实现 | 已完成 |
| 更新模块文档索引和门禁账本中的 passed 状态 | 本卡要求 |

## 5. 本轮不允许

| 项 | 裁决 |
|---|---|
| 绕过 bounded proof build card 直接 full build | 禁止 |
| 迁移旧 System engine | 禁止 |
| 扩展为 System full build 或 segmented production build | 禁止 |
| 修改 MALF / Alpha / Signal / Position / Portfolio Plan / Trade 代码 | 禁止 |
| 触发上游业务重算 | 禁止 |
| 把 Trade pre-gate draft 直接当作 released 上游 | 禁止 |

## 6. 下一步入口

System Readout bounded proof 通过后，System 下一步只能进入：

```text
Pipeline freeze review
```

后续 bounded proof build card 必须以以下已冻结文档为权威输入：

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
