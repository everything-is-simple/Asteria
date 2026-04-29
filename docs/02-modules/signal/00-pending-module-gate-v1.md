# Signal Pending Module Gate v1

日期：2026-04-29

状态：freeze review passed / superseded

## 1. 当前裁决

Signal 是 Alpha 之后的主线模块。本目录已在 `signal-freeze-review-20260429-01` 中完成
freeze review，六件套已冻结，但仍不允许进入代码施工。

截至 2026-04-29，当前唯一允许推进的是 `Signal bounded proof build card`。不得把
Signal freeze review passed 解释为 Signal runner、Signal 正式 DB 或下游施工许可。

## 2. 等待条件

Signal bounded proof 施工必须等待：

```text
Signal bounded proof build card
```

该 build card 打开前，Signal 不得创建正式信号账本。

## 3. 上游依赖

Signal 的唯一上游语义来源应为已放行的 Alpha 输出。Signal 不得直接绕过 Alpha 重解释 MALF。

## 4. 禁止项

| 禁止项 | 原因 |
|---|---|
| 修改 Alpha 历史输出 | 下游不得回写上游 |
| 重定义 MALF WavePosition | MALF 是结构真值 |
| 输出 portfolio allocation | 归属 Portfolio Plan |
| 输出 order / fill | 归属 Trade |
| 把多个 Alpha 草案直接当作正式信号 | 必须等 Alpha 合同冻结 |
| 创建 Signal / Position / Portfolio / Trade / System / Pipeline 正式 DB | 当前卡不授权 |

## 5. 已补齐的 pre-gate draft

以下文档已通过 freeze review；冻结只表示设计契约通过，不表示施工许可：

| 文档 | 状态 |
|---|---|
| `00-authority-design-v1.md` | frozen / freeze review passed |
| `01-semantic-contract-v1.md` | frozen / freeze review passed |
| `02-database-schema-spec-v1.md` | frozen / freeze review passed |
| `03-runner-contract-v1.md` | frozen / freeze review passed |
| `04-audit-spec-v1.md` | frozen / freeze review passed |
| `05-build-card-v1.md` | frozen / freeze review passed / superseded |

下一步只能打开 Signal bounded proof build card，并继续禁止 Signal full build、下游施工和全链路 pipeline。
