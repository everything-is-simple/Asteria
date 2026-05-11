# Pipeline Year Replay Disposition Decision Evidence Index

日期：2026-05-11

run_id：`pipeline-year-replay-disposition-decision-card-20260510-01`

## 1. Runtime Evidence

| artifact | path |
|---|---|
| manifest | `H:\Asteria-report\pipeline\2026-05-10\pipeline-year-replay-disposition-decision-card-20260510-01\manifest.json` |
| closeout | `H:\Asteria-report\pipeline\2026-05-10\pipeline-year-replay-disposition-decision-card-20260510-01\closeout.md` |
| validated_zip | `H:\Asteria-Validated\Asteria-pipeline-year-replay-disposition-decision-card-20260510-01.zip` |

## 2. Repo Evidence

| file | role |
|---|---|
| `src/asteria/pipeline/year_replay_disposition_decision_contracts.py` | disposition request / summary contract |
| `src/asteria/pipeline/year_replay_disposition_decision.py` | read-only disposition implementation |
| `scripts/pipeline/run_pipeline_year_replay_disposition_decision.py` | disposition CLI |
| `tests/unit/pipeline/test_pipeline_year_replay_disposition_decision.py` | decision logic coverage |
| `tests/unit/governance/test_pipeline_year_replay_disposition_decision_gate_transition.py` | live next-card transition coverage |
| `governance/module_gate_registry.toml` | live next-card and Pipeline active-card truth |
| `governance/module_api_contracts/pipeline.toml` | Pipeline next action / gate_state truth |
| `docs/03-refactor/00-module-gate-ledger-v1.md` | current live gate summary |
| `docs/03-refactor/04-asteria-full-system-roadmap-v1.md` | Stage 11 backlog authority |
| `docs/04-execution/00-conclusion-index-v1.md` | passed conclusion and live next card index |
| `docs/04-execution/records/pipeline/system-wide-daily-dirty-scope-protocol-card.card.md` | newly prepared Stage 11 entry card |

## 3. Upstream Evidence

| file | purpose |
|---|---|
| `docs/04-execution/records/pipeline/pipeline-year-replay-source-selection-repair-card-20260509-01.conclusion.md` | confirmed `source_lock_clean = true` and `follow-up attribution = calendar_semantic_gap_only` |
| `docs/04-execution/records/pipeline/pipeline-one-year-strategy-behavior-replay-rerun-build-card-20260509-01.conclusion.md` | preserved historical blocked rerun truth |
