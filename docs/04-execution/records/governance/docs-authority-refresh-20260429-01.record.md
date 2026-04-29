# Docs Authority Refresh Record

日期：2026-04-29

## 1. 卡信息

| 项 | 值 |
|---|---|
| module | `governance` |
| run_id | `docs-authority-refresh-20260429-01` |
| result | `passed` |

## 2. 执行顺序

1. 按 Asteria governance 要求重读 `README.md`、`AGENTS.md`、重构总纲、主线权威图、数据库拓扑和模块门禁账本。
2. 按 TDD 增加两个失败用例：资产清单降回旧 docs/code 快照、MALF 权威桥接缺少终稿引用。
3. 扩展 `src/asteria/governance/docs_sync.py`，检查最新 Validated docs/code 快照、MALF 权威 zip、MALF 权威目录和四个权威源文件。
4. 更新 Validated 资产清单和 `docs/README.md`，明确 `214427` 快照是当前重要快照锚点；之后的 HEAD 变更由执行记录与新归档补齐。
5. 删除 repo 根 `.ruff_cache`，避免治理检查继续报告违规缓存产物。
6. 运行 docs authority 回归测试、governance 单元测试和项目治理检查。
7. 补齐本卡 repo 内 card、evidence-index、record、conclusion，并登记 conclusion index。
8. 生成本卡外部 closeout、manifest 与 Validated zip。
9. 将深度研究报告、`214427` docs/code 快照和 MALF 三份终稿目录登记为执行层权威锚点。

## 3. 关键验证

| 验证 | 结果 |
|---|---|
| `H:\Asteria\.venv\Scripts\pytest.exe tests/unit/governance/test_project_docs_sync.py::test_docs_sync_rejects_stale_validated_docs_code_snapshot tests/unit/governance/test_project_docs_sync.py::test_docs_sync_rejects_missing_malf_authority_bridge_file_reference -q --basetemp=H:/Asteria-temp/pytest-tmp-docs-authority-refresh-20260429-01-green -o cache_dir=H:/Asteria-temp/pytest-cache-docs-authority-refresh-20260429-01-green` | `2 passed` |
| `H:\Asteria\.venv\Scripts\pytest.exe tests/unit/governance -q --basetemp=H:/Asteria-temp/pytest-tmp-docs-authority-refresh-20260429-01-governance -o cache_dir=H:/Asteria-temp/pytest-cache-docs-authority-refresh-20260429-01-governance` | `20 passed` |
| `H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py` | `passed` |
| `H:\Asteria\.venv\Scripts\python.exe scripts\governance\sync_project_docs.py --check` | `passed` |
| `H:\Asteria\.venv\Scripts\ruff.exe check . --cache-dir H:\Asteria-temp\ruff-cache` | `passed` |
| `H:\Asteria\.venv\Scripts\ruff.exe format --check . --cache-dir H:\Asteria-temp\ruff-cache` | `passed` |
| `H:\Asteria\.venv\Scripts\mypy.exe src --cache-dir H:\Asteria-temp\mypy-cache` | `passed` |
| `H:\Asteria\.venv\Scripts\pytest.exe --basetemp=H:/Asteria-temp/pytest-tmp-docs-authority-refresh-20260429-01 -o cache_dir=H:/Asteria-temp/pytest-cache-docs-authority-refresh-20260429-01` | `35 passed` |

## 4. 外部证据资产

| 资产 | 路径 |
|---|---|
| report_dir | `H:\Asteria-report\governance\2026-04-29\docs-authority-refresh-20260429-01` |
| manifest | `H:\Asteria-report\governance\2026-04-29\docs-authority-refresh-20260429-01\manifest.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-docs-authority-refresh-20260429-01.zip` |
| formal_db | `not applicable` |

## 5. 文档更新

- [card](docs-authority-refresh-20260429-01.card.md)
- [evidence-index](docs-authority-refresh-20260429-01.evidence-index.md)
- [conclusion](docs-authority-refresh-20260429-01.conclusion.md)
- [conclusion index](../../00-conclusion-index-v1.md)

## 6. 门禁更新

| 项 | 结果 |
|---|---|
| conclusion index registered | `yes` |
| allowed next action after card | `Alpha freeze review` |
| still blocked | `Alpha code construction; Alpha formal DB; downstream module construction; full-chain pipeline` |
