# Signal/PAS Contract Alignment Record

日期：2026-05-14

## 1. Card

| item | value |
|---|---|
| module | `pipeline` |
| runtime owner | `signal` |
| run_id | `v1-signal-contract-alignment-card-20260514-01` |
| result | `passed / signal contract aligned` |

## 2. Execution Steps

1. 核对 live authority，确认当前 live next 仍为 `none / terminal`。
2. 核对 core recovery roadmap，确认第 7 卡为 prepared next route card。
3. 复核第 6 卡 PAS proof DB 的 `pas_entry_candidate` 表面。
4. 按 TDD 新增 `tests/unit/signal/test_signal_pas_alignment.py` 并确认红灯。
5. 新增 Signal/PAS alignment-only 合同、runner、artifact writer 与 CLI。
6. 只读消费第 6 卡 temp PAS proof DB，输出 temp Signal/PAS alignment DB 与 report JSON。
7. 生成 validated archive。
8. 同步 roadmap、module gate ledger、conclusion index 与执行四件套。

## 3. Runtime Result

| item | result |
|---|---|
| source PAS DB | `H:\Asteria-temp\alpha_pas\v1-alpha-pas-bounded-proof-build-card-20260514-01\alpha_pas_bounded_proof.duckdb` |
| source PAS run | `v1-alpha-pas-bounded-proof-build-card-20260514-01` |
| mode / timeframe | `bounded / day` |
| PAS input candidates | `4395` |
| active PAS candidates | `1262` |
| aligned formal signals | `1262` |
| component ledger rows | `1262` |
| hard_fail_count | `0` |
| formal DB mutation | `no` |

## 4. Output Surfaces

| table | role |
|---|---|
| `signal_pas_input_snapshot` | preserve PAS candidate source facts, including non-active states |
| `signal_pas_formal_signal` | Signal consumable aligned signal surface |
| `signal_pas_component_ledger` | PAS candidate components supporting each aligned Signal |
| `signal_pas_audit` | contract and boundary checks |

## 5. Alignment Semantics

| rule | decision |
|---|---|
| active input | PAS `candidate_state in ('triggered', 'reentry_candidate')` |
| aggregation key | `symbol + timeframe + signal_date` |
| signal strength | max active PAS `strength_score` |
| signal family | stable sorted setup family string, e.g. `BOF+TST` |
| non-active states | retained in input snapshot; no active Signal emitted |
| execution hint | `T_PLUS_1_OPEN / next_trading_day_after_signal_date / open` |
| lineage | candidate id, PAS run, MALF WavePosition run, source concept trace |

## 6. Boundaries Preserved

| boundary | result |
|---|---|
| live next changed | `no` |
| formal DB mutation | `no` |
| existing `signal.duckdb` changed | `no` |
| return / PnL proof | `no` |
| broker feasibility reopened | `no` |
| position / portfolio / order / fill / account output | `no` |

## 7. Verification

本卡触碰 Python、CLI、tests、Markdown、report、validated archive，因此运行 targeted tests、
existing Signal bounded proof regression、ruff、mypy、governance、workflow strict 与 diff check。
