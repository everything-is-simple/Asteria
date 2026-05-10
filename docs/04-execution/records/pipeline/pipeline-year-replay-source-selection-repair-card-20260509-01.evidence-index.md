# Pipeline Year Replay Source Selection Repair Evidence Index

日期：2026-05-10

## 1. Repo Evidence

| evidence | path |
|---|---|
| card | `docs/04-execution/records/pipeline/pipeline-year-replay-source-selection-repair-card-20260509-01.card.md` |
| record | `docs/04-execution/records/pipeline/pipeline-year-replay-source-selection-repair-card-20260509-01.record.md` |
| conclusion | `docs/04-execution/records/pipeline/pipeline-year-replay-source-selection-repair-card-20260509-01.conclusion.md` |
| next prepared card | `docs/04-execution/records/pipeline/pipeline-year-replay-disposition-decision-card-20260510-01.card.md` |
| conclusion index | `docs/04-execution/00-conclusion-index-v1.md` |
| gate ledger | `docs/03-refactor/00-module-gate-ledger-v1.md` |
| roadmap | `docs/03-refactor/04-asteria-full-system-roadmap-v1.md` |
| governance registry | `governance/module_gate_registry.toml` |
| Pipeline module contract | `governance/module_api_contracts/pipeline.toml` |
| released-source resolver | `src/asteria/pipeline/released_source_selection.py` |
| repair implementation | `src/asteria/pipeline/year_replay_source_selection_repair.py` |
| repair contracts | `src/asteria/pipeline/year_replay_source_selection_repair_contracts.py` |
| repair CLI | `scripts/pipeline/run_pipeline_year_replay_source_selection_repair.py` |
| unit coverage | `tests/unit/pipeline/test_pipeline_year_replay_source_selection_repair.py` |

## 2. External Evidence

| evidence | path |
|---|---|
| closeout | `H:\Asteria-report\pipeline\2026-05-10\pipeline-year-replay-source-selection-repair-card-20260509-01\closeout.md` |
| manifest | `H:\Asteria-report\pipeline\2026-05-10\pipeline-year-replay-source-selection-repair-card-20260509-01\manifest.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-pipeline-year-replay-source-selection-repair-card-20260509-01.zip` |

## 3. Boundary

本证据只证明 Pipeline source-selection / source-lock 已修回当前 released System truth，并把 live 下一卡切到 disposition decision。它不证明 rerun 已执行，也不替代 disposition 裁决。
