# V1 MALF v1.4 Immutability Anchor Record

日期：2026-05-14

run_id：`v1-malf-v1-4-immutability-anchor-card-20260514-01`

## 1. Execution Summary

本卡已完成。它只读核对 `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4`、
repo-local MALF authority design、v1.4 authority sync 结论与 v1.4 day runtime sync 结论，
输出后续 Alpha/PAS 恢复工作必须遵守的 MALF 不变量清单。

## 2. Steps

1. 重读 Asteria live authority，确认 `final-release-closeout-card` 已通过且当前 live next 仍为 `none / terminal`。
2. 复核 `v1-core-module-recovery-roadmap-freeze-card-20260514-01`，确认本卡是第二张 prepared route card。
3. 只读核对 MALF v1.4 package manifest、bridge、Core definitions、Core operational rules、Lifespan definitions 与 Service interface。
4. 核对 repo MALF authority design 与 MALF v1.4 authority / runtime evidence 边界。
5. 输出 MALF v1.4 不变量清单，并同步 roadmap、gate ledger、conclusion index、repo 四件套、外部 report / manifest 与 Validated archive。

## 3. Anchored Invariants

| invariant_id | invariant | authority |
|---|---|---|
| `MALF-V1-4-ANCHOR` | `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4` 是后续 Alpha/PAS 恢复工作的 MALF authority anchor | `MANIFEST.json`; `MALF_00_Three_Documents_Bridge_v1_4.md` |
| `V1-3-SEMANTIC-BASELINE` | v1.4 继承 v1.3 Core / Lifespan / Service 语义主线，01B 是 v1.4 normative delta | `MANIFEST.json`; bridge |
| `CORE-STRUCTURE-ONLY` | Core 只定义结构事实，不输出价值、买卖、仓位、订单 | `MALF_01_Core_Definitions_Theorems_v1_4.md` |
| `PRICEBAR-TRACEABILITY` | Core 结构必须追溯到 PriceBar 与 pivot rule version | Core definitions; operational rule O1 |
| `EVENT-ORDERING` | 同一 bar 内 Core 事件顺序固定为 `core-event-order-v1` | operational rule O2 |
| `STRICT-COMPARE` | break / confirmation 使用 strict compare，等于不触发 | operational rule O3 |
| `CANDIDATE-REPLACEMENT` | transition 中 active candidate 永远等于 latest candidate guard | operational rule O4 |
| `TRANSITION-CONTEXT` | transition primitive 使用 `transition_candidate`，不得更新 old wave | operational rule O5 |
| `INITIAL-RESET` | initial candidate failure 不创建 wave / break / transition | operational rule O6 |
| `CORE-SNAPSHOT` | Core 必须提供或等价提供可重放校验的 state snapshot | operational rule O7 |
| `REPLAY-DETERMINISM` | same source facts + same versions + same policies 必须重放一致 | operational rule O8 |
| `LIFESPAN-STATS-ONLY` | Lifespan 只统计已确认 wave，rank / birth descriptors 不表示收益概率或交易信号 | Lifespan definitions |
| `SERVICE-READONLY` | Service 只读发布 WavePosition，Alpha 可读但不得写回 MALF | Service interface |
| `STATE-SPACES-SEPARATE` | `system_state` 与 `wave_core_state` 必须分开发布，不得混用 | Service interface |
| `NO-DOWNSTREAM-WRITEBACK` | Alpha、Signal、Position、Portfolio Plan、Trade、System Readout 均不得写回 MALF | Service interface; repo authority design |

## 4. Boundary Result

| 项 | 结果 |
|---|---|
| live next action | `none / terminal` |
| live next reopened by this card | `no` |
| formal DB mutation | `no` |
| MALF semantic redefinition | `no` |
| Alpha/PAS contract redesign | `not opened` |
| historical code migration | `not opened` |
| next route card | `v1-alpha-pas-source-inventory-card` |

## 5. Verification

本卡为 roadmap-only / read-only / post-terminal authority anchor，不执行 runtime、不安装依赖、
不写正式 DB。验证范围为 live authority sanity check、MALF v1.4 package readback、
roadmap / execution four-piece / conclusion index / module gate ledger 一致性检查，以及 Asteria workflow strict check。
