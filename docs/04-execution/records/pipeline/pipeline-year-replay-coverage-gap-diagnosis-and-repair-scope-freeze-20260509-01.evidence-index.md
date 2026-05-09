# Pipeline Year Replay Coverage Gap Diagnosis Evidence Index

日期：2026-05-09

## 1. Execution Summary

| item | value |
|---|---|
| module | `pipeline` |
| run_id | `pipeline-year-replay-coverage-gap-diagnosis-and-repair-scope-freeze-20260509-01` |
| target_year | `2024` |
| status | `passed` |
| released_system_run_id | `system-readout-bounded-proof-build-card-20260508-01` |
| recommended_next_card | `malf-2024-natural-year-coverage-repair-card-20260509-01` |

## 2. Report Evidence

| asset | path |
|---|---|
| closeout | `H:\Asteria-report\pipeline\2026-05-09\pipeline-year-replay-coverage-gap-diagnosis-and-repair-scope-freeze-20260509-01\closeout.md` |
| manifest | `H:\Asteria-report\pipeline\2026-05-09\pipeline-year-replay-coverage-gap-diagnosis-and-repair-scope-freeze-20260509-01\manifest.json` |
| coverage_matrix | `H:\Asteria-report\pipeline\2026-05-09\pipeline-year-replay-coverage-gap-diagnosis-and-repair-scope-freeze-20260509-01\coverage-matrix.json` |
| coverage_attribution | `H:\Asteria-report\pipeline\2026-05-09\pipeline-year-replay-coverage-gap-diagnosis-and-repair-scope-freeze-20260509-01\coverage-attribution.md` |
| validated_zip | `H:\Asteria-Validated\Asteria-pipeline-year-replay-coverage-gap-diagnosis-and-repair-scope-freeze-20260509-01.zip` |

## 3. Repo Evidence

| file | role |
|---|---|
| `src/asteria/pipeline/year_replay_coverage_gap_diagnosis.py` | read-only diagnosis implementation |
| `scripts/pipeline/run_year_replay_coverage_gap_diagnosis.py` | diagnosis CLI |
| `tests/unit/pipeline/test_year_replay_coverage_gap_diagnosis.py` | attribution decision coverage |
| `governance/module_gate_registry.toml` | live next-card and pipeline active-card truth |
| `docs/04-execution/records/malf/malf-2024-natural-year-coverage-repair-card-20260509-01.card.md` | unique prepared next card |
