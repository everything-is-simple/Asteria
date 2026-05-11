# Pipeline Year Replay Disposition Decision Record

日期：2026-05-11

run_id：`pipeline-year-replay-disposition-decision-card-20260510-01`

## 1. Inputs

- `docs/04-execution/records/pipeline/pipeline-year-replay-source-selection-repair-card-20260509-01.conclusion.md`
- `docs/04-execution/records/pipeline/pipeline-year-replay-disposition-decision-card-20260510-01.card.md`
- `docs/04-execution/records/pipeline/pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01.conclusion.md`
- `docs/03-refactor/04-asteria-full-system-roadmap-v1.md`
- `governance/module_gate_registry.toml`
- `governance/module_api_contracts/pipeline.toml`
- `H:\Asteria-data\system.duckdb`

## 2. Formal Execution

| stage | command summary |
|---|---|
| disposition decision | `run_pipeline_year_replay_disposition_decision.py --run-id pipeline-year-replay-disposition-decision-card-20260510-01 --target-year 2024` |
| released-source resolver | read latest completed `system_readout_run` and current `system_source_manifest` from released `system.duckdb` |
| source-selection truth | read `pipeline-year-replay-source-selection-repair-card-20260509-01.conclusion.md` |
| live gate / contract check | read `module_gate_registry.toml` and `module_api_contracts/pipeline.toml` |
| Stage 11 backlog check | read `04-asteria-full-system-roadmap-v1.md` |

## 3. Disposition Result

- released `system_readout_run` 仍是 `system-readout-bounded-proof-build-card-20260508-01`。
- released observed window 已覆盖 `2024-01-02..2024-12-31`。
- MALF source lock 已真实指向 repaired MALF released run。
- follow-up attribution 仍为 `calendar_semantic_gap_only`，说明剩余问题不再是 released surface gap。
- 当前 full-year audit 仍硬要求 `2024-01-01..2024-12-31`；因此此刻再跑一次 rerun 只会重复触发同一个 coverage fail，不会产生新信息。
- 本卡据此裁定：不 rerun，做 truthful closeout，并把后续长期能力问题转入 Stage 11。

## 4. Live Truth Update

1. 关闭 `pipeline_year_replay_disposition_decision_card` 的 prepared 状态。
2. 将顶层 live `current_allowed_next_card` 与 Pipeline / System Readout follow-up next card 同步切换为
   `system_wide_daily_dirty_scope_protocol_card`。
3. 将 Pipeline 当前 active card / proof run / release conclusion / evidence index 同步到
   `pipeline-year-replay-disposition-decision-card-20260510-01`。
4. 创建 Stage 11 入口 prepared card：
   `system-wide-daily-dirty-scope-protocol-card`。

## 5. Boundary

- 本卡不宣称 year replay passed。
- 本卡不改 `pipeline_year_replay_full_year_coverage` 的 audit 规则。
- 本卡不重开 `year_replay_rerun`、System full build、Pipeline semantic repair、full rebuild、daily incremental 或 `v1 complete`。
