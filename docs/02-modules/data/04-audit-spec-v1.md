# Data Foundation Audit Spec v1

日期：2026-04-27

状态：draft / foundation-contract / not frozen

## 1. 目的

本审计规范定义 Data Foundation 的硬规则、抽样检查与失败裁决。

## 2. 硬规则

以下规则必须全部通过：

| 规则 | 要求 |
|---|---|
| Source traceability | 正式事实必须带有足够 `source_*` 信息 |
| Natural key uniqueness | 每张正式事实表自然键唯一 |
| Calendar consistency | `trade_date`、`bar_dt` 与交易日历一致 |
| No strategy leakage | 不得出现 Wave、Alpha、Signal、Position、Trade、System 字段 |
| Latest pointer uniqueness | `market_base_latest` 每组键只保留一行 |
| Reject isolation | 脏记录必须进入 reject audit，不得进入正式事实 |

## 3. 软观察

软观察不一定阻塞放行，但必须记录：

| 观察项 | 说明 |
|---|---|
| 缺失率异常 | 某些源字段异常缺失 |
| 某日源数据量突降 | 需要核对来源是否完整 |
| week / month 聚合量与预期差异 | 需要核对聚合边界 |
| tradability facts 剧烈变化 | 需要核对上游元数据来源 |

## 4. 抽样查询方向

至少应支持以下抽样方向：

```text
sample one source batch and trace to market_base
sample one trade_date and verify calendar alignment
sample one symbol across day/week/month and inspect base continuity
sample one tradability fact and inspect objective source chain
```

## 5. 失败裁决

| 失败类型 | 裁决 |
|---|---|
| 自然键冲突 | 阻塞放行 |
| 无来源追溯 | 阻塞放行 |
| 客观事实混入策略字段 | 阻塞放行 |
| latest 指针多行 | 阻塞放行 |
| 抽样异常但可解释 | 待修或带说明继续验证 |

## 6. 与主线的接口审计

Data Foundation 对主线的接口审计至少确认：

| 消费者 | 审计点 |
|---|---|
| MALF | `market_base_day` 与 `market_meta` 字段口径稳定 |
| Alpha | `market_meta` 中客观宇宙和行业事实稳定 |
| Portfolio Plan | tradability 与 universe 事实可只读消费 |
| Trade | 执行价格线不混入策略标签 |

## 7. 审计证据

审计证据应落入：

```text
H:\Asteria-report\data\<date>\
H:\Asteria-Validated\<asset-set>\
```

至少包含：

```text
audit run ledger
sample query outputs
failure or release conclusion
```
