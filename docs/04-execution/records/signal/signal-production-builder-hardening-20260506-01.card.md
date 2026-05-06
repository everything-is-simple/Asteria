# Signal Production Builder Hardening Card

日期：2026-05-06

状态：`passed`

## 1. 背景

Signal bounded proof 已通过，`signal.duckdb` 的 bounded 表面已清洁；但 full/segmented
production build 未放行。本卡承接 Alpha production builder hardening。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `signal` |
| run_id | `signal-production-builder-hardening-20260506-01` |
| stage | `production-builder-hardening / passed` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| prerequisite card | `alpha-production-builder-hardening-20260506-01` |
| source DBs | released Alpha family DBs |
| target DB | `H:\Asteria-data\signal.duckdb` |
| temp path | `H:\Asteria-temp\signal\<run_id>\` |

## 4. 权威边界

| 项 | 值 |
|---|---|
| upstream semantics | `read-only Alpha candidate / score / audit surfaces` |
| formal DB permission | `allowed only when this card is explicitly executed` |
| allowed next action before card | `signal_production_builder_hardening` |

## 5. 允许动作

- 补 Signal segmented/full/resume/audit-only runner 能力。
- 加固 `formal_signal_ledger`、`signal_component_ledger`、`signal_input_snapshot`、`signal_audit` 的 production audit。
- 证明 Signal full/segmented production 表面不偷带 Position、Portfolio 或 Trade 语义。
- 生成完整执行四件套与外部证据，并明确是否打开上游总控放行卡。

## 6. 禁止动作

- 不直接读取 MALF 绕过 Alpha。
- 不输出 position candidate、entry plan、exit plan、portfolio allocation、order 或 fill。
- 不创建 `src\asteria\position`、`scripts\position` 或 `position.duckdb`。
- 不建立 full-chain Pipeline runtime。

## 7. 后续门禁

本卡通过后，才允许进入：

```text
upstream-pre-position-release-decision-20260506-01
```

## 8. 关联入口

- [Signal target completeness review](signal-target-completeness-review-20260506-01.conclusion.md)
- [Signal bounded proof conclusion](signal-bounded-proof-20260429-01.conclusion.md)
- [gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
