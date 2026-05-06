# Alpha Production Builder Hardening Evidence Index

日期：2026-05-06

run_id：`alpha-production-builder-hardening-20260506-01`

## 1. Repo Records

| evidence | path |
|---|---|
| card | `docs/04-execution/records/alpha/alpha-production-builder-hardening-20260506-01.card.md` |
| record | `docs/04-execution/records/alpha/alpha-production-builder-hardening-20260506-01.record.md` |
| conclusion | `docs/04-execution/records/alpha/alpha-production-builder-hardening-20260506-01.conclusion.md` |
| conclusion index | `docs/04-execution/00-conclusion-index-v1.md` |
| gate ledger | `docs/03-refactor/00-module-gate-ledger-v1.md` |

## 2. Runtime Evidence

| evidence | path |
|---|---|
| source day DB | `H:\Asteria-data\malf_service_day.duckdb` |
| source week DB | `H:\Asteria-data\malf_service_week.duckdb` |
| source month DB | `H:\Asteria-data\malf_service_month.duckdb` |
| BOF DB | `H:\Asteria-data\alpha_bof.duckdb` |
| TST DB | `H:\Asteria-data\alpha_tst.duckdb` |
| PB DB | `H:\Asteria-data\alpha_pb.duckdb` |
| CPB DB | `H:\Asteria-data\alpha_cpb.duckdb` |
| BPB DB | `H:\Asteria-data\alpha_bpb.duckdb` |
| closeout | `H:\Asteria-report\alpha\2026-05-06\alpha-production-builder-hardening-20260506-01\closeout.md` |
| manifest | `H:\Asteria-report\alpha\2026-05-06\alpha-production-builder-hardening-20260506-01\manifest.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-alpha-production-builder-hardening-20260506-01.zip` |

## 3. Audit Result

| check | result |
|---|---|
| timeframes | `day / week / month` |
| families | `BOF / TST / PB / CPB / BPB` |
| per-family day rows | `4633` |
| per-family week rows | `759` |
| per-family month rows | `102` |
| hard_fail_count | `0` |
| event natural key duplicate groups | `0` |
| allowed next action | `signal_production_builder_hardening` |

## 4. Boundary

本证据只放行 Alpha 五族在 released MALF day/week/month WavePosition 表面的 production
builder hardening。它不创建 Signal full release，不打开 Position construction，不创建下游正式库，
也不建立 full-chain Pipeline runtime。
