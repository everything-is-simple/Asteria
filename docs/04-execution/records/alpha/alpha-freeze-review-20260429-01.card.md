# Alpha Freeze Review Card

日期：2026-04-29

## 1. 背景

MALF day bounded proof 已通过，`malf_service_day.duckdb` 已发布 Alpha 可只读消费的
WavePosition。当前门禁只允许执行 Alpha freeze review：审阅 Alpha 六件套与
WavePosition 只读契约，裁决 Alpha 是否可冻结。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `alpha` |
| run_id | `alpha-freeze-review-20260429-01` |
| stage | `freeze-review` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| source | `H:\Asteria-data\malf_service_day.duckdb` |
| scope | `day / service-v1 / Alpha six-doc review` |
| prerequisite docs | `docs/02-modules/alpha/` |
| authority assets | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2`; `H:\Asteria-Validated\Asteria-malf-day-bounded-proof-20260428-01.zip` |

## 4. 权威边界

| 项 | 值 |
|---|---|
| upstream semantics | `read-only MALF WavePosition` |
| formal DB permission | `not allowed` |
| allowed next action before card | `Alpha freeze review` |

## 5. 允许动作

- 审阅 Alpha 六件套是否只读消费 `malf_wave_position` / `malf_wave_position_latest`。
- 审阅 Alpha schema、runner、audit contract 是否禁止回写 MALF 与下游越权输出。
- 形成 Alpha freeze review 四件套、report closeout、manifest 和 Validated evidence zip。
- 若 hard review 通过，将 Alpha 文档状态更新为 `frozen / freeze review passed`。

## 6. 禁止动作

- 不创建 `alpha_bof.duckdb`、`alpha_tst.duckdb`、`alpha_pb.duckdb`、`alpha_cpb.duckdb` 或 `alpha_bpb.duckdb`。
- 不创建 `scripts/alpha/run_*.py` 或正式 Alpha runner。
- 不迁移旧 Alpha engine。
- 不创建 Signal / Position / Portfolio Plan / Trade / System / Pipeline 施工。
- 不允许 Alpha、Signal、Portfolio、Trade 或 System 写回 MALF。

## 7. 关联入口

- [gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
- [conclusion index](../../00-conclusion-index-v1.md)
- [Alpha authority design](../../../02-modules/alpha/00-authority-design-v1.md)
- [MALF day bounded proof conclusion](../malf/malf-day-bounded-proof-20260428-01.conclusion.md)
