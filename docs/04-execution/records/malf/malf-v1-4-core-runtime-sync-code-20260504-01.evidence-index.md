# MALF v1.4 Core Runtime Sync Code Evidence Index

日期：2026-05-04

状态：`code-only evidence / formal rebuild pending`

## 1. 证据边界

本索引只登记 v1.4 day runtime sync 第一张代码卡证据。它不是正式 DuckDB rebuild
evidence，不替代 `malf-v1-3-formal-rebuild-closeout-20260502-01`，也不声明
`v1.4 day runtime proof passed`。

## 2. Repo Evidence

| 类别 | 入口 | 说明 |
|---|---|---|
| card | [card](malf-v1-4-core-runtime-sync-code-20260504-01.card.md) | code/runtime-sync 第一张卡 |
| record | [record](malf-v1-4-core-runtime-sync-code-20260504-01.record.md) | 执行记录 |
| conclusion | [conclusion](malf-v1-4-core-runtime-sync-code-20260504-01.conclusion.md) | code-only 结论 |
| MALF docs | `docs/02-modules/malf/` | v1.4 runtime sync 文档同步 |
| contract | `governance/module_api_contracts/malf.toml` | MALF API contract metadata |
| tests | `tests/unit/malf/` | v1.4 gap 测试与回归测试 |

## 3. 验证证据

| 命令 | 期望 |
|---|---|
| `tests\unit\malf` | MALF unit tests pass |
| `scripts\governance\check_project_governance.py` | governance checks pass |
| `ruff check .` | no lint failures |
| `ruff format --check .` | formatting clean |
| `mypy src` | type checks pass |
| `git diff --check` | no whitespace errors |

## 4. 非证据

- 本卡没有在 `H:\Asteria-data` 重建或 promote 新的 MALF 正式 DB。
- 本卡没有更新 `H:\Asteria-Validated` release evidence。
- 本卡没有放行 week/month proof、Position 施工或 downstream construction。
