# Alpha Build Card v1

日期：2026-04-29

状态：frozen / freeze review passed / superseded by next build card

## 1. 本卡目标

记录 Alpha 六件套已通过 freeze review，并为下一张 Alpha bounded proof build card
划定边界。

本卡不允许代码施工，不允许创建正式 DuckDB；Alpha 冻结结论由
`alpha-freeze-review-20260429-01` 形成。

## 2. 当前卡位

| 项 | 值 |
|---|---|
| active_module | `alpha` |
| card_type | freeze review closure |
| implementation_allowed | no |
| formal_db_write_allowed | no |
| freeze_allowed | completed |
| current_allowed_next_action | `Alpha bounded proof build card` |

## 3. 前置门槛

Alpha 进入 bounded proof 施工前必须等待：

```text
MALF day WavePosition release evidence passed
Alpha freeze review passed
Alpha bounded proof build card
```

## 4. 本轮允许

| 项 | 裁决 |
|---|---|
| 冻结 Alpha 六件套 | 已完成 |
| 明确 Alpha 只读消费 WavePosition | 允许 |
| 定义 Alpha 不写回 MALF 的硬边界 | 允许 |
| 定义五个 alpha family DB 的 schema | 允许 |
| 定义 runner / audit contract | 允许 |
| 更新模块文档索引和门禁账本中的 freeze review passed 状态 | 允许 |

## 5. 本轮不允许

| 项 | 裁决 |
|---|---|
| 迁移旧 Alpha engine | 禁止 |
| 创建正式 Alpha DuckDB | 禁止 |
| 修改 MALF / Signal / Position / Portfolio / Trade / System 代码 | 禁止 |
| 建立 Signal 聚合逻辑 | 禁止 |
| 把旧 BOF/TST/PB/CPB/BPB 结果直接升格为权威规则 | 禁止 |

## 6. 下一步入口

MALF day bounded proof 已通过并发布 WavePosition，Alpha freeze review 已通过。当前
Alpha 只能进入：

```text
Alpha bounded proof build card
```

该下一卡必须引用并遵守：

```text
docs/02-modules/alpha/00-authority-design-v1.md
docs/02-modules/alpha/01-semantic-contract-v1.md
docs/02-modules/alpha/02-database-schema-spec-v1.md
docs/02-modules/alpha/03-runner-contract-v1.md
docs/02-modules/alpha/04-audit-spec-v1.md
docs/02-modules/alpha/05-build-card-v1.md
docs/04-execution/records/alpha/alpha-freeze-review-20260429-01.conclusion.md
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
| Alpha pre-gate 文档 | `H:\Asteria\docs\02-modules\alpha\` |
| 模块门禁账本 | `H:\Asteria\docs\03-refactor\00-module-gate-ledger-v1.md` |
| 主线模块文档索引 | `H:\Asteria\docs\02-modules\04-mainline-module-delivery-index-v1.md` |
