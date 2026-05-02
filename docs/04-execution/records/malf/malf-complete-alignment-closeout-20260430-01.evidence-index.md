# MALF Complete Alignment Closeout Evidence Index

日期：2026-04-30

状态：`passed`

## 1. Evidence Assets

| asset | path |
|---|---|
| run_id | `malf-complete-alignment-closeout-20260430-01` |
| report_dir | `H:\Asteria-report\malf\2026-04-30\malf-complete-alignment-closeout-20260430-01` |
| closeout | `H:\Asteria-report\malf\2026-04-30\malf-complete-alignment-closeout-20260430-01\closeout.md` |
| manifest | `H:\Asteria-report\malf\2026-04-30\malf-complete-alignment-closeout-20260430-01\manifest.json` |
| table_counts | `H:\Asteria-report\malf\2026-04-30\malf-complete-alignment-closeout-20260430-01\table-counts.json` |
| audit_summary | `H:\Asteria-report\malf\2026-04-30\malf-complete-alignment-closeout-20260430-01\audit-summary.json` |
| validated_zip | `H:\Asteria-Validated\2.backups\Asteria-malf-complete-alignment-closeout-20260430-01.zip` |
| backup_dir | `H:\Asteria-data\archive\malf-complete-alignment-closeout-20260430-01` |

## 2. Formal DBs

| DB | status |
|---|---|
| `H:\Asteria-data\malf_core_day.duckdb` | promoted from clean staging |
| `H:\Asteria-data\malf_lifespan_day.duckdb` | promoted from clean staging |
| `H:\Asteria-data\malf_service_day.duckdb` | promoted from clean staging |

## 3. Audit Results

| check | value |
|---|---:|
| hard audit rows | 20 |
| hard_fail_count | 0 |
| full-table Service natural-key duplicate groups | 0 |
| candidate reference mismatch count | 0 |

## 4. Row Counts

| table | rows |
|---|---:|
| `malf_wave_ledger` | 71 |
| `malf_candidate_ledger` | 689 |
| `malf_lifespan_snapshot` | 933 |
| `malf_lifespan_profile` | 4 |
| `malf_wave_position` | 933 |
| `malf_wave_position_latest` | 4 |
| `malf_interface_audit` | 20 |

## 5. Superseded Evidence

This closeout supersedes the formal current-evidence status of:

- `malf-lifespan-dense-bar-snapshot-resolution-20260429-01`
- `malf-alignment-hard-audit-hardening-20260430-01`

Those records remain historical facts, but current MALF day dense formal evidence is this
complete alignment closeout.

## 6. Repo Links

- [card](malf-complete-alignment-closeout-20260430-01.card.md)
- [record](malf-complete-alignment-closeout-20260430-01.record.md)
- [conclusion](malf-complete-alignment-closeout-20260430-01.conclusion.md)
