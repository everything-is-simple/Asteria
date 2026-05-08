# Pipeline Build Card v1

日期：2026-04-29

状态：frozen / freeze review passed / single-module orchestration build prepared / build not executed

## 1. 本卡目标

本文件记录 Pipeline 在 `pipeline-freeze-review-20260508-01` 与
`pipeline-build-runtime-authorization-scope-freeze-20260508-01` 通过后的当前卡位：
六件套已冻结为文档合同表面，且下一卡只允许进入 single-module orchestration build prepared / not executed；
仍未打开 `pipeline.duckdb`、已执行的正式 runtime、full-chain dry-run 或 full-chain bounded proof。

## 2. 当前卡位

| 项 | 值 |
|---|---|
| active_module | `pipeline` |
| card_type | single-module orchestration build prepared after scope freeze |
| implementation_allowed | no |
| formal_db_write_allowed | no |
| freeze_allowed | already passed via `pipeline-freeze-review-20260508-01` |
| next_prepared_card | `pipeline-single-module-orchestration-build-card-20260508-01` |

## 3. 前置门槛

Pipeline future build/runtime 仍必须等待：

```text
Pipeline freeze review passed
pipeline-build-runtime-authorization-scope-freeze passed
pipeline-single-module-orchestration-build-card prepared
```

## 4. 本轮允许

| 项 | 裁决 |
|---|---|
| 冻结 Pipeline 六件套为文档合同表面 | 已完成 |
| 明确 Pipeline 只做编排和记录 | 已完成 |
| 定义 Pipeline 不写回业务模块的硬边界 | 已完成 |
| 冻结 `pipeline.duckdb` 的文档 schema surface | 已完成 |
| 冻结 runner / audit 文档合同 | 已完成 |
| 明确第一张执行卡只能是 single-module orchestration build | 已完成 |
| 更新模块文档索引和门禁账本中的 current prepared state | 本卡要求 |

## 5. 本轮不允许

| 项 | 裁决 |
|---|---|
| 创建正式 Pipeline DuckDB | 禁止 |
| 创建 `src\asteria\pipeline` 或 `scripts\pipeline` 正式 runtime | 禁止 |
| 跳过 prepared card 直接建立 single-module orchestration build | 禁止 |
| 建立 full-chain dry-run | 禁止 |
| 建立 full-chain bounded proof | 禁止 |
| 修改任何业务模块代码或输出 | 禁止 |
| 在 Pipeline 中定义业务语义 | 禁止 |
| 绕过单模块施工门禁 | 禁止 |

## 6. 下一步入口

当前已准备但未执行的下一张卡是 `pipeline-single-module-orchestration-build-card-20260508-01`。
未来如需进入 full-chain dry-run 或 full-chain bounded proof，仍必须另开明确 card，不得把
freeze review passed 或 single-module prepared 状态直接解释成全链路施工授权。

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
| Pipeline pre-gate 文档 | `H:\Asteria\docs\02-modules\pipeline\` |
| 模块门禁账本 | `H:\Asteria\docs\03-refactor\00-module-gate-ledger-v1.md` |
| 主线模块文档索引 | `H:\Asteria\docs\02-modules\04-mainline-module-delivery-index-v1.md` |
