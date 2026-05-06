# MALF Week Bounded Proof Build Record

日期：2026-05-06

run_id：`malf-week-bounded-proof-build-20260506-01`

## 1. Inputs

- `H:\Asteria-data\market_base_week.duckdb`
- `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_4`
- `docs/04-execution/records/data/data-reference-target-maintenance-closeout-20260506-01.conclusion.md`

## 2. Runtime Repairs

- `MalfDayRequest` timeframe allowlist 扩展到 `day / week`。
- Core、Lifespan、Service、Audit 四个现有 MALF stage runner 增加显式 `--timeframe` 参数。
- week build 复用 v1.4 day runtime 口径，只切换 source DB、target DB 与 timeframe；不修改 MALF 语义权威定义。
- 新增 unit coverage，证明 week fixture 能写入 week Core/Lifespan/Service 并通过 hard audit。

## 3. Formal Execution

| stage | 命令摘要 |
|---|---|
| core | `run_malf_day_core_build.py --timeframe week --run-id malf-week-bounded-proof-build-20260506-01 --rule-version core-rule-fractal-1bar-v1` |
| lifespan | `run_malf_day_lifespan_build.py --timeframe week --run-id malf-week-bounded-proof-build-20260506-01 --rule-version lifespan-dense-week-v1 --sample-version malf-week-formal-2024-s20-v1` |
| service | `run_malf_day_service_build.py --timeframe week --run-id malf-week-bounded-proof-build-20260506-01 --service-version malf-wave-position-week-v1` |
| audit | `run_malf_day_audit.py --timeframe week --run-id malf-week-bounded-proof-build-20260506-01` |

执行 scope：

```text
week / 2024-01-01..2024-12-31 / symbol_limit=20
source line = market_base_week.market_base_bar / analysis_price_line / backward
```

staging DB 先落在：

```text
H:\Asteria-temp\malf\malf-week-bounded-proof-build-20260506-01\staging\
```

hard audit 通过后 promote 到正式库：

```text
H:\Asteria-data\malf_core_week.duckdb
H:\Asteria-data\malf_lifespan_week.duckdb
H:\Asteria-data\malf_service_week.duckdb
```

## 4. Formal Outputs

- `H:\Asteria-data\malf_core_week.duckdb`
- `H:\Asteria-data\malf_lifespan_week.duckdb`
- `H:\Asteria-data\malf_service_week.duckdb`
- `H:\Asteria-report\malf\2026-05-06\malf-week-bounded-proof-build-20260506-01-audit-summary.json`
- `H:\Asteria-report\malf\2026-05-06\malf-week-bounded-proof-build-20260506-01\closeout.md`
- `H:\Asteria-report\malf\2026-05-06\malf-week-bounded-proof-build-20260506-01\manifest.json`
- `H:\Asteria-report\malf\2026-05-06\malf-week-bounded-proof-build-20260506-01\table-counts.json`
- `H:\Asteria-Validated\Asteria-malf-week-bounded-proof-build-20260506-01.zip`

## 5. Verification

- `pytest tests\unit\malf\test_bounded_proof_runner.py tests\unit\malf\test_v14_runtime_sync.py -q`
- week Core/Lifespan/Service staging build
- week hard audit
- formal DB post-promote natural-key check

最终结果：

```text
hard_fail_count = 0
WavePosition natural key duplicate groups = 0
```
