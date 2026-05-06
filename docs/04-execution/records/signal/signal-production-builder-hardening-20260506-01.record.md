# Signal Production Builder Hardening Record

日期：2026-05-06

状态：`passed`

## 1. Scope

本卡只施工 Signal production builder hardening。它承接
`alpha-production-builder-hardening-20260506-01`，只读消费五个 Alpha family 正式库：

```text
alpha_bof.duckdb
alpha_tst.duckdb
alpha_pb.duckdb
alpha_cpb.duckdb
alpha_bpb.duckdb
```

本卡不创建 Position、Portfolio、Trade、System 或 Pipeline 产物。

## 2. Implementation Summary

- Signal request mode allowlist 扩展到 `bounded / segmented / full / resume / audit-only`。
- Signal timeframe allowlist 扩展到 `day / week / month`。
- 新增 `run_signal_production_builder.py`，编排 released Alpha family DBs 的 day/week/month build。
- checkpoint 文件名加入 timeframe，避免同一 run_id 的 day/week/month 互相复用。
- Signal input snapshot 增加 `source_alpha_run_id`，正式执行锁定
  `alpha-production-builder-hardening-20260506-01`，避免混读旧 bounded Alpha rows。
- full mode 对同 timeframe / signal rule surface 执行替换，防止旧 bounded Signal rows 与 production rows
  形成自然键重复。

## 3. Formal Execution

| stage | 命令摘要 |
|---|---|
| production builder | `run_signal_production_builder.py --mode full --run-id signal-production-builder-hardening-20260506-01` |

执行输入：

| 项 | 值 |
|---|---|
| source_alpha_root | `H:\Asteria-data` |
| source_alpha_run_id | `alpha-production-builder-hardening-20260506-01` |
| target_signal_db | `H:\Asteria-data\signal.duckdb` |
| report_root | `H:\Asteria-report` |
| validated_root | `H:\Asteria-Validated` |
| timeframes | `day / week / month` |

## 4. Result

| timeframe | input candidates | formal signals | components | hard audit |
|---|---:|---:|---:|---:|
| `day` | 23165 | 4633 | 23165 | 0 |
| `week` | 3795 | 759 | 3795 | 0 |
| `month` | 510 | 102 | 510 | 0 |

Natural key verification:

| check | result |
|---|---:|
| formal signal duplicate groups | 0 |
| component duplicate groups | 0 |
| source Alpha run ids | `alpha-production-builder-hardening-20260506-01` only |

## 5. Evidence

| artifact | path |
|---|---|
| report dir | `H:\Asteria-report\signal\2026-05-06\signal-production-builder-hardening-20260506-01\` |
| validated zip | `H:\Asteria-Validated\Asteria-signal-production-builder-hardening-20260506-01.zip` |
| audit summary day | `H:\Asteria-report\signal\2026-05-06\signal-production-builder-hardening-20260506-01-day-audit-summary.json` |
| audit summary week | `H:\Asteria-report\signal\2026-05-06\signal-production-builder-hardening-20260506-01-week-audit-summary.json` |
| audit summary month | `H:\Asteria-report\signal\2026-05-06\signal-production-builder-hardening-20260506-01-month-audit-summary.json` |

## 6. Boundary

本卡只放行 Signal 在 released Alpha day/week/month production builder 表面的 formal signal
ledger。它不打开 Position construction，不创建 `position.duckdb`，不写资金、订单、成交或
Pipeline runtime 语义。
