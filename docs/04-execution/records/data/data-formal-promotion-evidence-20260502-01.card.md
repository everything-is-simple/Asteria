# Data Formal Promotion Evidence Card

日期：2026-05-02

状态：`formal-promotion / foundation-only`

## 1. Scope

本卡把第 3 卡通过审计的 working DB promote 为 Asteria 首轮正式 Data Foundation DB。

## 2. Allowed

- 从 `H:\Asteria-temp\data\data-legacy-import-runner-working-build-20260502-01` promote。
- 写入 `H:\Asteria-data\raw_market.duckdb`。
- 写入 `H:\Asteria-data\market_base_day/week/month.duckdb`。
- 执行正式 DB hard audit。
- 生成 closeout、manifest、audit summary 与 Validated zip。

## 3. Forbidden

- 不声明 Data full build released。
- 不创建 `market_meta.duckdb`。
- 不把 index/block 纳入 MALF 首轮证明输入。
- 不打开 Position、Portfolio、Trade、System 或 full-chain pipeline。

## 4. Acceptance

- 四个正式 Data DB 存在。
- raw/base natural key audit 通过。
- base latest 指针无重复。
- 不含策略字段。
