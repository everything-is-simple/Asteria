# Alpha Pending Module Gate v1

日期：2026-04-29

状态：frozen / freeze review passed / bounded proof build card next

## 1. 当前裁决

Alpha 是 MALF 之后的第一下游主线模块。本目录六件套已由
`alpha-freeze-review-20260429-01` 冻结，但本轮不允许进入施工。

截至 2026-04-29，MALF day bounded proof 已通过，WavePosition release evidence 已落档。
Alpha freeze review 已通过；下一步只能写 Alpha bounded proof build card。

## 2. 等待条件

Alpha 施工必须等待：

```text
MALF day WavePosition release evidence passed
Alpha freeze review passed
Alpha bounded proof build card
```

`malf_wave_position` 和接口审计结论已可审计；施工放行前还必须有独立的
Alpha bounded proof build card。

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

## 5. 已冻结的六件套

以下文档已通过 freeze review，但不表示代码施工或正式 DB 创建许可：

| 文档 | 状态 |
|---|---|
| `00-authority-design-v1.md` | frozen / freeze review passed |
| `01-semantic-contract-v1.md` | frozen / freeze review passed |
| `02-database-schema-spec-v1.md` | frozen / freeze review passed |
| `03-runner-contract-v1.md` | frozen / freeze review passed |
| `04-audit-spec-v1.md` | frozen / freeze review passed |
| `05-build-card-v1.md` | frozen / freeze review passed |

当前下一步只允许 `Alpha bounded proof build card`。
