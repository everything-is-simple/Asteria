# V1 Usage Value Decision Evidence Index

日期：2026-05-13

run_id：`v1-usage-value-decision-card-20260513-01`

## 1. Status

`passed / usage value decision completed`

## 2. Repo Evidence

| file | role |
|---|---|
| `src/asteria/pipeline/v1_usage_value_decision_contracts.py` | value decision request / summary contract |
| `src/asteria/pipeline/v1_usage_value_decision.py` | read-only decision implementation |
| `src/asteria/pipeline/v1_usage_value_decision_render.py` | report/closeout rendering helper |
| `scripts/pipeline/run_v1_usage_value_decision.py` | decision CLI |
| `tests/unit/pipeline/test_v1_usage_value_decision.py` | runner behavior coverage |
| `tests/unit/governance/test_v1_usage_value_decision_route.py` | route and terminal live-next preservation coverage |
| `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md` | roadmap route authority and decision result |

## 3. External Evidence

| source | purpose |
|---|---|
| `H:\Asteria-report\pipeline\2026-05-13\v1-usage-readout-report-card-20260513-01\usage-readout-manifest.json` | source usage readout input |
| `H:\Asteria-report\pipeline\2026-05-13\v1-downstream-reference-audit-20260513-01\downstream-reference-audit-manifest.json` | supplemental downstream semantics input |
| `H:\Asteria-report\pipeline\2026-05-13\v1-usage-value-decision-card-20260513-01\usage-value-decision-manifest.json` | machine-readable value decision output |
| `H:\Asteria-report\pipeline\2026-05-13\v1-usage-value-decision-card-20260513-01\usage-value-decision-report.md` | human-readable value decision report |
| `H:\Asteria-report\pipeline\2026-05-13\v1-usage-value-decision-card-20260513-01\closeout.md` | external closeout |
| `H:\Asteria-Validated\Asteria-v1-usage-value-decision-card-20260513-01.zip` | validated archive |

## 4. Non-Evidence

本卡不提供：

- 对 `H:\Asteria-data` 的 rebuild、补写或 promote；
- 收益回测或 PnL attribution；
- `fill_ledger` 真实成交闭环；
- broker adapter 或实盘交易能力；
- production daily incremental activation。
