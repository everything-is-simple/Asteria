# Data Ledger Daily Incremental Hardening Record

日期：2026-05-11

## 1. 卡信息

| 项 | 值 |
|---|---|
| module | `data` |
| run_id | `data-ledger-daily-incremental-hardening-card` |
| result | `passed / data daily incremental sample hardened` |
| next allowed action | `malf_daily_incremental_ledger_build_card` |

## 2. 执行顺序

1. 新增 Data daily incremental hardening runner 与 CLI。
2. 在单测中覆盖 unchanged source skip、changed source recompute、dirty scope、resume、week/month read-only audit。
3. 扩展 Data production audit，使四个行情账本都检查 run ledger、dirty scope/latest/bar 自然键唯一性，且确认 `raw_market_source_file` 可作为 source manifest diff 来源。
4. 在 `H:\Asteria-temp` 构造小样本 source/target，执行 `daily_incremental`、`resume`、`audit-only` 三种模式。
5. 生成 `H:\Asteria-report` closeout/manifest 与 `H:\Asteria-Validated` validated zip。
6. 将 live next 从 Data hardening 切到 `malf_daily_incremental_ledger_build_card`，但不执行 MALF runtime。

## 3. 关键验证

| 验证 | 结果 |
|---|---|
| `tests\unit\data\test_daily_incremental_hardening.py` | `5 passed` |
| `tests\unit\data\test_production_audit.py` | `10 passed` |
| sample `daily_incremental` CLI | `passed` |
| sample `resume` CLI | `passed` |
| sample `audit-only` CLI | `passed` |

## 4. 边界

- 本卡只覆盖 `raw_market.duckdb`、`market_base_day.duckdb`、`market_base_week.duckdb`、`market_base_month.duckdb`。
- `market_base_week/month` 在本卡只做账本一致性与 dirty scope 审计，不从 day 重新聚合。
- `market_meta.duckdb` 不作为新增 daily bar 账本。
- 本卡未修改正式 `H:\Asteria-data`。
- MALF、Alpha/Signal、downstream 与 Pipeline runtime 均未执行。
