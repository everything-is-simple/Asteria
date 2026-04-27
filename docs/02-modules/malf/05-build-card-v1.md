# MALF Build Card v1

日期：2026-04-27

状态：frozen

## 1. 本卡目标

冻结 MALF day 的文档、schema、runner、audit 契约，为下一轮 MALF bounded proof 施工提供唯一依据。

## 2. 本轮允许

| 项 | 裁决 |
|---|---|
| 整理 MALF 六件套设计文档 | 允许 |
| 引用 MALF 三份权威源文档 | 允许 |
| 定义 day 三库表族和自然键 | 允许 |
| 定义 runner contract | 允许 |
| 定义 audit spec | 允许 |
| 更新模块门禁账本 | 允许 |

## 3. 本轮不允许

| 项 | 裁决 |
|---|---|
| 迁移旧 MALF engine | 禁止 |
| 创建正式 MALF DuckDB | 禁止 |
| 修改 Alpha / Signal / Position / Portfolio / Trade / System 代码 | 禁止 |
| 建立 pipeline 全链路 | 禁止 |
| 下游模块补充自有语义 | 禁止 |

## 4. 下一施工入口

下一轮 MALF 施工只允许从 bounded proof 开始：

```text
scripts/malf/run_malf_day_core_build.py
scripts/malf/run_malf_day_lifespan_build.py
scripts/malf/run_malf_day_service_build.py
scripts/malf/run_malf_day_audit.py
```

代码文件尚未在本轮创建。

## 5. 验收命令

文档交付后必须运行：

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
```

release gate 前再运行：

```powershell
H:\Asteria\.venv\Scripts\ruff.exe check .
H:\Asteria\.venv\Scripts\ruff.exe format --check .
H:\Asteria\.venv\Scripts\mypy.exe src
H:\Asteria\.venv\Scripts\pytest.exe
```

## 6. 交付物

| 交付物 | 路径 |
|---|---|
| 模块文档 | `H:\Asteria\docs\02-modules\malf\` |
| 交付索引 | `H:\Asteria\docs\02-modules\04-mainline-module-delivery-index-v1.md` |
| 可交付 zip | `H:\Asteria-Validated\Asteria-mainline-module-docs-v1.zip` |
