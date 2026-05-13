# V1 Usage Readout Report Evidence Index

日期：2026-05-13

run_id：`v1-usage-readout-report-card-20260513-01`

## 1. Runtime Evidence

| artifact | path |
|---|---|
| usage readout manifest | `H:\Asteria-report\pipeline\2026-05-13\v1-usage-readout-report-card-20260513-01\usage-readout-manifest.json` |
| human readout report | `H:\Asteria-report\pipeline\2026-05-13\v1-usage-readout-report-card-20260513-01\usage-readout-report.md` |
| closeout | `H:\Asteria-report\pipeline\2026-05-13\v1-usage-readout-report-card-20260513-01\closeout.md` |
| temp manifest | `H:\Asteria-temp\pipeline\v1-usage-readout-report-card-20260513-01\usage-readout-temp-manifest.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-v1-usage-readout-report-card-20260513-01.zip` |

## 2. Repo Evidence

| file | role |
|---|---|
| `src/asteria/pipeline/v1_usage_readout_report_contracts.py` | readout report route contract and table specs |
| `src/asteria/pipeline/v1_usage_readout_report.py` | read-only report implementation |
| `src/asteria/pipeline/v1_usage_readout_report_render.py` | report/closeout rendering helper |
| `scripts/pipeline/run_v1_usage_readout_report.py` | readout CLI |
| `tests/unit/pipeline/test_v1_usage_readout_report.py` | runner behavior coverage |
| `tests/unit/governance/test_v1_usage_readout_report_route.py` | route and terminal live-next preservation coverage |
| `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md` | roadmap route authority and readout result |
| `docs/04-execution/00-conclusion-index-v1.md` | repo conclusion registration with terminal live-next preserved |
| `docs/04-execution/records/pipeline/v1-usage-readout-report-card-20260513-01.card.md` | readout card truth |
| `docs/04-execution/records/pipeline/v1-usage-readout-report-card-20260513-01.record.md` | execution record |
| `docs/04-execution/records/pipeline/v1-usage-readout-report-card-20260513-01.conclusion.md` | final route conclusion |

## 3. Source Evidence

| source | purpose |
|---|---|
| `H:\Asteria-report\pipeline\2026-05-12\v1-usage-validation-scope-card-20260512-01\scope-manifest.json` | frozen 31-symbol read-only usage validation scope |
| `H:\Asteria-data\*.duckdb` | current 25 formal DB read-only source |
| `governance/module_gate_registry.toml` | terminal live-next preservation proof |
| `docs/04-execution/records/pipeline/v1-application-db-readiness-audit-card-20260513-01.conclusion.md` | predecessor DB readiness proof |

## 4. Non-Evidence

本卡不提供：

- 对 `H:\Asteria-data` 的 rebuild、补写或 promote；
- `fill_ledger` 真实成交闭环；
- ST、停牌、完整上市退市或历史行业沿革的新增正式 coverage；
- v1 使用价值裁决；
- 日更生产化范围冻结或 activation 证据。
