# Governance Release Gate Closure Record

日期：2026-04-28

## 1. 卡信息

| 项 | 值 |
|---|---|
| module | `governance` |
| run_id | `governance-release-gate-closure-20260428-01` |
| result | `passed` |

## 2. 执行顺序

1. 按 TDD 增加治理失败用例：缺 conclusion、缺 evidence-index、缺 validated zip、缺 manifest、registry `next_card` 与 conclusion 不一致。
2. 新增 `src/asteria/governance/release_gates.py`，集中检查 release gate 四件套与 evidence 外部资产。
3. 在 `src/asteria/governance/checks.py` 中接入 release gate 检查。
4. 修正检查语义：所有已登记 passed 卡都要有四件套；只有主线模块 release gate 才与 module gate registry 的 `next_card` 绑定。
5. 生成本卡外部 closeout、manifest 与 validated zip。
6. 补齐本卡 repo 内 card、evidence-index、record、conclusion，并登记 conclusion index。
7. 明确本卡只关闭治理检查链，不打开 Alpha 施工或任何下游正式 DB。

## 3. 关键验证

| 验证 | 结果 |
|---|---|
| `H:\Asteria\.venv\Scripts\pytest.exe tests\unit\governance -q` | `18 passed` |
| `H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py` | `passed` |
| `H:\Asteria\.venv\Scripts\ruff.exe check . --cache-dir H:\Asteria-temp\ruff-cache` | `passed` |
| `H:\Asteria\.venv\Scripts\ruff.exe format --check . --cache-dir H:\Asteria-temp\ruff-cache` | `passed` |
| `H:\Asteria\.venv\Scripts\mypy.exe src --cache-dir H:\Asteria-temp\mypy-cache` | `passed` |
| `H:\Asteria\.venv\Scripts\pytest.exe --basetemp H:\Asteria-temp\pytest-full-governance-closure` | `33 passed` |

## 4. 外部证据资产

| 资产 | 路径 |
|---|---|
| report_dir | `H:\Asteria-report\governance\2026-04-28\governance-release-gate-closure-20260428-01` |
| manifest | `H:\Asteria-report\governance\2026-04-28\governance-release-gate-closure-20260428-01\manifest.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-governance-release-gate-closure-20260428-01.zip` |
| formal_db | `not applicable` |

## 5. 文档更新

- [card](governance-release-gate-closure-20260428-01.card.md)
- [evidence-index](governance-release-gate-closure-20260428-01.evidence-index.md)
- [conclusion](governance-release-gate-closure-20260428-01.conclusion.md)
- [conclusion index](../../00-conclusion-index-v1.md)

## 6. 门禁更新

| 项 | 结果 |
|---|---|
| conclusion index registered | `yes` |
| allowed next action after card | `Alpha freeze review` |
| still blocked | `Alpha code construction; Alpha formal DB; downstream module construction; full-chain pipeline` |
