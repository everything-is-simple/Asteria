# v1-vectorbt-portfolio-analytics-proof-card-20260514-01 Evidence Index

| Evidence | Path | Purpose |
|---|---|---|
| Runner | `src/asteria/pipeline/v1_vectorbt_portfolio_analytics_proof.py` | Executes the read-only vectorbt portfolio analytics proof |
| Artifact IO | `src/asteria/pipeline/v1_vectorbt_portfolio_analytics_proof_io.py` | Writes manifest, report, closeout, temp manifest, and validated archive |
| Contracts | `src/asteria/pipeline/v1_vectorbt_portfolio_analytics_proof_contracts.py` | Freezes run id, request, summary, and next route constants |
| Renderer | `src/asteria/pipeline/v1_vectorbt_portfolio_analytics_proof_render.py` | Renders manifest, report, and closeout |
| CLI | `scripts/pipeline/run_v1_vectorbt_portfolio_analytics_proof.py` | Runs the proof from the command line |
| Dependency | `pyproject.toml` | Adds `vectorbt>=1.0.0` |
| Runner allowlist | `src/asteria/governance/pipeline_runner_surface.py` | Allows the new post-terminal pipeline runner |
| Roadmap | `docs/03-refactor/05-asteria-v1-usage-validation-roadmap-v1.md` | Records passed status and next route card |
| Gate ledger | `docs/03-refactor/00-module-gate-ledger-v1.md` | Preserves terminal live truth and records route status |
| Conclusion index | `docs/04-execution/00-conclusion-index-v1.md` | Registers this card conclusion |
| Unit test | `tests/unit/pipeline/test_v1_vectorbt_portfolio_analytics_proof.py` | Verifies runner behavior and blocked paths |
| Governance test | `tests/unit/governance/test_v1_vectorbt_portfolio_analytics_proof_route.py` | Verifies route governance registration |
| Runner surface test | `tests/unit/pipeline/test_runner_surface.py` | Verifies runner allowlist |
| Report manifest | `H:\Asteria-report\pipeline\2026-05-14\v1-vectorbt-portfolio-analytics-proof-card-20260514-01\vectorbt-portfolio-analytics-manifest.json` | Machine-readable formal proof result |
| Human report | `H:\Asteria-report\pipeline\2026-05-14\v1-vectorbt-portfolio-analytics-proof-card-20260514-01\vectorbt-portfolio-analytics-report.md` | Human-readable portfolio analytics report |
| Closeout | `H:\Asteria-report\pipeline\2026-05-14\v1-vectorbt-portfolio-analytics-proof-card-20260514-01\closeout.md` | Formal closeout summary |
| Temp manifest | `H:\Asteria-temp\pipeline\v1-vectorbt-portfolio-analytics-proof-card-20260514-01\vectorbt-portfolio-analytics-temp-manifest.json` | Run-scoped temp manifest |
| Validated zip | `H:\Asteria-Validated\Asteria-v1-vectorbt-portfolio-analytics-proof-card-20260514-01.zip` | Archived evidence package |
