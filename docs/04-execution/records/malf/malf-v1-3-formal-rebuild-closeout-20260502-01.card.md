# MALF v1.3 Formal Rebuild Closeout Card

日期：2026-05-02

状态：`formal-data bounded proof / v1.3 closeout`

## 1. Scope

本卡使用正式 Data Foundation 输入重建 MALF v1.3 day evidence。

输入：

```text
H:\Asteria-data\market_base_day.duckdb
```

首轮范围：

```text
day / 2024-01-01..2024-12-31 / symbol_limit=20
```

## 2. Allowed

- 修复 MALF v1.3 gap repair。
- 重建 day Core / Lifespan / Service。
- 执行 MALF hard audit。
- 生成 closeout、manifest、table counts、Validated zip。

## 3. Forbidden

- 不打开 week/month proof。
- 不打开 Position construction。
- 不打开 Alpha/Signal full build 或下游施工。
- 不让下游回写 MALF。

## 4. Acceptance

- MALF v1.3 day formal-data bounded rebuild 完成。
- hard_fail_count = 0。
- conclusion index 明确当前 MALF v1.3 evidence 状态与边界。
