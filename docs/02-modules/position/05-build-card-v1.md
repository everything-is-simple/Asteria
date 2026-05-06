# Position Build Card v1

日期：2026-04-27

状态：freeze review passed / bounded-proof card specification frozen / build not executed

## 1. 本卡目标

冻结 Position bounded proof build card 的合同表面，为下一张可执行 build card 做准备。

本文件不是已执行 build card；本次不允许代码施工，不允许创建正式 DuckDB。

## 2. 当前卡位

| 项 | 值 |
|---|---|
| active_module | `position` |
| card_type | bounded-proof card specification / not executed |
| implementation_allowed | no |
| formal_db_write_allowed | no |
| freeze_allowed | yes, review-only design freeze passed |
| bounded_proof_execution_allowed | no |

## 3. 前置门槛

Position bounded proof 施工前必须等待：

```text
Position bounded proof build card
```

## 4. 本轮允许

| 项 | 裁决 |
|---|---|
| 冻结 Position 六件套合同表面 | 允许 |
| 明确 Position 只读消费 Signal 输出 | 允许 |
| 定义 Position 不回写 Signal / Alpha / MALF 的硬边界 | 允许 |
| 冻结 `position.duckdb` 的设计口径 | 允许，文档层 |
| 冻结 runner / audit 合同 | 允许，文档层 |
| 更新模块文档索引和门禁账本中的 freeze review 状态 | 允许 |

## 5. 本轮不允许

| 项 | 裁决 |
|---|---|
| 迁移旧 Position engine | 禁止 |
| 创建正式 Position DuckDB | 禁止 |
| 修改 MALF / Alpha / Signal / Portfolio / Trade / System 代码 | 禁止 |
| 建立 Portfolio Plan 资金裁决逻辑 | 禁止 |
| 把本文件当作已执行 bounded proof | 禁止 |

## 6. 下一步入口

Position freeze review re-entry 通过后，下一步才能打开：

```text
Position bounded proof build card
```

该 build card 执行前必须引用并遵守：

```text
docs/02-modules/position/00-authority-design-v1.md
docs/02-modules/position/01-semantic-contract-v1.md
docs/02-modules/position/02-database-schema-spec-v1.md
docs/02-modules/position/03-runner-contract-v1.md
docs/02-modules/position/04-audit-spec-v1.md
docs/02-modules/position/05-build-card-v1.md
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
| Position pre-gate 文档 | `H:\Asteria\docs\02-modules\position\` |
| 模块门禁账本 | `H:\Asteria\docs\03-refactor\00-module-gate-ledger-v1.md` |
| 主线模块文档索引 | `H:\Asteria\docs\02-modules\04-mainline-module-delivery-index-v1.md` |
