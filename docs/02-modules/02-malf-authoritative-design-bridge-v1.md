# MALF 权威设计桥接 v1

日期：2026-04-29

## 1. 权威锚点

Asteria 当前 MALF 设计锚点为：

```text
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_3
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_3.zip
```

v1.2 作为历史 closeout 锚点保留：

```text
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2
H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2.zip
```

v1.3 定义清晰、定理自洽，已由
`malf-v1-3-formal-rebuild-closeout-20260502-01` 承接为当前 MALF day formal-data
bounded evidence；week/month 证明尚未执行。

| 文件 | Asteria 内部地位 |
|---|---|
| `MALF_00_Three_Documents_Bridge_v1_2.md` | v1.2 三文件关系定义；当前已通过 closeout 的历史 baseline |
| `MALF_01_Core_Definitions_Theorems_v1_3.md` | Core 真值定义；v1.2 baseline 已引用同名 Core 语义 |
| `MALF_02_Lifespan_Stats_Definitions_Theorems_v1_2.md` | v1.2 Lifespan 统计定义；当前已通过 closeout 的历史 baseline |
| `MALF_03_System_Service_Interface_v1_2.md` | v1.2 Service 接口定义；当前已通过 closeout 的历史 baseline |
| `MALF_00_Three_Documents_Bridge_v1_3.md` | v1.3 三文件关系与边界 |
| `MALF_02_Lifespan_Stats_Definitions_Theorems_v1_3.md` | Lifespan 统计定义与 birth descriptors |
| `MALF_03_System_Service_Interface_v1_3.md` | Service 接口定义与 transition trace |
| `MALF_04_Core_Chart_View_v1_3.md` | Core 图表辅助理解 |
| `MALF_05_Lifespan_Chart_View_v1_3.md` | Lifespan 图表辅助理解 |
| `MALF_06_Service_Chart_View_v1_3.md` | Service 图表辅助理解 |
| `MALF_07_Definition_Theorem_Review_and_Implementation_Delta_v1_3.md` | v1.3 评审结论与实现差异 |

`H:\Asteria-Validated\Asteria-docs-code-20260502-104932.zip` 是本桥接页的当前
repo 快照基线；快照之后的新事实必须继续由 `docs/04-execution/` 执行闭环和
Validated release evidence 补充。

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
| Current Effective Guard | v1.3 已在 Core builder 与 break 语义中承接 |
| Transition Boundary | v1.3 已写入 `malf_transition_ledger` 与 Service trace |
| Progress Confirmation | v1.3 已在 candidate / new wave creation 逻辑中承接 |

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
| birth descriptors | v1.3 已同步到 Lifespan / Service 字段 |

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

截至 2026-05-02，`malf-v1-3-formal-rebuild-closeout-20260502-01` 已用正式
`market_base_day.duckdb` 输入完成 MALF v1.3 day formal-data bounded proof，并取代旧
dense / hard-audit evidence 作为当前 MALF day formal evidence。week/month 证明尚未执行。

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
