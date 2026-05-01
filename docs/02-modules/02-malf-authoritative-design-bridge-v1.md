# MALF 权威设计桥接 v1

日期：2026-04-29

## 1. 权威锚点

Asteria 当前已通过实现证据承接的 MALF 设计锚点为：

```text
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2.zip
```

2026-05-01 已形成新的 MALF v1.3 语义升级权威包：

```text
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_3
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_3.zip
```

v1.3 定义清晰、定理自洽，可以作为后续 repo 文档同步与代码修订依据；但在
`malf-v1-3-authority-sync-code-revision-20260501-01` 或后续执行卡通过前，不声明
当前实现已经覆盖 v1.3 全语义。

| 文件 | Asteria 内部地位 |
|---|---|
| `MALF_00_Three_Documents_Bridge_v1_2.md` | v1.2 三文件关系定义；当前已通过 closeout 的历史 baseline |
| `MALF_01_Core_Definitions_Theorems_v1_3.md` | Core 真值定义；v1.2 baseline 已引用同名 Core 语义 |
| `MALF_02_Lifespan_Stats_Definitions_Theorems_v1_2.md` | v1.2 Lifespan 统计定义；当前已通过 closeout 的历史 baseline |
| `MALF_03_System_Service_Interface_v1_2.md` | v1.2 Service 接口定义；当前已通过 closeout 的历史 baseline |
| `MALF_00_Three_Documents_Bridge_v1_3.md` | v1.3 三文件关系与边界 |
| `MALF_02_Lifespan_Stats_Definitions_Theorems_v1_3.md` | Lifespan 统计定义与 birth descriptors |
| `MALF_03_System_Service_Interface_v1_3.md` | Service 接口定义与 transition trace |
| `MALF_07_Definition_Theorem_Review_and_Implementation_Delta_v1_3.md` | v1.3 评审结论与实现差异 |

`H:\Asteria-Validated\Asteria-docs-code-20260428-214427.zip` 是本桥接页的
重要 repo 快照基线；快照之后的 MALF day 放行事实由 `docs/04-execution/`
执行闭环和 Validated release evidence 补充。

## 2. Asteria 中的 MALF

MALF 是 Asteria 第一主线模块。

```mermaid
flowchart TD
    A[market_base bars] --> B[MALF-Core]
    B --> C[MALF-Lifespan-Stats]
    C --> D[MALF-Service]
    D --> E[WavePosition]
    E --> F[Alpha]
```

## 3. 三段式落库

MALF 在 Asteria 中按 timeframe 拆为三库：

| 语义层 | DB 示例 | 来源文件 |
|---|---|---|
| Core | `malf_core_day.duckdb` | MALF-Core |
| Lifespan | `malf_lifespan_day.duckdb` | MALF-Lifespan-Stats |
| Service | `malf_service_day.duckdb` | MALF-System-Service |

## 4. Core 必须实现的对象

| 对象 | 表族 |
|---|---|
| Pivot | `malf_pivot_ledger` |
| Structure Primitive | `malf_structure_ledger` |
| Wave | `malf_wave_ledger` |
| Break | `malf_break_ledger` |
| Transition | `malf_transition_ledger` |
| Candidate Guard | `malf_candidate_ledger` |
| Current Effective Guard | v1.3 待同步到 `malf_wave_ledger` / `malf_break_ledger` |
| Transition Boundary | v1.3 待同步到 `malf_transition_ledger` |
| Progress Confirmation | v1.3 待同步到 `malf_candidate_ledger` 与 new wave creation |

## 5. Lifespan 必须实现的对象

| 对象 | 表族 |
|---|---|
| new-count | `malf_lifespan_snapshot` |
| no-new-span | `malf_lifespan_snapshot` |
| update-rank | `malf_lifespan_profile` |
| stagnation-rank | `malf_lifespan_profile` |
| life-state | `malf_lifespan_snapshot` |
| sample scope | `malf_sample_version` |
| rule version | `malf_rule_version` |
| birth descriptors | v1.3 待同步到 Lifespan / Service 字段 |

## 6. Service 必须实现的对象

| 对象 | 表族 |
|---|---|
| WavePosition | `malf_wave_position` |
| latest view | `malf_wave_position_latest` |
| interface audit | `malf_interface_audit` |

## 7. MALF 不得输出

| 禁止输出 | 归属模块 |
|---|---|
| 买入/卖出 | Alpha / Signal |
| 仓位大小 | Position / Portfolio Plan |
| 订单 | Trade |
| 收益预测 | Alpha 或 Research，不属于 MALF |

## 8. MALF 第一施工顺序

MALF 不直接全量上 day/week/month。

第一施工顺序与当前状态：

```mermaid
flowchart TD
    A[Freeze MALF schema spec] --> B[Build day Core bounded proof]
    B --> C[Build day Lifespan bounded proof]
    C --> D[Build day Service WavePosition proof]
    D --> E[Run MALF invariant audit]
    E --> F[Release day]
    F --> G[Replicate to week/month]
```

截至 2026-04-29，`Release day` 已由
`malf-day-bounded-proof-20260428-01` 记录为 `passed`。该结论只放行 MALF day
bounded proof 与 Alpha 只读 WavePosition 前置条件；week/month 复制、全量构建、
Pipeline 全链路和 Alpha 代码施工仍需要后续卡。

截至 2026-04-30，`malf-complete-alignment-closeout-20260430-01` 已取代旧 dense /
hard-audit evidence 作为当前 MALF day dense formal evidence。v1.3 仍是待实现语义升级。

## 9. 必须验收的不变量

| 不变量 | 来源 |
|---|---|
| terminated wave 不得重新 alive | Core |
| break 后不得延伸旧 wave | Core |
| transition 必须关联 old_wave_id | Core / Service |
| transition.direction 必须等于 old_direction | Lifespan / Service |
| transition 中同一时刻只能有一个 active candidate | Core |
| new wave 必须有 active candidate_guard + progress_confirmation | Core |
| new wave confirmation bar 的 no_new_span = 0 | Lifespan |
| transition_span 不并入 no_new_span | Lifespan |
| wave_core_state 不得取 transition | Service |

## 10. 当前下游授权

当前唯一业务下一步是：

```text
Position freeze review reentry / review-only
```

Alpha、Signal、Position、Portfolio Plan、Trade、System Readout 和 Pipeline 仍不得写回
MALF，也不得把 WavePosition 的发布解释为自身代码施工许可。
