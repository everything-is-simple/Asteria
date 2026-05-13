# V1 Downstream Reference Audit Evidence Index

日期：2026-05-13

## 1. External Evidence

| artifact | role |
|---|---|
| `H:\Asteria-report\pipeline\2026-05-13\v1-downstream-reference-audit-20260513-01\downstream-reference-audit-report.md` | human downstream semantics benchmark report |
| `H:\Asteria-report\pipeline\2026-05-13\v1-downstream-reference-audit-20260513-01\downstream-reference-audit-manifest.json` | machine-readable benchmark manifest |
| `H:\Asteria-report\pipeline\2026-05-13\v1-downstream-reference-audit-20260513-01\closeout.md` | external closeout summary |
| `H:\Asteria-temp\pipeline\v1-downstream-reference-audit-20260513-01\downstream-reference-audit-temp-manifest.json` | run-scoped temp manifest |
| `H:\Asteria-Validated\Asteria-v1-downstream-reference-audit-20260513-01.zip` | validated archive |

## 2. Repo Evidence

| file | role |
|---|---|
| `src/asteria/pipeline/v1_downstream_reference_audit_contracts.py` | supplemental audit contract and benchmark rows |
| `src/asteria/pipeline/v1_downstream_reference_audit.py` | read-only audit implementation |
| `src/asteria/pipeline/v1_downstream_reference_audit_render.py` | report and closeout rendering helper |
| `scripts/pipeline/run_downstream_reference_audit.py` | CLI wrapper |
| `src/asteria/governance/pipeline_runner_surface.py` | pipeline runner allowlist |
| `tests/unit/pipeline/test_v1_downstream_reference_audit.py` | runner behavior coverage |
| `tests/unit/governance/test_v1_downstream_reference_audit_route.py` | route and supplemental recording coverage |
| `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md` | route authority and supplemental input entry |

## 3. Source References

| source | role |
|---|---|
| `https://github.com/fasiondog/hikyuu` | system trading component decomposition reference |
| `https://hikyuu.readthedocs.io/zh-cn/latest/trade_sys/system.html` | SYS / Signal / MoneyManager / Slippage / TradeRequest reference |
| `https://hikyuu.readthedocs.io/zh-cn/latest/trade_portfolio/trade_portfolio.html` | PF / selector / allocation reference |
| `https://github.com/everything-is-simple/finhack` | research to backtest to live access workflow reference |
| `https://easytrader.readthedocs.io/zh-cn/master/miniqmt/` | broker order / entrust / trade callback boundary reference |

## 4. Boundary

This evidence set is read-only. It does not mutate `H:\Asteria-data`, does not reopen
live next, and does not redefine downstream business semantics.
