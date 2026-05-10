# Pipeline Year Replay Source Selection Repair Record

日期：2026-05-10

run_id：`pipeline-year-replay-source-selection-repair-card-20260509-01`

## 1. Inputs

- `docs/04-execution/records/pipeline/pipeline-system-readout-2024-coverage-repair-handoff-20260510-01.conclusion.md`
- `docs/04-execution/records/pipeline/pipeline-year-replay-source-selection-repair-card-20260509-01.card.md`
- `governance/module_gate_registry.toml`
- `governance/module_api_contracts/pipeline.toml`
- `H:\Asteria-data\system.duckdb`

## 2. Formal Execution

| stage | command summary |
|---|---|
| source-selection repair | `run_pipeline_year_replay_source_selection_repair.py --run-id pipeline-year-replay-source-selection-repair-card-20260509-01 --target-year 2024` |
| released-source resolver | read latest completed `system_readout_run` and current `system_source_manifest` from released `system.duckdb` |
| follow-up diagnosis | `run_year_replay_coverage_gap_diagnosis(...)` on released System Readout truth |

## 3. Repair Result

- released `system_readout_run` 仍是 `system-readout-bounded-proof-build-card-20260508-01`，本卡没有改写 System truth。
- released observed window 已覆盖 `2024-01-02..2024-12-31`。
- MALF source lock 已真实指向 `malf-2024-natural-year-coverage-repair-card-20260509-01-batch-0001`。
- 下游 released source selection 已消费当前 repaired manifest，不再回落到旧 rerun 阶段的 locked source 假设。
- follow-up attribution 仍为 `calendar_semantic_gap_only`，说明 source-selection repair 已完成自身边界，不替代后续 disposition 决策。

## 4. Live Truth Update

1. 关闭 `pipeline_year_replay_source_selection_repair_card` 的 prepared 状态。
2. 将 Pipeline 当前唯一 prepared next card 切换为
   `pipeline-year-replay-disposition-decision-card-20260510-01`。
3. 同步 registry、Pipeline module contract、gate ledger、conclusion index 与 roadmap。

## 5. Boundary

- 本卡不执行 blocked replay rerun。
- 本卡不打开 System full build、Pipeline semantic repair、full rebuild、daily incremental。
- 本卡不裁定最终应该 rerun、closeout 还是进入 Stage 11；那是下一张 disposition decision card 的职责。
