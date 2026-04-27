# Signal Pending Module Gate v1

日期：2026-04-27

状态：pending / not frozen

## 1. 当前裁决

Signal 是 Alpha 之后的主线模块，本轮不冻结 Signal 设计，不允许进入施工。

## 2. 等待条件

Signal 必须等待：

```text
Alpha released
```

Alpha 放行前，Signal 不得定义正式信号账本。

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

## 5. 未来必须补齐

Signal 进入设计冻结前必须补齐：

```text
00-authority-design-v1.md
01-semantic-contract-v1.md
02-database-schema-spec-v1.md
03-runner-contract-v1.md
04-audit-spec-v1.md
05-build-card-v1.md
```
