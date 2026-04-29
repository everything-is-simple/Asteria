# Signal Freeze Review Card

日期：2026-04-29

## 1. 背景

Alpha bounded proof 已通过，五个 Alpha family DB 已发布可供 Signal 只读审阅的
`alpha_signal_candidate`。当前门禁只允许执行 Signal freeze review：审阅 Signal 六件套
和 Alpha candidate 只读契约，裁决 Signal 是否可冻结。

## 2. 基本信息

| 项 | 值 |
|---|---|
| module | `signal` |
| run_id | `signal-freeze-review-20260429-01` |
| stage | `freeze-review` |
| owner | `codex` |

## 3. 输入范围

| 项 | 值 |
|---|---|
| source | `H:\Asteria-data\alpha_bof.duckdb`; `H:\Asteria-data\alpha_tst.duckdb`; `H:\Asteria-data\alpha_pb.duckdb`; `H:\Asteria-data\alpha_cpb.duckdb`; `H:\Asteria-data\alpha_bpb.duckdb` |
| scope | `day / Alpha bounded proof release / Signal six-doc review` |
| prerequisite docs | `docs/02-modules/signal/` |
| authority assets | `H:\Asteria-Validated\Asteria-alpha-bounded-proof-20260429-01.zip`; `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2` |

## 4. 权威边界

| 项 | 值 |
|---|---|
| upstream semantics | `read-only Alpha signal candidates` |
| formal DB permission | `not allowed` |
| runner permission | `not allowed` |
| allowed next action before card | `Signal freeze review` |

## 5. 允许动作

- 审阅 Signal 六件套是否只读消费五个 Alpha family 的 `alpha_signal_candidate`。
- 审阅 Signal schema、runner、audit contract 是否禁止回写 Alpha / MALF 与下游越权输出。
- 形成 Signal freeze review 四件套、report closeout、manifest 和 Validated evidence zip。
- 若 hard review 通过，将 Signal 文档状态更新为 `frozen / freeze review passed`。

## 6. 禁止动作

- 不创建 `H:\Asteria-data\signal.duckdb`。
- 不创建 `scripts/signal/run_*.py` 或正式 Signal runner。
- 不迁移旧 Signal engine。
- 不创建 Position / Portfolio Plan / Trade / System / Pipeline 施工。
- 不允许 Signal 修改 Alpha DB 或回写 MALF。

## 7. 关联入口

- [gate ledger](../../../03-refactor/00-module-gate-ledger-v1.md)
- [conclusion index](../../00-conclusion-index-v1.md)
- [Signal authority design](../../../02-modules/signal/00-authority-design-v1.md)
- [Alpha bounded proof conclusion](../alpha/alpha-bounded-proof-20260429-01.conclusion.md)
