# MALF Implementation Traceability Annex v1

日期：2026-04-29

状态：Asteria-specific annex / traceability only

## 1. 边界

本附件不修改 `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2` 中任何 MALF
定义、定理或接口原文。它只把 MALF 权威语义追踪到 Asteria 的 schema、runner、
audit rule 和 evidence，避免后续 Alpha freeze review 依赖人工记忆判断是否偏移。

## 2. 权威输入

| 资产 | 地位 |
|---|---|
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2\MALF_00_Three_Documents_Bridge_v1_2.md` | 三文档关系桥接 |
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2\MALF_01_Core_Definitions_Theorems_v1_3.md` | Core 定义与定理权威 |
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2\MALF_02_Lifespan_Stats_Definitions_Theorems_v1_2.md` | Lifespan 统计定义与定理权威 |
| `H:\Asteria-Validated\MALF_Three_Part_Design_Set_v1_2\MALF_03_System_Service_Interface_v1_2.md` | WavePosition 服务接口权威 |
| `H:\Asteria-Validated\Asteria-docs-code-20260429-130309.zip` | Asteria 当前系统 docs/code 快照 |

## 3. MALF 到 Asteria 追踪表

| MALF theorem / definition | Asteria schema table / field | runner | audit rule | evidence |
|---|---|---|---|---|
| Core 结构事实由 pivot、structure、wave、break、transition、candidate 组成 | `malf_core_day.duckdb`: `malf_pivot_ledger`, `malf_structure_ledger`, `malf_wave_ledger`, `malf_break_ledger`, `malf_transition_ledger`, `malf_candidate_ledger` | `scripts/malf/run_malf_day_core_build.py` | Core 硬审计：terminated wave 不得重新 alive；break 后不得延伸旧 wave；transition 必须有关联 `old_wave_id` | `docs/04-execution/records/malf/malf-day-bounded-proof-20260428-01.conclusion.md` |
| wave core state 只表达 core wave 存活性 | `malf_wave_ledger.wave_core_state`, `malf_wave_position.wave_core_state` | `scripts/malf/run_malf_day_service_build.py` | Service 硬审计：`wave_core_state` 不得为 `transition`；不得与 `system_state` 合并 | `H:\Asteria-report\malf\2026-04-28\malf-day-bounded-proof-20260428-01\closeout.md` |
| transition 是 system/interface 状态，不是 wave_core_state | `malf_transition_ledger`, `malf_wave_position.system_state`, `malf_wave_position.old_wave_id`, `malf_wave_position.wave_id` | `scripts/malf/run_malf_day_service_build.py` | `system_state = transition` 时 `old_wave_id` 必填，`wave_id` 为空 | `docs/02-modules/malf/04-audit-spec-v1.md` |
| transition 期间 direction 使用 old_direction | `malf_transition_ledger.old_wave_id`, `malf_wave_position.direction` | `scripts/malf/run_malf_day_service_build.py` | Lifespan / Service 硬审计：transition 中 `direction` 必须为 old_direction | `H:\Asteria-Validated\Asteria-malf-day-bounded-proof-20260428-01.zip` |
| new wave confirmation bar 的 `no_new_span = 0` | `malf_lifespan_snapshot.no_new_span`, `malf_wave_position.no_new_span` | `scripts/malf/run_malf_day_lifespan_build.py`, `scripts/malf/run_malf_day_service_build.py` | Lifespan 硬审计：new wave confirmation bar 的 `no_new_span = 0` | `docs/04-execution/records/malf/malf-day-bounded-proof-20260428-01.evidence-index.md` |
| `transition_span` 不并入 `no_new_span` | `malf_transition_ledger`, `malf_wave_position.transition_span`, `malf_wave_position.no_new_span` | `scripts/malf/run_malf_day_lifespan_build.py`, `scripts/malf/run_malf_day_service_build.py` | Lifespan 硬审计：`transition_span` 不并入 `no_new_span` | `docs/02-modules/malf/02-database-schema-spec-v1.md` |
| WavePosition 是 Alpha 面向的只读服务接口 | `malf_service_day.duckdb`: `malf_wave_position`, `malf_wave_position_latest` | `scripts/malf/run_malf_day_service_build.py` | WavePosition 自然键唯一；latest 每个 `symbol + timeframe + service_version` 只有一行 | `governance/module_api_contracts/malf.toml` |
| MALF 不输出策略动作、仓位、订单或回写入口 | `malf_wave_position` 只含结构与 lifespan 事实字段；无 buy/sell/weight/order 字段 | `scripts/malf/run_malf_day_service_build.py` | module API contract forbidden outputs；pre-gate 下游不得写回 MALF | `governance/module_api_contracts/alpha.toml`, `governance/module_api_contracts/malf.toml` |
| MALF day proof 只放行 Alpha freeze review | no schema change | no runner change | conclusion allowed next action 必须为 `Alpha freeze review`；registry next_card 必须为 `alpha_freeze_review` | `docs/04-execution/00-conclusion-index-v1.md`, `governance/module_gate_registry.toml` |

## 4. Alpha freeze review 使用方式

Alpha freeze review 只能引用本附件来确认：

1. Alpha 是否只读消费 `malf_wave_position` / `malf_wave_position_latest`。
2. Alpha 是否避免重定义 `wave_core_state`、`system_state`、`direction`、`no_new_span`
   和 `transition_span`。
3. Alpha 是否没有创建 MALF 回写入口、正式 Alpha DB 或 Alpha runner。
4. Alpha freeze review 是否基于 `pending Alpha freeze review conclusion` 作出冻结裁决。

本附件不能被解释为 Alpha 施工卡、Alpha schema 冻结或下游模块放行。
