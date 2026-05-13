# V1 Application DB Readiness Audit Evidence Index

日期：2026-05-13

run_id：`v1-application-db-readiness-audit-card-20260513-01`

## 1. Runtime Evidence

| artifact | path |
|---|---|
| DB readiness manifest | `H:\Asteria-report\pipeline\2026-05-13\v1-application-db-readiness-audit-card-20260513-01\db-readiness-manifest.json` |
| closeout | `H:\Asteria-report\pipeline\2026-05-13\v1-application-db-readiness-audit-card-20260513-01\closeout.md` |
| validated_zip | `H:\Asteria-Validated\Asteria-v1-application-db-readiness-audit-card-20260513-01.zip` |

## 2. Repo Evidence

| file | role |
|---|---|
| `src/asteria/pipeline/v1_application_db_readiness_audit_contracts.py` | DB inventory and readiness contract |
| `src/asteria/pipeline/v1_application_db_readiness_audit.py` | read-only audit implementation |
| `scripts/pipeline/run_v1_application_db_readiness_audit.py` | audit CLI |
| `tests/unit/pipeline/test_v1_application_db_readiness_audit.py` | runner behavior coverage |
| `tests/unit/governance/test_v1_application_db_readiness_audit_route.py` | roadmap route and terminal live-next preservation coverage |
| `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md` | roadmap route authority and audit result |
| `docs/04-execution/00-conclusion-index-v1.md` | repo conclusion registration with terminal live-next preserved |
| `docs/04-execution/records/pipeline/v1-application-db-readiness-audit-card-20260513-01.card.md` | audit card truth |
| `docs/04-execution/records/pipeline/v1-application-db-readiness-audit-card-20260513-01.record.md` | execution record |
| `docs/04-execution/records/pipeline/v1-application-db-readiness-audit-card-20260513-01.conclusion.md` | final route conclusion |

## 3. Source Evidence

| source | purpose |
|---|---|
| `H:\Asteria-data\*.duckdb` | current 25 formal DB read-only audit source |
| `governance/module_gate_registry.toml` | terminal live-next preservation proof |
| `docs/04-execution/records/pipeline/v1-usage-validation-scope-card-20260512-01.conclusion.md` | predecessor scope freeze proof |

## 4. Non-Evidence

本卡不提供：

- 对 `H:\Asteria-data` 的 rebuild、补写或 promote；
- `fill_ledger` 真实成交闭环；
- ST、停牌、完整上市退市或历史行业沿革的新增正式 coverage；
- `v1-usage-readout-report-card` 的人读报告；
- 日更生产化范围冻结或 activation 证据。
