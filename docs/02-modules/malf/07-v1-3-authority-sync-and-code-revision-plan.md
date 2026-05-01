# MALF v1.3 Authority Sync and Code Revision Plan

日期：2026-05-01

状态：draft / documentation sync / code revision card prepared

## 1. 结论

`H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_3` 已形成 MALF v1.3 权威定义包。
本轮评审结论为：

```text
v1.3 定义清晰，定理自洽，可以作为后续 repo 文档同步与代码修订依据。
```

该结论不等于当前实现已经达到 v1.3。当前已通过实现证据仍是
`malf-complete-alignment-closeout-20260430-01`。

## 2. v1.3 权威输入

| 文件 | 用途 |
|---|---|
| `MALF_00_Three_Documents_Bridge_v1_3.md` | v1.3 总入口与边界 |
| `MALF_01_Core_Definitions_Theorems_v1_3.md` | Core 定义、Break、Transition、Candidate、New Wave |
| `MALF_02_Lifespan_Stats_Definitions_Theorems_v1_3.md` | Lifespan 统计、rank、birth descriptors |
| `MALF_03_System_Service_Interface_v1_3.md` | Service 只读接口与字段边界 |
| `MALF_04_Core_Chart_View_v1_3.md` | Core 图表辅助理解 |
| `MALF_05_Lifespan_Chart_View_v1_3.md` | Lifespan 图表辅助理解 |
| `MALF_06_Service_Chart_View_v1_3.md` | Service 图表辅助理解 |
| `MALF_07_Definition_Theorem_Review_and_Implementation_Delta_v1_3.md` | 定义/定理评审与实现差异表 |

## 3. 定义与定理评审摘要

| 主题 | 评审结论 |
|---|---|
| Break | 清晰。使用 `current_effective_HL` / `current_effective_LH`，不再指任意历史 guard |
| Transition | 清晰。旧 wave 死亡后、新 wave 确认前的 system state，不是 wave |
| Transition Boundary | 清晰。双边界可同时支撑 same-direction 与 opposite-direction new wave |
| Candidate Guard | 清晰。候选守护点不是 wave，必须等待 progress confirmation |
| New Wave | 自洽。必须 active candidate guard + later progress confirmation |
| Lifespan | 自洽。只统计 confirmed wave，birth descriptors 只描述形成过程 |
| Service | 自洽。只读发布 WavePosition，不输出交易动作，不接受下游写回 |

## 4. 文档同步范围

本轮已把 v1.3 作为待同步语义写入 MALF 本地文档，但不修改当前 passed gate：

| 本地文档 | 同步内容 |
|---|---|
| `00-authority-design-v1.md` | 增加 v1.3 权威包、评审结论与待同步裁决 |
| `01-semantic-contract-v1.md` | 增加 current effective guard、transition boundary、birth descriptor 等语义 |
| `02-database-schema-spec-v1.md` | 增加 v1.3 待同步字段 |
| `03-runner-contract-v1.md` | 记录 runner mode enforcement gap |
| `04-audit-spec-v1.md` | 增加 v1.3 待新增 hard audit |

## 5. 代码修订卡目标

建议后续执行卡：

```text
malf-v1-3-authority-sync-code-revision-20260501-01
```

目标：

1. 修订 Core schema / builder，显式追踪 current effective guard、broken guard、transition boundary。
2. 修订 Candidate / New Wave 逻辑，区分 candidate guard 与 progress confirmation。
3. 修订 Lifespan，增加 birth descriptors。
4. 修订 Service，发布 v1.3 transition trace 与 birth descriptor 字段。
5. 修订 runner bootstrap，确保 build runner 不以 `audit-only` 写业务表，`segmented` 必须有 scope。
6. 修订 `governance/module_api_contracts/malf.toml`，让 release evidence 与 exposed modes 对齐当前事实。
7. 扩展 hard audit 与 MALF unit tests。

## 6. 明确禁止

该修订卡未正式执行前，不允许：

| 禁止项 |
|---|
| 声称当前代码已经实现 v1.3 全语义 |
| 改写已通过 closeout 为 v1.3 passed |
| 打开 Alpha full build |
| 打开 Signal full build |
| 打开 Position construction |
| 让任何下游模块写回 MALF |
| 合并 `wave_core_state` 与 `system_state` |

## 7. 验证计划

正式代码卡至少需要：

```powershell
H:\Asteria\.venv\Scripts\pytest.exe tests\unit\malf -q --basetemp=H:/Asteria-temp/pytest-tmp-malf-v13-code-revision -o cache_dir=H:/Asteria-temp/pytest-cache-malf-v13-code-revision
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\ruff.exe check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\ruff.exe format --check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\mypy.exe src --cache-dir H:\Asteria-temp\mypy-cache
```

若代码卡涉及正式 DB 重建，还必须形成新的 MALF v1.3 evidence index、record 与 conclusion。
