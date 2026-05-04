# MALF v1.4 Core Formal Rebuild Audit Repair Evidence Index

日期：2026-05-04

状态：`passed`

## 1. Evidence Assets

| asset | path |
|---|---|
| run_id | `malf-v1-4-core-formal-rebuild-audit-repair-20260504-02` |
| report_dir | `H:\Asteria-report\malf\2026-05-04\malf-v1-4-core-formal-rebuild-audit-repair-20260504-02` |
| closeout | `H:\Asteria-report\malf\2026-05-04\malf-v1-4-core-formal-rebuild-audit-repair-20260504-02\closeout.md` |
| manifest | `H:\Asteria-report\malf\2026-05-04\malf-v1-4-core-formal-rebuild-audit-repair-20260504-02\manifest.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-malf-v1-4-core-formal-rebuild-audit-repair-20260504-02.zip` |
| repaired closeout | `docs/04-execution/records/malf/malf-v1-4-core-formal-rebuild-closeout-20260504-01.conclusion.md` |
| source filter surface | `src/asteria/malf/bootstrap_support.py` |
| core read surface | `src/asteria/malf/core_engine.py` |
| birth descriptor surface | `src/asteria/malf/birth_descriptors.py` |
| audit source-binding surface | `src/asteria/malf/audit_support.py` |
| regression tests | `tests/unit/malf/test_v14_runtime_sync_code.py` |

## 2. Repaired Audit Results

| check | result |
|---|---:|
| `service_wave_position_natural_key_unique` | `0` |
| `core_new_candidate_replaces_previous` | `0` |
| `service_v13_trace_matches_lifespan` | `0` |
| hard_fail_count | `0` |

## 3. Closeout Handoff

本卡不单独释放 runtime proof；它以 closeout rerun 真正通过为闭环条件。对应放行结果见：

- [closeout record](malf-v1-4-core-formal-rebuild-closeout-20260504-01.record.md)
- [closeout conclusion](malf-v1-4-core-formal-rebuild-closeout-20260504-01.conclusion.md)
- [closeout evidence-index](malf-v1-4-core-formal-rebuild-closeout-20260504-01.evidence-index.md)
