# Data Legacy Import Runner Working Build Record

日期：2026-05-02

run_id：`data-legacy-import-runner-working-build-20260502-01`

## 1. Inputs

- `H:\Lifespan-data\raw`
- `H:\Lifespan-data\base`
- `docs/04-execution/records/data/data-legacy-import-contract-freeze-20260502-01.conclusion.md`

## 2. Code Changes

- `src/asteria/data/contracts.py`
- `src/asteria/data/schema.py`
- `src/asteria/data/legacy_import.py`
- `scripts/data/run_legacy_data_import.py`
- `tests/unit/data/test_legacy_import.py`

## 3. Working Outputs

| DB | path |
|---|---|
| raw | `H:\Asteria-temp\data\data-legacy-import-runner-working-build-20260502-01\raw_market.duckdb` |
| base day | `H:\Asteria-temp\data\data-legacy-import-runner-working-build-20260502-01\market_base_day.duckdb` |
| base week | `H:\Asteria-temp\data\data-legacy-import-runner-working-build-20260502-01\market_base_week.duckdb` |
| base month | `H:\Asteria-temp\data\data-legacy-import-runner-working-build-20260502-01\market_base_month.duckdb` |

## 4. Row Counts

| scope | rows |
|---|---:|
| raw stock backward all timeframes | 20,628,416 |
| base day | 16,348,113 |
| base week | 3,453,967 |
| base month | 826,336 |

## 5. Boundary

本卡只证明 working import runner 可用。不写正式 Data DB，不改变 MALF evidence 状态。
