# Alpha Production Builder Hardening Card

日期：2026-05-06

状态：`passed`

## 1. 背景

Alpha bounded proof 已通过，但 full/segmented production builder 未放行。本卡承接
MALF week/month proof，通过后才可审 Alpha 是否达到 production target。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `alpha` |
| run_id | `alpha-production-builder-hardening-20260506-01` |
| stage | `production-builder-hardening / passed` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| prerequisite card | `malf-month-bounded-proof-build-20260506-01` |
| source DBs | `malf_service_day.duckdb`; `malf_service_week.duckdb`; `malf_service_month.duckdb` as released |
| target DBs | `alpha_bof.duckdb`; `alpha_tst.duckdb`; `alpha_pb.duckdb`; `alpha_cpb.duckdb`; `alpha_bpb.duckdb` |
| temp path | `H:\Asteria-temp\alpha\<run_id>\` |

## 4. 权威边界

| 项 | 值 |
|---|---|
| upstream semantics | `read-only MALF WavePosition surfaces` |
| formal DB permission | `allowed only when this card is explicitly executed` |
| allowed next action before card | `alpha_production_builder_hardening` |

## 5. 允许动作

- 补 Alpha segmented/full/resume/audit-only runner 能力。
- 加固五个 Alpha family 的 checkpoint、run ledger、schema/rule/sample version 和 audit 表面。
- 对 day/week/month 或 scope card 指定范围执行 production builder proof。
- 生成完整执行四件套与外部证据，并明确是否打开 Signal production builder。

## 6. 禁止动作

- 不修改 MALF 语义或写回 MALF。
- 不输出 Position、Portfolio、Trade 或资金执行语义。
- 不创建 `signal.duckdb` 的新 full release，除非后续 Signal 卡执行。
- 不打开 Position construction 或 Pipeline runtime。

## 7. 后续门禁

本卡通过后，才允许进入：

```text
signal-production-builder-hardening-20260506-01
```

## 8. 关联入口

- [Alpha target completeness review](alpha-target-completeness-review-20260506-01.conclusion.md)
- [Alpha bounded proof conclusion](alpha-bounded-proof-20260429-01.conclusion.md)
- [gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
