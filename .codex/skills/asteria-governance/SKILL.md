---
name: asteria-governance
description: Asteria 重构工作的项目治理规则。Codex 修改 Asteria 文档、Python 代码、模块边界、DuckDB schema、runner 合同、执行卡或 release gate 时使用。
---

# Asteria 治理

## 概览

使用本技能时，Asteria 变更必须保持文档先行、模块内收敛，并与 MALF 主导的主线顺序对齐。

当前权威链：

- `H:\Asteria-Validated\Asteria-deep-research-report-重构系统最新剖切面研究报告-20260428.md`
- `H:\Asteria-Validated\Asteria-docs-code-20260502-104932.zip`
- `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_3`
- `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_3.zip`
- `H:\Asteria-Validated\Asteria-data-formal-promotion-evidence-20260502-01.zip`
- `H:\Asteria-Validated\Asteria-malf-v1-3-formal-rebuild-closeout-20260502-01.zip`

当前门禁状态：

```text
Data legacy formal promotion passed -> MALF v1.3 formal-data bounded closeout passed -> Position freeze review reentry
```

`Position freeze review reentry` 只允许 review-only 审查。它不授权 Position
实现、Position DB 创建、下游施工或全链路 pipeline。

## 必读文件

修改正式代码、schema、runner 合同或模块门禁前，必须先读：

1. `README.md`
2. `AGENTS.md`
3. `docs/00-governance/00-asteria-refactor-charter-v1.md`
4. `docs/01-architecture/00-mainline-authoritative-map-v1.md`
5. `docs/01-architecture/01-database-topology-v1.md`
6. `docs/03-refactor/00-module-gate-ledger-v1.md`
7. `docs/04-execution/00-conclusion-index-v1.md`

## 工作流

1. 从 `docs/03-refactor/00-module-gate-ledger-v1.md` 确认当前 active module。
2. 确认目标变更仍在该模块边界内；若需要越界，先更新治理文档再实现。
3. 正式源码或 schema 施工前，必须已有 design、spec 或 card。
4. 生成的 DB、报告和临时产物必须放在 repo 外。
5. release 或 proof 类工作必须创建或更新执行四件套：
   `card`, `evidence-index`, `record`, and `conclusion`.
6. commit 前运行项目检查。

## 主线规则

- `data` 是地基基础设施，不是策略主线模块。
- 主线顺序固定为：`MALF -> Alpha -> Signal -> Position -> Portfolio Plan -> Trade -> System`。
- `Pipeline` 只能编排和记录，不得定义业务语义。
- 下游模块不得写回 MALF，也不得重定义 MALF 字段。
- 不得合并 `wave_core_state` 与 `system_state`。
- 同一时间只能有一个主线模块处于施工或 review 放行状态。
- `H:\Asteria-Validated` 只存 validated 资产，不作临时目录。

## 环境

Python provider 使用 `D:\miniconda\py310`，优先使用 repo-local virtualenv `H:\Asteria\.venv`。

使用 repo-local 环境运行检查：

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\ruff.exe check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\ruff.exe format --check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\mypy.exe src --cache-dir H:\Asteria-temp\mypy-cache
H:\Asteria\.venv\Scripts\pytest.exe --basetemp=H:/Asteria-temp/pytest-tmp-<run_id> -o cache_dir=H:/Asteria-temp/pytest-cache-<run_id>
```

不要把工具缓存留在 repo root。`H:\Asteria\.ruff_cache` 和
`H:\Asteria\.mypy_cache` 都视为意外临时产物：若出现就删除，不得 stage，
并按上方 cache 目录重新运行检查。

## 风格

- Python 文件保持在 500 行以内，脚本 wrapper 保持在 240 行以内。
- Markdown design/spec 文件保持在 1200 行以内。
- 注释只解释意图、边界和不明显的不变量。
- 避免只复述赋值或函数名的注释。
- 优先使用小而清晰的模块合同，不随意扩大 helper 抽象。
