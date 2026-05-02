# MALF v1.3 Formal Rebuild Closeout Record

日期：2026-05-02

run_id：`malf-v1-3-formal-rebuild-closeout-20260502-01`

## 1. Inputs

- `H:\Asteria-data\market_base_day.duckdb`
- `docs/04-execution/records/data/data-formal-promotion-evidence-20260502-01.conclusion.md`
- `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_3`

## 2. Repairs

- Lifespan Core reads are isolated by `run_id`.
- Core `structure_context` is no longer hard-coded to `active_wave`.
- Governance docs sync now points at MALF v1.3 and the 20260502 docs/code snapshot.
- Transition boundary high/low are ordered for real-data edge cases while old progress remains traceable.

## 3. Formal Outputs

| DB | path |
|---|---|
| Core | `H:\Asteria-data\malf_core_day.duckdb` |
| Lifespan | `H:\Asteria-data\malf_lifespan_day.duckdb` |
| Service | `H:\Asteria-data\malf_service_day.duckdb` |

## 4. Scope

| 项 | 值 |
|---|---|
| mode | `bounded formal-data proof` |
| timeframe | `day` |
| start_dt | `2024-01-01` |
| end_dt | `2024-12-31` |
| symbol_limit | `20` |
| source rows | `1,280,703` |

## 5. Boundary

本卡不纳入 week/month bounded proof，不打开 Position construction。
