# Coverage Gap Evidence Incomplete Closeout Evidence Index

日期：2026-05-09

## 1. Repo Evidence

| asset | role |
|---|---|
| `src/asteria/pipeline/downstream_coverage_gap_closeout.py` | downstream closeout decision and artifact writer |
| `src/asteria/pipeline/downstream_coverage_gap_closeout_contracts.py` | closeout request/summary contracts |
| `src/asteria/pipeline/system_probe_diagnosis.py` | shared temp system probe builder and diagnosis runner |
| `scripts/pipeline/run_downstream_coverage_gap_closeout.py` | closeout CLI |
| `tests/unit/pipeline/test_downstream_coverage_gap_closeout.py` | downstream closeout decision coverage |
| `governance/module_gate_registry.toml` | live next-card handoff to Position repair |
| `governance/module_api_contracts/pipeline.toml` | Pipeline contract-side next action and gate state sync |
| `docs/04-execution/records/position/position-2024-coverage-repair-card-20260509-01.card.md` | prepared next repair card |

## 2. External Evidence

| evidence | path |
|---|---|
| closeout | `H:\Asteria-report\pipeline\2026-05-09\coverage-gap-evidence-incomplete-closeout-card-20260509-01\closeout.md` |
| manifest | `H:\Asteria-report\pipeline\2026-05-09\coverage-gap-evidence-incomplete-closeout-card-20260509-01\manifest.json` |
| probe_manifest | `H:\Asteria-report\pipeline\2026-05-09\coverage-gap-evidence-incomplete-closeout-card-20260509-01\probe-manifest.json` |
| coverage_matrix | `H:\Asteria-report\pipeline\2026-05-09\coverage-gap-evidence-incomplete-closeout-card-20260509-01\coverage-matrix.json` |
| coverage_attribution | `H:\Asteria-report\pipeline\2026-05-09\coverage-gap-evidence-incomplete-closeout-card-20260509-01\coverage-attribution.md` |
| validated_zip | `H:\Asteria-Validated\Asteria-coverage-gap-evidence-incomplete-closeout-card-20260509-01.zip` |

## 3. Decision

| item | value |
|---|---|
| probe diagnosis run_id | `coverage-gap-evidence-incomplete-closeout-card-20260509-01-system-probe-diagnosis` |
| probe diagnosis recommended_next_card | `coverage-gap-evidence-incomplete-closeout-card-20260509-01` |
| closeout next card | `position-2024-coverage-repair-card-20260509-01` |
| closeout attribution | `downstream_surface_gap:position` |
| evidence issues | `none` |
