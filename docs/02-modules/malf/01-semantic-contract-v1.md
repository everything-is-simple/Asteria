# MALF Semantic Contract v1

日期：2026-04-30

状态：frozen / day bounded proof passed / complete alignment closeout passed

## 1. 合同目的

本合同定义 MALF 对 Asteria 主线提供的语义边界。下游只能消费这些语义，不得重定义、修补或写回 MALF。

MALF day bounded proof 与 complete alignment closeout 已通过；下游可以只读审阅
WavePosition 合同，但任何下游模块仍不得重定义、修补或写回 MALF。

## 2. 输入语义

MALF 第一阶段输入为 day 级别 market base bars。

| 输入 | 语义 |
|---|---|
| `symbol` | 标的代码 |
| `timeframe` | 第一阶段固定为 `day` |
| `bar_dt` | bar 日期 |
| `open/high/low/close` | 基础行情价格线 |
| `volume/amount` | 客观成交事实 |
| `source_*` | 数据来源追溯 |

MALF 不负责原始行情同步、复权裁决、交易日历修复或 universe 构造。

## 3. Core 语义

| 对象 | 语义 |
|---|---|
| Pivot | 结构极值点 |
| Structure Primitive | HH / HL / LL / LH 等结构原语 |
| Wave | 已确认的结构波段 |
| Current Effective Guard | active wave 内最新确认且仍有效的 HL / LH 守护原语 |
| Break | 旧 wave 的 current effective guard 被击穿 |
| Transition | break 后到新 wave 确认前的系统状态 |
| Transition Boundary | break 后由 transition 接管的上下边界 |
| Candidate Guard | transition 或 initialization 中用于确认 new wave 的候选守护极值 |
| Progress Confirmation | active candidate guard 之后的方向性推进确认 |

Core 的结构事实不得由 Lifespan、Service 或下游模块反向改写。

v1.3 裁决：Break 后旧 wave 立即 terminated，不得延伸，不得复活；new wave 必须由
active candidate guard 加后续 progress confirmation 共同确认。

## 4. Lifespan 语义

| 对象 | 语义 |
|---|---|
| `new_count` | wave 形成后的推进次数 |
| `no_new_span` | alive wave 未推进持续 bar 数 |
| `transition_span` | transition 持续 bar 数 |
| `update_rank` | 推进次数在样本中的位置 |
| `stagnation_rank` | 停滞跨度在样本中的位置 |
| `life_state` | 生命状态分类 |
| `position_quadrant` | update / stagnation 二维位置 |
| `birth_type` | initial / same-direction / opposite-direction |
| `candidate_wait_span` | active candidate guard 到 progress confirmation 的等待跨度 |
| `candidate_replacement_count` | transition 中 candidate guard 被相反方向 guard 替代的次数 |
| `confirmation_distance_abs` | confirmation 越过 transition boundary 的绝对距离 |
| `confirmation_distance_pct` | confirmation 越过 transition boundary 的比例距离 |

`transition_span` 不并入 `no_new_span`。

新增 birth descriptor 字段是 v1.3 待实现合同；在代码修订卡通过前，不得声称当前
Service 已完整发布这些字段。

## 5. Service 语义

MALF 对 Alpha 的唯一正式接口为：

```text
WavePosition
```

| 字段 | 语义 |
|---|---|
| `system_state` | `up_alive / down_alive / transition` |
| `wave_id` | alive 状态下的 active wave |
| `old_wave_id` | transition 状态下被终止旧 wave |
| `wave_core_state` | `alive / terminated` |
| `direction` | alive 中为 active direction，transition 中为 old_direction |
| `new_count` | 推进次数 |
| `no_new_span` | 未推进跨度 |
| `transition_span` | transition 跨度 |
| `update_rank` | 推进分位 |
| `stagnation_rank` | 停滞分位 |
| `life_state` | lifespan 状态 |
| `position_quadrant` | 二维位置 |
| `transition_boundary_high` | v1.3 transition 上边界，待 schema / service 同步 |
| `transition_boundary_low` | v1.3 transition 下边界，待 schema / service 同步 |
| `active_candidate_guard_pivot_id` | v1.3 active candidate guard 追溯，待 schema / service 同步 |
| `confirmation_pivot_id` | v1.3 new wave confirmation pivot 追溯，待 schema / service 同步 |
| `new_wave_id` | v1.3 transition 后确认的新 wave，待 schema / service 同步 |

`uninitialized` 是 Core/System 内部状态，不发布为 WavePosition 行。首次 wave 尚未确认的 bar 不写入 `malf_wave_position`；截至最新 run 仍未初始化的 symbol 不写入 `malf_wave_position_latest`，下游缺行即视为尚未初始化，而不是数据错误。

## 6. 不允许表达

| 表达 | 裁决 |
|---|---|
| `wave_core_state = transition` | 禁止 |
| Alpha 写回 MALF | 禁止 |
| Signal / Position / Portfolio / Trade 修正 MALF 字段 | 禁止 |
| MALF 输出 buy / sell / order / weight | 禁止 |
| 下游用自有字段重新定义 WavePosition | 禁止 |

## 7. 必须保持分离的状态

| 字段 | 允许值 | 说明 |
|---|---|---|
| `wave_core_state` | `alive / terminated` | wave 自身状态 |
| `system_state` | `up_alive / down_alive / transition` | 系统读出状态 |

二者不得合并。`transition` 是系统状态，不是 wave_core_state。

## 8. 下游消费原则

```mermaid
flowchart LR
    M[MALF WavePosition] --> A[Alpha readonly]
    A --> S[Signal]
    S --> P[Position]
    P --> PP[Portfolio Plan]
    PP --> T[Trade]
    T --> SY[System Readout]
```

Alpha 只能把 WavePosition 作为只读结构位置输入。后续模块只能沿主线向下游产生自身账本，不能改变 MALF 历史事实。
