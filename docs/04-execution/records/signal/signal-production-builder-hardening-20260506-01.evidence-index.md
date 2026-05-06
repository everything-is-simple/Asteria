# Signal Production Builder Hardening Evidence Index

日期：2026-05-06

状态：`passed`

## 1. Evidence Assets

| asset | path |
|---|---|
| report_dir | `H:\Asteria-report\signal\2026-05-06\signal-production-builder-hardening-20260506-01\` |
| manifest | `H:\Asteria-report\signal\2026-05-06\signal-production-builder-hardening-20260506-01\manifest.json` |
| closeout | `H:\Asteria-report\signal\2026-05-06\signal-production-builder-hardening-20260506-01\closeout.md` |
| day audit | `H:\Asteria-report\signal\2026-05-06\signal-production-builder-hardening-20260506-01-day-audit-summary.json` |
| week audit | `H:\Asteria-report\signal\2026-05-06\signal-production-builder-hardening-20260506-01-week-audit-summary.json` |
| month audit | `H:\Asteria-report\signal\2026-05-06\signal-production-builder-hardening-20260506-01-month-audit-summary.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-signal-production-builder-hardening-20260506-01.zip` |

## 2. Formal DB

| item | value |
|---|---|
| target DB | `H:\Asteria-data\signal.duckdb` |
| source Alpha run | `alpha-production-builder-hardening-20260506-01` |
| source Alpha DBs | `alpha_bof.duckdb`; `alpha_tst.duckdb`; `alpha_pb.duckdb`; `alpha_cpb.duckdb`; `alpha_bpb.duckdb` |

## 3. Audit Result

| check | result |
|---|---|
| timeframes | `day / week / month` |
| day formal_signal rows | `4633` |
| week formal_signal rows | `759` |
| month formal_signal rows | `102` |
| day input snapshot / component rows | `23165 / 23165` |
| week input snapshot / component rows | `3795 / 3795` |
| month input snapshot / component rows | `510 / 510` |
| hard_fail_count | `0` |
| formal signal natural-key duplicate groups | `0` |
| component natural-key duplicate groups | `0` |
| source Alpha run ids | `alpha-production-builder-hardening-20260506-01` only |
| allowed next action | `upstream_pre_position_release_decision` |

## 4. Boundary

本证据只放行 Signal day/week/month production builder hardening。它不授权 Position build、
Portfolio / Trade / System 施工或 full-chain Pipeline runtime。
