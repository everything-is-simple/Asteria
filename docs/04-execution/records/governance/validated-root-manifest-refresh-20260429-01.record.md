# Validated Root Manifest Refresh Record

日期：2026-04-29

## 1. 卡信息

| 项 | 值 |
|---|---|
| module | `governance` |
| run_id | `validated-root-manifest-refresh-20260429-01` |
| result | `passed` |

## 2. 执行顺序

1. 检查 `H:\Asteria-Validated` 当前顶层资产，确认尚无根 README 和机器 manifest。
2. 新增 `H:\Asteria-Validated\README.md`，声明 Validated 是权威输入和验证输出资产区，不是 scratch。
3. 新增 `H:\Asteria-Validated\validated-asset-manifest-20260429-01.json`，记录顶层资产、角色、大小、时间和 SHA256。
4. 在 `H:\Asteria-report\governance\2026-04-29\validated-root-manifest-refresh-20260429-01\` 生成 closeout 与 manifest。
5. 生成 `H:\Asteria-Validated\Asteria-validated-root-manifest-refresh-20260429-01.zip`。
6. 更新 repo 内 execution 四件套、conclusion index、execution README 和 Validated 资产清单。

## 3. 关键验证

| 验证 | 结果 |
|---|---|
| validated README exists | `passed` |
| validated manifest exists | `passed` |
| validated archive exists | `passed` |
| `H:\Asteria\.venv\Scripts\python.exe scripts\governance\sync_project_docs.py --check` | `passed` |
| `H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py` | `passed` |
| `git diff --check` | `passed` |

## 4. 外部证据资产

| 资产 | 路径 |
|---|---|
| validated_readme | `H:\Asteria-Validated\README.md` |
| validated_manifest | `H:\Asteria-Validated\validated-asset-manifest-20260429-01.json` |
| report_dir | `H:\Asteria-report\governance\2026-04-29\validated-root-manifest-refresh-20260429-01` |
| manifest | `H:\Asteria-report\governance\2026-04-29\validated-root-manifest-refresh-20260429-01\manifest.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-validated-root-manifest-refresh-20260429-01.zip` |
| formal_db | `not applicable` |

## 5. 文档更新

- [card](validated-root-manifest-refresh-20260429-01.card.md)
- [evidence-index](validated-root-manifest-refresh-20260429-01.evidence-index.md)
- [conclusion](validated-root-manifest-refresh-20260429-01.conclusion.md)
- [conclusion index](../../00-conclusion-index-v1.md)
- [validated asset inventory](../../../01-architecture/02-validated-asset-inventory-v1.md)

## 6. 门禁更新

| 项 | 结果 |
|---|---|
| conclusion index registered | `yes` |
| allowed next action after card | `Alpha freeze review` |
| still blocked | `Alpha code construction; Alpha formal DB; downstream module construction; full-chain pipeline` |
