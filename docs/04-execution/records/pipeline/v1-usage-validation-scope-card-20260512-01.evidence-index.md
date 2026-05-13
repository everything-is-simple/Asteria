# V1 Usage Validation Scope Evidence Index

日期：2026-05-12

run_id：`v1-usage-validation-scope-card-20260512-01`

## 1. Runtime Evidence

| artifact | path |
|---|---|
| scope manifest | `H:\Asteria-report\pipeline\2026-05-13\v1-usage-validation-scope-card-20260512-01\scope-manifest.json` |
| closeout | `H:\Asteria-report\pipeline\2026-05-13\v1-usage-validation-scope-card-20260512-01\closeout.md` |
| validated_zip | `H:\Asteria-Validated\Asteria-v1-usage-validation-scope-card-20260512-01.zip` |

## 2. Repo Evidence

| file | role |
|---|---|
| `src/asteria/pipeline/v1_usage_validation_scope_contracts.py` | scope freeze request / summary contract |
| `src/asteria/pipeline/v1_usage_validation_scope.py` | read-only industry selection and artifact writer |
| `scripts/pipeline/run_v1_usage_validation_scope.py` | scope freeze CLI |
| `tests/unit/pipeline/test_v1_usage_validation_scope.py` | selection logic and manual override coverage |
| `tests/unit/governance/test_v1_usage_validation_scope_route.py` | terminal live-next preservation and docs registration coverage |
| `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md` | roadmap route authority and frozen scope result |
| `docs/04-execution/00-conclusion-index-v1.md` | repo conclusion registration with terminal live-next preserved |
| `docs/04-execution/records/pipeline/v1-usage-validation-scope-card-20260512-01.card.md` | scope card truth |
| `docs/04-execution/records/pipeline/v1-usage-validation-scope-card-20260512-01.record.md` | execution record |
| `docs/04-execution/records/pipeline/v1-usage-validation-scope-card-20260512-01.conclusion.md` | final route conclusion |

## 3. Source Evidence

| file | purpose |
|---|---|
| `H:\Asteria-data\market_meta.duckdb` | released `industry_classification` and `instrument_master` source |
| `H:\Asteria-data\market_base_day.duckdb` | released execution-line amount and coverage source |
| `H:\Asteria-Validated\MALF-reference\申万行业分类\最新个股申万行业分类(完整版-截至7月末).xlsx` | external Shenwan classification reference for current snapshot naming |

## 4. Non-Evidence

本卡不提供：

- 对 `H:\Asteria-data` 的 rebuild、补写或 promote；
- ST、停牌、完整上市退市或历史行业沿革的新增正式 coverage；
- `v1-application-db-readiness-audit-card` 的执行结果；
- 日更生产化范围冻结或 activation 证据。
