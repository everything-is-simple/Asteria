# Data Foundation Audit Spec v1

日期：2026-05-02

状态：production-foundation released / production audit active / market_meta hard checks active

当前裁决：Data Foundation 已通过生产级地基 release audit，并已增加 day execution
line presence hard check。审计覆盖四个正式库、
`analysis_price_line=backward`、`execution_price_line=none`、source trace、自然键、
latest 指针、dirty scope、checkpoint/resume，以及最小正式 `market_meta.duckdb`。

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
| Price line separation | `analysis_price_line` 不得用于真实成交；`execution_price_line` 必须来自 `adj_mode = none` |
| Execution line presence | `market_base_day.duckdb` 必须存在 `execution_price_line / none` 正式行 |
| Market meta presence | `market_meta.duckdb` 必须存在并包含最小正式表族 |
| Market meta uniqueness | calendar、instrument、alias、universe、tradability、industry 自然键唯一 |
| Tradability source policy | `has_execution_bar` 只能来自 `execution_price_line / none` |
| Industry source policy | `industry_classification` 只能为空或来自 approved SW2021 xlsx snapshot |
| Incremental resume | checkpoint/resume 不得重复写入已完成 source scope |

## 3. 软观察

软观察不一定阻塞放行，但必须记录：

| 观察项 | 说明 |
|---|---|
| 缺失率异常 | 某些源字段异常缺失 |
| 某日源数据量突降 | 需要核对来源是否完整 |
| week / month 聚合量与预期差异 | 需要核对聚合边界 |
| tradability facts 剧烈变化 | 需要核对上游元数据来源 |
| industry source gap | 当前允许 `industry_classification` 为空，或只包含 approved SW2021 当前快照 |

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

当前 `market_meta` 只声明申万 2021 当前行业快照的部分覆盖；ST、停牌、真实
上市/退市状态和历史行业沿革仍不得作为 Alpha、Portfolio 或 Trade 的 released
reference fact 使用。

Trade 未来 release audit 必须额外确认 fill price、order price、fill amount 和现金账本
只来自 `execution_price_line`，不得使用 `analysis_price_line`。

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
