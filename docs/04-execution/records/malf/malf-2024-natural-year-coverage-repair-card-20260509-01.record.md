# MALF 2024 Natural-Year Coverage Repair Record

日期：2026-05-09

run_id：`malf-2024-natural-year-coverage-repair-card-20260509-01`

## 1. Inputs

- `H:\Asteria-data\market_base_day.duckdb`
- `H:\Asteria-data\malf_service_day.duckdb`
- `H:\Asteria-data\system.duckdb`
- `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4`
- `docs/04-execution/records/pipeline/pipeline-year-replay-coverage-gap-diagnosis-and-repair-scope-freeze-20260509-01.conclusion.md`

## 2. Preflight

- 锁定当前 released `system_readout_run = system-readout-bounded-proof-build-card-20260508-01`。
- 锁定其 `system_source_manifest.malf = malf-v1-4-core-runtime-sync-implementation-20260505-01`。
- 直接查询正式 `market_base_day` 与 `malf_service_day`，确认 Data 已覆盖
  `2024-01-02..2024-01-05`，而当前 released MALF run 仍从 `2024-01-08` 才开始。
- 先在 `H:\Asteria-temp` 上做 symbol probe，证明现有 MALF day segmented repair
  路径无需改 runtime 即可把 focus trading dates 放出来。

## 3. Repair Decision

- 不扩大到 Data / Alpha / Signal / System Readout / Pipeline 语义修补。
- 不把本卡偷换成 year replay rerun。
- 由于 Pipeline 和后续 rerun 都按单一 `source_run_id` 锁 MALF surface，本卡选择
  `000020.SZ` 作为最小 coherent released run repair 集。
- repair 采用现有 `run_malf_day_supplemental_build`：
  `segmented + day + year=2024 + explicit symbol set = ('000020.SZ',)`。

## 4. Formal Execution

| stage | command summary |
|---|---|
| rehearsal | temp probe on `000020.SZ` proved `2024-01-02..2024-01-05` can publish |
| repair | inline Python calling `run_malf_day_supplemental_build(...)` with run_id `malf-2024-natural-year-coverage-repair-card-20260509-01` |
| promote | stage `core -> lifespan -> service -> audit -> promote` |
| post-check | verify new formal run `malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001` in `malf_service_run` |

执行 scope：

```text
day / target year = 2024 / repaired symbol set = 000020.SZ
source line = market_base_day.market_base_bar / analysis_price_line / backward
```

staging DB 落在：

```text
H:\Asteria-temp\malf\malf-2024-natural-year-coverage-repair-card-20260509-01\batch-0001\
```

formal promote 目标保持：

```text
H:\Asteria-data\malf_core_day.duckdb
H:\Asteria-data\malf_lifespan_day.duckdb
H:\Asteria-data\malf_service_day.duckdb
```

## 5. Formal Outputs

- `H:\Asteria-data\malf_core_day.duckdb`
- `H:\Asteria-data\malf_lifespan_day.duckdb`
- `H:\Asteria-data\malf_service_day.duckdb`
- `H:\Asteria-report\malf\2026-05-09\malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001-audit-summary.json`
- `H:\Asteria-report\malf\2026-05-09\malf-2024-natural-year-coverage-repair-card-20260509-01\closeout.md`
- `H:\Asteria-report\malf\2026-05-09\malf-2024-natural-year-coverage-repair-card-20260509-01\manifest.json`
- `H:\Asteria-report\malf\2026-05-09\malf-2024-natural-year-coverage-repair-card-20260509-01\table-counts.json`
- `H:\Asteria-Validated\Asteria-malf-2024-natural-year-coverage-repair-card-20260509-01.zip`

## 6. Verification

- Focus trading dates on repaired released run:

```text
2024-01-02
2024-01-03
2024-01-04
2024-01-05
```

- `hard_fail_count = 0`
- `WavePosition natural key duplicate groups = 0`
- `system_source_manifest` still points to旧 MALF run；本卡只把下一步切到 rerun prepared card，不提前改写 system evidence
