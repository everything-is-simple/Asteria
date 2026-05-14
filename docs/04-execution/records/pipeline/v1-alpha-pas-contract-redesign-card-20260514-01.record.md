# Alpha/PAS Contract Redesign Record

日期：2026-05-14

## 1. Card

| item | value |
|---|---|
| module | `pipeline` |
| run_id | `v1-alpha-pas-contract-redesign-card-20260514-01` |
| result | `passed / Alpha PAS contract redesigned` |

## 2. Execution Steps

1. 核对 live authority，确认 `current_allowed_next_card = ""` 且当前 live next 仍为 `none / terminal`。
2. 核对 core recovery roadmap，确认第五卡是 `v1-alpha-pas-contract-redesign-card`。
3. 消费 `docs/03-refactor/08-alpha-pas-authority-map-v1.md` 与第 4 卡 conclusion。
4. 创建 `H:\Asteria-Validated\Alpha_PAS_Design_Set_v1_0` 定义包。
5. 冻结 Alpha/PAS service surface、candidate lifecycle、source lineage、T+1 open proof hint 与 forbidden outputs。
6. 生成 package `MANIFEST.json`、`Alpha_PAS_Design_Set_v1_0.zip` 与 card validated archive。
7. 同步 roadmap、module gate ledger、conclusion index、repo 四件套、外部 report / manifest。

## 3. Frozen Package

| item | result |
|---|---|
| package directory | `H:\Asteria-Validated\Alpha_PAS_Design_Set_v1_0` |
| package zip | `H:\Asteria-Validated\Alpha_PAS_Design_Set_v1_0.zip` |
| package status | `frozen / contract redesigned / roadmap-only` |
| manifest | `H:\Asteria-Validated\Alpha_PAS_Design_Set_v1_0\MANIFEST.json` |
| next route card | `v1-alpha-pas-bounded-proof-build-card` |

## 4. Contract Summary

| area | result |
|---|---|
| fixed input | MALF v1.4 WavePosition / service facts; setup-time visible facts; authority map |
| output layers | `pas_market_context`; `pas_strength_profile`; `pas_setup_family`; `pas_trigger_event`; `pas_candidate_lifecycle`; `pas_historical_rank_profile`; `pas_entry_candidate`; `pas_management_handoff_hint`; `pas_failure_state`; `pas_source_lineage` |
| required lineage | source run, MALF WavePosition run, rule version, schema version, source concept trace, lineage |
| execution hint | `T_PLUS_1_OPEN` |
| trade date policy | `next_trading_day_after_signal_date` |
| price field | `open` |
| consumer | Signal and T+1 open proof |

## 5. Boundaries Preserved

| boundary | result |
|---|---|
| live next changed | `no` |
| formal DB mutation | `no` |
| historical code migration | `no` |
| runtime schema created | `no` |
| bounded proof executed | `no` |
| broker feasibility reopened | `no` |
| profit proof claimed | `no` |

## 6. Verification

本卡为 Markdown + manifest + repo 外 validated package 更新；未修改 Python、schema、runner、
tests 或正式 DuckDB，因此不运行 ruff / mypy / pytest。

执行的治理检查：

```powershell
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_project_governance.py
H:\Asteria\.venv\Scripts\python.exe scripts\governance\check_asteria_workflow.py --strict
git diff --check
```
