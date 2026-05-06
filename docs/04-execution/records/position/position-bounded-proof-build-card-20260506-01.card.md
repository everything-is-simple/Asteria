# Position Bounded Proof Build Card

日期：2026-05-06

状态：`prepared / not executed`

## 1. 背景

`position-freeze-review-reentry-20260430-01` 已完成 review-only 审查，并将 Position
六件套冻结为文档和合同表面。当前卡只是下一步可寻址的 build card，不代表本轮已经执行
Position bounded proof。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `position` |
| run_id | `position-bounded-proof-build-card-20260506-01` |
| stage | `bounded-proof / build-card-prepared / not executed` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| upstream release | `Signal bounded proof passed` |
| freeze review | `position-freeze-review-reentry-20260430-01` |
| source DB | `H:\Asteria-data\signal.duckdb` |
| source tables | `formal_signal_ledger`; `signal_component_ledger`; `signal_input_snapshot`; `signal_audit` |
| source boundary | `read-only released Signal bounded surface` |
| bounded scope | `day / bounded sample only; exact scope to be set by execution turn` |
| working path | `H:\Asteria-temp\position\<run_id>\` |
| formal DB path | `H:\Asteria-data\position.duckdb` |

## 4. 权威边界

| 项 | 值 |
|---|---|
| frozen docs | `docs/02-modules/position/00-authority-design-v1.md` through `05-build-card-v1.md` |
| release conclusion | `docs/04-execution/records/position/position-freeze-review-reentry-20260430-01.conclusion.md` |
| upstream semantics | `Signal aggregates intent; Position materializes holding logic` |
| formal DB permission | `not created by this review; allowed only when this card is explicitly executed` |
| allowed run modes | `bounded`; `resume`; `audit-only` |

## 5. 允许动作

- 后续执行 turn 可创建 Position bounded proof 所需的最小 runner、schema、audit 和测试。
- 后续执行 turn 可只读消费 `signal.duckdb` 的 released bounded proof 表面。
- 后续执行 turn 可在 bounded proof/audit 路径明确需要时创建 `H:\Asteria-data\position.duckdb`。
- 后续执行 turn 必须生成 Position bounded proof 的 record、evidence-index、conclusion、report
  closeout 和 validated evidence。

## 6. 当前仍禁止

- 本次 review-only 关闭不创建 `src\asteria\position`。
- 本次 review-only 关闭不创建 `scripts\position`。
- 本次 review-only 关闭不创建 `H:\Asteria-data\position.duckdb`。
- 不运行 Position full build、segmented production build 或 daily incremental build。
- 不创建 Portfolio Plan / Trade / System / Pipeline 正式 runner 或正式 DB。
- 不建立 full-chain Pipeline runtime。
- 不允许 Position 直接读取 Alpha 或 MALF 绕过 Signal。
- 不允许 Position 输出 `target_weight`、`portfolio_allocation`、`order_intent` 或 `fill` 语义。

## 7. 验收与后续门禁

本卡若在后续 turn 被执行，Position bounded proof 必须形成完整四件套：

```text
card
record
evidence-index
conclusion
```

Position bounded proof release gate 通过后，才允许进入 Portfolio Plan freeze review。

## 8. 验收命令

本卡和门禁状态更新后必须运行：

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
```

Position bounded proof release gate 前还必须运行：

```powershell
H:\Asteria\.venv\Scripts\ruff.exe check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\ruff.exe format --check . --cache-dir H:\Asteria-temp\ruff-cache
H:\Asteria\.venv\Scripts\mypy.exe src --cache-dir H:\Asteria-temp\mypy-cache
H:\Asteria\.venv\Scripts\pytest.exe --basetemp=H:/Asteria-temp/pytest-tmp-position-bounded-proof-20260506-01 -o cache_dir=H:/Asteria-temp/pytest-cache-position-bounded-proof-20260506-01
```

## 9. 关联入口

- [gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
- [conclusion index](../../00-conclusion-index-v1.md)
- [Position authority design](../../../02-modules/position/00-authority-design-v1.md)
- [Position semantic contract](../../../02-modules/position/01-semantic-contract-v1.md)
- [Position database schema spec](../../../02-modules/position/02-database-schema-spec-v1.md)
- [Position runner contract](../../../02-modules/position/03-runner-contract-v1.md)
- [Position audit spec](../../../02-modules/position/04-audit-spec-v1.md)
- [Position freeze review re-entry conclusion](position-freeze-review-reentry-20260430-01.conclusion.md)
