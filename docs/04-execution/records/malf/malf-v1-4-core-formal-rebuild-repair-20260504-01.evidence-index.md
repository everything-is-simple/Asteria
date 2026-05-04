# MALF v1.4 Core Formal Rebuild Repair Evidence Index

日期：2026-05-04

状态：`passed`

## 1. Code And Test Assets

| asset | path |
|---|---|
| closeout | `H:\Asteria-report\malf\2026-05-04\malf-v1-4-core-formal-rebuild-repair-20260504-01\closeout.md` |
| manifest | `H:\Asteria-report\malf\2026-05-04\malf-v1-4-core-formal-rebuild-repair-20260504-01\manifest.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-malf-v1-4-core-formal-rebuild-repair-20260504-01.zip` |
| insert contract source | `src/asteria/malf/insert_contracts.py` |
| Core / Lifespan / Service writer surface | `src/asteria/malf/bootstrap.py` |
| run table writer surface | `src/asteria/malf/bootstrap_support.py` |
| compat schema surface | `src/asteria/malf/schema.py` |
| legacy promoted regression | `tests/unit/malf/test_v14_legacy_promoted_tables.py` |
| v1.4 behavior guardrail | `tests/unit/malf/test_v14_runtime_sync_code.py` |

## 2. Verification Results

| check | result |
|---|---|
| governance check | `passed` |
| ruff check | `passed` |
| ruff format --check | `passed` |
| mypy src | `passed` |
| MALF unit tests | `29 passed` |
| `git diff --check` | `passed` |

## 3. Formal Compatibility Evidence

| surface | result |
|---|---|
| `H:\Asteria-data\malf_core_day.duckdb.malf_core_run` | v1.4 policy fields written into named columns; `created_at` remains timestamp |
| `H:\Asteria-data\malf_lifespan_day.duckdb.malf_lifespan_run` | v1.4 policy fields written into named columns; `created_at` remains timestamp |
| `H:\Asteria-data\malf_service_day.duckdb.malf_service_run` | v1.4 policy fields written into named columns; `created_at` remains timestamp |
| `H:\Asteria-data\malf_core_day.duckdb.malf_pivot_ledger` | `pivot_detection_rule_version` written into named column |
| `scripts/malf/run_malf_day_core_build.py` | `completed` on formal DB |
| `scripts/malf/run_malf_day_lifespan_build.py` | `completed` on formal DB |
| `scripts/malf/run_malf_day_service_build.py` | `completed` on formal DB |

## 4. Closeout Handoff

repair 解开了“首个正式写入事务即失败”的阻塞，但后续 closeout rerun 在 hard audit 处发现新的
独立阻塞，详见：

- `docs/04-execution/records/malf/malf-v1-4-core-formal-rebuild-closeout-20260504-01.record.md`
- `docs/04-execution/records/malf/malf-v1-4-core-formal-rebuild-closeout-20260504-01.conclusion.md`
- `docs/04-execution/records/malf/malf-v1-4-core-formal-rebuild-audit-repair-20260504-02.card.md`
