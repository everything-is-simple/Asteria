# Formal Full Rebuild And Daily Incremental Release Proof Card Evidence Index

日期：2026-05-12

## 1. Runtime Evidence Shape

| evidence | path |
|---|---|
| closeout | `H:\Asteria-report\pipeline\2026-05-12\formal-full-rebuild-and-daily-incremental-release-proof-card\closeout.md` |
| manifest | `H:\Asteria-Validated\Asteria-formal-full-rebuild-and-daily-incremental-release-proof-card-manifest.json` |
| validated_zip | `H:\Asteria-Validated\Asteria-formal-full-rebuild-and-daily-incremental-release-proof-card-20260512-01.zip` |

| evidence | role |
|---|---|
| `H:\Asteria-temp\formal-release-source-proof\formal-release-source-proof-20260512-01\source-surface-audit.json` | source surface audit |
| `H:\Asteria-temp\formal-release-source-proof\formal-release-source-proof-20260512-01\source-proof-summary.json` | source proof summary |
| `H:\Asteria-temp\formal-release-source-proof\formal-release-source-proof-20260512-01\formal-release-proof-manifest.json` | source proof manifest |
| `H:\Asteria-report\pipeline\2026-05-12\formal-release-source-proof-20260512-01\summary.json` | source proof report summary |
| `H:\Asteria-report\pipeline\2026-05-12\formal-full-rebuild-and-daily-incremental-release-proof-card\summary.json` | proof summary |
| `H:\Asteria-report\pipeline\2026-05-12\formal-full-rebuild-and-daily-incremental-release-proof-card\closeout.md` | proof closeout |
| `H:\Asteria-temp\formal-release-proof\formal-full-rebuild-and-daily-incremental-release-proof-card\db-manifest.json` | DB manifest |
| `H:\Asteria-temp\formal-release-proof\formal-full-rebuild-and-daily-incremental-release-proof-card\backup-manifest.json` | backup manifest |
| `H:\Asteria-temp\formal-release-proof\formal-full-rebuild-and-daily-incremental-release-proof-card\staging-manifest.json` | staging manifest |
| `H:\Asteria-temp\formal-release-proof\formal-full-rebuild-and-daily-incremental-release-proof-card\promote-manifest.json` | promote manifest |
| `H:\Asteria-temp\formal-release-proof\formal-full-rebuild-and-daily-incremental-release-proof-card\resume-idempotence-manifest.json` | resume/idempotence manifest |
| `H:\Asteria-temp\formal-release-proof\formal-full-rebuild-and-daily-incremental-release-proof-card\final-release-evidence.json` | final release evidence |
| `H:\Asteria-Validated\Asteria-formal-full-rebuild-and-daily-incremental-release-proof-card-manifest.json` | validated manifest |
| `H:\Asteria-Validated\Asteria-formal-full-rebuild-and-daily-incremental-release-proof-card-20260512-01.zip` | validated archive |

## 2. Repo Evidence

| evidence | role |
|---|---|
| `src/asteria/pipeline/formal_release_source_proof.py` | source surface gap matrix runner |
| `scripts/pipeline/run_formal_release_source_proof.py` | source surface proof CLI entrypoint |
| `src/asteria/pipeline/formal_release_proof.py` | guarded proof runner |
| `scripts/pipeline/run_formal_release_proof.py` | CLI entrypoint |
| `tests/unit/pipeline/test_formal_release_source_proof.py` | source surface matrix coverage |
| `tests/unit/pipeline/test_formal_release_proof.py` | runner and CLI coverage |
| `tests/unit/pipeline/test_runner_surface.py` | runner allowlist coverage |
| `tests/unit/governance/test_formal_release_proof_gate_transition.py` | governance transition coverage |
| `governance/module_gate_registry.toml` | live next-card authority |
| `governance/module_api_contracts/pipeline.toml` | Pipeline contract authority |

## 3. Proof Result

| proof | evidence state |
|---|---|
| source surface gap matrix | `passed` |
| formal full rebuild proof | `passed` |
| daily incremental release proof | `passed` |
| resume/idempotence release proof | `passed` |
| final release evidence complete | `passed` |
| System full build | not claimed |
| `v1 complete` | not claimed |
