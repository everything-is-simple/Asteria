# Downstream Daily Impact Ledger Schema Card Record

日期：2026-05-11

## 1. 卡信息

| 项 | 值 |
|---|---|
| module | `pipeline` |
| run_id | `downstream-daily-impact-ledger-schema-card` |
| result | `passed / downstream daily impact schema frozen` |
| next allowed action | `downstream_daily_incremental_runner_build_card` |

## 2. 执行顺序

1. 更新 `governance/module_api_contracts/{position,portfolio_plan,trade,system_readout,pipeline}.toml`，冻结 downstream Stage 11 `daily_protocol_*` 字段。
2. 更新 `governance/database_topology_registry.toml`，把 `position / portfolio_plan / trade / system` 的 future checkpoint / replay scope 收口到 `symbol + trade_date + source_run_id`。
3. 更新 `governance/module_gate_registry.toml`、`docs/03-refactor/00-module-gate-ledger-v1.md`、`docs/04-execution/00-conclusion-index-v1.md`、`docs/03-refactor/04-asteria-full-system-roadmap-v1.md` 与 `docs/02-modules/pipeline/00-authority-design-v1.md`，把 live next 前推到 `downstream_daily_incremental_runner_build_card`。
4. 更新 Position / Portfolio Plan / Trade / System Readout 的 schema spec，明确 Stage 11 daily impact map、日期锚点与 non-goals。
5. 生成本卡 `record / conclusion / evidence-index`，并创建 prepared next card `downstream-daily-incremental-runner-build-card.card.md`。

## 3. 关键验证

| 验证 | 结果 |
|---|---|
| `tests\unit\governance\test_downstream_daily_impact_ledger_schema_gate_transition.py` | `passed` |
| `tests\unit\governance\test_alpha_signal_daily_incremental_ledger_gate_transition.py` | `passed` |
| `tests\unit\governance\test_stage11_daily_dirty_scope_protocol_gate_transition.py` | `passed` |
| `python scripts\governance\check_project_governance.py` | `passed` |

## 4. 边界

- 本卡只冻结 contract / governance / design，不执行 Position / Portfolio Plan / Trade / System Readout daily runtime。
- 本卡不新增 downstream runner、CLI、temp DB proof，也不修改正式 `H:\Asteria-data`。
- 本卡不改业务自然键；`daily impact map` 只是协议层映射，不把业务主键改写为 `trade_date + symbol`。
- `portfolio_trim_ledger` 继续继承父 `portfolio_admission.plan_dt`；`summary_dt / audit_dt` 继续只保留辅助审计角色。
