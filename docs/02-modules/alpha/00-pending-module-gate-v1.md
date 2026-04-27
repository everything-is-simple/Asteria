# Alpha Pending Module Gate v1

日期：2026-04-27

状态：pending / not frozen

## 1. 当前裁决

Alpha 是 MALF 之后的第一下游主线模块，但本轮不冻结 Alpha 设计，不允许进入施工。

## 2. 等待条件

Alpha 必须等待：

```text
MALF WavePosition service released
```

放行前必须已经存在可审计的 `malf_wave_position` 和接口审计结论。

## 3. 只允许继承的上游语义

Alpha 只能只读消费 MALF Service 的 WavePosition：

```text
symbol
timeframe
bar_dt
system_state
wave_core_state
direction
new_count
no_new_span
transition_span
update_rank
stagnation_rank
life_state
position_quadrant
```

## 4. 禁止项

| 禁止项 | 原因 |
|---|---|
| 写回 MALF | 下游不得改变结构事实 |
| 重定义 WavePosition 字段 | 上游语义只能由 MALF 定义 |
| 输出 position size | 归属 Position / Portfolio Plan |
| 输出 order | 归属 Trade |
| 把可交易性客观事实当作 Alpha 语义 | 客观事实属于 Data Foundation |

## 5. 未来必须补齐

Alpha 进入设计冻结前必须补齐：

```text
00-authority-design-v1.md
01-semantic-contract-v1.md
02-database-schema-spec-v1.md
03-runner-contract-v1.md
04-audit-spec-v1.md
05-build-card-v1.md
```
