# Data Legacy Import Contract Freeze Card

日期：2026-05-02

状态：`contract-freeze / foundation-only`

## 1. Scope

本卡冻结上一版 Lifespan 本地 raw/base DuckDB 导入 Asteria 的最小合同。

首轮范围：

```text
stock-only
day / week / month
backward adjusted base
```

## 2. Allowed

- 更新 Data Foundation 六件套中的 legacy import 合同。
- 固定字段映射、目标 DB、working/promote 边界。
- 更新 gate ledger、governance registry 与 conclusion index。
- 登记 Card 3 runner working build 为下一步。

## 3. Forbidden

- 不执行旧库导入。
- 不创建或 promote `H:\Asteria-data` 正式 Data DB。
- 不放行完整 Data Foundation full build。
- 不打开 Position、Portfolio、Trade、System 或 full-chain pipeline。

## 4. Acceptance

- Data 六件套明确 `stock / backward / day-week-month` legacy import 合同。
- 目标库明确为 `raw_market.duckdb` 与 `market_base_day/week/month.duckdb`。
- `index` 与 `block` 明确仅登记为 sidecar availability。
- 治理面明确 Data 是 foundation-only，不占策略主线施工位。
