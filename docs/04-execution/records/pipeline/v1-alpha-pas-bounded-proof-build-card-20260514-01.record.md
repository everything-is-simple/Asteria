# Alpha/PAS Bounded Proof Build Record

日期：2026-05-14

## 1. Card

| item | value |
|---|---|
| module | `pipeline` |
| runtime owner | `alpha` |
| run_id | `v1-alpha-pas-bounded-proof-build-card-20260514-01` |
| result | `passed / Alpha PAS bounded proof built` |

## 2. Execution Steps

1. 核对 live authority，确认当前 live next 仍为 `none / terminal`。
2. 核对 core recovery roadmap，确认第 6 卡为 prepared next route card。
3. 消费 `Alpha_PAS_Design_Set_v1_0` 与 `docs/03-refactor/08-alpha-pas-authority-map-v1.md`。
4. 按 TDD 新增 `tests/unit/alpha/test_alpha_pas_bounded_proof.py` 并确认红灯。
5. 新增 Alpha/PAS proof-only 合同、规则、artifact writer 与 CLI。
6. 只读消费 `H:\Asteria-data\malf_service_day.duckdb`，输出 temp proof DB 与 report JSON。
7. 生成 validated archive。
8. 同步 roadmap、module gate ledger、conclusion index 与执行四件套。

## 3. Runtime Result

| item | result |
|---|---|
| source DB | `H:\Asteria-data\malf_service_day.duckdb` |
| source service version | `malf-wave-position-dense-v1` |
| source MALF run | `malf-v1-4-core-runtime-sync-implementation-20260505-01` |
| requested scope | `day / 2024-01-02..2024-12-31 / symbol_limit=31` |
| observed source rows | `4395` |
| observed symbols | `19` |
| observed date window | `2024-01-08..2024-12-31` |
| PAS candidates | `4395` |
| lifecycle catalog states | `8` |
| hard_fail_count | `0` |
| formal DB mutation | `no` |

The observed window starts at `2024-01-08` because this card locks to
`malf-v1-4-core-runtime-sync-implementation-20260505-01`; later repaired MALF runs are not mixed into
this proof.

## 4. Output Surfaces

| table | role |
|---|---|
| `pas_market_context` | MALF setup context and boundary facts |
| `pas_strength_profile` | completed baseline and in-flight confirmation split |
| `pas_trigger_event` | trigger state and reason code |
| `pas_candidate_lifecycle` | current lifecycle state per candidate |
| `pas_lifecycle_state_catalog` | all eight contract lifecycle states |
| `pas_historical_rank_profile` | bounded rank / sparsity profile |
| `pas_entry_candidate` | Signal / T+1 proof consumable candidate surface |
| `pas_failure_state` | waiting / cancelled / modified / invalidated reason surface |
| `pas_source_lineage` | source run and concept trace |

## 5. Candidate Distribution

| dimension | counts |
|---|---|
| state | `invalidated=2142`; `modified=991`; `reentry_candidate=1185`; `triggered=77` |
| setup family | `BOF=186`; `BPB=2142`; `CPB=336`; `PB=290`; `TST=1441` |

## 6. Boundaries Preserved

| boundary | result |
|---|---|
| live next changed | `no` |
| formal DB mutation | `no` |
| MALF rewrite | `no` |
| historical code migration | `no` |
| return / PnL proof | `no` |
| broker feasibility reopened | `no` |
| position / portfolio / order / fill / account output | `no` |

## 7. Verification

本卡触碰 Python、CLI、tests、Markdown、report、validated archive，因此运行 targeted tests、
existing Alpha bounded proof regression、ruff、mypy、governance、workflow strict 与 diff check。
