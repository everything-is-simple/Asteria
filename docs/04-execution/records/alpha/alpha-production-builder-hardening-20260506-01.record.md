# Alpha Production Builder Hardening Record

日期：2026-05-06

run_id：`alpha-production-builder-hardening-20260506-01`

## 1. Inputs

- `H:\Asteria-data\malf_service_day.duckdb`
- `H:\Asteria-data\malf_service_week.duckdb`
- `H:\Asteria-data\malf_service_month.duckdb`
- `docs/04-execution/records/malf/malf-month-bounded-proof-build-20260506-01.conclusion.md`

## 2. Runtime Repairs

- Alpha request timeframe allowlist 扩展到 `day / week / month`。
- Alpha runner mode allowlist 扩展到 `bounded / segmented / full / resume / audit-only`。
- 新增 `run_alpha_production_builder.py`，按 released MALF Service DB 编排五个 Alpha family。
- checkpoint 文件名加入 timeframe，避免同一 run_id 的 day/week/month 互相复用或覆盖。
- 正式写入改为命名列 insert，降低历史 DuckDB 列序漂移风险。
- day 输入增加 `source_malf_run_id` 与 `source_malf_sample_version` 锁定，避免混读历史同名 `service_version` rows。
- audit 增加 MALF sample version 可追溯检查。

## 3. Formal Execution

| stage | 命令摘要 |
|---|---|
| production builder | `run_alpha_production_builder.py --mode full --run-id alpha-production-builder-hardening-20260506-01` |

执行输入：

| timeframe | source DB | service version | source run |
|---|---|---|---|
| day | `malf_service_day.duckdb` | `malf-wave-position-dense-v1` | `malf-v1-4-core-runtime-sync-implementation-20260505-01` |
| week | `malf_service_week.duckdb` | `malf-wave-position-week-v1` | `malf-week-bounded-proof-build-20260506-01` |
| month | `malf_service_month.duckdb` | `malf-wave-position-month-v1` | `malf-month-bounded-proof-build-20260506-01` |

## 4. Formal Outputs

- `H:\Asteria-data\alpha_bof.duckdb`
- `H:\Asteria-data\alpha_tst.duckdb`
- `H:\Asteria-data\alpha_pb.duckdb`
- `H:\Asteria-data\alpha_cpb.duckdb`
- `H:\Asteria-data\alpha_bpb.duckdb`
- `H:\Asteria-report\alpha\2026-05-06\alpha-production-builder-hardening-20260506-01\closeout.md`
- `H:\Asteria-report\alpha\2026-05-06\alpha-production-builder-hardening-20260506-01\manifest.json`
- `H:\Asteria-Validated\Asteria-alpha-production-builder-hardening-20260506-01.zip`

## 5. Verification

- `pytest tests\unit\alpha\test_alpha_bounded_proof_runner.py`
- production builder formal execution
- formal Alpha DB post-run hard audit rollup
- formal Alpha DB event natural-key duplicate check

最终结果：

```text
hard_fail_count = 0
event natural key duplicate groups = 0
per family event/score/candidate rows = day 4633 + week 759 + month 102
```
