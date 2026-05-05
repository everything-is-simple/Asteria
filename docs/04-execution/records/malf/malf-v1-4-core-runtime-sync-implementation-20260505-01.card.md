# MALF v1.4 Core Runtime Sync Implementation Card

日期：2026-05-05

状态：`formal-data bounded proof / v1.4 day runtime sync closeout`

## 1. Scope

本卡只施工 MALF day runtime sync，并在同步后的代码下重建正式 day 三库。

输入：

```text
H:\Asteria-data\market_base_day.duckdb
```

首轮范围：

```text
day / 2024-01-01..2024-12-31 / symbol_limit=20
official source line = analysis_price_line / backward
```

## 2. Allowed

- 同步 `core_engine / schema / contracts / bootstrap` 到 MALF v1.4 day 语义。
- 补齐 `malf_core_state_snapshot`、policy/version metadata 与 candidate event type。
- 用正式 Data 输入重建 `malf_core_day / malf_lifespan_day / malf_service_day`。
- 执行 MALF hard audit，并形成新的 repo-local execution four-pack 与 validated zip。

## 3. Forbidden

- 不打开 week/month proof。
- 不修改 Data 合同或让 Data runner 代替 MALF 写三库。
- 不打开 Alpha / Signal / Position / downstream construction。
- 不把 execution price line 混入 MALF day Core 输入。

## 4. Acceptance

- MALF day current runtime evidence 升级为 v1.4 runtime-aligned proof。
- `malf_core_state_snapshot` 正式入库，且 v1.4 policy fields 可审计。
- hard_fail_count = 0。
- 结论必须明确：当前只更新 day runtime proof，不声明 week/month 或 full build 通过。
