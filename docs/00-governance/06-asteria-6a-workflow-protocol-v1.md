# Asteria 6A Workflow Protocol v1

日期：2026-05-12

## 1. 定位

本文件把 `H:\Asteria-Validated\MALF-reference\workflows\6A工作流.md`
中的 6A 执行骨架迁移为 Asteria 当前主线的项目工作流。它不是新的业务权威，
也不替代 gate registry、module gate ledger、roadmap 或 conclusion index。

本协议只回答一个问题：

```text
每一张 Asteria 执行卡如何推进、验证、归档、同步。
```

## 2. 工具顺序

每次 Asteria 工作默认按以下工具顺序运行：

1. `codebase-retrieval`：先理解 repo 结构、治理面、代码流和相关符号。
2. `context7`：只有外部库/API 行为依赖当前文档时使用。
3. `fetch`：读取用户给定的具体 URL 或外部页面。
4. `sequential-thinking`：复杂裁决、根因分析、迁移计划或多分支判断时使用。
5. `codex_apps`：创建自动化、查看自动化、线程 heartbeat 等 Codex app 动作。

精确字符串、文件名和错误文本可以在 `codebase-retrieval` 之后使用本地 exact search。

## 3. Asteria-6A

### A1 Align

目标是先确认当前 live authority，而不是从记忆或上一轮聊天继续。

必须核对：

- `README.md`
- `AGENTS.md`
- `docs/00-governance/00-asteria-refactor-charter-v1.md`
- `docs/01-architecture/00-mainline-authoritative-map-v1.md`
- `docs/01-architecture/01-database-topology-v1.md`
- `governance/module_gate_registry.toml`
- `docs/03-refactor/00-module-gate-ledger-v1.md`
- `docs/03-refactor/04-asteria-full-system-roadmap-v1.md`
- `docs/04-execution/00-conclusion-index-v1.md`

输出必须说明当前卡、卡类型、允许动作、禁止动作和证据基线。

### A2 Architect

目标是把当前卡拆成 1-3 个可验收子项。

卡类型决定执行路径：

| 卡类型 | 执行动作 |
|---|---|
| `review-only` | 只读审查、写 conclusion/evidence，不迁移代码、不建正式 DB |
| `scope-freeze` | 冻结边界、更新治理面，不执行 runtime |
| `proof/build` | runner、tests、report、audit、evidence 同步闭环 |
| `repair` | 只修归因断点，不扩大到相邻模块 |
| `closeout` | 只读现有证据做 passed/blocked 裁决 |
| `maintenance` | 只在明确 maintenance card 下扩展 foundation surface |

### A3 Act

只执行当前卡授权范围。不得把一个卡自然扩成 full build、semantic repair、
业务模块语义重定义或正式 DB 写入。

正式数据写入仍必须经过 guarded runner：

```text
H:\Asteria-temp staging rebuild
-> formal DB backup
-> explicit --allow-formal-data-write
-> audit passed
-> promote
```

### A4 Assert

验证应随风险扩展。默认检查顺序：

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_asteria_workflow.py --strict
H:\Asteria\.venv\Scripts\ruff.exe check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\ruff.exe format --check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\mypy.exe src --cache-dir H:\Asteria-temp\mypy-cache
H:\Asteria\.venv\Scripts\pytest.exe --basetemp=H:/Asteria-temp/pytest-tmp-<run_id> -o cache_dir=H:/Asteria-temp/pytest-cache-<run_id>
```

窄卡可以先跑 targeted tests，但 release / closeout / governance card 必须说明未跑全量检查的原因。

### A5 Archive

所有正式证据必须落在 repo 外：

| 证据 | 位置 |
|---|---|
| 人读报告、closeout、manifest | `H:\Asteria-report` |
| validated zip / authority package | `H:\Asteria-Validated` |
| 临时 DB、pytest、cache、staging | `H:\Asteria-temp` |

`H:\Asteria-Validated` 只存 validated input/output assets，不作 scratch。

### A6 Advance

完成前必须同步 Asteria 执行四件套和 live authority：

- `docs/04-execution/records/<module>/<run_id>.card.md`
- `docs/04-execution/records/<module>/<run_id>.record.md`
- `docs/04-execution/records/<module>/<run_id>.evidence-index.md`
- `docs/04-execution/records/<module>/<run_id>.conclusion.md`
- `docs/04-execution/00-conclusion-index-v1.md`
- `docs/03-refactor/00-module-gate-ledger-v1.md`
- `governance/module_gate_registry.toml`
- module API contract / roadmap / Validated inventory when the card touches those surfaces

没有完成 A6，不得宣告任务完成。blocked 卡也必须落 conclusion 和 evidence-index。

## 4. Codex Hooks 用法

项目本地 hook bundle 位于：

```text
plugins/asteria-workflow/hooks.json
```

建议启用的 hook：

| Hook | 作用 |
|---|---|
| `SessionStart` | 提醒 A1 必读权威面和 MCP 顺序 |
| `UserPromptSubmit` | 用户说“继续/下一卡/提交推送”时提醒先查 live authority |
| `PreToolUse` | 写文件、跑正式数据或执行 shell 前提示 scope/gate 边界 |
| `PostToolUse` | 工具执行后提醒 A4/A5/A6 证据闭环 |
| `Stop` | 结束前提醒说明 passed/blocked、验证范围和下一步 |

hook 只做提醒和轻量检查，不代替 `check_project_governance.py`。

## 5. Codex Automation 用法

当前推荐的 Asteria 自动化是：

```text
asteria-daily-workflow-drift-scan
```

它每天只读检查：

- live next 是否与 registry、gate ledger、conclusion index 一致；
- AGENTS 是否滞后于 live authority；
- Asteria-6A protocol 和 hooks bundle 是否仍存在；
- workflow 所需 MCP 配置是否仍可见。

自动化不得直接修改 repo、正式 DB 或 Validated 资产。

## 6. 完成判定

一次 Asteria 工作只有在以下问题都有明确答案时，才算可以收口：

| 问题 | 要求 |
|---|---|
| 这张卡完成了吗 | 分开回答 implementation、validation、closeout |
| 是 passed 还是 blocked | 不得把测试通过等同于 release passed |
| 证据在哪里 | 给出 repo record、report、Validated 或 N/A 原因 |
| 下一步是什么 | 从 live authority 回答；terminal 状态也可以是合法答案 |
| 是否越权 | 明确说明没有打开的模块、full build 或正式写入 |
