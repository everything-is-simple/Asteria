# Data Legacy Import Runner Working Build Card

日期：2026-05-02

状态：`working-build / foundation-only`

## 1. Scope

本卡实现旧版 Lifespan raw/base DuckDB 到 Asteria canonical working DB 的导入 runner。

首轮范围：

```text
stock-only
day / week / month
backward adjusted base
```

## 2. Allowed

- 新增 legacy import runner 与 CLI。
- 输出 working DB 到 `H:\Asteria-temp\data\<run_id>\`。
- 添加 unit tests 覆盖小型 legacy DuckDB fixture、字段映射、唯一性与 row count。
- 生成 working build closeout、manifest、audit summary 与 validated evidence zip。

## 3. Forbidden

- 不写 `H:\Asteria-data`。
- 不 promote 正式 Data DB。
- 不打开 MALF rebuild；MALF 回归到 Card 5。
- 不打开 Position、Portfolio、Trade、System 或 full-chain pipeline。

## 4. Acceptance

- working `raw_market.duckdb` 生成成功。
- working `market_base_day/week/month.duckdb` 生成成功。
- raw/base row count 与旧库 backward stock 范围对齐。
- base 自然键与 latest 指针无重复。
