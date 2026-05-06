# MALF Month Bounded Proof Build Card

日期：2026-05-06

状态：`passed / month bounded proof`

## 1. 背景

本卡承接 `malf-week-bounded-proof-build-20260506-01`。目标是在 week proof 通过后，
补齐 month Core/Lifespan/Service 三库和对应 runtime evidence。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `malf` |
| run_id | `malf-month-bounded-proof-build-20260506-01` |
| stage | `bounded-proof / month / passed` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| prerequisite card | `malf-week-bounded-proof-build-20260506-01` |
| authority assets | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4` |
| source DB | `H:\Asteria-data\market_base_month.duckdb`; `H:\Asteria-data\market_meta.duckdb` |
| target DBs | `malf_core_month.duckdb`; `malf_lifespan_month.duckdb`; `malf_service_month.duckdb` |
| temp path | `H:\Asteria-temp\malf\<run_id>\` |

## 4. 权威边界

| 项 | 值 |
|---|---|
| upstream semantics | `read-only Data source facts` |
| formal DB permission | `allowed only when this card is explicitly executed` |
| allowed next action before card | `malf_month_bounded_proof_build` |
| allowed next action after pass | `alpha_production_builder_hardening` |

## 5. 允许动作

- 复用已通过的 MALF day/week runtime 合同，执行 month bounded proof build。
- 构建 month Core、Lifespan、Service staging DB，并通过 hard audit 后 promote。
- 证明 month `WavePosition` 自然键唯一、hard fail 为 0、run/audit/version 表面完整。
- 生成完整执行四件套与外部证据。

## 6. 禁止动作

- 不修改 MALF 语义权威定义。
- 不打开 Alpha/Signal production builder，除非本卡 conclusion 明确放行下一卡。
- 不创建 Position 或下游正式库。
- 不建立 full-chain Pipeline runtime。

## 7. 后续门禁

本卡通过后，才允许进入：

```text
alpha-production-builder-hardening-20260506-01
```

## 8. 关联入口

- [MALF week card](malf-week-bounded-proof-build-20260506-01.card.md)
- [MALF target completeness review](malf-authority-runtime-completeness-review-20260506-01.conclusion.md)
- [gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
